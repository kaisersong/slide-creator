# 动效封面 / Animated Covers

When a user asks which animated covers exist, wants previews, or describes a moving first slide, use this catalog. Present friendly names and visual differences; users do not need shader/backend names or animation parameters.

## Currently available

| 用户名称 | BRIEF.style.preset | 首页效果 | 正文风格 |
|---|---|---|---|
| 极光封面 / Aurora Cover | custom:shader-hero | 夜空中的绿青极光帘幕、光丝与缓慢流动的褶皱 | 米白编辑风正文，深色收尾 |
| 奇幻彩虹 / Fantasy Rainbow | custom:fantasy-rainbow | 满屏流动的虹彩色带与光场 | 白底编辑风正文，近黑收尾 |
| 熔金流体 / Molten Flow | custom:molten-flow | 黑底金橙色立体金属光带，持续扭转与高光流动 | 暖米白正文，深棕收尾 |
| 星核跃迁 / Stellar Vortex | custom:stellar-vortex | 蓝紫星核、旋转光环与穿行粒子，空间纵深强 | 冷白正文，靛蓝收尾 |

All four themes animate only the first slide. Content and closing pages stay static, and animation stops when the cover is inactive. Aurora Cover automatically uses WebGL2 for double-clicked local files and plain HTTP/IP; secure web origins prefer WebGPU. Fantasy Rainbow uses its existing WebGL controller. Molten Flow and Stellar Vortex use their shared WebGL2 cover controller. No server or extra assets are required to play the single HTML locally. Reduced motion and unavailable graphics use a static fallback.

ASCII Stream animates content pages as well; do not offer it as a cover-only choice.

## User prompts

- “有哪些动效封面？给我看预览。” — show these four options. If rendered previews are requested, materialize valid short BRIEFs and render through the standard program path; do not hand-author a final deck or depend on demos being present in the runtime package.
- “用极光封面，做一份产品发布演示。” — select custom:shader-hero; no follow-up questions about animated page ranges or GPU parameters.
- “用奇幻彩虹风格，把这些内容做成 slide。” — select custom:fantasy-rainbow.
- “用熔金流体，做一份醒目的品牌发布演示。” — select custom:molten-flow; recommend this for warm, bold, sculptural openings.
- “用星核跃迁，做一份未来感的技术发布演示。” — select custom:stellar-vortex; recommend this for vivid depth and particle motion.
- “给我做一份有动效首页的演示。” — recommend from this catalog and the content context; default to Aurora Cover when the user has supplied no further preference.

Load the selected theme's compiled model contract and keep its BRIEF preset locked. The current entry selects a complete theme, including its content-page style. Arbitrarily combining a different preset's content pages with one of these cover effects is not a supported effect field; do not promise that combination without implementing its render contract.

Only list shipped, renderable themes as available. Proposed effects and library components are future candidates, not selectable presets. New effects must keep cover-only lifecycle, offline playback, detailed fallback, and static export behavior before joining this catalog.
