"""
pytest_docker_service package contains fixtures factories starting docker containers.
"""
import random
import time
from typing import Any, Callable, Dict, Generator, List, Optional, TYPE_CHECKING

import docker
import pytest
import tenacity

if TYPE_CHECKING:
    from docker import DockerClient
    from docker.models.containers import Container
    from _pytest.fixtures import _Scope


@pytest.fixture(scope="session")
def _docker_client() -> "DockerClient":
    """
    Return a docker client configured from environment variables.
    """
    return docker.from_env()


def docker_container(
        scope: "_Scope",
        image_name: str,
        container_name: Optional[str] = "",
        build_path: Optional[str] = None,
        ports: Dict[str, Any] = None,
        environment: Dict[str, str] = None,
) -> Callable:
    """
    Fixtures factory that returns a container that is running the specified image.

    :param scope: the pytest fixture scope (https://docs.pytest.org/en/latest/how-to/fixtures.html#scope-sharing-fixtures-across-classes-modules-packages-or-session)
    :param image_name: name of the docker image to run
    :param container_name: name for the docker container to start
    :param build_path: path to the directory containing the Dockerfile
    :param environment: the environment variables to set inside the container
    :param ports: the ports to bind inside the container
    :return: a pytest fixture function
    """
    _environment: Dict[str, Any] = environment if environment else {}  # https://mypy.readthedocs.io/en/stable/common_issues.html#narrowing-and-inner-functions
    _container_name: str = (
        container_name
        if container_name
        else f"{image_name.split('/')[-1]}-{random.randint(0, 999999):06d}"
    )

    @pytest.fixture(scope=scope)
    def _docker_container(_docker_client: "DockerClient") -> Generator:
        if build_path:
            image, _ = _docker_client.images.build(path=build_path, tag=image_name)
        else:
            image = _docker_client.images.pull(repository=image_name)

        container = _docker_client.containers.run(
            image.id,
            detach=True,
            environment=_environment,
            name=_container_name,
            ports=ports,
        )
        time.sleep(1)
        _check_container_running(container)

        _environment["host"] = "localhost"
        _environment["port_map"] = _get_port_map(container, ports)

        yield _environment

        container.remove(force=True)

    return _docker_container


def _get_port_map(container: "Container", ports: Dict[str, Any] = None) -> Dict[str, List[str]]:
    if not ports:
        return {}

    ports_settings = container.attrs["NetworkSettings"]["Ports"]
    port_map = {}
    for port in ports.keys():
        host_ports = [p["HostPort"] for p in ports_settings[port]]
        port_map[port] = host_ports if len(host_ports) > 1 else host_ports[0]

    return port_map


@tenacity.retry(
    wait=tenacity.wait_fixed(1),
    stop=tenacity.stop_after_delay(10),
    retry_error_callback=lambda *args: pytest.fail("could not start docker container"),
)
def _check_container_running(container: "Container"):
    """
    Fails the test if the container status does not change to 'running'.
    """
    container.reload()
    if container.status != "running":
        raise RuntimeError(
            f"container {container.name} failed to start: status '{container.status}' / expected status 'running'",
        )
