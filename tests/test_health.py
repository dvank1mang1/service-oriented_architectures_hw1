import json
import threading
import unittest
from http import HTTPStatus
from urllib.error import HTTPError
from urllib.request import urlopen

from src.catalog_service import create_server


class HealthEndpointTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = create_server(host="127.0.0.1", port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        host, port = cls.server.server_address
        cls.base_url = f"http://{host}:{port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_health_returns_200_and_service_identity(self) -> None:
        with urlopen(f"{self.base_url}/health", timeout=2) as response:
            self.assertEqual(response.status, HTTPStatus.OK)
            self.assertEqual(response.headers.get_content_type(), "application/json")
            self.assertEqual(
                json.load(response),
                {"status": "ok", "service": "catalog-service"},
            )

    def test_unknown_route_returns_404(self) -> None:
        with self.assertRaises(HTTPError) as context:
            urlopen(f"{self.base_url}/products", timeout=2)
        self.assertEqual(context.exception.code, HTTPStatus.NOT_FOUND)


if __name__ == "__main__":
    unittest.main()
