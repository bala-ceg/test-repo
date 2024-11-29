import os
import pytest
from src.assistant.tools.list_files.list_files import execute

def test_list_files_success(tmp_path):
    # Create sample files in a temporary directory
    (tmp_path / "file1.txt").write_text("Content 1")
    (tmp_path / "file2.txt").write_text("Content 2")

    result = execute(str(tmp_path))
    assert result["status"] == "success"
    assert "file1.txt" in result["message"]["files"]
    assert "file2.txt" in result["message"]["files"]

def test_list_files_invalid_path():
    result = execute("/nonexistent/path")
    assert result["status"] == "error"
    assert "Failed to list files" in result["message"]
