from src.portfinder.portfind import port_find
from typer.testing import CliRunner
from src.portfinder.cli import app

test_runner = CliRunner()


def test_port_find_no_args(capsys):
    output = test_runner.invoke(app, []).stdout
    assert "Usage:" in output


def test_port_find_localhost(capsys):
    output = test_runner.invoke(app, ["localhost", "--start", "1024", "--end", "5000"]).stdout
    assert "_" * 60 in output
    assert f"Please wait, scanning 1024 - 5000 ports in remote host: 127.0.0.1" in output
    assert "_" * 60 in output
    assert "Found 1 open port(s) [5000].\n" in output


def test_invalid_address(capsys):
    output = test_runner.invoke(app, ["abcdef", "--start", "1", "--end", "1024"]).stdout
    assert output == "Invalid IP address 'abcdef'.\n"

def test_invalid_port_range(capsys):
    output = test_runner.invoke(app, ["127.0.0.1", "--start", "1025", "--end", "1024"]).stdout
    assert "Usage:" in output

def test_invalid_start_range(capsys):
    output = test_runner.invoke(app, ["127.0.0.1", "--start", "abc", "--end", "1024"]).stdout
    assert "Invalid value for '--start': 'abc' is not a valid integer." in output

def test_invalid_end_range(capsys):
    output = test_runner.invoke(app, ["127.0.0.1", "--start", "1024", "--end", "abc"]).stdout
    assert "Invalid value for '--end': 'abc' is not a valid integer." in output

def test_no_open_ports(capsys):
    output = test_runner.invoke(app, ["127.0.0.1", "--start", "1", "--end", "1024"]).stdout
    assert "_" * 60 in output
    assert f"Please wait, scanning 1 - 1024 ports in remote host: 127.0.0.1" in output
    assert "_" * 60 in output
    assert "Found 1 open port(s) [631].\n" in output


def test_port_find(capsys):
    port_find(address="127.0.0.1", start=1024, end=5000)
    output = test_runner.invoke(app, ["127.0.0.1", "--start", "1024", "--end", "5000"]).stdout
    assert "_" * 60 in output
    assert f"Please wait, scanning 1024 - 5000 ports in remote host: 127.0.0.1" in output
    assert "_" * 60 in output
    assert "127.0.0.1 -> port 5000 is open!\n" in output
    assert "Found 1 open port(s) [5000].\n" in output


def test_port_find_with_start_arg(capsys):
    output = test_runner.invoke(app, ["127.0.0.1", "--start", "65000"]).stdout
    assert "_" * 60 in output
    assert f"Please wait, scanning 65000 - 65535 ports in remote host: 127.0.0.1" in output
    assert "_" * 60 in output
    assert "Found 0 open port(s) []." in output
