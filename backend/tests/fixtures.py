from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

TRADE = {
    "name": "trade",
    "fields": [
        {"name": "tradeId", "type": "string", "required": True},
        {"name": "amount", "type": "number", "required": True},
        {"name": "status", "type": "string"},
    ],
}
BATCH = {
    "schema": "trade",
    "rows": [
        {"tradeId": "T001", "amount": 1000, "status": "OPEN"},
        {"tradeId": "T002", "amount": 2500, "status": "CLOSED"},
        {"tradeId": "T003", "amount": -500},
    ],
}
DASHBOARD = {
    "name": "trade-dashboard",
    "schema": "trade",
    "views": [
        {"type": "summary", "field": "amount", "aggregation": "sum"},
        {"type": "table", "columns": ["tradeId", "amount"]},
    ],
}


CUSTOMER = {
    "name": "customer",
    "fields": [
        {"name": "customerId", "type": "string", "required": True},
        {"name": "name", "type": "string", "required": True},
        {"name": "country", "type": "string"},
    ],
}
CUSTOMER_ROW = {"customerId": "C001", "name": "Alex", "country": "SG"}
CUSTOMER_DASHBOARD = {
    "name": "customer-dashboard",
    "schema": "customer",
    "views": [
        {"type": "table", "columns": ["customerId", "name", "country"]},
    ],
}
