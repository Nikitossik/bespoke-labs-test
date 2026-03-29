"""
Use this file to define pytest tests that verify the outputs of the task.

This file will be copied to /tests/test_outputs.py and run by the /tests/test.sh file
from the working directory.
"""


import re
import subprocess
import importlib.util


def _load_main_module():
    spec = importlib.util.spec_from_file_location("app_main", "/app/main.py")
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_get_today_iso_returns_date_string():
    module = _load_main_module()
    value = module.get_today_iso()
    assert isinstance(value, str)
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", value), value


def test_main_returns_date_string():
    module = _load_main_module()
    value = module.main()
    assert isinstance(value, str)
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", value), value


def test_main_py_executes_without_output():
    result = subprocess.run(
        ["python", "/app/main.py"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == ""