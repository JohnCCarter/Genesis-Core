import re

from starlette.testclient import TestClient

from core.server import app

client = TestClient(app)

r = client.get("/ui")
r.raise_for_status()
html = r.text

checks = {
    "policy_symbol_select": bool(re.search(r'id="policy_symbol_select"', html)),
    "order_symbol_disabled": bool(re.search(r'id="symbol_select"[^>]*disabled', html)),
}
print(checks)
