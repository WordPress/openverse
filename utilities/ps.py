import subprocess
from dataclasses import dataclass


@dataclass
class Service:
    name: str
    image: str
    bindings: set[tuple[int, int]]

    def print(self):
        """
        Print the formatted output for the service. The output contains the following:
        - name (in bold)
        - each URL (with the correct protocol) and the container port to which it maps
        It specially handles the singular NGINX port 9443 which serves over ``https``.
        """

        print(f"\033[1m{self.name} ({self.image}):\033[0m")
        for host_port, container_port in self.bindings:
            proto = "http"
            if self.name == "proxy" and container_port == 9443:
                proto = "https"
            print(f"- {proto:>5}://0.0.0.0:{host_port} (→ {container_port})")


def get_ps() -> list[str]:
    """
    Invoke Docker "ps" with a filter to get the configuration for all services. The
    info is returned as a list of plain text lines.

    :return: the output printed by the subprocess to STDOUT
    """

    proc = subprocess.run(
        [
            "docker",
            "ps",
            "--filter",
            "network=openverse_default",
            "--format",
            "{{.Names}}\t{{.Image}}\t{{.Ports}}\n",
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"docker ps failed with code {proc.returncode} and output: {proc.stderr}"
        )
    return proc.stdout.split("\n")


def parse_ps() -> list[Service]:
    """
    Convert the output lines given by Docker "ps" into a list of services and
    their port mappings.
    :return: a list of running services with their port
    """

    services: list[Service] = []

    lines = get_ps()
    lines = [stripped for line in lines if (stripped := line.strip())]
    for line in lines:
        service, image, ports = line.split("\t")
        # Services are usually of the form openverse-<name>-1 or openverse_<name>_1,
        # but we can't always tell which one is used.
        strip_char = service.removeprefix("openverse")[0]
        name = service.split(strip_char, 1)[1].rsplit(strip_char, 1)[0]
        # Image names may start with "openverse-" or "openverse_" or be an upstream
        # image name like redis:4.0.0
        if "openverse" in image:
            image_name = image[len("openverse") + 1 :]
        else:
            image_name = image.split(":", 1)[0]
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
            services.append(Service(name, image_name, bindings))

    return services


def print_ps():
    """Print the formatted output for each service."""

    print("=" * 80)
    print(f"{'Service Ports':^80}")
    print("=" * 80)
    for service in parse_ps():
        service.print()
    print("=" * 80)


if __name__ == "__main__":
    print_ps()
