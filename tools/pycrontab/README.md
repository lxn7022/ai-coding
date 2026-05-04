# pycrontab — `linux_cron.py` 使用说明

基于 [python-crontab](https://gitlab.com/doctormo/python-crontab) 的命令行小工具，对 Linux **crontab** 做列出、添加、删除、修改。未指定 `--tabfile` 时，读写的是**当前登录用户**的系统 crontab（与直接执行 `crontab -e` 为同一数据源）。

## 环境准备

```bash
cd pycrontab
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

直接执行脚本：

```bash
python linux_cron.py --help
python linux_cron.py list --help
```

## 全局参数（写在子命令前面）

| 参数 | 说明 |
|------|------|
| `--tabfile PATH` | 从指定文件读写 crontab，用于测试或自定义路径；文件不存在时会创建空文件。 |
| `--user-name NAME` | 操作指定系统用户的 crontab（通常需要相应权限）。未指定 `--tabfile` 时，默认等价于当前用户。 |
| `--user` | 显式表示当前用户（与默认行为一致，可省略）。 |
| `-n` / `--dry-run` | 只打印将要执行的操作，**不写回** crontab 或 `--tabfile`。 |

## 子命令一览

| 子命令 | 别名 | 作用 |
|--------|------|------|
| `list` | `query` | 列出任务 |
| `add` | — | 添加任务 |
| `remove` | `delete`、`rm` | 删除任务 |
| `modify` | `edit`、`set` | 修改任务 |

查看子命令帮助：

```bash
python linux_cron.py list --help
python linux_cron.py add --help
python linux_cron.py remove --help
python linux_cron.py modify --help
```

---

### `list` / `query` — 查询

列出带序号的任务行，序号从 **1** 开始，与 `remove -i` / `modify -i` 对应。

```bash
python linux_cron.py list
```

包含已禁用条目（库内视为禁用的任务）：

```bash
python linux_cron.py list --all
```

---

### `add` — 添加

| 参数 | 必填 | 说明 |
|------|------|------|
| `-s` / `--schedule` | 是 | 五段式 cron，例如 `*/5 * * * *` |
| `-c` / `--command` | 是 | 要执行的命令，**建议写绝对路径** |
| `--comment` | 否 | 写入该 job 的注释 |

示例：

```bash
python linux_cron.py add -s '*/10 * * * *' -c '/usr/bin/python3 /opt/app/heartbeat.py'
python linux_cron.py add -s '0 3 * * *' -c '/usr/local/bin/backup.sh' --comment nightly-backup
```

---

### `remove` / `delete` / `rm` — 删除

必须指定 **`--index`** 或 **`--match-command`** 之一。

| 参数 | 说明 |
|------|------|
| `-i` / `--index N` | 删除 `list` 中第 N 条 |
| `-m` / `--match-command STR` | 删除 **command 字段包含** `STR` 且**唯一匹配**的那一条；多条匹配会报错，需改用更精确的子串或 `--index` |

示例：

```bash
python linux_cron.py list
python linux_cron.py rm -i 2
python linux_cron.py rm -m '/opt/app/heartbeat.py'
```

---

### `modify` / `edit` / `set` — 修改

同样需要 **`--index`** 或 **`--match-command`** 定位一条任务。

至少提供下列之一：

| 参数 | 说明 |
|------|------|
| `--new-schedule` | 新的五段式 cron |
| `--new-command` | 新的命令字符串 |
| `--comment` | 设置注释；单独写 `--comment` 且**不带值**表示清空注释；`--comment 说明文字` 为设置内容 |

示例：

```bash
python linux_cron.py modify -i 1 --new-schedule '0 */6 * * *'
python linux_cron.py modify -m 'heartbeat.py' --new-command '/usr/bin/python3 /opt/app/heartbeat2.py'
python linux_cron.py modify -i 1 --comment ''
```

---

## 使用 `--tabfile` 做本地演练

不触碰真实 crontab，适合脚本或 CI 自测：

```bash
python linux_cron.py --tabfile ./demo.cron list
python linux_cron.py --tabfile ./demo.cron add -s '* * * * *' -c '/bin/true'
python linux_cron.py -n --tabfile ./demo.cron rm -i 1   # 仅预览删除，不写文件
```

## 依赖与上游文档

- 依赖：`requirements.txt` 中的 `python-crontab`
- 库说明：<https://gitlab.com/doctormo/python-crontab>

## 说明

- 修改系统 crontab 前建议先 **`list`** 确认序号，或使用 **`-n` / `--dry-run`** 预览。
- `python-crontab` 可能会把部分合法五段式规范成 `@hourly`、`@daily` 等形式，与 `list` 输出一致。
