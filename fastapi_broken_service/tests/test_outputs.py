"""
Use this file to define pytest tests that verify the outputs of the task.

This file will be copied to /tests/test_outputs.py and run by the /tests/test.sh file
from the working directory.
"""

import subprocess
import sys


def _ensure_test_dependencies() -> None:
    try:
        import fastapi 
        import httpx  
        import sqlalchemy
        import pydantic  
    except ModuleNotFoundError:
        subprocess.check_call(
            [
                "uv",
                "pip",
                "install",
                "--python",
                sys.executable,
                "fastapi==0.115.0",
                "httpx==0.27.2",
                "sqlalchemy==2.0.35",
                "pydantic==2.9.2",
            ]
        )


_ensure_test_dependencies()

import importlib
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient


DB_FILE = Path("/app/data.db")

MODULES_TO_CLEAR = [
    "main",
    "models",
    "schemas",
]


def _load_fresh_app_module():
    if DB_FILE.exists():
        DB_FILE.unlink()

    if "/app" not in sys.path:
        sys.path.insert(0, "/app")

    for module_name in MODULES_TO_CLEAR:
        if module_name in sys.modules:
            del sys.modules[module_name]

    app_module = importlib.import_module("main")
    return app_module


def _count_rows(idempotency_key: str) -> tuple[int, int]:
    con = sqlite3.connect(DB_FILE)
    try:
        payment_count = con.execute(
            "SELECT COUNT(*) FROM payments WHERE idempotency_key = ?",
            (idempotency_key,),
        ).fetchone()[0]
        attempt_count = con.execute(
            "SELECT COUNT(*) FROM payment_attempts WHERE idempotency_key = ?",
            (idempotency_key,),
        ).fetchone()[0]
        return payment_count, attempt_count
    finally:
        con.close()


def test_same_key_same_payload_is_idempotent():
    app_module = _load_fresh_app_module()
    client = TestClient(app_module.app)

    headers = {"Idempotency-Key": "same-key-1"}
    payload = {"amount": 1200}

    first = client.post("/payments", json=payload, headers=headers)
    assert first.status_code == 201, first.text
    first_body = first.json()

    second = client.post("/payments", json=payload, headers=headers)
    assert second.status_code == 200, second.text
    second_body = second.json()

    assert first_body["payment_id"] == second_body["payment_id"]
    assert second_body["amount"] == payload["amount"]

    payment_count, _ = _count_rows("same-key-1")
    assert payment_count == 1


def test_same_key_different_payload_returns_conflict():
    app_module = _load_fresh_app_module()
    client = TestClient(app_module.app)

    headers = {"Idempotency-Key": "same-key-different-amount"}

    first = client.post("/payments", json={"amount": 500}, headers=headers)
    assert first.status_code == 201, first.text

    second = client.post("/payments", json={"amount": 900}, headers=headers)
    assert second.status_code == 409, second.text

    payment_count, _ = _count_rows("same-key-different-amount")
    assert payment_count == 1


def test_retry_after_transient_failure_creates_single_payment():
    app_module = _load_fresh_app_module()
    client = TestClient(app_module.app)

    headers = {"Idempotency-Key": "retry-key-1"}
    payload = {"amount": 2100, "simulate_transient_failure": True}

    first = client.post("/payments", json=payload, headers=headers)
    assert first.status_code == 503, first.text

    second = client.post("/payments", json=payload, headers=headers)
    assert second.status_code == 201, second.text

    third = client.post("/payments", json=payload, headers=headers)
    assert third.status_code == 200, third.text

    second_id = second.json()["payment_id"]
    third_id = third.json()["payment_id"]
    assert second_id == third_id

    payment_count, attempt_count = _count_rows("retry-key-1")
    assert payment_count == 1
    assert attempt_count >= 2
