---
name: weibo-architecture-doc
overview: 为中型规模（DAU 10万~1000万、多可用区、P95<200ms）的微博系统输出一份可落地的架构设计文档，覆盖服务拆分、数据模型、关键链路、缓存/队列、分析与容灾安全。
todos:
  - id: doc-sections
    content: 按上述大纲生成最终设计文档（含流程图/时序图）
    status: completed
  - id: mermaid-diagrams
    content: 补充关键流程的 mermaid（发帖fanout、首页读路径、分析链路）
    status: completed
  - id: capacity-slo
    content: 补充容量估算与SLO/限流阈值的示例参数
    status: completed
isProject: false
---

## 目标与范围

- **目标**：实现类 Twitter 的核心微博能力（发微博、关注关系、时间线）并具备可扩展的数据分析能力；满足中型规模的性能与可用性要求。
- **SLA 假设**：多可用区部署；读多写少；P95<200ms（时间线/详情页为主）；RPO 分钟级，RTO 30~60 分钟（可后续演进到更强）。
- **MVP 功能范围**：
  - 发微博：文本+图片（图片走对象存储）
  - 社交：关注/取关
  - 时间线：Home（关注流）+ User（个人页）
  - 分析：事件采集、基础报表（DAU、发帖量、曝光/点击等）
- **非目标（本版不做/弱化）**：复杂推荐、全文搜索、私信、评论/转发、强审核链路（可预留扩展点）。

## 总体架构（分层 + 服务化）

- **接入层**
  - API Gateway / Ingress：鉴权、限流、灰度、路由、统一日志
  - BFF（可选）：移动端/网页端聚合接口（时间线常需要聚合多资源）
- **核心服务层（建议拆分）**
  - `AuthService`：登录态（JWT/Session）、风控开关
  - `UserService`：用户资料、计数器（粉丝/关注/微博数）
  - `SocialGraphService`：关注关系（写优化+双向查询）
  - `PostService`：微博元数据、内容、媒体引用
  - `TimelineService`：Home/User 时间线构建与读取（混合推拉）
  - `MediaService`：上传签名、回调、转码（可后置）
  - `CounterService`（可选）：点赞/阅读等计数（本版可只做曝光/点击）
- **数据与基础设施层**
  - OLTP：MySQL/PostgreSQL（分库分表预案）
  - Cache：Redis（KV、ZSET/SET、热点保护）
  - MQ：Kafka/Pulsar/RabbitMQ（写扩散、异步任务、分析埋点）
  - Object Storage：S3/MinIO/OSS（图片）
  - Search（预留）：OpenSearch/ES（后续）
  - Analytics：ClickHouse/Druid + 数据湖（可演进）

## 关键数据模型（高层设计）

- **用户与资料**
  - `users(id, handle, phone/email, status, created_at, ...)`
  - `user_profiles(user_id, name, avatar_url, bio, ...)`
- **关注关系（社交图）**
  - `follows(follower_id, followee_id, created_at)` 复合主键/唯一索引
  - 读模型（Redis）：
    - `following:{userId}` -> SET（关注的人）
    - `followers:{userId}` -> SET（粉丝）
- **微博与媒体**
  - `posts(id, author_id, created_at, visibility, ...)`
  - `post_contents(post_id, text, ...)`（可与 posts 合并；大字段单独表利于热数据）
  - `post_media(post_id, media_url, media_type, width, height, ...)`
- **时间线**
  - `user_timeline:{userId}` -> ZSET(score=created_at, member=postId)（个人页）
  - `home_timeline:{userId}` -> ZSET（关注流首页，推模式写入）
  - `fanout_task`（DB/MQ 任务）：写扩散记录与重试
- **分析事件**
  - `events(topic, user_id, post_id, ts, attrs...)`（MQ -> 实时/离线存储）

## 核心链路设计

### 发微博（写路径）

- 客户端上传图片：客户端 -> `MediaService` 获取预签名 -> 对象存储直传 -> 回调确认。
- 发微博 API：`PostService` 写入 `posts/post_contents/post_media`（事务内）。
- 写扩散：
  - 同步：写入作者 `user_timeline:{author}`（ZSET）
  - 异步：投递 `FanoutPostCreated` 到 MQ，由 `TimelineService` 执行 fanout。
- Fanout 策略（中型规模推荐“混合推拉”）：
  - **普通用户**：推模式，将 postId 写入粉丝的 `home_timeline:{fan}`（批量 pipeline）
  - **大V/粉丝过多**：拉模式，不对所有粉丝推；在粉丝读首页时合并（见读路径）
  - 阈值：例如粉丝数>50k 切到拉；并可动态调整。
- 一致性：时间线允许秒级最终一致；详情页强一致走 `PostService`。

### 拉取首页时间线（读路径）

- 首选：读取 `home_timeline:{user}`（Redis ZSET）分页。
- 回源/补齐：
  - 若缓存未命中或需要更旧数据：从持久化时间线表（可选）或按关注列表拉取合并。
  - 对大V拉模式：读取用户关注的大V最近 posts（如 `user_timeline:{vip}`）并在服务端做多路归并（k-way merge），与 `home_timeline` 合并去重。
- 热点与保护：
  - 首页分页使用游标（since_id/max_id 或 score+member），避免深分页。
  - Redis 采用 TTL+惰性更新；对热点用户启用请求合并（singleflight）与限流。

## 存储与缓存选型（中型规模）

- **OLTP**：PostgreSQL/MySQL（优先成熟高可用方案），读写分离；按 `author_id` 或 `post_id` hash 分片预案。
- **Redis**：
  - 关注集合、时间线ZSET、用户计数器、热点微博详情缓存。
  - 大 Key 控制：粉丝集合与 home_timeline 控制长度（如保留最近 N=1000 条）。
- **MQ（Kafka 优先）**：
  - `fanout` 主题：发帖写扩散
  - `events` 主题：曝光/点击等埋点
  - `async-jobs`：重试、回填、对账

## 分析链路（事件驱动）

- 客户端/服务端打点：曝光、点击、发帖、关注。
- 流式摄取：事件进入 Kafka ->
  - 实时：Flink/ksql -> ClickHouse（近实时看板）
  - 离线：Kafka Connect -> S3/HDFS -> Spark（留存、漏斗等）
- 基础指标：DAU、发帖量、关注/取关量、曝光/点击率、接口 P95。

## 可用性、容灾与一致性

- 多 AZ：数据库主从跨 AZ；Redis Cluster 多副本；Kafka 3 副本。
- 降级策略：
  - 时间线读取失败时降级为“仅看关注的大V最近微博”（拉模式）或“仅个人页”。
  - 只读模式（DB 故障时）优先保障读。
- 数据一致性分层：
  - 详情页：强一致（DB/缓存回源）
  - 时间线：最终一致（异步 fanout）

## 安全与风控（MVP 版本）

- 网关限流：按 userId/IP/token；对发帖/关注接口更严格。
- 反滥用：注册/登录风控预留，发帖频率限制。
- 隐私与合规：最小化存储敏感字段；审计日志。

## 观测与运维

- 指标：QPS、错误率、P95、队列堆积、fanout 延迟、Redis 命中率。
- 日志：traceId 全链路；关键业务事件日志。
- 告警：SLO burn rate、数据库延迟、缓存命中率突降、Kafka lag。

## 演进路线（从 MVP 到更大规模）

- 引入持久化时间线表（避免完全依赖 Redis）。
- 引入全文搜索与话题（ES/OpenSearch）。
- 推荐/热榜：基于事件与图谱的召回与排序。
- 多地域多活：按用户分区路由 + 异步复制，提升 RTO/RPO。

## 关键权衡说明

- 采用“混合推拉”时间线：在中型规模下兼顾读性能与写扩散成本。
- 时间线允许最终一致：换取高吞吐与可用性。
- 热数据缓存与长度截断：控制 Redis 成本，避免大 key 与雪崩。

