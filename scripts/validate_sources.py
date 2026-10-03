"""Fail closed if a copied Zenodo input differs from the provenance manifest."""

import hashlib
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


def main() -> None:
    manifest = json.loads((DATA / "source_manifest.json").read_text(encoding="utf-8"))
    failures = []
    for filename, metadata in manifest["files"].items():
        normalized = (DATA / filename).read_bytes().replace(b"\r\n", b"\n")
        actual = hashlib.sha256(normalized).hexdigest()
        if actual != metadata["sha256"]:
            failures.append(f"{filename}: expected {metadata['sha256']}, got {actual}")
    if failures:
        raise SystemExit("Source validation failed:\n" + "\n".join(failures))
    print(f"Verified {len(manifest['files'])} products from {manifest['record']}")


if __name__ == "__main__":
    main()
