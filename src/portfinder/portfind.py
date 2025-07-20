import typer
import ipaddress
import socket

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
        address: Annotated[str, typer.Argument(help="IP address to scan for open ports.")] = "127.0.0.1",
        start: Annotated[int, typer.Option(help="Starting port range.")] = LOWEST_PORT,
        end: Annotated[int, typer.Option(help="Ending port range.")] = HIGHEST_PORT,
):
    if not is_ip_address(address):
        print(f"Invalid IP address '{address}'.")
        exit(1)

    print("Checking address:", address,"..")

    with ThreadPoolExecutor(max_workers=500) as executor:
        results = executor.map(lambda port: scan_port(address, port), range(start, end + 1))
        open_ports = []
        for port in results:
            if not port:
                continue

            open_ports.append(port)
            print(f"{address} -> port {port} is open!")


    if len(open_ports) == 0:
        print("No open ports found hooray!")
    else:
        print(f"Found {len(open_ports)} open ports {open_ports}.")
