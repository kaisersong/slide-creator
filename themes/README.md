# Custom Themes

Drop a folder here to add your own design preset to slide-creator.

## Structure

```
themes/
  your-theme-name/
    reference.md      ← required: style description Claude reads
    starter.html      ← optional: pre-built boilerplate (like blue-sky-starter.html)
```

## reference.md format

Follow the same format as the built-in references (e.g. `references/chinese-chan.md`):

```markdown
# Your Theme Name — Style Reference

One-sentence description. Inspired by / aesthetic / mood.

---

## Colors

```css
:root {
    --bg:      #...;
    --text:    #...;
    --accent:  #...;
}
```

## Typography
...

## Layout
...

## Best For
Use cases, audience, occasion.
```

## starter.html (optional)

If your theme has complex visual elements (animated backgrounds, special layout systems),
provide a starter HTML file. Claude will read it and use it as the base instead of
building from scratch. See `references/blue-sky-starter.html` for an example.

## Example

`molten-flow/` — **Molten Flow / 熔金流体**. A twisting gold liquid-metal ribbon with moving reflections. Say “use Molten Flow” or select `custom:molten-flow`. [View the demo](../demos/molten-flow-zh.html).

`stellar-vortex/` — **Stellar Vortex / 星核跃迁**. A luminous cyan/violet stellar core with rotating accretion ribbons and particles travelling through depth. Say “use Stellar Vortex” or select `custom:stellar-vortex`. [View the demo](../demos/stellar-vortex-zh.html).

Both new themes animate only the first slide, use WebGL2 for offline single-file and HTTP/IP playback, and export a detailed static cover. Their shared lifecycle is embedded by `scripts/build-cover-themes.py`.

`shader-hero/` — **Aurora Cover / 极光封面**. Select `custom:shader-hero` or say “use Aurora Cover.” Only the first slide animates; content and closing pages remain static. Local file playback and ordinary HTTP/IP automatically use WebGL2; HTTPS prefers WebGPU. The single HTML includes all resources and works offline without a server. Unavailable GPU backends, reduced motion, and printing use the detailed static poster. PPTX/PNG export intent removes both GPU runtimes at generation time. Try [the six-slide demo](../demos/shader-hero-zh.html).

`_example-coral-dawn/` — a complete sample theme you can copy and adapt.
Directories starting with `_` are ignored by slide-creator and will not appear in the preset picker.

Also see:
- `references/chinese-chan.md` — a built-in reference in the same format
- `references/blue-sky-starter.html` — a full starter template

## Sharing themes

To share a theme with others, publish the folder as a git repo. Users clone it into their
`themes/` directory:

```bash
git clone https://github.com/yourname/slide-creator-theme-yourtheme \
  ~/.claude/skills/slide-creator/themes/yourtheme
```
