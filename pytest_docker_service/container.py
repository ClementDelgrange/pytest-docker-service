"""
This module exposes a wrapper around the docker Container object.
"""
import functools
import time
from typing import Dict, List

import docker.models.containers
import pytest
import tenacity


class Container:
    """
    The Container class wraps the docker Container object
    and adds some useful method for testing.
    """
    def __init__(self, container: docker.models.containers.Container):
        self._container = container

    @property
    def ready(self):
        """Returns True if the underlying docker container is in 'running' status."""
        return self._container.status == "running"

    def wait_ready(self):
        """
        Waits for the docker container to be ready and make the test fails if this doesn't happen.
        """

        def _report_last_error(retry_state):
            pytest.fail(
                f"failed to get container {self._container.name} ready: {retry_state.outcome.exception()}"
            )

        @tenacity.retry(
            wait=tenacity.wait_fixed(1),
            stop=tenacity.stop_after_delay(10),
            retry_error_callback=_report_last_error,
        )
        def _wait_ready():
            self._container.reload()
            if self._container.status == "exited":
                exit_code = self._container.attrs['State']['ExitCode']
                raise RuntimeError(
                    f"container {self._container.name} exited with code {exit_code}, "
                    f"logs: {self._container.logs().decode()}"
                )
            elif not self.ready:
                raise RuntimeError(
                    (
                        f"container {self._container.name} failed to start: "
                        f"status '{self._container.status}' / expected status 'running'"
                    )
                )

        time.sleep(1)
        _wait_ready()

    def remove(self, force):
        """Removes the underlying docker container."""
        self._container.remove(force=force)

    @functools.cached_property
    def port_map(self) -> Dict[str, List[str]]:
        """Returns the port mapping for the underlying docker container."""
        portmap: Dict[str, List[str]] = {}
        for port, setting in self._container.attrs["NetworkSettings"]["Ports"].items():
            host_ports = {s["HostPort"] for s in setting if s['HostIp'] != '::'}  # exclude ipv6
            portmap[port] = list(host_ports) if len(host_ports) > 1 else host_ports.pop()

        return portmap
