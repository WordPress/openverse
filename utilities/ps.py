#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass
class Service:
    name: str
    bindings: set[tuple[int, int]]

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


def get_ps() -> list[str]:
    """
    Invoke Docker Compose to get the configuration for all services. The config is
    returned as a yaml string.

    :return: the output printed by the subprocess to STDOUT
    """

    proc = subprocess.run(
        [
            "docker",
            "ps",
            "--filter",
            "name=openverse",
            "--format",
            "{{.Names}}\n\t{{.Ports}}\n",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.split("\n")


def parse_ps() -> list[Service]:
    """
    Convert the yaml output given by Docker Compose config into a list of services and
    their port mappings.
    :return: a list of running services with their port
    """

    services: list[Service] = []

    lines = get_ps()
    data_iter = iter([stripped for line in lines if (stripped := line.strip())])
    # Iterate over the first two items in the list in pairs
    # https://stackoverflow.com/a/48347320/3277713
    for service, ports in zip(data_iter, data_iter):
        # Services are usually of the form openverse_<name>_1
        name = service.split("_", 1)[1].rsplit("_", 1)[0]
        bindings = set()
        for port_config in ports.split(","):
            if "->" not in port_config:
                # No published ports
                continue
            # Ports are of the form 0.0.0.0:50230->3000/tcp or :::50230->3000/tcp
            host_port, container_port = (
                port_config.split(":")[-1].split("/")[0].split("->")
            )
            bindings.add((host_port, container_port))
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
