import json
from copy import deepcopy

from fastapi.testclient import TestClient

from backend.src.app import create_app
from backend.tests.fixtures import BATCH, DASHBOARD, TRADE
from backend.tests.integration.routes.support import ApiTestCase


class HttpRouteTests(ApiTestCase):
    def test_schema_malformed_json(self):
        self.assert_error(
            self.client.post("/schema", content="{", headers={"Content-Type": "application/json"}),
            422,
            "$",
        )

    def test_schema_wrong_content_type(self):
        self.assert_error(
            self.client.post("/schema", content="{}", headers={"Content-Type": "text/plain"}),
            422,
            "$",
        )

    def test_ingest_malformed_json(self):
        self.assert_error(
            self.client.post("/ingest", content="{", headers={"Content-Type": "application/json"}),
            422,
            "$",
        )

    def test_dashboard_malformed_json(self):
        self.assert_error(
            self.client.post(
                "/dashboard", content="{", headers={"Content-Type": "application/json"}
            ),
            422,
            "$",
        )

    def test_nonfinite_json_metadata_is_rejected_before_registration(self):
        for token in ("NaN", "Infinity", "-Infinity", "1e400"):
            for endpoint, definition in (("/schema", TRADE), ("/dashboard", DASHBOARD)):
                with self.subTest(token=token, endpoint=endpoint):
                    client = TestClient(create_app())
                    if endpoint == "/dashboard":
                        client.post("/schema", json=TRADE)
                    payload = (
                        json.dumps(definition)[:-1] + ', "metadata": {"value": ' + token + "}}"
                    )
                    self.assert_error(
                        client.post(
                            endpoint, content=payload, headers={"Content-Type": "application/json"}
                        ),
                        422,
                        "$",
                    )
                    self.assertEqual(client.post(endpoint, json=definition).status_code, 201)

    def test_duplicate_json_keys_reject_the_entire_batch(self):
        self.service.register_schema(deepcopy(TRADE))
        self.service.ingest(deepcopy(BATCH))
        for payload in (
            '{"schema":"missing","schema":"trade","rows":[]}',
            '{"schema":"trade","rows":[{"tradeId":"T4","amount":10},'
            '{"tradeId":"T5","amount":1000,"amount":1}]}',
        ):
            with self.subTest(payload=payload):
                self.assert_error(
                    self.client.post(
                        "/ingest", content=payload, headers={"Content-Type": "application/json"}
                    ),
                    422,
                    "$",
                )
                self.assertEqual(self.service.get_rows("trade"), BATCH["rows"])

    def test_valid_json_metadata_is_preserved(self):
        definition = deepcopy(TRADE)
        definition["metadata"] = {"name": "desk", "nested": {"name": "risk", "scale": 1.25}}
        definition["fields"][1]["aggregation"] = "sum"
        response = self.client.post("/schema", json=definition)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), definition)
        self.assertEqual(self.service.get_schema("trade"), definition)
