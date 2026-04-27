

"""
使用 GeoHash + Redis ZSet 实现附近的人检索。
核心思路：
1) 单 ZSet 存 user_id，score 为 geohash(base32) 转整数；
2) Hash 存每个用户经纬度详情；
3) 查询时先按 geohash score 范围粗筛，再按Hash中真实距离精筛。
"""

from __future__ import annotations

import math
import time
from typing import Any, Dict, List, Tuple

try:
    import geohash as geohash_lib  # type: ignore[reportMissingImports]  # pip install geohash2
except ImportError:
    geohash_lib = None

try:
    import redis  # type: ignore[reportMissingImports]  # pip install redis
except ImportError:
    redis = None


BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
BITS = [16, 8, 4, 2, 1]


def geohash_encode(lat: float, lon: float, precision: int = 7) -> str:
    """将经纬度编码为 geohash。"""
    lat_min, lat_max = -90.0, 90.0
    lon_min, lon_max = -180.0, 180.0
    is_even = True
    bit = 0
    ch = 0
    result: List[str] = []

    while len(result) < precision:
        if is_even:
            mid = (lon_min + lon_max) / 2
            if lon >= mid:
                ch |= BITS[bit]
                lon_min = mid
            else:
                lon_max = mid
        else:
            mid = (lat_min + lat_max) / 2
            if lat >= mid:
                ch |= BITS[bit]
                lat_min = mid
            else:
                lat_max = mid

        is_even = not is_even
        if bit < 4:
            bit += 1
        else:
            result.append(BASE32[ch])
            bit = 0
            ch = 0

    return "".join(result)


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """计算两点球面距离（米）。"""
    r = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def geohash_cell_size_deg(precision: int) -> Tuple[float, float]:
    """
    返回给定 geohash 精度下，单元格的近似 (纬度跨度, 经度跨度)。
    """
    total_bits = precision * 5
    lon_bits = (total_bits + 1) // 2
    lat_bits = total_bits // 2
    lat_step = 180.0 / (2**lat_bits)
    lon_step = 360.0 / (2**lon_bits)
    return lat_step, lon_step


def precision_for_radius(radius_m: float) -> int:
    """
    根据查询半径选择 geohash 精度（经验值）。
    值越大网格越小，候选越精确。
    """
    if radius_m <= 20:
        return 9
    if radius_m <= 80:
        return 8
    if radius_m <= 600:
        return 7
    if radius_m <= 2500:
        return 6
    if radius_m <= 20000:
        return 5
    if radius_m <= 80000:
        return 4
    return 3


class MockRedisClient:
    """极简 Redis mock，仅用于本地无 Redis 时演示。"""

    def __init__(self) -> None:
        self._zsets: Dict[str, Dict[str, float]] = {}
        self._hashes: Dict[str, Dict[str, float | str]] = {}
        self._ttl: Dict[str, float] = {}

    def zadd(self, key: str, mapping: Dict[str, float]) -> None:
        zset = self._zsets.setdefault(key, {})
        for member, score in mapping.items():
            zset[member] = score

    def zrem(self, key: str, member: str) -> None:
        zset = self._zsets.get(key)
        if not zset:
            return
        zset.pop(member, None)

    def zrevrange(self, key: str, start: int, stop: int) -> List[str]:
        zset = self._zsets.get(key, {})
        members = sorted(zset.items(), key=lambda x: x[1], reverse=True)
        if stop == -1:
            sliced = members[start:]
        else:
            sliced = members[start : stop + 1]
        return [member for member, _ in sliced]

    def zrangebyscore(self, key: str, min_score: int, max_score: int) -> List[str]:
        zset = self._zsets.get(key, {})
        members = [(m, s) for m, s in zset.items() if min_score <= s <= max_score]
        members.sort(key=lambda x: x[1])
        return [member for member, _ in members]

    def hset(self, key: str, mapping: Dict[str, float | str]) -> None:
        h = self._hashes.setdefault(key, {})
        h.update(mapping)

    def hgetall(self, key: str) -> Dict[str, str]:
        h = self._hashes.get(key, {})
        return {str(k): str(v) for k, v in h.items()}

    def delete(self, key: str) -> None:
        self._hashes.pop(key, None)
        self._ttl.pop(key, None)

    def expire(self, key: str, seconds: int) -> None:
        self._ttl[key] = time.time() + seconds


class NearbyPeopleService:
    def __init__(
        self,
        redis_client: Any = None,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
    ) -> None:
        if redis_client is not None:
            self.redis_client = redis_client
        elif redis is not None:
            self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        else:
            # 本地未安装 redis 包时自动回退 mock，方便算法验证
            self.redis_client = MockRedisClient()
        self.zset_key = "users:location"
        self.geo_precision = 9
        self.detail_ttl_seconds = 3600

    def _geohash_to_score(self, geohash_str: str) -> int:
        """将 GeoHash 字符串转换为 ZSet 排序分数。"""
        score = 0
        for char in geohash_str:
            score = score * 32 + BASE32.index(char)
        return score

    def _get_geohash_prefix(
        self, latitude: float, longitude: float, precision: int | None = None
    ) -> str:
        """生成 GeoHash 编码。"""
        p = precision if precision is not None else self.geo_precision
        if geohash_lib is not None:
            return geohash_lib.encode(latitude, longitude, p)
        return geohash_encode(latitude, longitude, p)

    def _prefix_score_range(self, prefix: str, full_precision: int) -> Tuple[int, int]:
        """
        计算 geohash 前缀在 full_precision 长度下对应的 score 闭区间。
        例如 full=9, prefix=7，则补齐 2 位 base32 的最小/最大区间。
        """
        prefix_score = self._geohash_to_score(prefix)
        suffix_len = full_precision - len(prefix)
        factor = 32**suffix_len
        min_score = prefix_score * factor
        max_score = (prefix_score + 1) * factor - 1
        return min_score, max_score

    def _query_precision_for_radius(self, radius_m: float) -> int:
        """
        查询时用于粗筛的 geohash 前缀精度。
        注意：写入固定 9 位，查询可降精度扩大召回。
        """
        if radius_m <= 80:
            return 8
        if radius_m <= 600:
            return 7
        if radius_m <= 2500:
            return 6
        if radius_m <= 20000:
            return 5
        return 4

    def _detail_key(self, user_id: str) -> str:
        return f"user:location:detail:{user_id}"

    def update_location(
        self, user_id: str, latitude: float, longitude: float
    ) -> None:
        """兼容旧命名，内部委托 add_user_location。"""
        self.add_user_location(user_id, latitude, longitude)

    def add_user_location(self, user_id: str, latitude: float, longitude: float) -> None:
        """添加或更新用户位置。"""
        geohash_str = self._get_geohash_prefix(latitude, longitude, self.geo_precision)
        score = self._geohash_to_score(geohash_str)

        self.redis_client.zadd(self.zset_key, {user_id: score})

        detail_key = self._detail_key(user_id)
        self.redis_client.hset(
            detail_key,
            mapping={
                "latitude": latitude,
                "longitude": longitude,
                "geohash": geohash_str,
                "updated_at": int(time.time()),
            },
        )
        self.redis_client.expire(detail_key, self.detail_ttl_seconds)

    def nearby(
        self,
        latitude: float,
        longitude: float,
        radius_m: float = 1000.0,
        limit: int = 20,
        include_self: bool = False,
        self_user_id: str | None = None,
    ) -> List[Tuple[str, float]]:
        query_precision = self._query_precision_for_radius(radius_m)
        prefix = self._get_geohash_prefix(latitude, longitude, query_precision)
        min_score, max_score = self._prefix_score_range(prefix, self.geo_precision)
        candidate_user_ids = self.redis_client.zrangebyscore(
            self.zset_key, min_score, max_score
        )
        result: List[Tuple[str, float]] = []
        for user_id in candidate_user_ids:
            if not include_self and self_user_id and user_id == self_user_id:
                continue

            detail = self.redis_client.hgetall(self._detail_key(user_id))
            if not detail:
                continue
            try:
                user_lat = float(detail["latitude"])
                user_lon = float(detail["longitude"])
            except (KeyError, TypeError, ValueError):
                continue

            dist = haversine_meters(latitude, longitude, user_lat, user_lon)
            if dist <= radius_m:
                result.append((user_id, dist))

        result.sort(key=lambda x: x[1])
        return result[:limit]

    def remove_user(self, user_id: str) -> None:
        """可选：移除用户位置。"""
        self.redis_client.zrem(self.zset_key, user_id)
        self.redis_client.delete(self._detail_key(user_id))


if __name__ == "__main__":
    redis_client = MockRedisClient()
    service = NearbyPeopleService(redis_client=redis_client)

    # 以天安门为中心，准备近/中/远多组测试数据
    demo_users = [
        ("u1", 39.908722, 116.397499, "天安门(中心点)"),
        ("u13", 39.908725, 116.397502, "中心附近约0.4m(500m内)"),
        ("u14", 39.908740, 116.397520, "中心附近约2.8m(500m内)"),
        ("u9", 39.911200, 116.397499, "中心北侧约275m(500m内)"),
        ("u10", 39.906900, 116.398200, "中心西南约210m(500m内)"),
        ("u2", 39.909500, 116.405000, "王府井方向(近)"),
        ("u3", 39.914000, 116.397000, "景山方向(近)"),
        ("u11", 39.900900, 116.397499, "中心南侧约870m(1500m内)"),
        ("u12", 39.908722, 116.413000, "中心正东约1320m(1500m内)"),
        ("u4", 39.900000, 116.380000, "西南方向(中)"),
        ("u5", 39.915156, 116.403861, "故宫东北角(近)"),
        ("u6", 39.933500, 116.420000, "东直门附近(远)"),
        ("u7", 39.881800, 116.412400, "南站方向(远)"),
        ("u8", 39.984702, 116.318417, "中关村(很远)"),
    ]
    for uid, lat, lon, _ in demo_users:
        service.add_user_location(uid, lat, lon)

    center_lat, center_lon = 39.908722, 116.397499
    print("已写入测试数据：")
    for uid, _, _, desc in demo_users:
        print(f"- {uid}: {desc}")

    for radius in (500, 1500, 5000):
        nearby_users = service.nearby(center_lat, center_lon, radius_m=radius, limit=10)
        print(f"\n附近的人（半径 {radius}m）:")
        if not nearby_users:
            print("  无结果")
            continue
        for uid, dist in nearby_users:
            print(f"  {uid}: {dist:.1f}m")
