import typer
from .portfind import port_find


app = typer.Typer()
app.command()(port_find)


if __name__ == "__main__":
    app()