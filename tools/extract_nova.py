"""Extract the existing Nova package into an isolated development directory."""
from pathlib import Path, PurePosixPath
import zipfile
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
package = root / "repo/skin.madnoxnova/skin.madnoxnova-21.11.8.zip"
target = root / "work" / "nova-source"
with zipfile.ZipFile(package) as archive:
    for entry in archive.infolist():
        path = PurePosixPath(entry.filename)
        if path.is_absolute() or ".." in path.parts or "\\" in entry.filename:
            raise ValueError(f"Unsafe archive path: {entry.filename}")
    manifest = ET.fromstring(archive.read("skin.madnoxnova/addon.xml"))
    if manifest.get("id") != "skin.madnoxnova":
        raise ValueError("Unexpected skin ID")
    archive.extractall(target)
    for entry in archive.namelist():
        if entry.endswith(".xml") and "/16x9/" in entry:
            print(entry)
print(f"Extracted source to {target}")
