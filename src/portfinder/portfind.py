import typer
from typing_extensions import Annotated


def port_find(address: Annotated[str, typer.Argument(help="IP address to scan for open ports.")] = "127.0.0.1"):
    print("Checking address:", address)