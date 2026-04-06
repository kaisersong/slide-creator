import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "check-doc-sync.py"
TMP_ROOT = ROOT / ".tmp-test-doc-sync"
TMP_ROOT.mkdir(exist_ok=True)


def write_fixture_repo(tmp_path: Path, *, skill: str, readme: str, workflow: str) -> Path:
    root = tmp_path / "repo"
    (root / "references").mkdir(parents=True, exist_ok=True)
    (root / "SKILL.md").write_text(skill, encoding="utf-8")
    (root / "README.md").write_text(readme, encoding="utf-8")
    (root / "references" / "workflow.md").write_text(workflow, encoding="utf-8")
    return root


def run_checker(repo_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo_root), *args],
        capture_output=True,
        text=True,
        timeout=15,
    )


def make_case_dir(name: str) -> Path:
    case_dir = TMP_ROOT / name
    shutil.rmtree(case_dir, ignore_errors=True)
    case_dir.mkdir(parents=True, exist_ok=True)
    return case_dir


def test_doc_sync_checker_passes_for_valid_fixture():
    repo = write_fixture_repo(
        make_case_dir("valid"),
        skill=(
            "Edit Mode (default-on, optional)\n"
            "Two-stage workflow: --plan then --generate\n"
            "Custom theme: themes/<name>/reference.md\n"
        ),
        readme=(
            "Two-stage workflow with --plan and --generate.\n"
            "Inline editing is Default-on, optional.\n"
            "Custom theme system via themes/your-theme/reference.md.\n"
        ),
        workflow=(
            "single AskUserQuestion call with all 5 questions at once\n"
            "Enhancement Mode (existing HTML)\n"
            "Validate the edited deck at a practical presentation size such as 1280x720 before handing it back.\n"
        ),
    )

    result = run_checker(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout


def test_doc_sync_checker_fails_on_drift():
    repo = write_fixture_repo(
        make_case_dir("drift"),
        skill="Every generated HTML file MUST include both of these\n",
        readme="Share to URL via Vercel\n",
        workflow="Phase 6: Share\n",
    )

    result = run_checker(repo)

    assert result.returncode == 1
    assert "edit-mode-default" in result.stdout
    assert "no-share-language" in result.stdout


def test_doc_sync_checker_dry_run_does_not_modify_files():
    repo = write_fixture_repo(
        make_case_dir("dry-run"),
        skill=(
            "Edit Mode (default-on, optional)\n"
            "Two-stage workflow: --plan then --generate\n"
            "Custom theme: themes/<name>/reference.md\n"
        ),
        readme=(
            "Two-stage workflow with --plan and --generate.\n"
            "Inline editing is Default-on, optional.\n"
            "Custom theme system via themes/your-theme/reference.md.\n"
        ),
        workflow=(
            "single AskUserQuestion call with all 5 questions at once\n"
            "Enhancement Mode (existing HTML)\n"
            "Validate the edited deck at a practical presentation size such as 1280x720 before handing it back.\n"
        ),
    )
    before = {
        path.relative_to(repo): path.read_text(encoding="utf-8")
        for path in (repo / "SKILL.md", repo / "README.md", repo / "references" / "workflow.md")
    }

    result = run_checker(repo, "--dry-run")

    after = {
        path.relative_to(repo): path.read_text(encoding="utf-8")
        for path in (repo / "SKILL.md", repo / "README.md", repo / "references" / "workflow.md")
    }

    assert result.returncode == 0, result.stdout + result.stderr
    assert "DRY RUN" in result.stdout
    assert before == after


def test_repo_docs_are_current():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(ROOT), "--dry-run"],
        capture_output=True,
        text=True,
        timeout=15,
    )

    assert result.returncode == 0, result.stdout + result.stderr
