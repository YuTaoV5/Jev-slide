"""Package the provided NanoJev snapshot without altering its contents."""

from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


PROJECT = Path(__file__).resolve().parents[2] / "related_work/projects/NanoJev-main"
DEST = Path(__file__).with_name("NanoJev-main.zip")

with ZipFile(DEST, "w", compression=ZIP_DEFLATED, compresslevel=2) as archive:
    for path in sorted(PROJECT.rglob("*")):
        if path.is_file():
            archive.write(path, path.relative_to(PROJECT.parent))

digest = sha256()
with DEST.open("rb") as source:
    for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
        digest.update(chunk)
print(DEST, DEST.stat().st_size, digest.hexdigest())
