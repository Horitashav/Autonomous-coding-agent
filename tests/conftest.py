import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.engine.url import make_url

load_dotenv()
if test_database_url := os.getenv("TEST_DATABASE_URL"):
    os.environ["DATABASE_URL"] = test_database_url

from agent.api.database import engine  # noqa: E402
import agent.api.models  # noqa: E402, F401


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Refuse unsafe database targets and verify migrations initialized the schema."""
    database_name = make_url(str(engine.url)).database or ""
    if "test" not in database_name.lower() and "ci" not in database_name.lower():
        raise RuntimeError(
            f"Refusing to run tests against database '{database_name}'. "
            "Set TEST_DATABASE_URL or DATABASE_URL to a dedicated test database."
        )

    with engine.connect() as connection:
        current_database, current_schema = connection.execute(
            text("SELECT current_database(), current_schema()")
        ).one()
        users_exists = connection.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'users'
                )
                """
            )
        ).scalar_one()

    if current_schema != "public" or not users_exists:
        raise RuntimeError(
            f"Database '{current_database}' (schema '{current_schema}') has no public.users "
            "table visible in the public schema. Run `alembic upgrade head` against this "
            "test database before pytest."
        )

    print(
        f"[PYTEST DB] database={current_database} schema={current_schema} "
        f"public.users={'present' if users_exists else 'missing'}"
    )
