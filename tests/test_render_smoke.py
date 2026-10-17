"""Smoke/integration tests for the Render deployment candidate."""
import os
import tempfile
import unittest
from pathlib import Path

_DB_FILE = Path(tempfile.gettempdir()) / f"voltguard-test-{os.getpid()}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_FILE.as_posix()}"
os.environ["SECRET_KEY"] = "test-only-secret-key-with-more-than-32-characters"
os.environ["ENABLE_DEMO_USERS"] = "0"
os.environ["SIMULATE_TELEMETRY"] = "0"

from fastapi.testclient import TestClient
from main import app


class VoltGuardSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def create_tenant(self, suffix):
        tenant_id = f"TEST-{suffix}".upper()
        username = f"admin_{suffix}".replace("-", "_")
        response = self.client.post("/api/tenant/register", json={
            "tenant_id": tenant_id,
            "username": username,
            "password": "Senha-forte-de-teste-2026!"
        })
        self.assertEqual(response.status_code, 200, response.text)
        login = self.client.post("/api/token", json={
            "username": username,
            "password": "Senha-forte-de-teste-2026!"
        })
        self.assertEqual(login.status_code, 200, login.text)
        return tenant_id, {"Authorization": f"Bearer {login.json()['access_token']}"}

    def test_health_and_headers(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.headers.get("x-content-type-options"), "nosniff")

    def test_registration_login_and_tenant_isolation(self):
        tenant_a, headers_a = self.create_tenant("A")
        tenant_b, headers_b = self.create_tenant("B")
        a = self.client.get("/api/panels", headers=headers_a)
        b = self.client.get("/api/panels", headers=headers_b)
        self.assertEqual(a.status_code, 200, a.text)
        self.assertEqual(b.status_code, 200, b.text)
        self.assertEqual(a.json()["tenant_id"], tenant_a)
        self.assertEqual(b.json()["tenant_id"], tenant_b)
        ids_a = {panel["id"] for panel in a.json()["panels"]}
        ids_b = {panel["id"] for panel in b.json()["panels"]}
        self.assertTrue(ids_a)
        self.assertTrue(ids_b)
        self.assertTrue(ids_a.isdisjoint(ids_b))
        foreign_panel = next(iter(ids_b))
        forbidden_access = self.client.get(f"/api/panels/qr/{foreign_panel}", headers=headers_a)
        self.assertEqual(forbidden_access.status_code, 404)

    def test_inventory_cannot_become_negative(self):
        _, headers = self.create_tenant("STOCK")
        panels = self.client.get("/api/panels", headers=headers).json()["panels"]
        response = self.client.post("/api/inventory/update", headers=headers, json={
            "part_name": "Peça de teste", "category": "Teste", "quantity_change": 5,
            "unit_cost": 10, "min_threshold": 1
        })
        self.assertEqual(response.status_code, 200, response.text)
        response = self.client.post("/api/inventory/update", headers=headers, json={
            "part_name": "Peça de teste", "category": "Teste", "quantity_change": -6,
            "unit_cost": 10, "min_threshold": 1
        })
        self.assertEqual(response.status_code, 422, response.text)

    def test_alarm_lifecycle_and_tenant_isolation(self):
        tenant, headers = self.create_tenant("ALARMS")
        other_tenant, other_headers = self.create_tenant("OTHERALARMS")
        panel = self.client.get("/api/panels", headers=headers).json()["panels"][0]
        ingest = self.client.post("/api/telemetry", headers=headers, json={
            "panel_id": panel["id"], "temperature": 120, "current": 20, "voltage": "380V AC"
        })
        self.assertEqual(ingest.status_code, 200, ingest.text)
        alarms = self.client.get("/api/alarms?status_filter=ACTIVE", headers=headers)
        self.assertEqual(alarms.status_code, 200, alarms.text)
        self.assertTrue(any(a["alarm_type"] == "HIGH_TEMPERATURE" for a in alarms.json()))
        alarm = next(a for a in alarms.json() if a["alarm_type"] == "HIGH_TEMPERATURE")
        self.assertEqual(self.client.post(f"/api/alarms/{alarm['id']}/acknowledge", headers=headers).status_code, 200)
        foreign = self.client.post(f"/api/alarms/{alarm['id']}/clear", headers=other_headers)
        self.assertEqual(foreign.status_code, 404)
        clear_telemetry = self.client.post("/api/telemetry", headers=headers, json={
            "panel_id": panel["id"], "temperature": 30, "current": 20, "voltage": "380V AC"
        })
        self.assertEqual(clear_telemetry.status_code, 200, clear_telemetry.text)
        cleared = self.client.get(f"/api/alarms?status_filter=CLEARED", headers=headers)
        self.assertTrue(any(a["id"] == alarm["id"] for a in cleared.json()))

    def test_report_requires_authentication(self):
        response = self.client.get("/api/export/executive-report")
        self.assertEqual(response.status_code, 401)

    def test_weak_password_rejected(self):
        response = self.client.post("/api/tenant/register", json={
            "tenant_id": "TEST-WEAK", "username": "weak_user", "password": "1234567890"
        })
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
