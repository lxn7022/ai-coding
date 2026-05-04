"""
真实环境集成测试：子进程调用 linux_cron.py，直接读写当前用户的系统 crontab。

任务命令指向本仓库 test_cron.sh，并在命令行末尾用唯一注释片段标识，
以便用 ``rm -m`` / ``modify -m`` 精确定位与清理，避免依赖 ``-i`` 序号。

运行（需已安装 requirements.txt）::

    cd pycrontab && python -m unittest test_linux_cron_integration -v

注意：会临时向系统 crontab 增加一行并在结束时删除；若进程被强杀可能残留，
可手动 ``linux_cron.py list`` 后删除含 ``__LINUX_CRON_ITEST__`` 的条目。
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
import uuid
from pathlib import Path

_PKG = Path(__file__).resolve().parent
_LINUX_CRON = _PKG / "linux_cron.py"
_TEST_CRON_SH = _PKG / "test_cron.sh"


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(_LINUX_CRON), *args]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(_PKG),
    )


def _cleanup_by_match(needle: str) -> None:
    """尽力删除 command 含 needle 的任务；不存在时忽略失败。"""
    subprocess.run(
        [sys.executable, str(_LINUX_CRON), "rm", "-m", needle],
        capture_output=True,
        text=True,
        cwd=str(_PKG),
    )


def _cannot_write_system_crontab(result: subprocess.CompletedProcess[str]) -> bool:
    err = (result.stderr or "") + (result.stdout or "")
    needles = (
        "Read-only file system",
        "Permission denied",
        "Operation not permitted",
        "you are not allowed to use this program",
    )
    return any(n.lower() in err.lower() for n in needles)


class TestLinuxCronRealEnv(unittest.TestCase):
    """使用当前用户系统 crontab。"""

    def setUp(self) -> None:
        self.assertTrue(
            _LINUX_CRON.is_file(),
            f"缺少 {_LINUX_CRON}",
        )
        self.assertTrue(
            _TEST_CRON_SH.is_file(),
            f"缺少 {_TEST_CRON_SH}",
        )
        if not os.access(_TEST_CRON_SH, os.X_OK):
            os.chmod(_TEST_CRON_SH, 0o755)

    def test_system_crontab_cycle_with_test_cron_shell(self) -> None:
        """add → list → 执行脚本 → modify -m → rm -m；全程用唯一子串定位。"""
        token = f"__LINUX_CRON_ITEST__{uuid.uuid4().hex}__"
        # 勿用「命令 # token」：# 常被 python-crontab 当成 job 注释，不会进 command，-m 匹配不到。
        cron_cmd = f"/bin/sh -c '{_TEST_CRON_SH} && : {token}'"

        try:
            r = _run_cli(
                "add",
                "-s",
                "* * * * *",
                "-c",
                cron_cmd,
                "--comment",
                "linux-cron-integration",
            )
            if r.returncode != 0 and _cannot_write_system_crontab(r):
                raise unittest.SkipTest(
                    "当前环境无法写入系统 crontab（例如容器/沙箱只读）；"
                    "在可正常执行 crontab -e 的登录会话中再运行本测试。",
                )
            self.assertEqual(
                r.returncode,
                0,
                msg=f"add stderr: {r.stderr!r} stdout: {r.stdout!r}",
            )
            self.assertIn("已添加", r.stdout)

            r = _run_cli("list")
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            self.assertIn(str(_TEST_CRON_SH), r.stdout)
            self.assertIn(token, r.stdout)
            self.assertIn("linux-cron-integration", r.stdout)

            run_sh = subprocess.run(
                [str(_TEST_CRON_SH)],
                capture_output=True,
                text=True,
                cwd=str(_PKG),
            )
            self.assertEqual(run_sh.returncode, 0, msg=run_sh.stderr)
            self.assertIn("[INFO] test_cron", run_sh.stdout)
            self.assertIn("path=", run_sh.stdout)
            self.assertIn("timestamp=", run_sh.stdout)

            r = _run_cli(
                "modify",
                "-m",
                token,
                "--new-schedule",
                "0 * * * *",
            )
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            self.assertIn("已修改", r.stdout)

            r = _run_cli("rm", "-m", token)
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            self.assertIn("已删除", r.stdout)

            r = _run_cli("list")
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            self.assertNotIn(
                token,
                r.stdout,
                msg="删除后 list 仍含测试 token，可能误删失败或重复条目",
            )
        finally:
            _cleanup_by_match(token)


if __name__ == "__main__":
    unittest.main()
