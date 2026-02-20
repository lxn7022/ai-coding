#!/usr/bin/env python3
"""
文本行打散（shuffle）工具。

- 内存版：整文件读入内存后打散，适合中小文件。
- 外排序版：分块读入、赋随机键、排序写 run、K 路归并输出，内存占用与块大小相关，适合超大文件。
"""
import heapq
import os
import random
import struct
import sys
import tempfile


def shuffle_inmemory(in_path: str, out_path: str, encoding: str = "utf-8") -> None:
    """将文本文件所有行读入内存，打散后写入输出文件。"""
    with open(in_path, encoding=encoding, errors="replace") as f:
        lines = f.readlines()
    random.shuffle(lines)
    with open(out_path, "w", encoding=encoding) as f:
        f.writelines(lines)


def _write_run(path: str, pairs: list, encoding: str = "utf-8") -> None:
    """将 (key, line) 列表按 key 排序后写入 path。每条：8 字节 key + 4 字节长度 + 行字节。"""
    pairs.sort(key=lambda x: x[0])
    with open(path, "wb") as out:
        for key, line in pairs:
            b = line.encode(encoding, errors="replace")
            out.write(struct.pack("dI", key, len(b)))
            out.write(b)


def _read_run(path: str, encoding: str = "utf-8"):
    """从 run 文件逐条读出 (key, line)。"""
    with open(path, "rb") as f:
        while True:
            header = f.read(12)
            if len(header) < 12:
                break
            key, length = struct.unpack("dI", header)
            yield key, f.read(length).decode(encoding, errors="replace")


def shuffle_external(
    in_path: str,
    out_path: str | None,
    chunk_lines: int = 100_000,
    encoding: str = "utf-8",
) -> None:
    """外排序打散：分块读入、赋随机键、排序写 run，再 K 路归并输出。"""
    run_paths = []
    run_dir = tempfile.mkdtemp()
    try:
        with open(in_path, "r", encoding=encoding, errors="replace") as f:
            while True:
                chunk = []
                for _ in range(chunk_lines):
                    line = f.readline()
                    if not line:
                        break
                    chunk.append(line)
                if not chunk:
                    break
                pairs = [(random.random(), line) for line in chunk]
                run_path = os.path.join(run_dir, f"run_{len(run_paths)}")
                _write_run(run_path, pairs, encoding)
                run_paths.append(run_path)

        if not run_paths:
            return

        iterators = [_read_run(p, encoding) for p in run_paths]
        merged = heapq.merge(*iterators, key=lambda x: x[0])

        out = (
            open(out_path, "w", encoding=encoding)
            if out_path
            else sys.stdout
        )
        try:
            for _, line in merged:
                out.write(line)
        finally:
            if out_path:
                out.close()
    finally:
        for p in run_paths:
            try:
                os.remove(p)
            except OSError:
                pass
        try:
            os.rmdir(run_dir)
        except OSError:
            pass


def main() -> None:
    in_path = sys.argv[1] if len(sys.argv) > 1 else None
    out_path = sys.argv[2] if len(sys.argv) > 2 else None
    chunk_arg = sys.argv[3] if len(sys.argv) > 3 else None
    chunk = int(chunk_arg) if chunk_arg is not None else 0

    if not in_path:
        # 从 stdin 读入，内存打散后输出
        lines = sys.stdin.readlines()
        random.shuffle(lines)
        out = open(out_path, "w", encoding="utf-8") if out_path else sys.stdout
        try:
            out.writelines(lines)
        finally:
            if out_path:
                out.close()
        return

    if not out_path:
        print(
            "用法: python exam_veo.py <输入文件> <输出文件> [块行数]\n"
            "  块行数省略时用内存版；指定时用外排序版。",
            file=sys.stderr,
        )
        sys.exit(1)

    if chunk > 0:
        shuffle_external(in_path, out_path, chunk_lines=chunk)
    else:
        shuffle_inmemory(in_path, out_path)


if __name__ == "__main__":
    main()
