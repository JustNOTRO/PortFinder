import sys
import subprocess
import runpy
import pytest

from typer.testing import CliRunner
from src.portfinder.cli import app


runner = CliRunner()


def test_default_address():
    result = runner.invoke(app)
    assert result.exit_code == 0
    assert "Checking address: 127.0.0.1" in result.output


def test_custom_address():
    result = runner.invoke(app, ["127.0.0.2"])
    assert result.exit_code == 0
    assert "Checking address: 127.0.0.2" in result.output

def test_cmd_runs():
    original_argv = sys.argv.copy()
    try:
        sys.argv = ["src.portfinder"]

        with pytest.raises(SystemExit) as exc:
            runpy.run_module("src.portfinder.__main__", run_name="__main__")

        assert exc.value.code == 0

        result = subprocess.run(
            [sys.executable, "-m", "src.portfinder.cli"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Checking address" in result.stdout
    finally:
        sys.argv = original_argv
