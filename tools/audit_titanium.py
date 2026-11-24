"""Offline preflight for the existing Kodi repository. Python 3, no dependencies."""
from pathlib import Path
import hashlib
import sys
import zipfile
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1] / "repo"
index = root / "addons.xml"
addons = ET.parse(index).getroot().findall("addon")
ids = {a.attrib["id"] for a in addons}
errors = []
warnings = []
checksum = root / "addons.xml.md5"
if checksum.exists() and checksum.read_text().strip().lower() != hashlib.md5(index.read_bytes()).hexdigest():
    errors.append("Repository checksum mismatch")
for addon in addons:
    aid, version = addon.attrib["id"], addon.attrib["version"]
    package = root / aid / (aid + "-" + version + ".zip")
    for dep in addon.findall("./requires/import"):
        name = dep.attrib["addon"]
        if name not in ids and not name.startswith(("xbmc.", "kodi.")) and dep.get("optional") != "true":
            warnings.append(f"{aid}: external or missing required dependency {name}")
    if not package.is_file():
        errors.append(f"Missing package: {package.relative_to(root)}")
        continue
    try:
        with zipfile.ZipFile(package) as z:
            bad = z.testzip()
            if bad:
                errors.append(f"{aid}: corrupt member {bad}")
            manifest = ET.fromstring(z.read(aid + "/addon.xml"))
            if (manifest.get("id"), manifest.get("version")) != (aid, version):
                errors.append(f"{aid}: package manifest differs from index")
            if aid.startswith("skin."):
                for member in z.namelist():
                    if member.endswith(".xml") and member.startswith(aid + "/16x9/"):
                        try:
                            ET.fromstring(z.read(member))
                        except ET.ParseError as exc:
                            errors.append(f"{member}: {exc}")
    except (OSError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
        errors.append(f"{aid}: {exc}")
for warning in warnings:
    print("WARNING:", warning)
for error in errors:
    print("ERROR:", error)
print(f"Checked {len(addons)} entries; {len(errors)} errors, {len(warnings)} warnings")
sys.exit(bool(errors))
