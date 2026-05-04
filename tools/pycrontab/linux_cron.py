#!/usr/bin/env python3
"""
使用 python-crontab 管理当前 Linux 用户（或指定用户）的 crontab：添加、删除、列出、修改。
文档: https://gitlab.com/doctormo/python-crontab
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

from crontab import CronTab


SPEC = """

利用python-crontab库，管理linux的定时任务；
写一个脚本工具，实现定时任务的添加、删除、查询、修改；
官方文档：gitlab.com/doctormo/python-crontab；

"""


def _open_crontab(
    *,
    user: bool | str | None,
    tabfile: str | None,
) -> CronTab:
    if tabfile:
        path = Path(tabfile)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("", encoding="utf-8")
        return CronTab(tabfile=tabfile)
    if user is True:
        return CronTab(user=True)
    if isinstance(user, str):
        return CronTab(user=user)
    return CronTab()


def _jobs_list(cron: CronTab) -> list:
    return list(cron)


def _resolve_job_by_index(cron: CronTab, index: int):
    jobs = _jobs_list(cron)
    if index < 1 or index > len(jobs):
        raise SystemExit(f"无效序号 {index}，当前共有 {len(jobs)} 条任务")
    return jobs[index - 1]


def _resolve_job_by_command_contains(cron: CronTab, needle: str):
    matches = [j for j in cron if needle in (j.command or "")]
    if not matches:
        raise SystemExit(f"未找到 command 包含 {needle!r} 的任务")
    if len(matches) > 1:
        raise SystemExit(
            f"command 包含 {needle!r} 的任务有 {len(matches)} 条，请改用 --index 或更精确的 --match-command"
        )
    return matches[0]


def cmd_list(cron: CronTab, *, show_disabled: bool) -> None:
    jobs = _jobs_list(cron)
    if not jobs:
        print("(无定时任务)")
        return
    for i, job in enumerate(jobs, start=1):
        if not show_disabled and not job.is_enabled():
            continue
        flag = "" if job.is_enabled() else "[已禁用] "
        comment = job.comment or ""
        suffix = f"  # {comment}" if comment else ""
        print(f"{i:>4}  {flag}{job.slices.render()}  {job.command}{suffix}")


def _preview_line(schedule: str, command: str, comment: str | None) -> str:
    """在独立空表中解析 schedule，得到与写入时一致的渲染（如 @hourly）。"""
    tmp = CronTab(tab="")
    j = tmp.new(command=command)
    j.setall(schedule)
    if comment:
        j.set_comment(comment)
    return f"{j.slices.render()} {j.command}"


def _simulate_modified_schedule_command(
    job,
    *,
    new_schedule: str | None,
    new_command: str | None,
) -> str:
    """不修改原 job，预览修改后的「时间片 + 命令」一行（与 list 的展示字段一致）。"""
    tmp = CronTab(tab="")
    cmd = new_command if new_command is not None else job.command
    j = tmp.new(command=cmd)
    if new_schedule is not None:
        j.setall(new_schedule)
    else:
        j.setall(job.slices.render())
    return f"{j.slices.render()} {j.command}"


def cmd_add(
    cron: CronTab,
    *,
    schedule: str,
    command: str,
    comment: str | None,
    write: bool,
) -> None:
    if not write:
        print("将添加:", _preview_line(schedule, command, comment))
        return
    job = cron.new(command=command)
    job.setall(schedule)
    if comment:
        job.set_comment(comment)
    cron.write()
    print("已添加:", job.slices.render(), job.command)


def cmd_remove(
    cron: CronTab,
    *,
    index: int | None,
    match_command: str | None,
    write: bool,
) -> None:
    if index is not None:
        job = _resolve_job_by_index(cron, index)
    elif match_command:
        job = _resolve_job_by_command_contains(cron, match_command)
    else:
        raise SystemExit("请指定 --index 或 --match-command")

    preview = f"{job.slices.render()} {job.command}"
    if not write:
        print("将删除:", preview)
        return
    cron.remove(job)
    cron.write()
    print("已删除:", preview)


def cmd_modify(
    cron: CronTab,
    *,
    index: int | None,
    match_command: str | None,
    new_schedule: str | None,
    new_command: str | None,
    comment: str | None,
    write: bool,
) -> None:
    if index is not None:
        job = _resolve_job_by_index(cron, index)
    elif match_command:
        job = _resolve_job_by_command_contains(cron, match_command)
    else:
        raise SystemExit("请指定 --index 或 --match-command")

    before = f"{job.slices.render()} {job.command}"
    if not write:
        after = _simulate_modified_schedule_command(
            job,
            new_schedule=new_schedule,
            new_command=new_command,
        )
        print("将修改:")
        print("  原:", before)
        print("  现:", after)
        if comment is not None:
            note = "（注释将清空）" if comment == "" else "（注释将更新）"
            print(" ", note)
        return

    if new_schedule is not None:
        job.setall(new_schedule)
    if new_command is not None:
        job.command = new_command
    if comment is not None:
        if comment == "":
            job.set_comment("")
        else:
            job.set_comment(comment)
    cron.write()
    after = f"{job.slices.render()} {job.command}"
    print("已修改:")
    print("  原:", before)
    print("  现:", after)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="使用 python-crontab 管理 crontab（添加 / 删除 / 列出 / 修改）",
    )
    p.add_argument(
        "--tabfile",
        metavar="PATH",
        help="从文件读写 crontab（测试用），不指定则使用系统用户 crontab",
    )
    ug = p.add_mutually_exclusive_group()
    ug.add_argument(
        "--user",
        action="store_true",
        help="当前登录用户的 crontab（默认）",
    )
    ug.add_argument(
        "--user-name",
        metavar="NAME",
        help="指定系统用户名（通常需对应权限）",
    )
    p.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="只打印将要执行的操作，不写回 crontab",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    sp_list = sub.add_parser("list", aliases=["query"], help="列出任务")
    sp_list.add_argument(
        "--all",
        action="store_true",
        help="包含已禁用的行（以 # 开头的任务）",
    )

    sp_add = sub.add_parser("add", help="添加任务")
    sp_add.add_argument(
        "-s",
        "--schedule",
        required=True,
        help="五段式 cron 表达式，如 '*/5 * * * *'",
    )
    sp_add.add_argument(
        "-c",
        "--command",
        required=True,
        help="要执行的 shell 命令（建议写绝对路径）",
    )
    sp_add.add_argument(
        "--comment",
        default=None,
        help="可选注释（写入 crontab 的 job 注释）",
    )

    sp_rm = sub.add_parser("remove", aliases=["delete", "rm"], help="删除任务")
    sp_rm.add_argument(
        "-i",
        "--index",
        type=int,
        default=None,
        help="list 中显示的序号（从 1 开始）",
    )
    sp_rm.add_argument(
        "-m",
        "--match-command",
        default=None,
        help="按 command 子串唯一匹配删除（多条匹配会报错）",
    )

    sp_mod = sub.add_parser("modify", aliases=["edit", "set"], help="修改任务")
    sp_mod.add_argument(
        "-i",
        "--index",
        type=int,
        default=None,
        help="list 中显示的序号（从 1 开始）",
    )
    sp_mod.add_argument(
        "-m",
        "--match-command",
        default=None,
        help="按 command 子串唯一匹配（多条匹配会报错）",
    )
    sp_mod.add_argument(
        "--new-schedule",
        default=None,
        help="新的五段式 cron 表达式",
    )
    sp_mod.add_argument(
        "--new-command",
        default=None,
        help="新的命令字符串",
    )
    sp_mod.add_argument(
        "--comment",
        default=None,
        nargs="?",
        const="",
        help="设置或清空注释；不带值表示清空",
    )

    return p


def main(argv: Iterable[str] | None = None) -> int:
    args = _build_parser().parse_args(list(argv) if argv is not None else None)

    user_kw: bool | str | None
    if args.tabfile:
        user_kw = None
    elif args.user_name:
        user_kw = args.user_name
    else:
        user_kw = True

    cron = _open_crontab(user=user_kw, tabfile=args.tabfile)
    write = not args.dry_run

    if args.cmd in ("list", "query"):
        cmd_list(cron, show_disabled=args.all)
    elif args.cmd == "add":
        cmd_add(
            cron,
            schedule=args.schedule,
            command=args.command,
            comment=args.comment,
            write=write,
        )
    elif args.cmd in ("remove", "delete", "rm"):
        cmd_remove(
            cron,
            index=args.index,
            match_command=args.match_command,
            write=write,
        )
    elif args.cmd in ("modify", "edit", "set"):
        if (
            args.new_schedule is None
            and args.new_command is None
            and args.comment is None
        ):
            raise SystemExit("modify 至少需要 --new-schedule、--new-command 或 --comment 之一")
        cmd_modify(
            cron,
            index=args.index,
            match_command=args.match_command,
            new_schedule=args.new_schedule,
            new_command=args.new_command,
            comment=args.comment,
            write=write,
        )
    else:
        raise SystemExit(f"未知子命令: {args.cmd}")

    if args.dry_run:
        print("(dry-run: 未写入 crontab)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        sys.stderr.close()
