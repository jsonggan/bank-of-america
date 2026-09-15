import unittest

from fastapi.testclient import TestClient

from backend.src.app import create_app
from backend.src.service import DashboardService


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.service = DashboardService()
        self.app = create_app(self.service)
        self.client = TestClient(self.app)

    def assert_error(self, response, status, path):
        self.assertEqual(response.status_code, status)
        self.assertEqual(response.headers["content-type"].split(";")[0], "application/json")
        detail = response.json()["errors"][0]
        self.assertEqual(detail["path"], path)
        self.assertTrue(detail["reason"])
        return detail
