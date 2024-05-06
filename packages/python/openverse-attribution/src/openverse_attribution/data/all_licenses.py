import json
from pathlib import Path


all_licenses_data = Path(__file__).parent / "all_licenses.json"
all_licenses = json.loads(all_licenses_data.read_bytes())
