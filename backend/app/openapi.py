"""Writes the OpenAPI document for the frontend client generator (spec 08 §1).

    uv run python -m app.openapi ../frontend/lib/api/openapi.json
"""

import json
import sys
from pathlib import Path

from app.core.config import get_settings
from app.main import create_app


def main() -> None:
    # Same document whatever the local .env says: debug routes are never part of the contract.
    settings = get_settings().model_copy(update={"debug_endpoints_enabled": False})
    document = create_app(settings).openapi()
    document["info"]["version"] = "v1"  # keep the file stable across releases
    output = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(output, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(output)


if __name__ == "__main__":
    main()
