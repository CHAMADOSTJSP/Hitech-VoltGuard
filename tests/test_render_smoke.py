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

    def test_demo_simulation_creates_persistent_alarms(self):
        _, headers = self.create_tenant("SIMALARMS")
        panels = self.client.get("/api/panels", headers=headers).json()["panels"]
        panel = panels[0]
        response = self.client.post("/api/demo/force-failure", headers=headers, json={"panel_id": panel["id"]})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertGreaterEqual(response.json()["active_alarms"], 2)
        alarms = self.client.get("/api/alarms?status_filter=ACTIVE", headers=headers)
        self.assertEqual(alarms.status_code, 200, alarms.text)
        types = {alarm["alarm_type"] for alarm in alarms.json() if alarm["panel_id"] == panel["id"]}
        self.assertIn("HIGH_TEMPERATURE", types)
        self.assertIn("HIGH_CURRENT", types)

    def test_asset_creation_and_tenant_isolation(self):
        tenant, headers = self.create_tenant("ASSET")
        other_tenant, other_headers = self.create_tenant("ASSETOTHER")
        panel = self.client.get("/api/panels", headers=headers).json()["panels"][0]
        created = self.client.post("/api/assets", headers=headers, json={
            "asset_tag": "ATIVO-001", "name": "Motor da bomba", "asset_type": "MOTOR",
            "location": "Sala de bombas", "manufacturer": "Fabricante teste", "panel_id": panel["id"]
        })
        self.assertEqual(created.status_code, 201, created.text)
        self.assertEqual(len(self.client.get("/api/assets", headers=headers).json()), 1)
        self.assertEqual(self.client.get("/api/assets", headers=other_headers).json(), [])
        duplicate = self.client.post("/api/assets", headers=headers, json={"asset_tag":"ATIVO-001","name":"Duplicado"})
        self.assertEqual(duplicate.status_code, 409)

    def test_maintenance_plan_generates_tasks_and_recurs(self):
        _, headers = self.create_tenant("MAINT")
        panel = self.client.get("/api/panels", headers=headers).json()["panels"][0]
        asset = self.client.post("/api/assets", headers=headers, json={"asset_tag":"AT-MANUT","name":"Painel teste","panel_id":panel["id"]})
        self.assertEqual(asset.status_code, 201, asset.text)
        plan = self.client.post("/api/maintenance/plans", headers=headers, json={"asset_id":asset.json()["id"],"title":"Inspeção mensal","interval_days":30,"checklist":"Visual;Conexões"})
        self.assertEqual(plan.status_code, 201, plan.text)
        tasks = self.client.get("/api/maintenance/tasks", headers=headers).json()
        self.assertEqual(len(tasks), 1)
        task_id = tasks[0]["id"]
        completed = self.client.patch(f"/api/maintenance/tasks/{task_id}", headers=headers, json={"status":"CONCLUIDA"})
        self.assertEqual(completed.status_code, 200, completed.text)
        self.assertEqual(len(self.client.get("/api/maintenance/tasks", headers=headers).json()), 2)

    def test_device_credential_ingestion_and_revocation(self):
        _, headers = self.create_tenant("DEVICE")
        panel = self.client.get("/api/panels", headers=headers).json()["panels"][0]
        credential = self.client.post("/api/devices/credentials", headers=headers, json={"panel_id":panel["id"],"name":"Gateway teste"})
        self.assertEqual(credential.status_code, 201, credential.text)
        token = credential.json()["device_token"]
        payload = {"panel_id":panel["id"],"temperature":45,"current":120,"voltage":"380V AC"}
        ingest = self.client.post("/api/device/telemetry", headers={"Authorization":f"Bearer {token}"}, json=payload)
        self.assertEqual(ingest.status_code, 200, ingest.text)
        self.assertEqual(ingest.json()["panel_id"], panel["id"])
        # Verify end-to-end persistence of all measurements, not just the current panel snapshot.
        dashboard = self.client.get("/api/panels", headers=headers)
        self.assertEqual(dashboard.status_code, 200, dashboard.text)
        latest = dashboard.json()["history"][panel["id"]][-1]
        self.assertEqual(latest["temperature"], 45)
        self.assertEqual(latest["current"], 120)
        self.assertEqual(latest["voltage"], "380V AC")
        credentials = self.client.get("/api/devices/credentials", headers=headers).json()
        self.assertTrue(credentials[0]["last_used_at"])
        wrong_panel = self.client.post("/api/device/telemetry", headers={"Authorization":f"Bearer {token}"}, json={**payload,"panel_id":"OUTRO"})
        self.assertEqual(wrong_panel.status_code, 403)
        revoked = self.client.post(f"/api/devices/credentials/{credential.json()['id']}/revoke", headers=headers)
        self.assertEqual(revoked.status_code, 200, revoked.text)
        rejected = self.client.post("/api/device/telemetry", headers={"Authorization":f"Bearer {token}"}, json=payload)
        self.assertEqual(rejected.status_code, 401)

    def test_device_telemetry_rejects_missing_token_and_invalid_ranges(self):
        _, headers = self.create_tenant("DEVICEVALIDATION")
        panel = self.client.get("/api/panels", headers=headers).json()["panels"][0]
        credential = self.client.post("/api/devices/credentials", headers=headers, json={"panel_id":panel["id"],"name":"Gateway validação"})
        self.assertEqual(credential.status_code, 201, credential.text)
        token = credential.json()["device_token"]
        payload = {"panel_id":panel["id"],"temperature":25,"current":10,"voltage":"380V AC"}
        no_token = self.client.post("/api/device/telemetry", json=payload)
        self.assertEqual(no_token.status_code, 401)
        invalid = self.client.post("/api/device/telemetry", headers={"Authorization":f"Bearer {token}"}, json={**payload,"current":-1})
        self.assertEqual(invalid.status_code, 422)

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
