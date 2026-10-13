from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts" / "validate_source_fidelity.py"


def unit(
    unit_id: str,
    text: str,
    *,
    weight: float = 1.0,
    protected: bool = False,
    source_ref: str | None = None,
    selector: str | None = None,
) -> dict:
    result = {
        "id": unit_id,
        "text": text,
        "weight": weight,
        "protected": protected,
    }
    if source_ref is not None:
        result["source_ref"] = source_ref
    if selector is not None:
        result["selector"] = selector
    return result


def relation(
    relation_id: str,
    relation_type: str,
    source: str,
    target: str,
    *,
    weight: float = 1.0,
    protected: bool = False,
) -> dict:
    return {
        "id": relation_id,
        "type": relation_type,
        "from": source,
        "to": target,
        "weight": weight,
        "protected": protected,
    }


def coverage(*slides: dict) -> dict:
    return {
        "thresholds": {
            "text_retention": 0.90,
            "relation_retention": 0.90,
        },
        "slides": list(slides),
    }


def slide(number: int, units: list[dict], relations: list[dict] | None = None) -> dict:
    return {
        "slide_number": number,
        "units": units,
        "relations": relations or [],
    }


def run_gate(tmp_path: Path, html: str, source_coverage: dict, *, report: bool = False):
    html_path = tmp_path / "deck.html"
    coverage_path = tmp_path / "coverage.json"
    html_path.write_text(html, encoding="utf-8")
    coverage_path.write_text(
        json.dumps(source_coverage, ensure_ascii=False), encoding="utf-8"
    )
    command = [sys.executable, str(VALIDATOR), str(html_path), str(coverage_path)]
    report_path = tmp_path / "report.json"
    if report:
        command.extend(["--report", str(report_path)])
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    parsed = json.loads(completed.stdout)
    if report:
        assert json.loads(report_path.read_text(encoding="utf-8")) == parsed
    return completed, parsed


def test_valid_deck_passes_and_reports_macro_and_weighted_scores(tmp_path: Path):
    html = """
    <html><body>
      <section class="slide" data-notes="Do not count this note.">
        <div data-source-ref="claim-1">Revenue reached 120 million USD.</div>
        <figure data-relation="citation-1">
          <blockquote data-node-id="quote-1">Build for trust.</blockquote>
          <figcaption data-node-id="author-1">Ada Example</figcaption>
        </figure>
      </section>
      <section class="slide">
        <h2>Next step</h2><p>Ship the audited plan.</p>
      </section>
    </body></html>
    """
    source_coverage = coverage(
        slide(
            1,
            [
                unit(
                    "claim-1",
                    "Revenue reached 120 million USD.",
                    weight=7,
                    protected=True,
                    source_ref="claim-1",
                ),
                unit("quote-1", "Build for trust.", protected=True),
                unit("author-1", "Ada Example", protected=True),
                unit("minor-omission", "Optional appendix detail"),
            ],
            [
                relation(
                    "citation-1",
                    "author_quote_binding",
                    "author-1",
                    "quote-1",
                    protected=True,
                )
            ],
        ),
        slide(
            2,
            [
                unit("title-2", "Next step", protected=True),
                unit("body-2", "Ship the audited plan."),
            ],
        ),
    )

    completed, report = run_gate(tmp_path, html, source_coverage, report=True)

    assert completed.returncode == 0
    assert report["pass"] is True
    assert report["summary"]["macro_average"] == {
        "text_retention": 0.95,
        "relation_retention": 1.0,
    }
    assert report["summary"]["weighted_average"] == {
        "text_retention": 0.916667,
        "relation_retention": 1.0,
    }


def test_each_slide_must_reach_ninety_percent_not_only_deck_average(tmp_path: Path):
    html = """
    <section class="slide">Complete first page</section>
    <section class="slide">Heavy retained text</section>
    """
    source_coverage = coverage(
        slide(1, [unit("s1", "Complete first page", weight=100)]),
        slide(
            2,
            [
                unit("heavy", "Heavy retained text", weight=8),
                unit("missing", "Missing material", weight=2),
            ],
        ),
    )

    completed, report = run_gate(tmp_path, html, source_coverage)

    assert completed.returncode == 1
    assert report["summary"]["weighted_average"]["text_retention"] > 0.90
    assert report["slides"][1]["text"]["score"] == 0.8
    assert report["summary"]["failed_slides"] == [2]


def test_missing_protected_number_and_unit_fails_even_above_weight_threshold(tmp_path: Path):
    html = '<section class="slide">Capacity increased substantially.</section>'
    source_coverage = coverage(
        slide(
            1,
            [
                unit("claim", "Capacity increased substantially.", weight=19),
                unit("number-unit", "42 MW", weight=1, protected=True),
            ],
        )
    )

    completed, report = run_gate(tmp_path, html, source_coverage)

    assert completed.returncode == 1
    text = report["slides"][0]["text"]
    assert text["score"] == 0.95
    assert text["protected_pass"] is False
    assert text["missing_protected"] == ["number-unit"]


def test_text_present_only_in_data_notes_or_speaker_notes_does_not_count(tmp_path: Path):
    html = """
    <section class="slide" data-notes="Protected launch date: 30 June">
      <div class="speaker-notes">Protected launch date: 30 June</div>
      <p>Visible summary</p>
    </section>
    """
    source_coverage = coverage(
        slide(1, [unit("date", "Protected launch date: 30 June", protected=True)])
    )

    completed, report = run_gate(tmp_path, html, source_coverage)

    assert completed.returncode == 1
    assert report["slides"][0]["text"]["units"][0]["matched"] is False


def test_hidden_duplicate_text_does_not_count(tmp_path: Path):
    html = """
    <style>.ghost { display: none !important; }</style>
    <section class="slide">
      <!-- Confidential baseline 17 kg -->
      <script>Confidential baseline 17 kg</script>
      <template>Confidential baseline 17 kg</template>
      <noscript>Confidential baseline 17 kg</noscript>
      <span class="ghost">Confidential baseline 17 kg</span>
      <span aria-hidden="true">Confidential baseline 17 kg</span>
      <span hidden>Confidential baseline 17 kg</span>
      <span style="display: none">Confidential baseline 17 kg</span>
      <span style="visibility: hidden">Confidential baseline 17 kg</span>
      <p>Visible summary</p>
    </section>
    """
    source_coverage = coverage(
        slide(1, [unit("baseline", "Confidential baseline 17 kg", protected=True)])
    )

    completed, report = run_gate(tmp_path, html, source_coverage)

    assert completed.returncode == 1
    assert report["slides"][0]["text"]["units"][0]["matched"] is False


def test_global_forbidden_text_fails_only_when_visible(tmp_path: Path):
    html = """
    <section class="slide"><h1>Question only</h1><div aria-hidden="true">LAST MILE</div></section>
    <section class="slide"><h1>Another title</h1><p>LAST MILE</p></section>
    """
    source_coverage = coverage(
        slide(1, [unit("title-1", "Question only", protected=True)]),
        slide(2, [unit("title-2", "Another title", protected=True)]),
    )
    source_coverage["forbidden_text"] = ["LAST MILE"]

    completed, report = run_gate(tmp_path, html, source_coverage)

    assert completed.returncode == 1
    assert report["slides"][0]["forbidden"]["pass"] is True
    assert report["slides"][1]["forbidden"]["matched_text"] == ["LAST MILE"]


def test_title_only_forbidden_selectors_reject_visible_supporting_content(tmp_path: Path):
    html = '<section class="slide"><h1>Only this title</h1><p class="iri-lead">Extra prompt</p></section>'
    source_coverage = coverage(
        {
            **slide(1, [unit("title", "Only this title", protected=True)]),
            "forbidden_selectors": [".iri-lead", ".iri-fact", ".iri-convergence-word"],
        }
    )

    completed, report = run_gate(tmp_path, html, source_coverage)

    assert completed.returncode == 1
    assert report["slides"][0]["forbidden"]["matched_selectors"] == [".iri-lead"]


def test_reversed_directed_relation_fails(tmp_path: Path):
    html = """
    <section class="slide">
      <div data-node-id="cause">Cause</div>
      <div data-node-id="effect">Effect</div>
      <i data-relation="causes-1" data-edge-from="effect" data-edge-to="cause"></i>
    </section>
    """
    source_coverage = coverage(
        slide(
            1,
            [unit("copy", "Cause Effect", protected=True)],
            [relation("causes-1", "causes", "cause", "effect", protected=True)],
        )
    )

    completed, report = run_gate(tmp_path, html, source_coverage)

    assert completed.returncode == 1
    relation_result = report["slides"][0]["relations"]["relations"][0]
    assert relation_result["matched"] is False
    assert relation_result["method"] == "directed_edge_reversed"


def test_author_quote_binding_requires_the_expected_endpoints_in_one_relation(tmp_path: Path):
    html = """
    <section class="slide">
      <div data-relation="citation-1">
        <blockquote data-node-id="quote-1">Accuracy before fluency.</blockquote>
        <cite data-node-id="author-2">Wrong Author</cite>
      </div>
      <cite data-node-id="author-1">Right Author</cite>
    </section>
    """
    source_coverage = coverage(
        slide(
            1,
            [
                unit("quote", "Accuracy before fluency.", protected=True),
                unit("author", "Right Author", protected=True),
            ],
            [
                relation(
                    "citation-1",
                    "author_quote_binding",
                    "author-1",
                    "quote-1",
                    protected=True,
                )
            ],
        )
    )

    completed, report = run_gate(tmp_path, html, source_coverage)

    assert completed.returncode == 1
    relations = report["slides"][0]["relations"]
    assert relations["score"] == 0.0
    assert relations["missing_protected"] == ["citation-1"]


def test_single_source_ref_node_cannot_cover_two_distinct_units(tmp_path: Path):
    html = """
    <section class="slide">
      <div data-source-ref="source-line-1">Alpha statement. Beta statement.</div>
    </section>
    """
    source_coverage = coverage(
        slide(
            1,
            [
                unit(
                    "alpha",
                    "Alpha statement.",
                    protected=True,
                    source_ref="source-line-1",
                ),
                unit(
                    "beta",
                    "Beta statement.",
                    protected=True,
                    selector='[data-source-ref~="source-line-1"]',
                ),
            ],
        )
    )

    completed, report = run_gate(tmp_path, html, source_coverage)

    assert completed.returncode == 1
    units = report["slides"][0]["text"]["units"]
    assert [item["matched"] for item in units] == [True, False]
    assert units[1]["reason"] == "source_ref_evidence_already_used"


def test_group_endpoints_and_multi_value_source_refs_are_supported(tmp_path: Path):
    html = """
    <section class="slide">
      <div data-group-id="layer-1" data-source-ref="title-1 detail-1">Layer 1 detail</div>
      <div data-group-id="layer-2">Layer 2</div>
      <i data-relation="ordered-before" data-edge-from="layer-1" data-edge-to="layer-2"></i>
    </section>
    """
    source_coverage = coverage(
        slide(
            1,
            [unit("title", "Layer 1", source_ref="title-1")],
            [relation("layer-order", "ordered-before", "layer-1", "layer-2", protected=True)],
        )
    )

    completed, report = run_gate(tmp_path, html, source_coverage)

    assert completed.returncode == 0
    assert report["pass"] is True


def test_containment_and_dom_order_relation_types_are_supported(tmp_path: Path):
    html = """
    <section class="slide">
      <div data-group-id="parent"><span data-node-id="child">Child</span></div>
      <div data-group-id="later">Later</div>
    </section>
    """
    source_coverage = coverage(
        slide(
            1,
            [unit("copy", "Child Later", protected=True)],
            [
                relation("nested", "contains", "parent", "child", protected=True),
                relation("ordered", "before", "parent", "later", protected=True),
            ],
        )
    )

    completed, report = run_gate(tmp_path, html, source_coverage)

    assert completed.returncode == 0
    methods = [item["method"] for item in report["slides"][0]["relations"]["relations"]]
    assert methods == ["dom_containment", "dom_order"]


def test_missing_required_threshold_is_invalid_input(tmp_path: Path):
    source_coverage = coverage(slide(1, [unit("copy", "Visible")]))
    del source_coverage["thresholds"]["relation_retention"]

    completed, report = run_gate(
        tmp_path, '<section class="slide">Visible</section>', source_coverage
    )

    assert completed.returncode == 2
    assert report["pass"] is False
    assert report["errors"] == ["thresholds.relation_retention is required"]
