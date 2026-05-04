#!/usr/bin/env bash
# 供 crontab 调用时打印本脚本路径与当前时间戳
_self="${BASH_SOURCE[0]:-$0}"
_path="$(cd "$(dirname "$_self")" && pwd)/$(basename "$_self")"
_ts="$(date '+%Y-%m-%d %H:%M:%S %z')"
_epoch="$(date +%s)"
echo "${_ts} [INFO] test_cron path=${_path} timestamp=${_epoch}"
