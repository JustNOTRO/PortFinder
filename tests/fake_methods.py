async def async_port_mock(ip, port, timeout):
    return port if port == 5000 else None


async def no_open_ports_mock(ip, port, timeout):
    return None