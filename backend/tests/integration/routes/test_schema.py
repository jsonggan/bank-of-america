from copy import deepcopy

from fastapi.testclient import TestClient

from backend.src.app import create_app
from backend.tests.fixtures import BATCH, DASHBOARD, TRADE
from backend.tests.integration.routes.support import ApiTestCase


class SchemaRouteTests(ApiTestCase):
    def test_post_schema(self):
        response = self.client.post("/schema", json=TRADE)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), TRADE)
        self.assertEqual(self.service.get_schema("trade"), TRADE)

    def test_schema_validation_error(self):
        self.assert_error(
            self.client.post("/schema", json={"name": "trade", "fields": []}), 422, "fields"
        )
        self.assertEqual(self.client.post("/schema", json=TRADE).status_code, 201)

    def test_schema_duplicate(self):
        self.client.post("/schema", json=TRADE)
        self.assert_error(self.client.post("/schema", json=TRADE), 409, "name")
        self.assertEqual(self.service.get_schema("trade"), TRADE)

    def test_schema_body_array(self):
        self.assert_error(self.client.post("/schema", json=[]), 422, "$")

    def test_post_ingest(self):
        self.service.register_schema(deepcopy(TRADE))
        response = self.client.post("/ingest", json=BATCH)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"accepted": 3})
        self.assertEqual(self.service.get_rows("trade"), BATCH["rows"])

    def test_ingest_row_validation(self):
        self.service.register_schema(deepcopy(TRADE))
        response = self.client.post(
            "/ingest", json={"schema": "trade", "rows": [{"tradeId": "T1"}]}
        )
        detail = self.assert_error(response, 422, "rows[0].amount")
        self.assertEqual(detail["row"], 0)
        self.assertEqual(detail["field"], "amount")
        self.assertEqual(self.service.get_rows("trade"), [])

    def test_ingest_unknown_schema(self):
        self.assert_error(self.client.post("/ingest", json=BATCH), 404, "schema")

    def test_ingest_malformed_structure(self):
        self.service.register_schema(deepcopy(TRADE))
        self.assert_error(
            self.client.post("/ingest", json={"schema": "trade", "rows": {}}), 422, "rows"
        )

    def test_strict_row_error_matrix(self):
        cases = [
            ({"tradeId": "T1"}, "amount"),
            ({"tradeId": 123, "amount": 1000}, "tradeId"),
            ({"tradeId": "T1", "amount": "1000"}, "amount"),
            ({"tradeId": "T1", "amount": True}, "amount"),
            ({"tradeId": "T1", "amount": None}, "amount"),
            ({"tradeId": "T1", "amount": 1000, "status": None}, "status"),
            ({"tradeId": "T1", "amount": 1000, "currency": "USD"}, "currency"),
        ]
        for row, field in cases:
            with self.subTest(row=row):
                client = TestClient(create_app())
                client.post("/schema", json=TRADE)
                client.post("/dashboard", json=DASHBOARD)
                response = client.post("/ingest", json={"schema": "trade", "rows": [row]})
                detail = self.assert_error(response, 422, f"rows[0].{field}")
                self.assertEqual(detail["row"], 0)
                self.assertEqual(detail["field"], field)
                self.assertEqual(
                    client.get("/dashboard/trade-dashboard").json(),
                    {
                        "views": [
                            {"type": "summary", "value": 0},
                            {"type": "table", "rows": []},
                        ]
                    },
                )
