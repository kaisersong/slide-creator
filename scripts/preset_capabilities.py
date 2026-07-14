from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


def _discover_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "references").is_dir() and (candidate / "schemas").is_dir():
            return candidate
    return here.parent


ROOT = _discover_root()
REFERENCES_DIR = ROOT / "references"
THEMES_DIR = ROOT / "themes"
PRESET_SUPPORT_PATH = ROOT / "references" / "preset-support-tiers.json"


PRESET_REFERENCE_MAP = {
    "aurora mesh": "aurora-mesh.md",
    "blue sky": "blue-sky-starter.html",
    "bold signal": "bold-signal.md",
    "chinese chan": "chinese-chan.md",
    "creative voltage": "creative-voltage.md",
    "dark botanical": "dark-botanical.md",
    "data story": "data-story.md",
    "electric studio": "electric-studio.md",
    "enterprise dark": "enterprise-dark.md",
    "glassmorphism": "glassmorphism.md",
    "modern newspaper": "modern-newspaper.md",
    "neo-brutalism": "neo-brutalism.md",
    "neo-retro dev deck": "neo-retro-dev.md",
    "neon cyber": "neon-cyber.md",
    "notebook tabs": "notebook-tabs.md",
    "paper & ink": "paper-ink.md",
    "pastel geometry": "pastel-geometry.md",
    "split pastel": "split-pastel.md",
    "strategy consulting": "strategy-consulting.md",
    "swiss modern": "swiss-modern.md",
    "terminal green": "terminal-green.md",
    "vintage editorial": "vintage-editorial.md",
}


CANONICAL_PRESET_NAMES = {
    "aurora mesh": "Aurora Mesh",
    "blue sky": "Blue Sky",
    "bold signal": "Bold Signal",
    "chinese chan": "Chinese Chan",
    "creative voltage": "Creative Voltage",
    "dark botanical": "Dark Botanical",
    "data story": "Data Story",
    "electric studio": "Electric Studio",
    "enterprise dark": "Enterprise Dark",
    "glassmorphism": "Glassmorphism",
    "modern newspaper": "Modern Newspaper",
    "neo-brutalism": "Neo-Brutalism",
    "neo-retro dev deck": "Neo-Retro Dev Deck",
    "neon cyber": "Neon Cyber",
    "notebook tabs": "Notebook Tabs",
    "paper & ink": "Paper & Ink",
    "pastel geometry": "Pastel Geometry",
    "split pastel": "Split Pastel",
    "strategy consulting": "Strategy Consulting",
    "swiss modern": "Swiss Modern",
    "terminal green": "Terminal Green",
    "vintage editorial": "Vintage Editorial",
}

PRESET_NAME_ALIASES = {
    "neo-retro dev": "neo-retro dev deck",
}


READY_NATIVE_PRESETS = {
    "swiss modern",
    "enterprise dark",
    "data story",
    "blue sky",
    "chinese chan",
}

DEFAULT_READY_PRESETS = {
    "swiss modern",
    "enterprise dark",
    "data story",
    "blue sky",
}

CONTEXTUAL_READY_PRESETS = {"chinese chan"}

CUSTOM_THEME_ALTERNATIVES = ("Swiss Modern", "Enterprise Dark", "Data Story", "Blue Sky")

READY_ALTERNATIVES = {
    "terminal green": ("Data Story", "Enterprise Dark", "Swiss Modern"),
    "strategy consulting": ("Enterprise Dark", "Swiss Modern", "Data Story"),
    "modern newspaper": ("Swiss Modern", "Data Story", "Chinese Chan"),
    "paper & ink": ("Chinese Chan", "Swiss Modern", "Data Story"),
    "glassmorphism": ("Blue Sky", "Swiss Modern", "Enterprise Dark"),
    "bold signal": ("Enterprise Dark", "Blue Sky", "Swiss Modern"),
    "aurora mesh": ("Blue Sky", "Enterprise Dark", "Data Story"),
    "neon cyber": ("Data Story", "Blue Sky", "Enterprise Dark"),
    "neo-retro dev deck": ("Data Story", "Enterprise Dark", "Blue Sky"),
    "notebook tabs": ("Chinese Chan", "Swiss Modern", "Data Story"),
}


@dataclass(frozen=True)
class PresetRenderCapability:
    preset: str
    canonical_preset: str | None
    reference_path: str | None
    support_tier: str
    generation_status: str
    recommendation_status: str
    renderer_strategy: str
    archetype_requirements: tuple[str, ...]
    can_render: bool
    can_recommend: bool
    explicit_request_behavior: str
    reason: str | None
    user_message: str
    ready_alternatives: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def render_error_payload(self) -> dict[str, Any]:
        return {
            "code": "preset_not_generator_ready",
            "preset": self.preset,
            "canonical_preset": self.canonical_preset,
            "generation_status": self.generation_status,
            "renderer_strategy": self.renderer_strategy,
            "can_render": self.can_render,
            "reason": self.reason,
            "alternatives": list(self.ready_alternatives),
            "user_message": self.user_message,
        }


def normalize_preset_name(value: str | None) -> str:
    normalized = (value or "").strip().lower()
    return PRESET_NAME_ALIASES.get(normalized, normalized)


def strip_custom_prefix(value: str | None) -> str:
    return normalize_preset_name(value).removeprefix("custom:").strip()


def load_preset_support_matrix() -> dict[str, Any]:
    return json.loads(PRESET_SUPPORT_PATH.read_text(encoding="utf-8"))


def discover_custom_themes() -> dict[str, Path]:
    themes: dict[str, Path] = {}
    if not THEMES_DIR.is_dir():
        return themes
    for directory in sorted(THEMES_DIR.iterdir()):
        if directory.name.startswith("_") or not directory.is_dir():
            continue
        reference = directory / "reference.md"
        if reference.exists():
            themes[normalize_preset_name(directory.name)] = reference.resolve()
    return themes


def is_custom_theme(preset: str) -> bool:
    return strip_custom_prefix(preset) in discover_custom_themes()


def _support_tier_for_builtin(normalized: str) -> str:
    matrix = load_preset_support_matrix()
    for tier, tier_presets in matrix.get("tiers", {}).items():
        if any(normalize_preset_name(candidate) == normalized for candidate in tier_presets):
            return tier
    raise KeyError(f"Unknown built-in preset in support matrix: {normalized}")


def _normalized_policy_state_members(state: str) -> set[str]:
    matrix = load_preset_support_matrix()
    support_states = matrix.get("policy", {}).get("support_states", {})
    return {
        normalize_preset_name(candidate)
        for candidate in support_states.get(state, [])
    }


def _generation_state_for_builtin(normalized: str) -> str:
    if normalized in _normalized_policy_state_members("native_deterministic_core"):
        return "native"
    if normalized in _normalized_policy_state_members("unified_profile_renderer"):
        return "profile"
    if normalized in _normalized_policy_state_members("unsupported_archive"):
        return "unsupported"
    raise KeyError(f"Unknown built-in preset generation state: {normalized}")


def support_tier_for_preset(preset: str) -> str:
    normalized = normalize_preset_name(preset)
    if normalized in PRESET_REFERENCE_MAP:
        return _support_tier_for_builtin(normalized)
    if is_custom_theme(preset):
        return "custom"
    raise KeyError(f"Unknown preset in support matrix: {preset}")


def canonical_preset_name(preset: str) -> str:
    normalized = normalize_preset_name(preset)
    if normalized in CANONICAL_PRESET_NAMES:
        return CANONICAL_PRESET_NAMES[normalized]
    clean = strip_custom_prefix(preset)
    custom_themes = discover_custom_themes()
    if clean in custom_themes:
        return custom_themes[clean].parent.name.title()
    raise KeyError(f"Unknown preset in support matrix: {preset}")


def resolve_style_reference_path(preset_or_path: str | Path) -> Path:
    candidate = Path(preset_or_path)
    if candidate.exists():
        return candidate.resolve()

    raw = str(preset_or_path)
    normalized = normalize_preset_name(raw)
    custom_themes = discover_custom_themes()

    if normalized.startswith("custom:"):
        clean = strip_custom_prefix(raw)
        if clean in custom_themes:
            return custom_themes[clean]
        raise FileNotFoundError(f"Unknown custom theme: {raw}")

    if normalized in PRESET_REFERENCE_MAP:
        return (REFERENCES_DIR / PRESET_REFERENCE_MAP[normalized]).resolve()

    if normalized in custom_themes:
        return custom_themes[normalized]

    raise FileNotFoundError(f"Unknown preset or reference path: {preset_or_path}")


def _reference_path_for_builtin(normalized: str) -> str:
    return str((REFERENCES_DIR / PRESET_REFERENCE_MAP[normalized]).resolve().relative_to(ROOT))


def _reference_path_for_custom(reference_path: Path) -> str:
    try:
        return str(reference_path.resolve().relative_to(ROOT))
    except ValueError:
        return str(reference_path.resolve())


def _reference_path_matches_builtin(path: Path) -> str | None:
    resolved = path.resolve()
    for normalized, relative in PRESET_REFERENCE_MAP.items():
        if (REFERENCES_DIR / relative).resolve() == resolved:
            return normalized
    return None


def _is_theme_reference_path(path: Path) -> bool:
    resolved = path.resolve()
    return resolved.name == "reference.md" and THEMES_DIR.resolve() in resolved.parents


def _custom_capability(reference_path: Path, display_name: str | None = None) -> PresetRenderCapability:
    name = display_name or reference_path.parent.name.title()
    return PresetRenderCapability(
        preset=name,
        canonical_preset=name,
        reference_path=_reference_path_for_custom(reference_path),
        support_tier="custom",
        generation_status="custom",
        recommendation_status="opt_in",
        renderer_strategy="custom_theme",
        archetype_requirements=(),
        can_render=True,
        can_recommend=False,
        explicit_request_behavior="render",
        reason=None,
        user_message=f"Custom theme '{name}' is available for explicit generation.",
        ready_alternatives=CUSTOM_THEME_ALTERNATIVES,
    )


def _ready_capability(normalized: str, *, support_tier: str) -> PresetRenderCapability:
    canonical = CANONICAL_PRESET_NAMES[normalized]
    recommendation_status = "default" if normalized in DEFAULT_READY_PRESETS else "contextual"
    return PresetRenderCapability(
        preset=canonical,
        canonical_preset=canonical,
        reference_path=_reference_path_for_builtin(normalized),
        support_tier=support_tier,
        generation_status="ready",
        recommendation_status=recommendation_status,
        renderer_strategy="native",
        archetype_requirements=(),
        can_render=True,
        can_recommend=True,
        explicit_request_behavior="render",
        reason=None,
        user_message=f"{canonical} has a stable deterministic renderer.",
        ready_alternatives=(),
    )


def _reference_driven_requirements(normalized: str) -> tuple[str, ...]:
    if normalized in {"strategy consulting", "terminal green", "modern newspaper", "neo-retro dev deck"}:
        return ("native_semantics",)
    if normalized in {"notebook tabs", "neon cyber"}:
        return ("runtime",)
    if normalized in {"glassmorphism", "aurora mesh"}:
        return ("browser_effect",)
    return ("static",)


def _reference_driven_capability(normalized: str, *, support_tier: str) -> PresetRenderCapability:
    canonical = CANONICAL_PRESET_NAMES[normalized]
    alternatives = READY_ALTERNATIVES.get(normalized, CUSTOM_THEME_ALTERNATIVES)
    reason = "style reference exists, deterministic generator not implemented"
    alternatives_text = " / ".join(alternatives)
    return PresetRenderCapability(
        preset=canonical,
        canonical_preset=canonical,
        reference_path=_reference_path_for_builtin(normalized),
        support_tier=support_tier,
        generation_status="reference_driven",
        recommendation_status="opt_in",
        renderer_strategy="reference_driven",
        archetype_requirements=_reference_driven_requirements(normalized),
        can_render=True,
        can_recommend=False,
        explicit_request_behavior="render_reference_driven",
        reason=reason,
        user_message=(
            f"我识别到你选择了 {canonical}。这个风格目前已收录设计参考，"
            f"但还没有 deterministic renderer；本次应走 reference-driven 生成，"
            f"读取风格 reference、共享模板和 strict validation 后输出 HTML。"
            f"如果校验失败，可降级到 {alternatives_text}。"
        ),
        ready_alternatives=alternatives,
    )


def _profile_requirements(normalized: str) -> tuple[str, ...]:
    if normalized in {"terminal green", "neon cyber", "neo-retro dev deck", "notebook tabs"}:
        return ("unified_profile", "technical_terminal")
    if normalized in {"paper & ink", "modern newspaper", "vintage editorial", "dark botanical"}:
        return ("unified_profile", "editorial_static")
    if normalized in {"strategy consulting"}:
        return ("unified_profile", "consulting_structured")
    if normalized in {"glassmorphism"}:
        return ("unified_profile", "glass_material")
    if normalized in {"neo-brutalism"}:
        return ("unified_profile", "brutalist_graphic")
    return ("unified_profile", "signal_pitch")


def _profile_capability(normalized: str, *, support_tier: str) -> PresetRenderCapability:
    canonical = CANONICAL_PRESET_NAMES[normalized]
    alternatives = READY_ALTERNATIVES.get(normalized, CUSTOM_THEME_ALTERNATIVES)
    return PresetRenderCapability(
        preset=canonical,
        canonical_preset=canonical,
        reference_path=_reference_path_for_builtin(normalized),
        support_tier=support_tier,
        generation_status="profile",
        recommendation_status="opt_in",
        renderer_strategy="unified_profile",
        archetype_requirements=_profile_requirements(normalized),
        can_render=True,
        can_recommend=False,
        explicit_request_behavior="render",
        reason=None,
        user_message=(
            f"{canonical} is explicitly renderable through the unified profile renderer. "
            "It is not part of the native deterministic core or the default recommendation surface."
        ),
        ready_alternatives=alternatives,
    )


def _unsupported_capability(label: str, reference_path: str | None = None) -> PresetRenderCapability:
    alternatives = CUSTOM_THEME_ALTERNATIVES
    return PresetRenderCapability(
        preset=label,
        canonical_preset=None,
        reference_path=reference_path,
        support_tier="unknown",
        generation_status="unsupported",
        recommendation_status="hidden",
        renderer_strategy="unsupported",
        archetype_requirements=(),
        can_render=False,
        can_recommend=False,
        explicit_request_behavior="fail_closed",
        reason="unknown preset or unsupported reference path",
        user_message=(
            f"我无法将 {label} 匹配到可稳定生成的内置 preset 或 custom theme。"
            f"可稳定生成的选择是 {' / '.join(alternatives)}，也可以提供 themes/<name>/reference.md。"
        ),
        ready_alternatives=alternatives,
    )


def get_preset_render_capability(preset_or_path: str | Path) -> PresetRenderCapability:
    raw = str(preset_or_path)
    candidate = Path(preset_or_path)

    if candidate.exists():
        resolved = candidate.resolve()
        if _is_theme_reference_path(resolved):
            return _custom_capability(resolved)
        builtin = _reference_path_matches_builtin(resolved)
        if builtin:
            support_tier = _support_tier_for_builtin(builtin)
            generation_state = _generation_state_for_builtin(builtin)
            if generation_state == "native":
                return _ready_capability(builtin, support_tier=support_tier)
            if generation_state == "profile":
                return _profile_capability(builtin, support_tier=support_tier)
            return _unsupported_capability(raw, reference_path=str(resolved))
        return _unsupported_capability(raw, reference_path=str(resolved))

    normalized = normalize_preset_name(raw)
    custom_themes = discover_custom_themes()

    if normalized.startswith("custom:"):
        clean = strip_custom_prefix(raw)
        if clean in custom_themes:
            return _custom_capability(custom_themes[clean])
        return _unsupported_capability(raw)

    if normalized in PRESET_REFERENCE_MAP:
        support_tier = _support_tier_for_builtin(normalized)
        generation_state = _generation_state_for_builtin(normalized)
        if generation_state == "native":
            return _ready_capability(normalized, support_tier=support_tier)
        if generation_state == "profile":
            return _profile_capability(normalized, support_tier=support_tier)
        return _unsupported_capability(raw)

    if normalized in custom_themes:
        return _custom_capability(custom_themes[normalized])

    return _unsupported_capability(raw)


def renderable_recommendation_presets(*, include_contextual: bool = True) -> list[str]:
    allowed = {"default", "contextual"} if include_contextual else {"default"}
    return [
        CANONICAL_PRESET_NAMES[key]
        for key in PRESET_REFERENCE_MAP
        if get_preset_render_capability(CANONICAL_PRESET_NAMES[key]).recommendation_status in allowed
        and get_preset_render_capability(CANONICAL_PRESET_NAMES[key]).can_render
    ]


def default_recommendation_presets() -> list[str]:
    return [
        CANONICAL_PRESET_NAMES[key]
        for key in ("swiss modern", "enterprise dark", "data story", "blue sky")
    ]
