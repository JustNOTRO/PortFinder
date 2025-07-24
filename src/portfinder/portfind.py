import typer
import ipaddress
import asyncio

from typing import Optional

LOCAL_HOST_ADDRESS = "127.0.0.1"
LOWEST_PORT = 0
HIGHEST_PORT = 65_535
DEFAULT_TIMEOUT = 0.10

async def scan_port(ip, port, timeout):
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port),
            timeout
        )

        writer.close()
        await writer.wait_closed()
        return port
    except (asyncio.TimeoutError, OSError):
        return None


def is_ip_address(ip_str):
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        return ip_obj.version == 4 or ip_obj.version == 6
    except ValueError:
        return False


def port_find(address: Optional[str] = typer.Argument(None, help="IP address to scan for open ports."),
              start: int = typer.Option(LOWEST_PORT, "--start", help="Starting port range.", min=LOWEST_PORT,
                                        max=HIGHEST_PORT),
              end: int = typer.Option(HIGHEST_PORT, "--end", help="Ending port range.", min=LOWEST_PORT,
                                      max=HIGHEST_PORT),
              timeout: float = typer.Option(DEFAULT_TIMEOUT, "--timeout", help="Timeout for each port scan.")
              ):
    if address is None:
        raise typer.BadParameter("IP address is required.")

    if address == "localhost":
        address = LOCAL_HOST_ADDRESS

    if not is_ip_address(address):
        raise typer.BadParameter(f"Invalid IP address '{address}'.")

    if start > end:
        raise typer.BadParameter("start port cannot be greater than end port.")

    asyncio.run(async_port_find(address, start, end, timeout))


async def async_port_find(address, start, end, timeout):
    print("_" * 63)
    print(f"Please wait, scanning {start} - {end} ports in remote host: {address}")
    print("_" * 63)

    semaphore = asyncio.Semaphore(100)

    async def scan_with_semaphore(port):
        async with semaphore:
            return await scan_port(address, port, timeout)

    tasks = [scan_with_semaphore(port) for port in range(start, end + 1)]
    results = await asyncio.gather(*tasks)

    open_ports = []
    for port in results:
        if port is None:
            continue

        open_ports.append(port)
        print(f"{address} -> port {port} is open!")

    print(f"Found {len(open_ports)} open port(s) {open_ports}.")
