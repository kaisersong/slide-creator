"""Model-facing contract compiled from existing runtime owners, without CSS/JS."""
from __future__ import annotations

import copy
import json
from typing import Any

from low_context import ROOT, compile_style_contract, StyleContractError
from preset_capabilities import discover_custom_themes, get_preset_render_capability, CANONICAL_PRESET_NAMES
from title_profiles import resolve_title_profile


def build_model_context(preset: str) -> dict[str, Any]:
    capability = get_preset_render_capability(preset)
    if not capability.can_render and not preset.startswith("custom:"):
        canonical=CANONICAL_PRESET_NAMES.get(preset.lower().replace("-"," "))
        if canonical:
            preset=canonical
            capability=get_preset_render_capability(preset)
    if not capability.can_render:
        raise StyleContractError(json.dumps(capability.render_error_payload(), ensure_ascii=False))
    contract = compile_style_contract(preset)
    template = copy.deepcopy(json.loads((ROOT / "references/brief-template.json").read_text()))
    template.update(brief_id="your-deck", title="", audience="", desired_action="", notes="")
    template["deck"].update(page_count=5, deck_type="user-content")
    template["style"].update(preset=preset, tone="", visual_density="medium")
    template["content"] = {"source_policy":"distill-only", "must_include":[], "must_avoid":[]}
    template["narrative"] = {"thesis":"", "page_roles":[], "slides":[]}
    template["timing"] = {kind:{key:"not measured" for key in ("plan","generate","validate","polish","total")} for kind in ("estimate","actual")}
    schema = json.loads((ROOT / "schemas/generation-brief.schema.json").read_text())
    slide_shape = schema["properties"]["narrative"]["properties"]["slides"]["items"]
    return {
        "contract_version":1, "preset":preset, "canonical_preset":capability.canonical_preset,
        "renderer_strategy":capability.renderer_strategy, "support_tier":capability.support_tier,
        "style_source":contract["source_path"], "style_digest":contract["digest"],
        "visual_contract":{key:contract[key] for key in ("font_families","allowed_layout_ids","style_reminders")},
        "title_profile":resolve_title_profile(preset),
        "color_tokens":{key:value for key,value in contract["tokens"].items() if any(s in key for s in ("bg","text","accent","red","navy"))},
        "brief_skeleton":template,
        "slide_required":slide_shape["required"],
        "slide_optional":{key: ({"enum":value["enum"]} if "enum" in value else value["type"])
                          for key,value in slide_shape["properties"].items() if key not in slide_shape["required"]},
        "rules":[
            "Fill every empty field and create page_roles/slides for all requested pages (5-20). The skeleton is not a valid final BRIEF.",
            "Use slide claim, explanation, visual_intent, supporting_facts and numeric_facts to preserve source evidence and rich content.",
            "Put all complete local evidence statements, including measurements, in supporting_facts. numeric_facts is an auxiliary index for metric binding, not additional table rows.",
            "One main claim and one main exhibit per page. Use varied layout families; do not reduce evidence to title-only slides.",
            "Distribute all source facts across pages. Do not pad evidence tables by repeating a fact, or copy global_facts into every page.",
            "Do not repeat the full evidence list in explanation. Prefer a distinct source-backed scope or next action; do not invent causal interpretation to create an insight.",
            "preferred_layout_family is a family such as hero, evidence, comparison, flow, close. Do not put layout IDs in that field.",
            "Preserve the chosen preset; the renderer owns CSS, runtime, export DOM, title balancing and layout implementation.",
            "Keep all numeric values paired with source entities and units. Keep targets and unknowns explicit. Never invent measurements.",
            "Copy quantified source statements into supporting_facts without changing the counted entity or qualifier. Two regulated customers needing review is not a count of two reviews. Keep the same entities in explanations and speaker notes.",
            "Keep observations, targets, proposals and causal hypotheses distinct. Interview reports do not prove a root cause. Preserve source actors, action order and scope; do not add inferred actors or conditions to evidence.",
            "If the source has no measurements, set chart_policy=avoid; explain the next test instead of using counts as evidence.",
            "Do not combine unlike units (activation %, latency ms, percentage-point change) in one quantitative series. Use labeled cards or chart_policy=avoid on that page.",
            "Use a concrete assertion as a title; preserve uncertainty. Avoid generic Overview/Introduction/Summary labels.",
            "Keep the user language. Put speaker directions in slide.speaker_note only. Do not add new top-level BRIEF fields.",
            "explanation, key_point, claim and supporting_facts are audience-visible content. Never put 演讲备注, 这一页, Explain that, Tell operators, Walk through, or thesis= in these fields.",
            "Use short assertion titles: aim for <=12 CJK characters or <=6 English words. Put full evidence and conditions in body fields, not an overlong title.",
            "supporting_facts must be complete audience-visible facts, conditions or actions; distribute them across pages, normally 2-4 items per page. Do not use fragment labels, instructions to the slide designer, or prose copied from this contract.",
            "Provide local supporting_facts on every page, including cover and close; sparse pages may have one fact. Set desired_action to the exact audience decision/next step, including scope and timing; it is visible on the closing page.",
            "Use at most 12 English words in a compact card item. explanation can use several short factual sentences; put longer speaking guidance in speaker_note.",
            "Do not use a before/after comparison for two unrelated facts or unchanged requirements; use evidence or flow instead.",
            "Do not inspect runtime source on the normal generation path. Read the full selected style reference only for a concrete missing design decision.",
        ],
        "technical_language_reference":"references/technical-language.md (technical content only)",
        "custom_themes":[path.parent.name for path in discover_custom_themes().values()],
    }


def print_model_context(preset: str) -> int:
    try:
        context = build_model_context(preset)
    except (StyleContractError, OSError, ValueError) as exc:
        print(f"CONTEXT ERROR: {exc}")
        return 1
    print(json.dumps(context, ensure_ascii=False, separators=(",", ":")))
    return 0
