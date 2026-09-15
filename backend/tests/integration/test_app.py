import json
import unittest

from fastapi.testclient import TestClient

from backend.src.app import create_app
from backend.src.config import AppConfig
from backend.src.service import DashboardService
from backend.tests.fixtures import (
    BATCH,
    CUSTOMER,
    CUSTOMER_DASHBOARD,
    CUSTOMER_ROW,
    DASHBOARD,
    REPO_ROOT,
    TRADE,
)
from backend.tests.integration.server import http_json, running_backend


class AppTests(unittest.TestCase):
    def test_openapi_documents_json_bodies_and_interactive_docs_are_available(self):
        with TestClient(create_app()) as client:
            self.assertEqual(client.get("/docs").status_code, 200)
            specification = client.get("/openapi.json").json()
            for path in ("/schema", "/ingest", "/dashboard"):
                body = specification["paths"][path]["post"]["requestBody"]
                self.assertTrue(body["required"])
                self.assertIn("example", body["content"]["application/json"])
            self.assertIn("get", specification["paths"]["/dashboard/{name}"])

    def test_application_metadata_can_be_configured(self):
        config = AppConfig(title="Test API", version="2.0.0", description="Test instance")
        with TestClient(create_app(config=config)) as client:
            info = client.get("/openapi.json").json()["info"]
            self.assertEqual(info["title"], "Test API")
            self.assertEqual(info["version"], "2.0.0")
            self.assertEqual(info["description"], "Test instance")

    def test_openapi_groups_the_two_workflows(self):
        with TestClient(create_app()) as client:
            paths = client.get("/openapi.json").json()["paths"]
            for path in ("/schema", "/ingest"):
                self.assertEqual(paths[path]["post"]["tags"], ["Schemas and ingestion"])
            self.assertEqual(paths["/dashboard"]["post"]["tags"], ["Dashboards"])
            self.assertEqual(paths["/dashboard/{name}"]["get"]["tags"], ["Dashboards"])

    def test_routes_share_injected_state_without_leaking_to_other_apps(self):
        service = DashboardService()
        with TestClient(create_app(service)) as first, TestClient(create_app()) as second:
            self.assertEqual(first.post("/schema", json=TRADE).status_code, 201)
            self.assertEqual(first.post("/ingest", json=BATCH).json(), {"accepted": 3})
            self.assertEqual(first.post("/dashboard", json=DASHBOARD).status_code, 201)
            self.assertEqual(
                first.get("/dashboard/trade-dashboard").json()["views"][0]["value"], 3000
            )
            self.assertEqual(service.get_rows("trade"), BATCH["rows"])
            self.assertEqual(service.get_schema("trade"), TRADE)
            self.assertEqual(service.get_dashboard_config("trade-dashboard"), DASHBOARD)
            self.assertEqual(second.post("/ingest", json=BATCH).status_code, 404)
            self.assertEqual(second.get("/dashboard/trade-dashboard").status_code, 404)
            self.assertEqual(second.post("/schema", json=TRADE).status_code, 201)
            self.assertEqual(second.post("/dashboard", json=DASHBOARD).status_code, 201)
            self.assertEqual(
                second.get("/dashboard/trade-dashboard").json(),
                {"views": [{"type": "summary", "value": 0}, {"type": "table", "rows": []}]},
            )


class WorkflowTests(unittest.TestCase):
    def test_documented_example_files(self):
        client = TestClient(create_app())
        examples = REPO_ROOT / "examples"
        for schema in ("trade", "customer"):
            for suffix, endpoint, status in (
                ("schema", "/schema", 201),
                ("rows", "/ingest", 200),
                ("dashboard", "/dashboard", 201),
            ):
                payload = json.loads((examples / f"{schema}-{suffix}.json").read_text())
                response = client.post(endpoint, json=payload)
                self.assertEqual(response.status_code, status, response.json())
        trade = client.get("/dashboard/trade-dashboard")
        self.assertEqual(trade.status_code, 200)
        self.assertEqual(trade.json()["views"][0], {"type": "summary", "value": 3000})
        self.assertEqual(
            trade.json()["views"][1]["rows"],
            [
                {"tradeId": "T001", "amount": 1000},
                {"tradeId": "T002", "amount": 2500},
                {"tradeId": "T003", "amount": -500},
            ],
        )
        customer = client.get("/dashboard/customer-dashboard")
        self.assertEqual(customer.status_code, 200)
        self.assertEqual(customer.json(), {"views": [{"type": "table", "rows": [CUSTOMER_ROW]}]})

    def test_full_trade_and_customer_flow(self):
        client = TestClient(create_app())
        self.assertEqual(client.post("/schema", json=TRADE).status_code, 201)
        self.assertEqual(client.post("/ingest", json=BATCH).json(), {"accepted": 3})
        self.assertEqual(client.post("/dashboard", json=DASHBOARD).status_code, 201)
        trade = client.get("/dashboard/trade-dashboard")
        self.assertEqual(trade.status_code, 200)
        self.assertEqual(
            trade.json(),
            {
                "views": [
                    {"type": "summary", "value": 3000},
                    {
                        "type": "table",
                        "rows": [
                            {"tradeId": row["tradeId"], "amount": row["amount"]}
                            for row in BATCH["rows"]
                        ],
                    },
                ]
            },
        )
        self.assertEqual(client.post("/schema", json=CUSTOMER).status_code, 201)
        self.assertEqual(
            client.post("/ingest", json={"schema": "customer", "rows": [CUSTOMER_ROW]}).json(),
            {"accepted": 1},
        )
        self.assertEqual(client.post("/dashboard", json=CUSTOMER_DASHBOARD).status_code, 201)
        self.assertEqual(
            client.get("/dashboard/customer-dashboard").json(),
            {"views": [{"type": "table", "rows": [CUSTOMER_ROW]}]},
        )
        self.assertEqual(client.get("/dashboard/trade-dashboard").json(), trade.json())

    def test_rejected_batch_preserves_dashboard_then_new_rows_appear(self):
        client = TestClient(create_app())
        client.post("/schema", json=TRADE)
        client.post("/ingest", json=BATCH)
        client.post("/dashboard", json=DASHBOARD)
        before = client.get("/dashboard/trade-dashboard").json()
        response = client.post(
            "/ingest",
            json={
                "schema": "trade",
                "rows": [
                    {"tradeId": "T004", "amount": 200},
                    {"tradeId": "BAD"},
                ],
            },
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["errors"][0]["row"], 1)
        self.assertEqual(client.get("/dashboard/trade-dashboard").json(), before)
        self.assertEqual(
            client.post(
                "/ingest", json={"schema": "trade", "rows": [{"tradeId": "T004", "amount": 200}]}
            ).status_code,
            200,
        )
        after = client.get("/dashboard/trade-dashboard").json()
        self.assertEqual(after["views"][0]["value"], 3200)
        self.assertEqual(len(after["views"][1]["rows"]), 4)
        self.assertEqual(after["views"][1]["rows"][-1], {"tradeId": "T004", "amount": 200})


class ProcessRestartTests(unittest.TestCase):
    def test_g12_restart_discards_schemas_rows_and_dashboards(self):
        with running_backend() as base_url:
            self.assertEqual(http_json(base_url, "/schema", TRADE)[0], 201)
            self.assertEqual(http_json(base_url, "/ingest", BATCH), (200, {"accepted": 3}))
            self.assertEqual(http_json(base_url, "/dashboard", DASHBOARD)[0], 201)
            status, dashboard = http_json(base_url, "/dashboard/trade-dashboard")
            self.assertEqual(status, 200)
            self.assertEqual(dashboard["views"][0]["value"], 3000)
        with running_backend() as base_url:
            self.assertEqual(http_json(base_url, "/dashboard/trade-dashboard")[0], 404)
            self.assertEqual(http_json(base_url, "/ingest", BATCH)[0], 404)
            self.assertEqual(http_json(base_url, "/schema", TRADE)[0], 201)
            self.assertEqual(http_json(base_url, "/dashboard", DASHBOARD)[0], 201)
            self.assertEqual(
                http_json(base_url, "/dashboard/trade-dashboard"),
                (
                    200,
                    {
                        "views": [
                            {"type": "summary", "value": 0},
                            {"type": "table", "rows": []},
                        ]
                    },
                ),
            )
