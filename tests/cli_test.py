import sys
import subprocess
import runpy
import pytest

from typer.testing import CliRunner
from src.portfinder.cli import app
from src.portfinder.portfind import scan_port
from .fake_methods import no_open_ports_mock

test_runner = CliRunner()


def test_custom_address(monkeypatch):
    monkeypatch.setattr(scan_port.__module__ + '.scan_port', no_open_ports_mock)
    result = test_runner.invoke(app, ["127.0.0.2", "--start", "1", "--end", "1024"])
    assert result.exit_code == 0
    assert "Please wait, scanning 1 - 1024 ports in remote host: 127.0.0.2" in result.stdout
    assert "Found 0 open port(s) []" in result.stdout


def test_invalid_address():
    result = test_runner.invoke(app, ["abcdef"])
    assert result.exit_code == 2
    assert "Invalid IP address 'abcdef'." in result.stdout


def test_no_address_shows():
    result = test_runner.invoke(app, [])
    assert result.exit_code == 2
    assert "IP address is required." in result.stdout


def test_cmd_runs():
    original_argv = sys.argv.copy()
    try:
        sys.argv = ["src.portfinder.cli"]

        with pytest.raises(SystemExit) as exc:
            runpy.run_module("src.portfinder.cli", run_name="__main__")
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
