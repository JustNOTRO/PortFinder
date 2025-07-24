import sys
import subprocess
import runpy
import pytest


from .fake_methods import async_port_mock
from .fake_methods import no_open_ports_mock

from typer.testing import CliRunner
from src.portfinder.cli import app
from src.portfinder.portfind import scan_port, DEFAULT_TIMEOUT

TEST_TIMEOUT = 0.100
runner = CliRunner()


def test_port_find_no_args():
    result = runner.invoke(app, [])
    assert result.exit_code == 2
    assert "Usage:" in result.output


def test_port_find_localhost(monkeypatch):
    monkeypatch.setattr(scan_port.__module__ + '.scan_port', async_port_mock)

    result = runner.invoke(app, ["localhost", "--start", "1024", "--end", "5000"])
    assert result.exit_code == 0
    assert "_" * 60 in result.stdout
    assert "Please wait, scanning 1024 - 5000 ports in remote host: 127.0.0.1" in result.stdout
    assert "_" * 60 in result.stdout
    assert "127.0.0.1 -> port 5000 is open!" in result.stdout
    assert "Found 1 open port(s) [5000]." in result.stdout


def test_invalid_address():
    result = runner.invoke(app, ["abcdef", "--start", "1", "--end", "1024"])
    assert result.exit_code == 2
    assert "Invalid IP address 'abcdef'." in result.output


def test_invalid_port_range(monkeypatch):
    result = runner.invoke(app, ["127.0.0.1", "--start", "1025", "--end", "1024"])
    assert result.exit_code == 2
    assert "Invalid value: start port cannot be greater than end port. " in result.output


def test_no_open_ports(monkeypatch):
    monkeypatch.setattr(scan_port.__module__ + '.scan_port', no_open_ports_mock)
    result = runner.invoke(app, ["127.0.0.1", "--start", "1", "--end", "1024"])
    assert result.exit_code == 0
    assert "_" * 60 in result.stdout
    assert "Please wait, scanning 1 - 1024 ports in remote host: 127.0.0.1" in result.stdout
    assert "Found 0 open port(s) []" in result.stdout


def test_port_find_cmd_runs(monkeypatch):
    monkeypatch.setattr(scan_port.__module__ + '.scan_port', async_port_mock)
    sys.modules.pop('src.portfinder.cli', None)
    sys.argv = ['src.portfinder.cli']

    with pytest.raises(SystemExit) as exc:
        runpy.run_module('src.portfinder.cli', run_name='__main__')
    assert exc.value.code == 2

    result = subprocess.run([
        sys.executable, '-m', 'src.portfinder.cli',
        '127.0.0.1', '--start', '1', '--end', '1'
    ], capture_output=True, text=True)
    assert result.returncode == 0
    assert 'Please wait, scanning' in result.stdout


@pytest.mark.asyncio
async def test_scan_port():
    result = await scan_port("127.0.0.1", 5000, TEST_TIMEOUT)
    assert result is 5000

@pytest.mark.asyncio
async def test_scan_port_returns_none():
    result = await scan_port("127.0.0.1", 1, TEST_TIMEOUT)
    assert result is None
