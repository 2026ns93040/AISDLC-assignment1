import os

import pytest
from fastapi.testclient import TestClient

os.environ["LIBRARY_DATABASE_URL"] = "sqlite:///:memory:"

from src.main import app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("LIBRARY_DATABASE_URL", "sqlite:///:memory:")
    app.dependency_overrides.clear()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
