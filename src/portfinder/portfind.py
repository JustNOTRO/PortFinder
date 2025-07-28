import typer
import ipaddress
import asyncio
import socket

from typing import Optional

LOCAL_HOST_ADDRESS = "127.0.0.1"
PING_REQUEST = "PING"

LOWEST_PORT = 0
HIGHEST_PORT = 65_535
DEFAULT_TIMEOUT = 0.10


class DatagramScanProtocol(asyncio.DatagramProtocol):
    def __init__(self, ip, port, scan_finished: asyncio.Future):
        self.ip = ip
        self.port = port
        self.scan_finished = scan_finished
        self.transport = None

    def datagram_received(self, data, addr):
        print("Received:", data.decode())
        if not self.scan_finished.done():
            self.scan_finished.set_result(True)

    def error_received(self, exc):
        if not self.scan_finished.done():
            self.scan_finished.set_exception(exc)

    def connection_made(self, transport):
        self.transport = transport
        self.transport.sendto(PING_REQUEST.encode(), (self.ip, self.port))

    def connection_lost(self, exc):
        pass


async def scan_port(ip, port, timeout):
    try:
        return await scan_tcp_port(ip, port, timeout)
    except (asyncio.TimeoutError, OSError):
        return await scan_udp_port(ip, port, timeout)


async def scan_tcp_port(ip, port, timeout):
    _, writer = await asyncio.wait_for(
        asyncio.open_connection(ip, port),
        timeout
    )

    writer.close()
    await writer.wait_closed()
    return port


async def scan_udp_port(ip, port, timeout):
    loop = asyncio.get_running_loop()
    scan_finished = loop.create_future()

    transport, _ = await loop.create_datagram_endpoint(
        lambda: DatagramScanProtocol(ip, port, scan_finished),
        local_addr=("0.0.0.0", 0)
    )

    try:
        await asyncio.wait_for(scan_finished, timeout)
        return port
    except (asyncio.TimeoutError, OSError):
        return None
    finally:
        transport.close()


def is_ip_address(ip_str):
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        return ip_obj.version == 4 or ip_obj.version == 6
    except ValueError:
        return False


def try_resolve_domain(domain):
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        raise typer.BadParameter(f"Invalid IP address '{domain}'.")


def port_find(address: Optional[str] = typer.Argument(None, help="IP address to scan for open ports."),
              start: int = typer.Option(LOWEST_PORT, "--start", help="Starting port range.", min=LOWEST_PORT,
                                        max=HIGHEST_PORT),
              end: int = typer.Option(HIGHEST_PORT, "--end", help="Ending port range.", min=LOWEST_PORT,
                                      max=HIGHEST_PORT),
              timeout: float = typer.Option(DEFAULT_TIMEOUT, "--timeout", help="Timeout for each port scan.")
              ):
    asyncio.run(async_port_find(address, start, end, timeout))


async def async_port_find(address, start, end, timeout):
    if address is None:
        raise typer.BadParameter("IP address is required.")

    if address == "localhost":
        address = LOCAL_HOST_ADDRESS

    if not is_ip_address(address):
        address = try_resolve_domain(address)

    if start > end:
        raise typer.BadParameter("start port cannot be greater than end port.")

    message = f"Please wait, scanning {start} - {end} ports in remote host: {address}"
    message_len = len(message)

    print("_" * message_len)
    print(message)
    print("_" * message_len)

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
