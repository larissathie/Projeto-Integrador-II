import os
import sys

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app, db


@pytest.fixture()
def client():
    """Configure um cliente de teste com um banco em memória."""
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
    )

    ctx = app.app_context()
    ctx.push()
    db.create_all()

    try:
        yield app.test_client()
    finally:
        db.session.remove()
        db.drop_all()
        ctx.pop()
