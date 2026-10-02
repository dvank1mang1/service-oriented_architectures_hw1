"""HTTP skeleton for the future Catalog Service.

There is deliberately no marketplace business logic in this module.  It only
exposes a liveness endpoint required to demonstrate the deployment boundary.
"""

from __future__ import annotations

import json
import logging
import os
import signal
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOGGER = logging.getLogger("catalog-service")


class HealthHandler(BaseHTTPRequestHandler):
    server_version = "catalog-service"
    sys_version = ""

    def do_GET(self) -> None:  # noqa: N802 - method name is defined by BaseHTTPRequestHandler
        if self.path != "/health":
            self._write_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
            return

        self._write_json(
            HTTPStatus.OK,
            {"status": "ok", "service": "catalog-service"},
        )

    def _write_json(self, status: HTTPStatus, payload: dict[str, str]) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        LOGGER.info("%s - %s", self.address_string(), format % args)


def create_server(host: str = "0.0.0.0", port: int = 8080) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), HealthHandler)


def main() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    port = int(os.getenv("PORT", "8080"))
    server = create_server(port=port)

    def stop_server(signum: int, _frame: object) -> None:
        LOGGER.info("received signal %s, stopping", signum)
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, stop_server)
    signal.signal(signal.SIGINT, stop_server)

    LOGGER.info("catalog-service listening on port %s", port)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        LOGGER.info("catalog-service stopped")


if __name__ == "__main__":
    main()
