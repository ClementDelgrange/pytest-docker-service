import pathlib

import docker.errors
import pytest


def test_container_created(_docker_client, pytester):
    """
    Create a valid container with the `docker_container` fixture factory.
    The container should be deleted at the end of the test.
    """
    pytester.makeconftest(
        f"""
        import pathlib
        from pytest_docker_service import docker_container

        container = docker_container(
            scope="session",
            build_path="{pathlib.Path(__file__).parent.joinpath('e2e/docker/postgres')}",
            image_name="test-pg-database-starting",
            container_name="test-pg-database-container-starting",
            environment={{"POSTGRES_PASSWORD": "postgres", "POSTGRES_USER": "postgres", "POSTGRES_DB": "testdb"}},
        )
        """
    )

    pytester.makepyfile(
        """
        def test_docker_container_fail_to_start(container, _docker_client):
            c = _docker_client.containers.get("test-pg-database-container-starting")
            assert c is not None
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)

    with pytest.raises(docker.errors.NotFound):
        _docker_client.containers.get("test-pg-database-container-starting")


def test_failed_to_start_container(_docker_client, pytester):
    """
    Do not pass environment variables to the `docker_container` fixture generator to fail container initialization.
    The container should not be deleted at the end in this case.
    """
    pytester.makeconftest(
        f"""
        import pathlib
        from pytest_docker_service import docker_container
        
        container = docker_container(
            scope="session",
            build_path="{pathlib.Path(__file__).parent.joinpath('e2e/docker/postgres')}",
            image_name="test-pg-database-not-starting",
            container_name="test-pg-database-container-not-starting",
        )
        """
    )

    pytester.makepyfile(
        """
        def test_docker_container_fail_to_start(container):
            pass
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(errors=1)
    result.stdout.re_match_lines([".*container test-pg-database-container-not-starting failed to start: status 'exited' / expected status 'running'"])

    c = _docker_client.containers.get("test-pg-database-container-not-starting")
    assert c is not None
    c.remove(force=True)
