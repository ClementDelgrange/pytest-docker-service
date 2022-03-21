# pytest-docker-service
`pytest-docker-service` is a pytest plugin for writing integration tests based on docker containers.

The plugin provides a *fixtures factory*: a configurable function to register fixtures.

The package has been developed and tested with Python 3.10, and pytest version 6.2.

## Installation
Install `pytest-docker-service` with `pip`.

```
python -m pip install pytest-docker-service
```

## Usage
You just have to create a fixture in your `confest.py` or in individual test modules, using the `docker_container` helper.
Fixture is created with the scope provided through the `scope` parameter.
Other parameters are wrappers around the `docker-py` API (https://docker-py.readthedocs.io/en/stable/).

```python
import requests
from pytest_docker_service import docker_container

container = docker_container(
    scope="session",
    image_name="kennethreitz/httpbin",
    ports={"80/tcp": None},
)


def test_status_code(container):
    port = container.port_map["80/tcp"]

    status = 200
    response = requests.get(f"http://127.0.0.1:{port}/status/{status}")

    assert response.status_code == status
```

Of course, if you want to build your own docker image, it is possible.
Just set the `build_path` parameter pointing to the directory containing the Dockerfile.
```python
container = docker_container(
    scope="session",
    image_name="my-image",
    build_path="path/to/dockerfile/directory"
    ports={"80/tcp": None},
)


def test_status_code(container):
    port = container.port_map.["5432/tcp"]

    ...

```