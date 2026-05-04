from __future__ import annotations

import argparse
from dataclasses import dataclass
import sys
import textwrap
from typing import Dict, List, Sequence
from urllib.parse import unquote, urlparse

try:
    import psycopg2
    from psycopg2 import sql as pgsql
except ImportError as exc:
    raise SystemExit(
        "缺少依赖 psycopg2，请先安装：pip install psycopg2-binary"
    ) from exc


SYSTEM_SCHEMAS = {"pg_catalog", "information_schema"}


@dataclass(frozen=True)
class DBConfig:
    name: str
    db_type: str
    host: str
    port: int
    database: str
    username: str
    password: str

    def to_conn_kwargs(self, database: str | None = None) -> Dict[str, object]:
        return {
            "host": self.host,
            "port": self.port,
            "dbname": database or self.database,
            "user": self.username,
            "password": self.password,
        }


def parse_pg_dsn(dsn: str) -> DBConfig:
    """从 libpq/Postgres 风格 URL 解析为 DBConfig（与 ``postgresql://...`` 一致）。"""
    u = urlparse(dsn.strip())
    scheme = (u.scheme or "").lower()
    if scheme not in ("postgres", "postgresql"):
        raise ValueError(
            f"仅支持 postgresql / postgres DSN，当前为: {u.scheme!r}"
        )
    host = u.hostname or "localhost"
    port = u.port or 5432
    database = (u.path or "").lstrip("/") or "postgres"
    username = unquote(u.username) if u.username is not None else ""
    password = unquote(u.password) if u.password is not None else ""
    return DBConfig(
        name=database,
        db_type="pgsql",
        host=host,
        port=port,
        database=database,
        username=username,
        password=password,
    )


def parse_config(raw: str) -> DBConfig:
    lines = [line.strip() for line in raw.strip().splitlines() if line.strip()]
    if len(lines) < 2:
        raise ValueError("配置格式错误，至少需要名称和连接参数。")

    name = lines[0]
    values: Dict[str, str] = {}
    for line in lines[1:]:
        if ":" not in line:
            raise ValueError(f"配置行缺少分隔符 ':' -> {line}")
        key, value = line.split(":", 1)
        values[key.strip().lower()] = value.strip()

    required = {"type", "host", "port", "database", "username", "password"}
    missing = required - values.keys()
    if missing:
        raise ValueError(f"配置缺少必要字段: {', '.join(sorted(missing))}")

    return DBConfig(
        name=name,
        db_type=values["type"],
        host=values["host"],
        port=int(values["port"]),
        database=values["database"],
        username=values["username"],
        password=values["password"],
    )


def list_business_tables(base_cfg: DBConfig, database: str) -> List[str]:
    sql = """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
          AND table_schema <> ALL(%s)
        ORDER BY table_schema, table_name;
    """
    with psycopg2.connect(**base_cfg.to_conn_kwargs(database=database)) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (list(SYSTEM_SCHEMAS),))
            rows = cur.fetchall()
    return [f"{schema}.{table}" for schema, table in rows]


def list_tables_for_display(
    base_cfg: DBConfig, database: str
) -> List[tuple[str, str, str, str, str]]:
    sql = """
        SELECT
            schemaname AS schema_name,
            tablename AS table_name,
            'table' AS type_name,
            tableowner AS owner_name
        FROM pg_tables
        WHERE schemaname <> ALL(%s)
        ORDER BY schemaname, tablename;
    """
    with psycopg2.connect(**base_cfg.to_conn_kwargs(database=database)) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (list(SYSTEM_SCHEMAS),))
            base_rows = cur.fetchall()

        table_rows: List[tuple[str, str, str, str, str]] = []
        with conn.cursor() as count_cur:
            for schema_name, table_name, type_name, owner_name in base_rows:
                try:
                    count_cur.execute(
                        pgsql.SQL("SELECT COUNT(*) FROM {}.{}").format(
                            pgsql.Identifier(schema_name),
                            pgsql.Identifier(table_name),
                        )
                    )
                    row_count = str(count_cur.fetchone()[0])
                except Exception:
                    row_count = "N/A"
                table_rows.append(
                    (schema_name, table_name, type_name, owner_name, row_count)
                )
        return table_rows


def describe_table(
    base_cfg: DBConfig, database: str, schema_name: str, table_name: str
) -> tuple[List[tuple[str, str, str]], List[str]]:
    columns_sql = """
        SELECT
            a.attname AS column_name,
            pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
            trim(
                concat(
                    CASE WHEN a.attnotnull THEN 'not null' ELSE '' END,
                    CASE
                        WHEN ad.adbin IS NOT NULL
                        THEN concat(' default ', pg_get_expr(ad.adbin, ad.adrelid))
                        ELSE ''
                    END
                )
            ) AS modifiers
        FROM pg_attribute a
        JOIN pg_class c ON c.oid = a.attrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        LEFT JOIN pg_attrdef ad ON ad.adrelid = a.attrelid AND ad.adnum = a.attnum
        WHERE n.nspname = %s
          AND c.relname = %s
          AND a.attnum > 0
          AND NOT a.attisdropped
        ORDER BY a.attnum;
    """
    indexes_sql = """
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE schemaname = %s
          AND tablename = %s
        ORDER BY indexname;
    """

    with psycopg2.connect(**base_cfg.to_conn_kwargs(database=database)) as conn:
        with conn.cursor() as cur:
            cur.execute(columns_sql, (schema_name, table_name))
            columns = cur.fetchall()
            cur.execute(indexes_sql, (schema_name, table_name))
            index_rows = cur.fetchall()

    indexes: List[str] = []
    for index_name, index_def in index_rows:
        marker = f" INDEX {index_name} ON "
        if marker in index_def:
            indexes.append(index_def.split(marker, 1)[1])
        else:
            indexes.append(index_def)
    return columns, indexes


def render_pgcli_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    max_col_width = 72
    widths = [min(len(h), max_col_width) for h in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = min(max(widths[idx], len(str(cell))), max_col_width)

    def fmt_border() -> str:
        return "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def wrap_cell(cell: str, width: int) -> List[str]:
        if not cell:
            return [""]
        wrapped_lines = textwrap.wrap(
            cell,
            width=width,
            break_long_words=True,
            break_on_hyphens=False,
        )
        return wrapped_lines or [""]

    def fmt_row(row: Sequence[str]) -> List[str]:
        wrapped_cells = [wrap_cell(str(cell), widths[i]) for i, cell in enumerate(row)]
        line_count = max(len(lines) for lines in wrapped_cells)
        for lines in wrapped_cells:
            lines.extend([""] * (line_count - len(lines)))

        output_lines: List[str] = []
        for line_idx in range(line_count):
            output_lines.append(
                "| "
                + " | ".join(wrapped_cells[i][line_idx].ljust(widths[i]) for i in range(len(widths)))
                + " |"
            )
        return output_lines

    lines = [fmt_border(), *fmt_row(headers), fmt_border()]
    for row in rows:
        lines.extend(fmt_row(row))
    lines.append(fmt_border())
    suffix = "row" if len(rows) == 1 else "rows"
    lines.append(f"({len(rows)} {suffix})")
    return "\n".join(lines)


class DblistArgumentParser(argparse.ArgumentParser):
    """参数不合法时先给简短说明，再打印完整帮助（不再只有一行 usage）。"""

    def error(self, message: str) -> None:
        print(
            textwrap.dedent(
                """
                ------------------------------------------------------------
                命令行参数不完整或无效
                ------------------------------------------------------------
                本脚本必须带 --dsn，值为整段 PostgreSQL 连接 URL，例如：
                  python .\\dblist.py --dsn "postgresql://用户:密码@主机:5432/库名"
                （PowerShell 请用英文双引号包住整条 URL；也支持 postgres://；省略端口时按 5432。）

                表很多时可加 -t 关键字，只列出表名里含该字的表。密码里有 @、:、/、% 等须做 URL 编码。

                下面是完整说明（与运行  python .\\dblist.py -h  时相同）：
                ------------------------------------------------------------
                """
            ).strip(),
            file=sys.stdout,
        )
        self.print_help(sys.stdout)
        print(
            "\n------------------------------------------------------------\n"
            "若仍不确定，请把本页从「命令行参数不完整」起完整复制给同事或文档助手。\n"
            "------------------------------------------------------------",
            file=sys.stdout,
        )
        self.exit(2, f"{self.prog}: error: {message}\n")


def main() -> int:
    parser = DblistArgumentParser(
        prog="dblist.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "列出当前 PostgreSQL 数据库里的「业务表」并打印每张表的结构。\n"
            "\n"
            "会排除系统 schema（如 pg_catalog），只统计普通 BASE TABLE；\n"
            "输出包括表清单（含行数估算）、列名/类型/约束，以及索引定义。\n"
            "\n"
            "运行本脚本必须提供数据库连接：请用 --dsn 传入一整条连接 URL。"
        ),
        epilog=(
            "参数说明（必读）\n"
            "  --dsn\n"
            "      一条 Postgres 连接 URL，和常见配置里的 \"postgresql://...\" 相同。\n"
            "      各部分对应关系：\n"
            "        postgresql://  协议头（也支持 postgres://）\n"
            "        用户名:密码     登录账号（密码里若有 @、:、/、% 等字符须做 URL 编码，例如 @ 写成 %40）\n"
            "        @主机:端口      实例地址；不写端口时默认 5432\n"
            "        /数据库名       路径里第一段即要连上的 database\n"
            "\n"
            "  -t / --table-contains\n"
            "      可选。只保留「表名」里包含该字符串的表（大小写不敏感），\n"
            "      用于库很大时缩小输出范围。\n"
            "\n"
            "PowerShell 示例（注意整条 DSN 用双引号包起来）：\n"
            "  python .\\dblist.py --dsn \"postgresql://app_user:secret@10.0.0.1:5432/app_db\"\n"
            "  python .\\dblist.py --dsn \"postgresql://app_user:secret@10.0.0.1:5432/app_db\" -t msq\n"
            "\n"
            "依赖：pip install psycopg2-binary"
        ),
    )
    parser.add_argument(
        "--dsn",
        metavar="URL",
        required=True,
        help=(
            "数据库连接 URL，例如 postgresql://USER:PASSWORD@HOST:PORT/DATABASE"
        ),
    )
    parser.add_argument(
        "-t",
        "--table-contains",
        metavar="KEYWORD",
        help="可选：只列出表名中包含该关键字的表（不区分大小写）",
    )
    args = parser.parse_args()

    try:
        entry = parse_pg_dsn(args.dsn)
    except ValueError as exc:
        print(f"无效 DSN: {exc}")
        return 2
    if entry.db_type.lower() != "pgsql":
        print(f"暂不支持数据库类型: {entry.db_type}")
        return 1

    print(f"实例: {entry.host}:{entry.port}")
    print(f"当前数据库: {entry.database}")
    print("正在读取当前数据库的表清单...\n")
    try:
        tables = list_business_tables(entry, entry.database)
        table_rows = list_tables_for_display(entry, entry.database)
    except Exception as exc:  # pragma: no cover
        print(f"读取表清单失败: {exc}")
        return 1

    if args.table_contains:
        needle = args.table_contains.lower()
        tables = [name for name in tables if needle in name.lower()]
        table_rows = [row for row in table_rows if needle in row[1].lower()]

    if not tables:
        if args.table_contains:
            print(
                f"数据库 `{entry.database}` 中未找到表名包含 `{args.table_contains}` 的业务表。"
            )
        else:
            print(f"数据库 `{entry.database}` 暂无业务表。")
        return 0

    print(f"数据库 `{entry.database}` 的表清单：")
    print(
        render_pgcli_table(
            ["Schema", "Name", "Type", "Owner", "Rows"],
            [list(row) for row in table_rows],
        )
    )
    print()

    print("逐表结构详情：")
    for schema_name, table_name, _, _, _ in table_rows:
        display_name = table_name if schema_name == "public" else f"{schema_name}.{table_name}"
        print(f"{entry.database}> \\d {display_name}")
        try:
            columns, indexes = describe_table(entry, entry.database, schema_name, table_name)
            print(
                render_pgcli_table(
                    ["Column", "Type", "Modifiers"],
                    [[name, data_type, modifiers] for name, data_type, modifiers in columns],
                )
            )
            if indexes:
                print("Indexes:")
                for index_def in indexes:
                    print(f"    {index_def}")
        except Exception as exc:  # pragma: no cover
            print(f"读取表结构失败: {exc}")
        print()

    print("汇总:")
    print("- 数据库数量: 1")
    print(f"- 业务表总数: {len(tables)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

