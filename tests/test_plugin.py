import docker.errors
import pytest


def test_container_created_image_pulled(_docker_client, pytester):
    """
    Pull a docker image and create a valid container with the `docker_container` fixture factory.
    The container should be deleted at the end of the test.
    """
    pytester.makeconftest(
        """
        import pathlib
        from pytest_docker_service import docker_container

        container = docker_container(
            scope="session",
            image_name="postgres:14",
            container_name="test-pg-database-container-image-pulled",
            environment={"POSTGRES_PASSWORD": "postgres", "POSTGRES_USER": "postgres", "POSTGRES_DB": "testdb"},
        )
        """
    )

    pytester.makepyfile(
        """
        def test_docker_container_fail_to_start(container, _docker_client):
            c = _docker_client.containers.get("test-pg-database-container-image-pulled")
            assert c is not None
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)

    with pytest.raises(docker.errors.NotFound):
        _docker_client.containers.get("test-pg-database-container-image-pulled")


def test_container_created_image_build(_docker_client, pytester):
    """
    If `build_path` is provided, build the docker image and create a valid container
    with the `docker_container` fixture factory.
    The container should be deleted at the end of the test, but the image is kept.
    """
    pytester.makefile(
        "",
        Dockerfile="\n".join(
            (
                "FROM postgres:14",
                "ENV POSTGRES_DB=testdb",
                "ENV POSTGRES_USER=postgres",
                "ENV POSTGRES_PASSWORD=postgres",
            )
        ),
    )

    pytester.makeconftest(
        """
        import pathlib
        from pytest_docker_service import docker_container

        container = docker_container(
            scope="session",
            image_name="postgres_custom",
            container_name="test-pg-database-container-image-build",
            build_path=".",
        )
        """
    )

    pytester.makepyfile(
        """
        def test_docker_container_fail_to_start(container, _docker_client):
            c = _docker_client.containers.get("test-pg-database-container-image-build")
            assert c is not None
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)

    with pytest.raises(docker.errors.NotFound):
        _docker_client.containers.get("test-pg-database-container-image-build")

    assert _docker_client.images.get("postgres_custom")


def test_failed_to_start_container(_docker_client, pytester):
    """
    Do not pass environment variables to the `docker_container` fixture generator to fail container initialization.
    The container should not be deleted at the end in this case.
    """
    pytester.makeconftest(
        """
        import pathlib
        from pytest_docker_service import docker_container

        container = docker_container(
            scope="session",
            image_name="postgres:14",
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
    result.stdout.re_match_lines(
        [
            r".*container test-pg-database-container-not-starting exited with code \d+.*",
            r".*Error: Database is uninitialized and superuser password is not specified.*",
        ]
    )

    c = _docker_client.containers.get("test-pg-database-container-not-starting")
    assert c is not None
    c.remove(force=True)
