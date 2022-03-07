import configparser
import os
import sys
from pathlib import Path
from string import Template


check = "--check" in sys.argv

try:
    environment = sys.argv[1]
except IndexError:
    print("Usage: python create_prometheus_yaml.py [environment]")
    sys.exit(1)

_prom_conf_base_dir = Path.cwd() / "monitoring" / "configuration" / "prometheus"
out_path = _prom_conf_base_dir / f"prometheus.{environment}.yml"

try:
    os.stat(out_path)
    if check:
        print(f"Using existing prometheus.{environment}.yml")
        sys.exit(0)

    overwrite = (
        input(
            "Do you wish to overwrite the existing "
            f"configuration using {environment}.conf? [yes/N]: "
        )
        or "n"
    )
    if overwrite != "yes":
        sys.exit(1)
    print(f"Overwriting existing prometheus{environment}.yml with {environment}.conf")
except FileNotFoundError:
    if check:
        print(
            f"Failed to find prometheus.{environment}.yml. "
            f"Please run `just mkpromconf {environment}` and try again."
        )
        sys.exit(1)

    print(f"Generating new prometheus.{environment}.yml based on {environment}.conf")

with open(_prom_conf_base_dir / "prometheus.yml.template") as template_file:
    template = template_file.read()

config = configparser.ConfigParser()
if len(config.read(_prom_conf_base_dir / f"{environment}.conf")) != 1:
    print(
        f"Unable to read configuration for {environment} "
        f"at {_prom_conf_base_dir / f'{environment}.conf'}"
    )
    sys.exit(1)


mapping = {
    f"{section}__{prop}": config[section][prop]
    for section in config.sections()
    for prop in config[section]
}

compiled = Template(template).substitute(**mapping)

with open(out_path, "w") as out:
    out.write(compiled)

print(f"Successfully created prometheus.{environment}.yml from {environment}.conf")
sys.exit(0)
