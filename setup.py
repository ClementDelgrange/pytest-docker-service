import pathlib
from setuptools import find_packages, setup


cwd = pathlib.Path(__file__).parent
readme = (cwd / "README.md").read_text()

# Requirements
reqs = [
    "docker",
    "pytest",
    "tenacity",
]

# Classifiers
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers = [
    "Development Status :: 3 - Alpha",
    "Framework :: Pytest",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU Affero General Public License v3",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Topic :: Software Development :: Testing",
]

setup(
    name="pytest-docker-service",
    version="0.2.1",
    author="cdelgrange",
    license="GNU GPL v3",
    description="pytest plugin to start docker container",
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=classifiers,
    url="https://github.com/ClementDelgrange/pytest-docker-service",
    keywords=["pytest", "docker", "devops"],
    packages=find_packages(exclude=("tests",)),
    install_requires=reqs,
    python_requires=">=3.9",
    entry_points={
        "pytest11": ["docker-service = pytest_docker_service.plugin"],
    },
)
