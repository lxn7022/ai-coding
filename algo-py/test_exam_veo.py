"""exam_veo 模块的单测：内存打散、外排序打散、run 读写、main 入口。"""
from collections import Counter

import pytest

from exam_veo import (
    _read_run,
    _write_run,
    shuffle_external,
    shuffle_inmemory,
)


@pytest.fixture
def sample_lines():
    """供测试用的行列表。"""
    return ["a\n", "b\n", "c\n", "d\n", "e\n"]


@pytest.fixture
def input_file(tmp_path, sample_lines):
    """临时输入文件路径及内容。"""
    p = tmp_path / "in.txt"
    p.write_text("".join(sample_lines), encoding="utf-8")
    return p


class TestShuffleInmemory:
    """shuffle_inmemory 的单元测试。"""

    def test_same_lines_count_and_content(self, input_file, tmp_path, sample_lines):
        """打散后行数不变、内容集合不变。"""
        out = tmp_path / "out.txt"
        shuffle_inmemory(str(input_file), str(out))
        result = out.read_text(encoding="utf-8")
        result_lines = result.splitlines(keepends=True)
        assert len(result_lines) == len(sample_lines)
        assert Counter(result_lines) == Counter(sample_lines)

    def test_empty_file(self, tmp_path):
        """空文件不报错，输出为空。"""
        inp = tmp_path / "empty.txt"
        inp.write_text("", encoding="utf-8")
        out = tmp_path / "out.txt"
        shuffle_inmemory(str(inp), str(out))
        assert out.read_text(encoding="utf-8") == ""

    def test_single_line(self, tmp_path):
        """单行文件打散后仍为单行。"""
        inp = tmp_path / "one.txt"
        inp.write_text("only\n", encoding="utf-8")
        out = tmp_path / "out.txt"
        shuffle_inmemory(str(inp), str(out))
        assert out.read_text(encoding="utf-8") == "only\n"


class TestWriteReadRun:
    """_write_run / _read_run 往返测试。"""

    def test_roundtrip(self, tmp_path):
        """写入后读出，内容与顺序一致。"""
        path = str(tmp_path / "run.bin")
        pairs = [(0.1, "x\n"), (0.2, "y\n"), (0.3, "z\n")]
        _write_run(path, pairs)
        read_back = list(_read_run(path))
        assert read_back == pairs

    def test_roundtrip_utf8(self, tmp_path):
        """中文等 UTF-8 内容往返正确。"""
        path = str(tmp_path / "run.bin")
        pairs = [(0.5, "中\n"), (0.6, "文\n")]
        _write_run(path, pairs)
        read_back = list(_read_run(path))
        assert read_back == pairs


class TestShuffleExternal:
    """shuffle_external 的单元测试。"""

    def test_same_lines_count_and_content(self, input_file, tmp_path, sample_lines):
        """外排序打散后行数、内容集合不变。"""
        out = tmp_path / "out.txt"
        shuffle_external(str(input_file), str(out), chunk_lines=2)
        result = out.read_text(encoding="utf-8")
        result_lines = result.splitlines(keepends=True)
        assert len(result_lines) == len(sample_lines)
        assert Counter(result_lines) == Counter(sample_lines)

    def test_output_to_stdout(self, input_file, sample_lines, capsys):
        """out_path=None 时输出到 stdout。"""
        shuffle_external(str(input_file), None, chunk_lines=2)
        captured = capsys.readouterr()
        result_lines = (captured.out).splitlines(keepends=True)
        assert len(result_lines) == len(sample_lines)
        assert Counter(result_lines) == Counter(sample_lines)

    def test_empty_file(self, tmp_path):
        """空文件不报错；外排序版不产生 run，故不创建输出文件。"""
        inp = tmp_path / "empty.txt"
        inp.write_text("", encoding="utf-8")
        out = tmp_path / "out.txt"
        shuffle_external(str(inp), str(out), chunk_lines=10)
        assert not out.exists() or out.read_text(encoding="utf-8") == ""

    def test_single_chunk_larger_than_file(self, input_file, tmp_path, sample_lines):
        """块大小大于文件行数，单块完成。"""
        out = tmp_path / "out.txt"
        shuffle_external(str(input_file), str(out), chunk_lines=100)
        result_lines = out.read_text(encoding="utf-8").splitlines(keepends=True)
        assert len(result_lines) == len(sample_lines)
        assert Counter(result_lines) == Counter(sample_lines)


class TestMain:
    """main() 入口测试（通过修改 sys.argv）。"""

    def test_two_args_inmemory(self, input_file, tmp_path, sample_lines):
        """两个参数：走内存版，输出内容集合正确。"""
        out = tmp_path / "out.txt"
        import exam_veo
        old = list(exam_veo.sys.argv)
        try:
            exam_veo.sys.argv = ["exam_veo", str(input_file), str(out)]
            exam_veo.main()
        finally:
            exam_veo.sys.argv = old
        result_lines = out.read_text(encoding="utf-8").splitlines(keepends=True)
        assert len(result_lines) == len(sample_lines)
        assert Counter(result_lines) == Counter(sample_lines)

    def test_three_args_external(self, input_file, tmp_path, sample_lines):
        """三个参数：走外排序版。"""
        out = tmp_path / "out.txt"
        import exam_veo
        old = list(exam_veo.sys.argv)
        try:
            exam_veo.sys.argv = ["exam_veo", str(input_file), str(out), "2"]
            exam_veo.main()
        finally:
            exam_veo.sys.argv = old
        result_lines = out.read_text(encoding="utf-8").splitlines(keepends=True)
        assert len(result_lines) == len(sample_lines)
        assert Counter(result_lines) == Counter(sample_lines)

    def test_no_out_path_exits_with_message(self, input_file, capsys):
        """只有输入无输出时退出码 1 并打印用法。"""
        import exam_veo
        old = list(exam_veo.sys.argv)
        try:
            exam_veo.sys.argv = ["exam_veo", str(input_file)]
            with pytest.raises(SystemExit) as exc_info:
                exam_veo.main()
            assert exc_info.value.code == 1
        finally:
            exam_veo.sys.argv = old
        err = capsys.readouterr().err
        assert "用法" in err or "输入" in err or "输出" in err
