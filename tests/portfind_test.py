from src.portfinder.portfind import port_find
import pytest


def test_port_find_invalid_address(capsys):
    with pytest.raises(SystemExit):
        port_find(address="abcdef", start=1, end=1024)

    output = capsys.readouterr().out
    assert output == "Invalid IP address 'abcdef'.\n"

def test_port_find_no_open_ports(capsys):
    port_find(address="127.0.0.1", start=1, end=1024)
    output = capsys.readouterr().out
    assert "_" * 60 in output
    assert f"Please wait, scanning remote host: 127.0.0.1" in output
    assert "_" * 60 in output
    assert "Found 0 open port(s) [].\n" in output

def test_port_find(capsys):
    port_find(address="127.0.0.1", start=1024, end=5000)
    output = capsys.readouterr().out
    assert "_" * 60 in output
    assert f"Please wait, scanning remote host: 127.0.0.1" in output
    assert "_" * 60 in output
    assert "Found 1 open port(s) [5000].\n" in output

