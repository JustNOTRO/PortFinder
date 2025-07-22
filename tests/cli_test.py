import sys
import subprocess
import runpy
import pytest

from typer.testing import CliRunner
from src.portfinder.cli import app

test_runner = CliRunner()


def test_custom_address():
    result = test_runner.invoke(app, ["127.0.0.2", "--start", "1", "--end", "1024"])
    assert result.exit_code == 0
    assert "Please wait, scanning 1 - 1024 ports in remote host: 127.0.0.2" in result.stdout
    assert "Found 0 open port(s) []" in result.stdout


def test_invalid_address():
    result = test_runner.invoke(app, ["abcdef"])
    assert result.exit_code == 1
    assert "Invalid IP address 'abcdef'." in result.stdout


def test_no_address_shows_help_and_exits():
    result = test_runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout


def test_cmd_runs():
    original_argv = sys.argv.copy()
    try:
        # Simulate running the CLI module directly
        sys.argv = ["src.portfinder.cli"]

        # run_module will call the if __name__ == '__main__' block in cli.py
        with pytest.raises(SystemExit) as exc:
            runpy.run_module("src.portfinder.cli", run_name="__main__")
        assert exc.value.code == 0

        # Test the -m invocation of the CLI module
        result = subprocess.run(
            [sys.executable, "-m", "src.portfinder.cli"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Usage:" in result.stdout
    finally:
        sys.argv = original_argv
