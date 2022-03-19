"""
pytest_docker_service package contains fixtures factories starting docker containers.
"""
import random
from typing import Any, Callable, Dict, Generator, Optional, TYPE_CHECKING

import docker
import pytest

from .container import Container

if TYPE_CHECKING:
    from docker import DockerClient
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

        raw_container = _docker_client.containers.run(
            image.id,
            detach=True,
            environment=_environment,
            name=_container_name,
            ports=ports,
        )

        container = Container(raw_container)
        container.wait_ready()

        yield container

        container.remove(force=True)

    return _docker_container
