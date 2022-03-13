import psycopg
import pytest
import tenacity


def test_container_available(pg_container):
    """Once created, the docker container should be available via the exposed port."""
    conn_info = {
        "host": pg_container["host"],
        "port": pg_container["port"],
        "dbname": pg_container["POSTGRES_DB"],
        "user": pg_container["POSTGRES_USER"],
        "password": pg_container["POSTGRES_PASSWORD"],
    }

    @tenacity.retry(
        wait=tenacity.wait_fixed(1),
        stop=tenacity.stop_after_delay(15),
        retry_error_callback=lambda *args: pytest.fail("failed to connect to the container"),
    )
    def _connect():
        with psycopg.connect(**conn_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                row = cursor.fetchone()
                assert len(row) == 1
                assert row[0].startswith("PostgreSQL 14")

    _connect()
