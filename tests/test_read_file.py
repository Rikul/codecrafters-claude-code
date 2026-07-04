
from app.tools.read_file import ReadFileTool
read_file = ReadFileTool.call


def test_read_file_returns_contents(tmp_path):
    f = tmp_path / "hello.txt"
    f.write_text("hello world", encoding="utf-8")
    assert read_file(str(f)) == "hello world"


def test_read_file_nonexistent_returns_error():
    result = read_file("/nonexistent/path/file.txt")
    assert result.startswith("Error:")


def test_read_file_empty_file(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_text("", encoding="utf-8")
    assert read_file(str(f)) == ""


def test_read_file_multiline(tmp_path):
    content = "line1\nline2\nline3"
    f = tmp_path / "multi.txt"
    f.write_text(content, encoding="utf-8")
    assert read_file(str(f)) == content


def test_read_file_with_offset(tmp_path):
    f = tmp_path / "offset.txt"
    f.write_text("hello world", encoding="utf-8")
    assert read_file(str(f), offset=6) == "world"


def test_read_file_with_size(tmp_path):
    f = tmp_path / "size.txt"
    f.write_text("hello world", encoding="utf-8")
    assert read_file(str(f), size=5) == "hello"


def test_read_file_with_offset_and_size(tmp_path):
    f = tmp_path / "both.txt"
    f.write_text("hello world", encoding="utf-8")
    assert read_file(str(f), offset=3, size=4) == "lo w"


def test_read_file_offset_beyond_end(tmp_path):
    f = tmp_path / "short.txt"
    f.write_text("hi", encoding="utf-8")
    assert read_file(str(f), offset=100) == ""


def test_read_file_size_larger_than_remaining(tmp_path):
    f = tmp_path / "small.txt"
    f.write_text("hello", encoding="utf-8")
    assert read_file(str(f), offset=3, size=100) == "lo"
