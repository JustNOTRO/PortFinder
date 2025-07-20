from src.portfinder.portfind import port_find


def test_port_find_no_args(capsys):
    port_find()
    output = capsys.readouterr().out
    assert output == "Checking address: 127.0.0.1\n"

def test_port_find_with_args(capsys):
    port_find(address="128.0.0.1")
    output = capsys.readouterr().out
    assert output == "Checking address: 128.0.0.1\n"
