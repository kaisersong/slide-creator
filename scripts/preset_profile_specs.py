from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PresetComponentAdapter:
    role: str
    layout_class: str
    signature_classes: tuple[str, ...]
    component_kinds: tuple[str, ...]


@dataclass(frozen=True)
class PresetProfileSpec:
    preset: str
    family: str
    fonts: tuple[str, ...]
    css_vars: dict[str, str]
    body_classes: tuple[str, ...]
    signature_classes: tuple[str, ...]
    layout_sequence: tuple[str, ...]
    required_component_classes: tuple[str, ...]
    colors: tuple[str, ...] = ()
    background_strategy: str = ""
    adapter_key: str = ""
    visible_signature_classes: tuple[str, ...] = ()
    visible_signature_ids: tuple[str, ...] = ()
    background_signature_selectors: tuple[str, ...] = ()
    component_adapters: tuple[PresetComponentAdapter, ...] = ()


def _split(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split("|") if item.strip())


def _vars(names: str, colors: tuple[str, ...]) -> dict[str, str]:
    keys = _split(names)
    palette = colors or ("#111111",)
    result = {key: palette[index % len(palette)] for index, key in enumerate(keys)}
    if not any(key == "--bg" or key.startswith("--bg") for key in result):
        result["--bg"] = palette[0]
    return result


EXTRA_VISIBLE_CLASSES: dict[str, tuple[str, ...]] = {
    "Paper & Ink": (
        "rule",
        "rule-line",
        "body-text",
        "drop-cap",
        "pull-quote",
        "stat-row",
        "stat-val",
        "stat-label",
        "pain-list",
        "pain-item",
        "steps",
        "step",
    ),
    "Strategy Consulting": (
        "sc-action-title",
        "sc-section-header",
        "sc-evidence-card",
        "sc-metric",
        "sc-metric-label",
        "sc-reco-box",
        "sc-before-after",
        "sc-three-things",
        "sc-source",
        "sc-matrix",
    ),
    "Creative Voltage": (
        "voltage-title",
        "voltage-card",
        "voltage-blue-panel",
        "voltage-neon-badge",
        "voltage-halftone",
        "voltage-diamond",
    ),
    "Modern Newspaper": ("np-rule",),
    "Vintage Editorial": ("vintage-masthead", "editorial-rule", "drop-cap", "pullquote", "rule-thick"),
}


DECOR_ONLY_VISIBLE_CLASSES: dict[str, set[str]] = {
    "Creative Voltage": {"voltage-halftone"},
    "Terminal Green": {"rule"},
}


def _adapter_key(preset: str) -> str:
    return preset.lower().replace("&", "and").replace("-", " ").replace(" ", "_")


def _visible_classes(preset: str, component_classes: tuple[str, ...]) -> tuple[str, ...]:
    if preset == "Paper & Ink":
        return (
            "rule",
            "rule-line",
            "body-text",
            "drop-cap",
            "pull-quote",
            "stat-row",
            "stat-val",
            "stat-label",
            "pain-list",
            "pain-item",
            "steps",
            "step",
        )
    if preset == "Strategy Consulting":
        return (
            "sc-action-title",
            "sc-section-header",
            "sc-evidence-card",
            "sc-metric-label",
            "sc-reco-box",
            "sc-before-after",
            "sc-before-panel",
            "sc-after-panel",
            "sc-panel-label",
            "sc-three-things",
            "sc-source",
            "sc-quote-evidence",
            "sc-quote-block",
            "sc-quote-text",
            "sc-quote-attribution",
        )
    values: list[str] = []
    decor_only = DECOR_ONLY_VISIBLE_CLASSES.get(preset, set())
    for item in [*component_classes, *EXTRA_VISIBLE_CLASSES.get(preset, ())]:
        if item in decor_only:
            continue
        if item and item not in values:
            values.append(item)
    return tuple(values)


def _component_adapters(visible_classes: tuple[str, ...]) -> tuple[PresetComponentAdapter, ...]:
    chunks = [
        ("cover", "profile_cover", visible_classes[0:2], ("heading", "metric_card")),
        ("evidence", "profile_evidence", visible_classes[2:5], ("card", "metric_card")),
        ("workflow", "profile_workflow", visible_classes[5:8], ("timeline", "list")),
        ("close", "profile_close", visible_classes[8:12] or visible_classes[:2], ("card", "quote")),
    ]
    return tuple(
        PresetComponentAdapter(
            role=role,
            layout_class=layout_class,
            signature_classes=tuple(item for item in signature_classes if item),
            component_kinds=component_kinds,
        )
        for role, layout_class, signature_classes, component_kinds in chunks
    )


def _make(
    preset: str,
    family: str,
    *,
    fonts: str,
    vars: str,
    colors: str,
    classes: str,
    layouts: str,
) -> PresetProfileSpec:
    color_values = _split(colors)
    component_classes = _split(classes)
    visible_classes = _visible_classes(preset, component_classes)
    slug = preset.lower().replace("&", "and").replace(" ", "-")
    background_selectors = ("#slide-1",) if preset == "Paper & Ink" else (".slide-1",)
    return PresetProfileSpec(
        preset=preset,
        family=family,
        fonts=_split(fonts),
        css_vars=_vars(vars, color_values),
        body_classes=(f"profile-{slug}",),
        signature_classes=component_classes,
        layout_sequence=_split(layouts),
        required_component_classes=component_classes,
        colors=color_values,
        background_strategy=_adapter_key(preset),
        adapter_key=_adapter_key(preset),
        visible_signature_classes=visible_classes,
        background_signature_selectors=background_selectors,
        component_adapters=_component_adapters(visible_classes),
    )


PROFILE_SPECS: dict[str, PresetProfileSpec] = {
    "Aurora Mesh": _make(
        "Aurora Mesh",
        "signal_pitch",
        fonts="dm sans|monospace|noto sans sc|sans-serif|space grotesk|system-ui",
        vars="--accent|--bg-primary|--body-size|--card-bg|--card-border|--content-gap|--divider|--font-body|--font-display|--h2-size|--slide-padding|--subtitle-size|--text-body|--text-muted|--text-primary|--title-size",
        colors="#000|#00b4ff|#00f5c4|#0a0a1a|#999|#fff|#ffffff|rgba(0,0,0,0.5)|rgba(0,0,0,0.6)|rgba(0,0,0,0.78)|rgba(0,180,255,0.30)|rgba(0,245,196,0.12)|rgba(0,245,196,0.3)|rgba(0,245,196,0.30)|rgba(0,245,196,0.40)|rgba(0,255,180,0.20)",
        classes="aurora-accent|aurora-badge|aurora-card|aurora-content|aurora-divider|aurora-slide|aurora-stat|aurora-subtitle|aurora-title|feat-grid",
        layouts="aurora_hero|aurora_card|aurora_stat|aurora_split|aurora_trio|aurora_timeline",
    ),
    "Bold Signal": _make(
        "Bold Signal",
        "signal_pitch",
        fonts="-apple-system|archivo black|monospace|sans-serif|space grotesk|system-ui",
        vars="--bg-gradient|--bg-primary|--card-bg|--slide-count|--text-body|--text-muted|--text-on-card|--text-primary",
        colors="#000|#1a1a1a|#222|#2d2d2d|#ff5722|#ffffff|rgba(255,255,255,0.03)|rgba(255,255,255,0.05)|rgba(255,255,255,0.06)|rgba(255,255,255,0.08)",
        classes="bold-signal-card|bold-signal-title|signal-block",
        layouts="signal_cover|signal_cards|signal_split|signal_timeline|signal_close",
    ),
    "Creative Voltage": _make(
        "Creative Voltage",
        "signal_pitch",
        fonts="sans-serif|space mono|syne|system-ui",
        vars="--accent-neon|--bg-blue|--bg-primary|--body-size|--content-gap|--duration-normal|--ease-out-expo|--font-body|--font-display|--font-mono|--h2-size|--slide-padding|--small-size|--text-primary|--text-secondary|--title-size",
        colors="#000|#0066ff|#1a1a2e|#999|#d4ff00|#ffffff|rgba(0,0,0,0.5)|rgba(0,0,0,0.78)|rgba(0,102,255,0.08)|rgba(0,102,255,0.15)|rgba(0,102,255,0.3)|rgba(212,255,0,0.05)",
        classes="pill|stat|voltage-blue-panel|voltage-body|voltage-callout|voltage-card|voltage-dark-panel|voltage-diamond|voltage-features|voltage-halftone|voltage-mono|voltage-neon-badge|voltage-split|voltage-title",
        layouts="voltage_cover|voltage_panel|voltage_split|voltage_cards|voltage_close",
    ),
    "Dark Botanical": _make(
        "Dark Botanical",
        "editorial_static",
        fonts="cormorant|ibm plex mono|ibm plex sans|monospace|noto sans sc|sans-serif|serif|system-ui",
        vars="--accent-gold|--accent-pink|--accent-warm|--bg-primary|--body-size|--content-gap|--font-body|--font-display|--h2-size|--slide-padding|--small-size|--text-primary|--text-secondary|--title-size",
        colors="#000|#0a0a0a|#0f0f0f|#1e1e1e|#2a2520|#9a9590|#c9b896|#d4a574|#e8b4b8|#e8e4df|rgba(15,15,15,0.8)|rgba(201,184,150,0.1)|rgba(201,184,150,0.15)",
        classes="feature-grid|orb|orb-gold|orb-pink|orb-terra|preset-grid",
        layouts="botanical_cover|botanical_grid|botanical_split|botanical_quote|botanical_close",
    ),
    "Electric Studio": _make(
        "Electric Studio",
        "signal_pitch",
        fonts="manrope|monospace|noto sans sc|sans-serif|system-ui",
        vars="--accent|--accent-blue|--bg-dark|--bg-light|--bg-white|--body-size|--content-gap|--duration-normal|--ease-out-expo|--font-body|--font-display|--h2-size|--slide-padding|--small-size|--subtitle-size|--text-dark|--text-light|--text-secondary|--title-size",
        colors="#000|#0a0a0a|#4361ee|#999|#f4f5f9|#f8f9ff|#fff|#ffffff|rgba(0,0,0,0.18)|rgba(0,0,0,0.5)|rgba(0,0,0,0.6)|rgba(0,0,0,0.78)|rgba(10,10,10,0.06)|rgba(10,10,10,0.4)",
        classes="elec-label|elec-title|elec-body|elec-stat-number|code-block|cta-pill",
        layouts="electric_cover|electric_panels|electric_quote|electric_grid|electric_close",
    ),
    "Glassmorphism": _make(
        "Glassmorphism",
        "glass_material",
        fonts="-apple-system|blinkmacsystemfont|noto sans cjk sc|pingfang sc|sans-serif|segoe ui|sf pro display|system-ui",
        vars="--bg-gradient-1|--bg-gradient-2|--bg-gradient-3|--body-size|--content-gap|--duration-normal|--ease-out-expo|--glass-bg|--glass-border|--glass-text-dark|--glass-text-light|--h2-size|--orb-mint|--orb-pink|--orb-purple|--slide-padding|--small-size|--title-size",
        colors="#000|#1a1a2e|#1d6fa4|#667eea|#764ba2|#999|#a6c1ee|#a8edea|#f093fb|#f8cdda|#fed6e3|#fff|rgba(0,0,0,0.08)|rgba(0,0,0,0.10)|rgba(0,0,0,0.15)|rgba(0,0,0,0.5)|rgba(102,126,234,0.15)|rgba(102,126,234,0.3)|rgba(102,126,234,0.5)|rgba(168,237,234,0.4)",
        classes="glass-body|glass-card|glass-item|glass-title|grid|orb|orb1|orb2|orb3|pill",
        layouts="glass_hero|glass_card|glass_split|glass_trio|glass_stat",
    ),
    "Modern Newspaper": _make(
        "Modern Newspaper",
        "editorial_static",
        fonts="playfair display|sans-serif|source sans 3|source sans pro|system-ui",
        vars="--accent|--bg|--card-bg|--card-border|--divider|--duration-normal|--ease-out-expo|--slide-padding|--text-body|--text-muted|--text-primary|--text-secondary",
        colors="#000|#111|#1c1917|#44403c|#999|#fafaf9|#fff|rgba(0,0,0,0.50)|rgba(0,0,0,0.78)|rgba(0,0,0,0.85)|rgba(16,185,129,0.80)",
        classes="pill|stat|stats",
        layouts="newspaper_cover|newspaper_columns|newspaper_stats|newspaper_index|newspaper_close",
    ),
    "Neo-Brutalism": _make(
        "Neo-Brutalism",
        "brutalist_graphic",
        fonts="-apple-system|courier new|monospace|noto sans sc|sans-serif|space grotesk|system-ui",
        vars="--bg|--body-size|--btn-bg|--btn-text|--content-gap|--h2-size|--slide-padding|--small-size|--text|--title-size",
        colors="#000|#000000|#1a1a2e|#e0e0e0|#ffeb3b|#fff|#ffffff|rgba(0,0,0,0.08)|rgba(0,0,0,0.18)|rgba(0,0,0,0.2)|rgba(0,0,0,0.28)",
        classes="cta-rule|feature-grid|heavy-rule|left-panel|right-panel|brutalist-block|brutalist-poster",
        layouts="brutalist_cover|brutalist_blocks|brutalist_split|brutalist_manifesto|brutalist_close",
    ),
    "Neo-Retro Dev Deck": _make(
        "Neo-Retro Dev Deck",
        "technical_terminal",
        fonts="-apple-system|barlow condensed|ibm plex mono|ibm plex sans|monospace|noto sans sc|sans-serif",
        vars="--accent|--bg|--block-bg|--block-dark|--body-size|--border|--content-gap|--cyan|--green|--grid|--h2-size|--pink|--slide-padding|--small-size|--text|--title-size|--yellow",
        colors="#000|#00c8ff|#111111|#1a1a1a|#22c55e|#444|#666|#888|#999|#f5f2e8|#f7f5f0|#ff3c7e|#ffe14d|#fff|#ffffff",
        classes="accent-pink|arch-tint-pink|ba-panel|badge-pink|body-text|cards-grid|cmd-pink|cmd-table|hl-pink|metric-num-pink|metrics-grid",
        layouts="retro_cover|retro_cmd|retro_cards|retro_metrics|retro_close",
    ),
    "Neon Cyber": _make(
        "Neon Cyber",
        "technical_terminal",
        fonts="-apple-system|clash display|jetbrains mono|monospace|sans-serif|satoshi",
        vars="--bg|--bg-panel|--body-size|--border-glow|--content-gap|--cyan|--duration-normal|--ease-out-expo|--grid|--h2-size|--magenta|--slide-padding|--small-size|--text|--text-muted|--title-size",
        colors="#000|#00ffcc|#0a0f1c|#0e1525|#e0f0ff|#ff00aa|rgba(0,0,0,0.5)|rgba(0,255,204,0.01)|rgba(0,255,204,0.03)|rgba(0,255,204,0.04)|rgba(0,255,204,0.06)|rgba(0,255,204,0.1)|rgba(0,255,204,0.15)",
        classes="cyber-card|cyber-heading|cyber-label|cyber-title|grid|neon-body|neon-divider|neon-mono",
        layouts="cyber_cover|cyber_grid|cyber_terminal|cyber_split|cyber_close",
    ),
    "Notebook Tabs": _make(
        "Notebook Tabs",
        "technical_terminal",
        fonts="bodoni moda|dm sans|menlo|monospace|noto sans sc|sans-serif|sf mono|system-ui",
        vars="--bg-outer|--bg-page|--body-size|--content-gap|--font-body|--font-display|--h2-size|--slide-padding|--small-size|--tab-1|--tab-2|--tab-3|--tab-4|--tab-5|--tab-6|--tab-7|--tab-8|--text-primary|--text-secondary|--title-size",
        colors="#000|#1a1a1a|#2d2d2d|#666666|#98d4bb|#999|#a8d8ea|#b4d4b4|#c7b8ea|#f4b4a4|#f4b8c5|#f4c4a4|#f8f6f1|#ffe6a7|#fff|rgba(0,0,0,0.015)|rgba(0,0,0,0.02)|rgba(0,0,0,0.04)|rgba(0,0,0,0.05)",
        classes="ba-split|cmd-table|feat-grid|tab|tabs",
        layouts="tabs_cover|tabs_stack|tabs_split|tabs_grid|tabs_close",
    ),
    "Paper & Ink": _make(
        "Paper & Ink",
        "editorial_static",
        fonts="crimson pro|georgia|sans-serif|serif|system-ui",
        vars="--accent|--bg|--card-bg|--card-border|--divider|--duration-normal|--ease-out-expo|--slide-padding|--text-body|--text-muted|--text-primary|--text-secondary",
        colors="#000|#111|#1c1917|#999|#fefdf8|#fff|rgba(0,0,0,0.50)|rgba(0,0,0,0.78)|rgba(0,0,0,0.85)|rgba(16,185,129,0.80)|rgba(255,255,255,0.10)",
        classes="cta-layout|editing-layout|hero-layout|install-layout|pill|present-mode-layout|preset-gallery-layout|problem-layout|stat|stats|workflow-layout",
        layouts="paper_hero|paper_columns|paper_pullquote|paper_index|paper_close",
    ),
    "Pastel Geometry": _make(
        "Pastel Geometry",
        "geometric_soft",
        fonts="monospace|noto sans sc|plus jakarta sans|sans-serif|system-ui",
        vars="--accent|--bg-primary|--body-size|--card-bg|--content-gap|--font-body|--font-display|--h2-size|--pill-lavender|--pill-mint|--pill-peach|--pill-pink|--pill-sage|--pill-sky|--slide-padding|--small-size|--text-primary|--text-secondary|--title-size",
        colors="#000|#1a1a1a|#1a2530|#666666|#7bb8d4|#8fad9a|#9b8dc4|#a8d4c4|#c8d9e6|#f0b4d4|#f0c4a0|#faf9f7|#fff",
        classes="feat-grid|left-panel|link-text|pill|pink|preset-grid|right-panel|steps-grid|geo-shape|geo-frame|pastel-chip",
        layouts="geo_cover|geo_grid|geo_split|geo_steps|geo_close",
    ),
    "Split Pastel": _make(
        "Split Pastel",
        "split_editorial",
        fonts="fira code|monospace|noto sans sc|outfit|sans-serif|sf mono|system-ui",
        vars="--accent|--badge-lavender|--badge-mint|--badge-peach|--badge-pink|--badge-yellow|--bg-lavender|--bg-peach|--body-size|--content-gap|--font-body|--font-display|--h2-size|--slide-padding|--small-size|--text-dark|--text-secondary|--title-size",
        colors="#000|#1a1a1a|#666666|#b0e0c0|#b8a08a|#c8f0d8|#d4cef5|#e4dff0|#f0d4c0|#f0d4e0|#f0f0c8|#f5d4c4|#f5e6dc|#fff",
        classes="badge-pink|card|feature-grid|left-panel|pink|preset-grid|right-panel|step-num-pink|split-panel|soft-orb|pastel-metric",
        layouts="split_cover|split_statement|split_cards|split_timeline|split_close",
    ),
    "Strategy Consulting": _make(
        "Strategy Consulting",
        "consulting_structured",
        fonts="inherit|inter|sans-serif|system-ui",
        vars="--accent|--accent-light|--bg|--bg-accent|--bg-card|--border|--divider|--driver-gap|--highlight|--negative|--neutral|--positive|--slide-count|--text|--text-muted",
        colors="#000|#1a2b4a|#1b3a6b|#2e7d5b|#3366a8|#6b7a90|#c0392b|#c8d1dc|#d8dfe8|#eef2f7|#f0c850|#f7f8fa|#fff|#ffffff|rgba(27,58,107,0.04)",
        classes="sc-after-panel|sc-before-panel|sc-panel-label|sc-quote-attribution|sc-quote-block|sc-quote-evidence|sc-quote-text",
        layouts="consulting_exec|consulting_matrix|consulting_split|consulting_quote|consulting_close",
    ),
    "Terminal Green": _make(
        "Terminal Green",
        "technical_terminal",
        fonts="jetbrains mono|sans-serif|system-ui",
        vars="--bg|--bg-panel|--blue|--body-size|--border|--comment|--content-gap|--duration-normal|--ease-out-expo|--font-mono|--green|--green-muted|--h2-size|--red|--slide-padding|--small-size|--text|--text-muted|--title-size|--yellow",
        colors="#000|#0d1117|#111|#161b22|#30363d|#39d353|#484f58|#58a6ff|#8b949e|#c9d1d9|#e3b341|#f85149|rgba(0,0,0,0.5)",
        classes="feature-grid|preset-grid|rule|stat|terminal-block",
        layouts="terminal_boot|terminal_code|terminal_grid|terminal_timeline|terminal_close",
    ),
    "Vintage Editorial": _make(
        "Vintage Editorial",
        "editorial_static",
        fonts="courier new|fraunces|monospace|noto sans sc|sans-serif|serif|system-ui|work sans",
        vars="--accent-burgundy|--accent-warm|--bg-cream|--pdh|--pdw|--pox|--poy|--ps|--text-primary|--text-secondary",
        colors="#000|#1a1a1a|#555|#555555|#5a2a1a|#666|#6a1c28|#888|#8b2635|#aaa|#e8d4c0|#f5f3ee|#fff",
        classes="body-text|preset-grid|pullquote|rule|rule-thick|step-editorial|editorial-rule|drop-cap|vintage-masthead",
        layouts="vintage_masthead|vintage_columns|vintage_pullquote|vintage_index|vintage_close",
    ),
}
