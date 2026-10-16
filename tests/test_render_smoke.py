"""Smoke tests for the Render MVP. These tests use a temporary SQLite database."""
import os
import tempfile
import unittest
from pathlib import Path

DB_FILE = Path(tempfile.gettempdir()) / f"voltguard_test_{os.getpid()}.db"
if DB_FILE.exists():
    DB_FILE.unlink()
os.environ["SECRET_KEY"] = "test-secret-key-only-for-automated-tests-123456789"
os.environ["DATABASE_URL"] = f"sqlite:///{DB_FILE.as_posix()}"
os.environ["ENABLE_DEMO_USERS"] = "0"
os.environ["SIMULATE_TELEMETRY"] = "0"

from fastapi.testclient import TestClient  # noqa: E402
import main  # noqa: E402


class VoltGuardRenderSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        main.engine.dispose()
        if DB_FILE.exists():
            DB_FILE.unlink()

    def register_and_login(self, tenant, username):
        response = self.client.post("/api/tenant/register", json={
            "tenant_id": tenant,
            "username": username,
            "password": "Senha-forte-de-teste-2026",
        })
        self.assertEqual(response.status_code, 200, response.text)
        login = self.client.post("/api/token", json={
            "username": username,
            "password": "Senha-forte-de-teste-2026",
        })
        self.assertEqual(login.status_code, 200, login.text)
        return login.json()["access_token"]

    def test_health_and_home(self):
        health = self.client.get("/health")
        self.assertEqual(health.status_code, 200, health.text)
        self.assertEqual(health.json()["status"], "ok")
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        self.assertIn("HITECH VoltGuard", home.text)
        self.assertNotIn('value="123456"', home.text)

    def test_signup_login_and_tenant_isolation(self):
        token_a = self.register_and_login("TESTE-EMPRESA-A", "admin_teste_a")
        token_b = self.register_and_login("TESTE-EMPRESA-B", "admin_teste_b")
        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}
        panels_a = self.client.get("/api/panels", headers=headers_a)
        panels_b = self.client.get("/api/panels", headers=headers_b)
        self.assertEqual(panels_a.status_code, 200, panels_a.text)
        self.assertEqual(panels_b.status_code, 200, panels_b.text)
        self.assertEqual(len(panels_a.json()["panels"]), 3)
        self.assertEqual(len(panels_b.json()["panels"]), 3)
        ids_a = {p["id"] for p in panels_a.json()["panels"]}
        ids_b = {p["id"] for p in panels_b.json()["panels"]}
        self.assertTrue(ids_a.isdisjoint(ids_b))
        self.assertTrue(all("DEMO" in p["name"] for p in panels_a.json()["panels"]))

    def test_report_requires_authentication(self):
        response = self.client.get("/api/export/executive-report")
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
