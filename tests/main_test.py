import runpy
import sys
import pytest
import subprocess

from typer.testing import CliRunner
from src.portfinder.cli import app

runner = CliRunner()

def test_cli_help_from_app():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout

def test_cmd_runs():
    original_argv = sys.argv.copy()
    try:
        sys.argv = ["src.portfinder.cli"]

        with pytest.raises(SystemExit) as exc:
            runpy.run_module("src.portfinder.__main__", run_name="__main__")
        assert exc.value.code == 2

        result = subprocess.run(
            [sys.executable, "-m", "src.portfinder.cli"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
        assert "Usage:" in result.stderr
    finally:
        sys.argv = original_argv
