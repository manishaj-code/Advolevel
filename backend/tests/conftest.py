import asyncio
import os
import sys
from collections.abc import Iterator

import pytest
from dotenv import dotenv_values
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import create_app

# Settings are read lazily (get_settings), so configuring the env after the imports is fine.
os.environ["APP_ENV"] = "test"

# Unit tests never touch real services; placeholders only satisfy settings validation. Real
# values from the environment or backend/.env win, so `pytest -m integration` needs no extra setup.
_dotenv = dotenv_values(".env")
for _key, _placeholder in {
    "DATABASE_URL": "postgresql://advolevel:advolevel@127.0.0.1:5432/advolevel",
    "REDIS_URL": "redis://127.0.0.1:6379/0",
}.items():
    if not os.environ.get(_key) and not _dotenv.get(_key):
        os.environ[_key] = _placeholder

# psycopg's async mode cannot run on Windows' default Proactor loop (containers/CI are Linux).
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def make_settings(**overrides: object) -> Settings:
    return get_settings().model_copy(update=overrides)


@pytest.fixture
def app() -> FastAPI:
    return create_app(make_settings(debug_endpoints_enabled=True))


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
