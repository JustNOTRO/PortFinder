from typer.testing import CliRunner
from src.portfinder.cli import app


runner = CliRunner()

def test_port_find_triggered():
    result = runner.invoke(app)
    assert result.exit_code == 0
    assert "Checking address: 127.0.0.1" in result.output

def test_port_find_triggered_with_args():
    result = runner.invoke(app, "127.0.0.2")
    assert result.exit_code == 0
    assert "Checking address: 127.0.0.2" in result.output

