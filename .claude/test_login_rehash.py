"""Integration: POST /login persists the argon2 hash after a legacy bcrypt login.

Swap the imports marked `# ADAPT` to match your project.
"""
import bcrypt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.auth import router          # ADAPT: your auth router
from app.core import security
from app.db import Base, User, get_db    # ADAPT: your Base, User model, get_db dependency

EMAIL, PASSWORD = "user@example.com", "s3cret-pass"


def bcrypt_hash(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt(rounds=4)).decode()


@pytest.fixture(autouse=True)
def _settings(monkeypatch):
    monkeypatch.setattr(security.settings, "SECRET_KEY", "test-secret-key-at-least-32-bytes-long!!")


@pytest.fixture
def session_factory():
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False)


@pytest.fixture
def client(session_factory):
    app = FastAPI()
    app.include_router(router)

    def _get_db():
        with session_factory() as db:
            yield db

    app.dependency_overrides[get_db] = _get_db
    return TestClient(app)


def seed_user(session_factory, hashed: str) -> int:
    with session_factory() as db:
        user = User(email=EMAIL, hashed_password=hashed)
        db.add(user)
        db.commit()
        return user.id


def stored_hash(session_factory) -> str:
    with session_factory() as db:  # fresh session: read what is really in the DB
        return db.scalar(select(User.hashed_password).where(User.email == EMAIL))


def login(client, password=PASSWORD):
    return client.post("/login", data={"username": EMAIL, "password": password})


def test_legacy_bcrypt_login_persists_argon2_hash(client, session_factory):
    old = bcrypt_hash(PASSWORD)
    uid = seed_user(session_factory, old)

    resp = login(client)

    assert resp.status_code == 200
    assert security.decode_access_token(resp.json()["access_token"])["sub"] == str(uid)
    new = stored_hash(session_factory)
    assert new.startswith("$argon2")
    assert new != old


def test_login_still_works_after_upgrade(client, session_factory):
    seed_user(session_factory, bcrypt_hash(PASSWORD))
    assert login(client).status_code == 200
    upgraded = stored_hash(session_factory)

    assert login(client).status_code == 200
    assert stored_hash(session_factory) == upgraded  # no re-hash on second login


def test_wrong_password_does_not_touch_legacy_hash(client, session_factory):
    old = bcrypt_hash(PASSWORD)
    seed_user(session_factory, old)

    resp = login(client, "wrong-password")

    assert resp.status_code == 401
    assert stored_hash(session_factory) == old


def test_argon2_user_hash_unchanged_on_login(client, session_factory):
    current = security.hash_password(PASSWORD)
    seed_user(session_factory, current)

    assert login(client).status_code == 200
    assert stored_hash(session_factory) == current


def test_unknown_user_gets_401(client):
    assert login(client).status_code == 401
