"""
pytest_docker_service package contains fixtures factories starting docker containers.
"""
import time
from typing import Callable, Dict, Generator, TYPE_CHECKING

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
        build_path: str,
        image_name: str,
        container_name: str,
        environment: Dict[str, str] = None,
) -> Callable:
    """
    Fixtures factory that returns a container that is running the specified image.

    :param scope: the pytest fixture scope (https://docs.pytest.org/en/latest/how-to/fixtures.html#scope-sharing-fixtures-across-classes-modules-packages-or-session)
    :param build_path: path to the directory containing the Dockerfile
    :param image_name: name of the docker image to run
    :param container_name: name for the docker container to start
    :param environment: environment variables to set inside the container
    :return: a pytest fixture function
    """
    _environment: Dict[str, str] = environment if environment else {}  # https://mypy.readthedocs.io/en/stable/common_issues.html#narrowing-and-inner-functions

    @pytest.fixture(scope=scope)
    def _docker_container(_docker_client: "DockerClient") -> Generator:
        image, _ = _docker_client.images.build(path=build_path, tag=image_name)

        container = _docker_client.containers.run(
            image.id,
            detach=True,
            environment=_environment,
            name=container_name,
            ports={"5432/tcp": 0}
        )
        time.sleep(1)
        _check_container_running(container)

        _environment["host"] = "localhost"
        _environment["port"] = container.attrs['NetworkSettings']['Ports']['5432/tcp'][0]['HostPort']

        yield _environment

        container.remove(force=True)

    return _docker_container


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
