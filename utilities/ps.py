import json
import subprocess
import traceback
from dataclasses import dataclass


@dataclass
class Service:
    """A dataclass to represent a running service with its name, image, and port bindings."""

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
            if self.name == "proxy" and container_port == "9443":
                proto = "https"
            print(f"- {proto:>5}://0.0.0.0:{host_port:<5} (→ {container_port})")


def get_ps() -> list[str]:
    """
    Invoke Docker Compose "ps" with the JSON format flag and
    return a list of lines of JSON output.

    :return: the output printed by the subprocess to STDOUT
    """

    proc = subprocess.run(
        [
            "just",
            "dc",
            "ps",
            "--format",
            "json",
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
    Convert the output lines given by Docker Compose "ps" into a list of
    services and their port mappings.

    :return: a list of running services with their port
    """

    services: list[Service] = []

    lines = get_ps()
    lines = [stripped for line in lines if (stripped := line.strip())]
    for line in lines:
        container_ps = json.loads(line)
        service_name = container_ps["Service"]

        # Image names may start with "openverse-" or "openverse_" or be an upstream
        # image name like docker.io/redis:4.0.0
        container_image = container_ps["Image"]
        if "openverse" in container_image:
            image_name = container_image[len("openverse*") :]
        else:
            image_name = container_image.split(":", 1)[0]
        bindings = set()
        for port_config in container_ps["Publishers"]:
            published_port = port_config["PublishedPort"]
            if published_port:
                bindings.add((port_config["TargetPort"], published_port))
        if bindings:
            services.append(Service(service_name, image_name, bindings))

    return services


def print_ps():
    """Print the formatted output for each service."""

    print("=" * 80)
    print(f"{'Service Ports':^80}")
    print("=" * 80)
    try:
        for service in parse_ps():
            service.print()
    except Exception as err:
        print(traceback.format_exc())
        print("=" * 80)
        print(f"Failed to get service info ({err.__class__.__name__}): \n{err}")
    print("=" * 80)


if __name__ == "__main__":
    print_ps()
