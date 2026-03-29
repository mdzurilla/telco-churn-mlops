import unittest

from app.main import app
from app.api.v1.routers.health import health


class HealthEndpointTestCase(unittest.TestCase):
    def test_health_handler_returns_ok(self) -> None:
        self.assertEqual(health(), {"status": "ok"})

    def test_health_route_is_registered(self) -> None:
        matching_routes = [
            route
            for route in app.routes
            if getattr(route, "path", None) == "/v1/health"
        ]

        self.assertEqual(len(matching_routes), 1)
        self.assertIn("GET", matching_routes[0].methods)


if __name__ == "__main__":
    unittest.main()
