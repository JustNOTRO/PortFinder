import typer
import ipaddress
import socket

from typing import Optional
from typing_extensions import Annotated
from concurrent.futures import ThreadPoolExecutor

LOWEST_PORT = 0
HIGHEST_PORT = 65_535

def scan_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)
        result = sock.connect_ex((ip, port))
        sock.close()
        return port if result == 0 else None
    except socket.error:
        return None

def is_ip_address(ip_str):
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        return ip_obj.version == 4 or ip_obj.version == 6
    except ValueError:
        return False


def port_find(
    address: Optional[str] = typer.Argument(
        None,
        help="IP address to scan for open ports."
    ),
    start: int = typer.Option(0, "--start", help="Starting port range."),
    end:   int = typer.Option(65_535, "--end",   help="Ending port range."),
):
    if address is None:
        from .cli import app
        app(["--help"])
        typer.Exit(1)

    if not is_ip_address(address):
        print(f"Invalid IP address '{address}'.")
        typer.Exit(1)

    print("_" * 60)
    print(f"Please wait, scanning {start} - {end} ports in remote host: {address}")
    print("_" * 60)

    with ThreadPoolExecutor(max_workers=500) as executor:
        results = executor.map(lambda port: scan_port(address, port), range(start, end + 1))
        open_ports = []
        for result in results:
            if not result:
                continue

            open_ports.append(result)
            print(f"{address} -> port {result} is open!")

        executor.shutdown()

    print(f"Found {format(len(open_ports))} open port(s) {open_ports}.")
