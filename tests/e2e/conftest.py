import pathlib

from pytest_docker_service import docker_container


pg_container = docker_container(
    scope="session",
    build_path=str(pathlib.Path(__file__).parent.joinpath("docker/postgres")),
    image_name="test-pg-database",
    container_name="test-pg-database-container",
    environment={"POSTGRES_PASSWORD": "postgres", "POSTGRES_USER": "postgres", "POSTGRES_DB": "testdb"},
    ports={"5432/tcp": None},
)
