#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from dataclasses import dataclass

import yaml


@dataclass
class Service:
    name: str
    bindings: list[tuple[int, int]]

    def print(self):
        """
        Print the formatted output for the service. The output contains the following:
        - name (in bold)
        - each URL (with the correct protocol) and the container port to which it maps
        It specially handles the singular NGINX port 9443 which serves over ``https``.
        """

        print(f"\033[1m{self.name}:\033[0m")
        for host_port, container_port in self.bindings:
            proto = "http"
            if self.name == "proxy" and container_port == 9443:
                proto = "https"
            print(f"- {proto:>5}://0.0.0.0:{host_port} (→ {container_port})")


def get_ps() -> str:
    """
    Invoke Docker Compose to get the configuration for all services. The config is
    returned as a yaml string.

    :return: the output printed by the subprocess to STDOUT
    """

    proc = subprocess.run(
        ["just", "dc", "config"],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout


def parse_ps() -> list[Service]:
    """
    Convert the yaml output given by Docker Compose config into a list of services and
    their port mappings.
    :return: a list of running services with their port
    """

    services: list[Service] = []

    data = yaml.safe_load(get_ps())
    for name, service in data["services"].items():
        bindings = []
        for publisher in service.get("ports", []):
            container_port = publisher["target"]
            host_port = publisher["published"]
            if host_port:
                bindings.append((host_port, container_port))
        if bindings:
            services.append(Service(name, bindings))

    return services


def print_ps():
    """Print the formatted output for each service."""

    print("=" * 80)
    print(f"{'Services':^80}")
    print("=" * 80)
    for service in parse_ps():
        service.print()
    print("=" * 80)


if __name__ == "__main__":
    print_ps()
