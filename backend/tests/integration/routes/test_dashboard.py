from copy import deepcopy
from urllib.parse import quote

from backend.tests.fixtures import BATCH, DASHBOARD, TRADE
from backend.tests.integration.routes.support import ApiTestCase


class DashboardRouteTests(ApiTestCase):
    def test_post_dashboard(self):
        self.service.register_schema(deepcopy(TRADE))
        response = self.client.post("/dashboard", json=DASHBOARD)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), DASHBOARD)
        self.assertEqual(self.service.get_dashboard_config("trade-dashboard"), DASHBOARD)

    def test_dashboard_duplicate(self):
        self.service.register_schema(deepcopy(TRADE))
        self.client.post("/dashboard", json=DASHBOARD)
        self.assert_error(self.client.post("/dashboard", json=DASHBOARD), 409, "name")
        self.assertEqual(self.service.get_dashboard_config("trade-dashboard"), DASHBOARD)

    def test_dashboard_unknown_schema(self):
        self.assert_error(self.client.post("/dashboard", json=DASHBOARD), 404, "schema")

    def test_dashboard_invalid_config(self):
        self.service.register_schema(deepcopy(TRADE))
        definition = deepcopy(DASHBOARD)
        definition["views"] = []
        self.assert_error(self.client.post("/dashboard", json=definition), 422, "views")
        self.assertEqual(self.client.post("/dashboard", json=DASHBOARD).status_code, 201)

    def test_get_dashboard(self):
        self.service.register_schema(deepcopy(TRADE))
        self.service.ingest(deepcopy(BATCH))
        self.service.register_dashboard(deepcopy(DASHBOARD))
        response = self.client.get("/dashboard/trade-dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["views"][0], {"type": "summary", "value": 3000})
        self.assertEqual(
            response.json()["views"][1]["rows"],
            [{"tradeId": row["tradeId"], "amount": row["amount"]} for row in BATCH["rows"]],
        )

    def test_get_unknown_dashboard(self):
        self.assert_error(self.client.get("/dashboard/missing"), 404, "name")

    def test_get_sum_overflow(self):
        self.service.register_schema(deepcopy(TRADE))
        self.service.register_dashboard(deepcopy(DASHBOARD))
        self.service.ingest(
            {"schema": "trade", "rows": [{"tradeId": str(i), "amount": 1e308} for i in range(2)]}
        )
        self.assert_error(self.client.get("/dashboard/trade-dashboard"), 422, "views[0]")

    def test_unretrievable_dashboard_name_returns_validation_error(self):
        self.client.post("/schema", json=TRADE)
        for name in ("/risk", "risk/desk", "risk\nreport", ".", ".."):
            with self.subTest(name=name):
                self.assert_error(
                    self.client.post("/dashboard", json={**DASHBOARD, "name": name}),
                    422,
                    "name",
                )
        self.assertEqual(self.client.post("/dashboard", json=DASHBOARD).status_code, 201)

    def test_dashboard_names_round_trip_when_url_encoded(self):
        self.client.post("/schema", json=TRADE)
        self.client.post("/ingest", json=BATCH)
        for name in ("risk report", "caf\u00e9", "risk?#%", " trade-dashboard "):
            with self.subTest(name=name):
                response = self.client.post("/dashboard", json={**DASHBOARD, "name": name})
                self.assertEqual(response.status_code, 201)
                self.assertEqual(response.json()["name"], name)
                dashboard = self.client.get("/dashboard/" + quote(name, safe=""))
                self.assertEqual(dashboard.status_code, 200)
                self.assertEqual(dashboard.json()["views"][0]["value"], 3000)
