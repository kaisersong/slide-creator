#!/usr/bin/env python3
"""Package staged runtime bytes, optionally preserving published enterprise assets."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import stat
import subprocess
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
MAX_RUNTIME_BYTES = 5_000_000


def prune_redundant_archives(records: dict) -> list[str]:
    """Omit asset ZIPs only when every real payload already exists verbatim."""
    omitted = []
    for path, (content, _mode) in list(records.items()):
        if not path.endswith(".zip") or "/assets/" not in path:
            continue
        archive_name = PurePosixPath(path).name.encode()
        if any(archive_name in value for name, (value, _file_mode) in records.items()
               if Path(name).suffix in {".md", ".html", ".css", ".js", ".json", ".py"}):
            continue
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                members = [item for item in archive.infolist() if not item.is_dir()
                           and not item.filename.startswith("__MACOSX/")
                           and PurePosixPath(item.filename).name != ".DS_Store"]
                if not members:
                    continue
                for item in members:
                    sibling = str(PurePosixPath(path).parent / PurePosixPath(item.filename).name)
                    if (sibling not in records or item.file_size != len(records[sibling][0])
                            or archive.read(item) != records[sibling][0]):
                        break
                else:
                    del records[path]
                    omitted.append(path)
        except zipfile.BadZipFile:
            continue
    return omitted


def require_installable_size(path: Path) -> int:
    size = path.stat().st_size
    if size >= MAX_RUNTIME_BYTES:
        raise ValueError(f"Runtime ZIP is {size:,} bytes; Lingee requires strictly less than {MAX_RUNTIME_BYTES:,} bytes")
    return size


def package(output_dir: Path, previous: Path | None, previous_sha256: str | None) -> dict:
    skill = subprocess.check_output(["git", "show", ":SKILL.md"], cwd=ROOT, text=True)
    version = re.search(r"^version:\s*(\S+)", skill, re.M).group(1)
    assert re.fullmatch(r"\d+\.\d+\.\d+", version)
    entries = subprocess.check_output(
        ["git", "ls-files", "-z", "--stage", "SKILL.md", "main.py", "scripts", "schemas", "references", "themes"], cwd=ROOT
    ).split(b"\0")
    records = {}
    for entry in entries:
        if not entry:
            continue
        metadata, path_bytes = entry.split(b"\t", 1)
        mode, _blob, stage = metadata.decode().split()
        path = path_bytes.decode()
        if stage != "0" or mode not in {"100644", "100755"}:
            raise ValueError(f"Unsupported staged entry: {path}")
        records[path] = (subprocess.check_output(["git", "show", ":" + path], cwd=ROOT), int(mode[-3:], 8))
    manifest_path = "references/profile-templates/manifest.json"
    if manifest_path not in records:
        raise ValueError("Runtime profile template manifest is missing from the git index")
    templates = json.loads(records[manifest_path][0])
    support = json.loads(records["references/preset-support-tiers.json"][0])
    expected_presets = support["policy"]["support_states"]["unified_profile_renderer"]
    if templates.get("version") != 1 or set(templates.get("presets", {})) != set(expected_presets):
        raise ValueError("Runtime profile templates do not match the supported preset registry")
    for preset, languages in templates["presets"].items():
        if set(languages) != {"en", "zh"}:
            raise ValueError(f"Runtime profile languages incomplete: {preset}")
        for template in languages.values():
            path = template["path"]
            if not path.startswith("references/profile-templates/") or path not in records:
                raise ValueError(f"Runtime profile template missing from git index: {path}")
            if hashlib.sha256(records[path][0]).hexdigest() != template["sha256"]:
                raise ValueError(f"Runtime profile template checksum mismatch: {path}")
    preserved = []
    if previous:
        if not previous_sha256 or hashlib.sha256(previous.read_bytes()).hexdigest() != previous_sha256:
            raise ValueError("Published previous runtime checksum mismatch")
        with zipfile.ZipFile(previous) as archive:
            for item in archive.infolist():
                if item.is_dir():
                    continue
                if not item.filename.startswith("kai-slide-creator/"):
                    raise ValueError("Unexpected previous runtime root")
                path = item.filename.removeprefix("kai-slide-creator/")
                if Path(path).is_absolute() or ".." in Path(path).parts:
                    raise ValueError("Unsafe previous runtime path")
                if path in records:
                    continue
                if not path.startswith(("themes/cloudhub/", "themes/kingdee/")):
                    raise ValueError(f"Unexpected previous-package file: {path}")
                records[path] = (archive.read(item), (item.external_attr >> 16) & 0o777 or 0o644)
                preserved.append(path)
    omitted = prune_redundant_archives(records)
    preserved = [path for path in preserved if path not in omitted]
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"kai-slide-creator-v{version}-skill-runtime.zip"
    temporary = target.with_suffix(".zip.tmp")
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path, (content, mode) in sorted(records.items()):
                info = zipfile.ZipInfo("kai-slide-creator/" + path, date_time=(2026, 10, 9, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | mode) << 16
                archive.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        require_installable_size(temporary)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix(".zip.sha256").write_text(f"{digest}  {target.name}\n")
    manifest = {
        "version": version, "archive": target.name, "sha256": digest, "bytes": target.stat().st_size,
        "files": len(records), "preserved_enterprise_files": preserved,
        "max_runtime_bytes": MAX_RUNTIME_BYTES, "omitted_redundant_archives": omitted,
        "runtime_files": {path: hashlib.sha256(content).hexdigest() for path, (content, _mode) in sorted(records.items())},
    }
    (output_dir / "runtime-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--previous-runtime", type=Path)
    parser.add_argument("--previous-sha256")
    args = parser.parse_args()
    result = package(args.output_dir, args.previous_runtime, args.previous_sha256)
    print(json.dumps({key: result[key] for key in ("version", "archive", "sha256", "bytes", "files")}, ensure_ascii=False))
