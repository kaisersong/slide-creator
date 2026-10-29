import importlib.util
import io
from pathlib import Path
import zipfile

import pytest

SPEC = importlib.util.spec_from_file_location("runtime_package", Path(__file__).parents[1] / "scripts/package-runtime.py")
PACKAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE)


def nested_zip(files):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, value in files.items():
            archive.writestr(name, value)
    return buffer.getvalue()


def test_only_duplicate_asset_archive_is_removed_and_real_animation_survives():
    gif = b"GIF89a original animated asset"
    name = "themes/kingdee/assets/logo.gif"
    records = {name: (gif, 0o644), name + ".zip": (nested_zip({
        "logo.gif": gif, "__MACOSX/._logo.gif": b"finder metadata"}), 0o644)}
    assert PACKAGE.prune_redundant_archives(records) == [name + ".zip"]
    assert records == {name: (gif, 0o644)}


@pytest.mark.parametrize("files", [
    {"logo.gif": b"a different animation"},
    {"logo.gif": b"original", "required.txt": b"not duplicated"},
    {"__MACOSX/._logo.gif": b"metadata only"},
])
def test_archives_with_any_unique_content_are_retained(files):
    name = "themes/kingdee/assets/logo.gif"
    records = {name: (b"original", 0o644), name + ".zip": (nested_zip(files), 0o644)}
    before = dict(records)
    assert PACKAGE.prune_redundant_archives(records) == []
    assert records == before


def test_installation_limit_is_strictly_below_decimal_five_megabytes(tmp_path):
    path = tmp_path / "runtime.zip"
    with path.open("wb") as stream:
        stream.truncate(4_999_999)
    assert PACKAGE.require_installable_size(path) == 4_999_999
    with path.open("ab") as stream:
        stream.write(b"x")
    with pytest.raises(ValueError, match="strictly less than 5,000,000"):
        PACKAGE.require_installable_size(path)


def test_referenced_archive_is_retained_even_when_its_payload_is_duplicated():
    name = "themes/kingdee/assets/logo.gif"
    records = {name: (b"original", 0o644), name + ".zip": (nested_zip({"logo.gif": b"original"}), 0o644),
               "themes/kingdee/reference.md": (b"Download assets/logo.gif.zip", 0o644)}
    assert PACKAGE.prune_redundant_archives(records) == []
    assert name + ".zip" in records


def test_oversize_build_preserves_previous_archive_and_checksum(tmp_path, monkeypatch):
    import re
    import subprocess
    skill = subprocess.check_output(["git", "show", ":SKILL.md"], cwd=PACKAGE.ROOT, text=True)
    version = re.search(r"^version:\s*(\S+)", skill, re.M).group(1)
    target = tmp_path / f"kai-slide-creator-v{version}-skill-runtime.zip"
    target.write_bytes(b"previous verified package")
    checksum = target.with_suffix(".zip.sha256")
    checksum.write_bytes(b"previous checksum")
    monkeypatch.setattr(PACKAGE, "MAX_RUNTIME_BYTES", 1)
    with pytest.raises(ValueError, match="strictly less than"):
        PACKAGE.package(tmp_path, None, None)
    assert target.read_bytes() == b"previous verified package"
    assert checksum.read_bytes() == b"previous checksum"
    assert not target.with_suffix(".zip.tmp").exists()
