"""
Tests for slide-creator review checklist functionality.

Validates:
1. review-checklist.md exists and has required sections
2. SKILL.md documents --review command
3. workflow.md has Phase 3.5
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW_CHECKLIST = ROOT / "references" / "review-checklist.md"
SKILL_MD = ROOT / "SKILL.md"
WORKFLOW_MD = ROOT / "references" / "workflow.md"
DESIGN_QUALITY_MD = ROOT / "references" / "design-quality.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestReviewChecklistExists:
    """Test that review-checklist.md exists with required content."""

    def test_review_checklist_file_exists(self):
        assert REVIEW_CHECKLIST.exists(), "references/review-checklist.md should exist"

    def test_review_checklist_has_16_checkpoints(self):
        content = read_text(REVIEW_CHECKLIST)
        # Category 1: 6 auto-detectable
        assert "### 1.1" in content and "视角翻转" in content
        assert "### 1.2" in content and "结论先行" in content
        assert "### 1.3" in content and "概念法则" in content
        assert "### 1.4" in content and "连续密集" in content
        assert "### 1.5" in content and "字号" in content
        assert "### 1.6" in content and "眯眼" in content
        # Category 2: 10 AI-advised
        assert "### 2.1" in content and "痛点" in content
        assert "### 2.2" in content and "WIIFM" in content
        assert "### 2.3" in content and "MECE" in content
        assert "### 2.4" in content and "奥卡姆" in content
        assert "### 2.5" in content and "注意力" in content
        assert "### 2.6" in content and "张力" in content
        assert "### 2.7" in content and "缓冲" in content
        assert "### 2.8" in content and "黑话" in content
        assert "### 2.9" in content and "图像降噪" in content
        assert "### 2.10" in content and "图表降噪" in content

    def test_review_checklist_has_detection_rules(self):
        content = read_text(REVIEW_CHECKLIST)
        assert "**Detection**:" in content

    def test_review_checklist_has_result_categories(self):
        content = read_text(REVIEW_CHECKLIST)
        assert "✅" in content
        assert "🔧" in content
        assert "⚠️" in content
        assert "❌" in content


class TestSkillMdReviewCommand:
    """Test that SKILL.md documents --review command."""

    def test_skill_has_review_command(self):
        content = read_text(SKILL_MD)
        assert "--review" in content, "SKILL.md should document --review command"

    def test_skill_has_review_checklist_reference(self):
        content = read_text(SKILL_MD)
        assert "review-checklist.md" in content, "SKILL.md should reference review-checklist.md"

    def test_skill_documents_phase_35(self):
        content = read_text(SKILL_MD)
        assert "Phase 3.5" in content or "Review" in content


class TestWorkflowPhase35:
    """Test that workflow.md has Phase 3.5."""

    def test_workflow_has_phase_35(self):
        content = read_text(WORKFLOW_MD)
        assert "Phase 3.5" in content

    def test_workflow_phase_35_polish_only(self):
        content = read_text(WORKFLOW_MD)
        phase_35_section = content[content.find("Phase 3.5"):] if "Phase 3.5" in content else ""
        assert "Polish" in phase_35_section or "精修" in phase_35_section
        assert "Auto" in phase_35_section or "自动" in phase_35_section

    def test_workflow_phase_35_links_review_checklist(self):
        content = read_text(WORKFLOW_MD)
        assert "review-checklist.md" in content


class TestDesignQualityL1Index:
    """Test that design-quality.md has L1 index."""

    def test_design_quality_has_l1_reference(self):
        content = read_text(DESIGN_QUALITY_MD)
        assert "L1" in content or "review-checklist" in content