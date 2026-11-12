"""Fetch font inputs and refuse unexpected content; Iosevka is built separately."""
from pathlib import Path
import hashlib
import io
import json
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
lock = json.loads((ROOT / "sources/inputs.lock.json").read_text())
dest = ROOT / "sources/upstream"
dest.mkdir(parents=True, exist_ok=True)
for entry in lock["fonts"]:
    path = dest / entry["file"]
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]:
        print("Already verified", path.name)
        continue
    request = urllib.request.Request(entry["url"], headers={"User-Agent": "mmCodingFont-prototype"})
    with urllib.request.urlopen(request, timeout=120) as response:
        content = response.read()
    if entry["archive_member"]:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            content = archive.read(entry["archive_member"])
    if hashlib.sha256(content).hexdigest() != entry["sha256"]:
        raise ValueError(f"Checksum mismatch: {entry['file']}; no file replaced")
    path.write_bytes(content)
    print("Fetched and verified", path.name)
