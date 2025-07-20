import typer
from typing_extensions import Annotated


def port_find(address: Annotated[str, typer.Argument(help="--address for specifying an address")]= "127.0.0.1"):
    print("Checking address:", address)