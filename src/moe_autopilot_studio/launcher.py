from __future__ import annotations

import os
import socket
import threading
import webbrowser

import uvicorn

from moe_autopilot_studio.app import app


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def main() -> None:
    host = os.getenv("STUDIO_HOST", "127.0.0.1")
    if host.lower() not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("The Windows Studio launcher only binds to the loopback interface")
    requested = int(os.getenv("STUDIO_PORT", "0"))
    port = requested or free_port()
    if os.getenv("STUDIO_OPEN_BROWSER", "1") == "1":
        threading.Timer(1.0, lambda: webbrowser.open(f"http://{host}:{port}")).start()
    uvicorn.run(app, host=host, port=port, log_config=None, access_log=False)


if __name__ == "__main__":
    main()
