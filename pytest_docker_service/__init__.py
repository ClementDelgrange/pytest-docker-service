"""pytest_docker_service main module."""
from .plugin import docker_container

__all__ = [
    "docker_container",
]
