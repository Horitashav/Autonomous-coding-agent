"""Inspect a test database's active schema without exposing connection credentials."""

import os
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url


def main() -> int:
    database_url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not database_url:
        print(
            "[ERROR] Set TEST_DATABASE_URL or DATABASE_URL before inspection.",
            file=sys.stderr,
        )
        return 1

    url = make_url(database_url)
    database_name = url.database or ""
    if "test" not in database_name.lower() and "ci" not in database_name.lower():
        print(
            f"[ERROR] Refusing to inspect non-test database '{database_name}'.",
            file=sys.stderr,
        )
        return 1

    engine = create_engine(url)
    try:
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
    finally:
        engine.dispose()

    endpoint = f"{url.drivername}://{url.host or 'localhost'}"
    if url.port:
        endpoint += f":{url.port}"
    endpoint += f"/{database_name}"
    label = sys.argv[1] if len(sys.argv) > 1 else "DATABASE"
    print(
        f"[{label}] endpoint={endpoint} database={current_database} "
        f"schema={current_schema} public.users={'present' if users_exists else 'missing'}"
    )
    return 0 if current_schema == "public" and users_exists else 1


if __name__ == "__main__":
    raise SystemExit(main())
