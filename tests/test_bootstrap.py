"""Safety tests for one-time provisioning of an empty pilot database."""
import os
import sqlite3
import subprocess
import sys
import tempfile
from contextlib import closing
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "provision_first_tenant.py"
sys.path.insert(0, str(ROOT))
from scripts.provision_first_tenant import normalized_database_url


class FirstTenantBootstrapTests(unittest.TestCase):
    def test_normalizes_render_postgres_url_schemes(self):
        self.assertEqual(
            normalized_database_url("postgres://user:pass@db.example/app"),
            "postgresql+psycopg://user:pass@db.example/app",
        )
        self.assertEqual(
            normalized_database_url("postgresql://user:pass@db.example/app"),
            "postgresql+psycopg://user:pass@db.example/app",
        )

    def run_bootstrap(self, database_path: Path, stdin: str) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["DATABASE_URL"] = f"sqlite:///{database_path.as_posix()}"
        env["SECRET_KEY"] = "test-only-secret-key-with-more-than-32-characters"
        env.pop("RENDER", None)
        env.pop("ALLOW_SELF_SERVICE_REGISTRATION", None)
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--tenant-id", "BOOTSTRAP-TEST", "--username", "bootstrap_admin"],
            cwd=ROOT,
            env=env,
            input=stdin,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

    def test_refuses_a_database_with_any_existing_rows_without_mutating_it(self):
        with tempfile.TemporaryDirectory(prefix="voltguard-bootstrap-") as temp_dir:
            database_path = Path(temp_dir) / "existing.sqlite"
            with closing(sqlite3.connect(database_path)) as connection:
                with connection:
                    connection.execute("CREATE TABLE preserved_data (value TEXT NOT NULL)")
                    connection.execute("INSERT INTO preserved_data VALUES ('keep-me')")

            result = self.run_bootstrap(database_path, "")

            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("Banco não vazio", result.stderr)
            with closing(sqlite3.connect(database_path)) as connection:
                self.assertEqual(connection.execute("SELECT value FROM preserved_data").fetchone()[0], "keep-me")
                tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertEqual(tables, {"preserved_data"})

    def test_confirmation_is_required_before_schema_or_account_creation(self):
        with tempfile.TemporaryDirectory(prefix="voltguard-bootstrap-") as temp_dir:
            database_path = Path(temp_dir) / "new.sqlite"

            result = self.run_bootstrap(database_path, "wrong confirmation\n")

            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("Confirmação não corresponde", result.stderr)
            with closing(sqlite3.connect(database_path)) as connection:
                tables = connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            self.assertEqual(tables, [])

    def test_refuses_to_read_the_password_from_noninteractive_stdin(self):
        with tempfile.TemporaryDirectory(prefix="voltguard-bootstrap-") as temp_dir:
            database_path = Path(temp_dir) / "new.sqlite"
            stdin = "CREATE FIRST TENANT BOOTSTRAP-TEST\nsecret-from-pipe\nsecret-from-pipe\n"

            result = self.run_bootstrap(database_path, stdin)

            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("terminal interativo", result.stderr)
            self.assertNotIn("secret-from-pipe", result.stdout + result.stderr)
            with closing(sqlite3.connect(database_path)) as connection:
                tables = connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            self.assertEqual(tables, [])


if __name__ == "__main__":
    unittest.main()
