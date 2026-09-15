from backend.tests.integration.routes.support import ApiTestCase


class ErrorsRouteTests(ApiTestCase):
    def test_unknown_route_is_json(self):
        self.assert_error(self.client.get("/missing"), 404, "/missing")

    def test_wrong_method_is_json(self):
        self.assert_error(self.client.get("/schema"), 405, "/schema")

    def test_wrong_method_preserves_allow_header(self):
        response = self.client.get("/schema")
        self.assert_error(response, 405, "/schema")
        self.assertIn("POST", response.headers.get("allow", "").split(", "))
        self.assertNotIn("GET", response.headers.get("allow", "").split(", "))
