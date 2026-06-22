import os
from collections.abc import Generator

import pytest

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://quoteflow:quoteflow_password@localhost:5433/quoteflow_test"
)
os.environ["SECRET_KEY"] = "quoteflow_pro_test_secret_key"

from app.db.base import Base
from app.db.session import engine
from app.models import User  # noqa: F401


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)
