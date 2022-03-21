import pathlib

import psycopg
import pytest
import tenacity

from pytest_docker_service import docker_container

ENV = {
    "POSTGRES_PASSWORD": "postgres",
    "POSTGRES_USER": "postgres",
    "POSTGRES_DB": "testdb",
}


pg_container = docker_container(
    scope="session",
    build_path=str(pathlib.Path(__file__).parent.joinpath("docker/postgres")),
    image_name="test-pg-database",
    container_name="test-pg-database-container",
    environment=ENV,
    ports={"5432/tcp": None},
)


def test_container_available(pg_container):
    """Once created, the docker container should be available via the exposed port."""
    conn_info = {
        "host": "localhost",
        "port": pg_container.port_map["5432/tcp"],
        "dbname": ENV["POSTGRES_DB"],
        "user": ENV["POSTGRES_USER"],
        "password": ENV["POSTGRES_PASSWORD"],
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
