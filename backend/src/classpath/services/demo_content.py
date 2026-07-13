import json
from importlib.resources import files
from typing import Any


def load_demo_packages() -> list[dict[str, Any]]:
    resource = files("classpath.fixtures").joinpath("demo_learning_packages.json")
    data = json.loads(resource.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Demo package fixture must be a list")
    return data


def get_demo_package(package_key: str) -> dict[str, Any] | None:
    return next(
        (package for package in load_demo_packages() if package["package_key"] == package_key),
        None,
    )
