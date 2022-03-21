import requests
from pytest_docker_service import docker_container

container = docker_container(
    scope="session",
    image_name="kennethreitz/httpbin",
    ports={"80/tcp": None},
)


def test_status_code(container):
    port = container.port_map["80/tcp"]
    host = "127.0.0.1"

    status = 200
    response = requests.get(f"http://{host}:{port}/status/{status}")

    assert response.status_code == status
