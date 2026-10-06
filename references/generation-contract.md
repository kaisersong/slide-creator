# 从内容生成 BRIEF

模型负责内容、论点、证据与页间推进。程序负责完整风格、布局实现、CSS、播放/编辑、字体、导出 DOM 与 strict validation。

1. 保留用户明确指定的 preset；没有指定时按 SKILL 的推荐面选择。程序会发现 custom themes，并从原始风格 compiler 给出契约：
   `python3 main.py --model-context --preset "Data Story"`
2. 读取返回的 skeleton、允许布局与内容规则，填写一个完整 `BRIEF.json`。空 skeleton 只是字段形状，不能直接生成。页数 5–20；page_roles 和 slides 的长度等于 page_count，slide_number 连续从 1 开始。
3. 每页保留 claim、explanation、visual_intent 和必要的 supporting_facts/numeric_facts。先把来源中的事实分配到页，再选不同的主要展示。以上字段都会进入观众可见的正文；讲者指令只写逐页 `speaker_note`。不要把“演讲备注/这一页/Explain that/Tell operators”放进正文。未提供 speaker_note 的旧 BRIEF 继续用 explanation 生成备注。不要为了减少 token 删除条件、风险、单位或未知值。
4. 使用所选风格允许的展示。preferred_layout_family 填 hero/evidence/comparison/flow/close 等家族；具体 layout 由 renderer 决定。最多 5 条并列项；避免连续相同布局与标题页堆积。标题表达可被事实支持的判断，不能把目标写成已实现结果。区分观察、目标、建议与因果假设；访谈线索不能写成已证明的根因。保留原有主体、动作顺序和适用范围，不向证据补入推测的主体或条件。
5. 技术文稿额外读取 `references/technical-language.md`，尽量达到该文件定义的 ASD-STE100 对齐项目评分 80/100；它是观察项，不能以丢失事实换取语言分数。商业或创意文稿不强制 STE。
6. 运行 `python3 main.py --generate --brief BRIEF.json --output deck.html`。这个命令已验证 BRIEF，并在写最终文件前执行 strict gate。成功后不用重复运行相同 validator；失败时根据具体错误修正 BRIEF 再生成。严禁绕过 gate、手拼 HTML 或修改 runtime 来使当前任务通过。

正常生成不必读取 `html-template.md`、`js-engine.md`、`base-css.md`、完整 starter 或 renderer 源码。只有某个设计决策不在契约中时，按需读取选中 preset 的有关章节；实现错误必须明确报告，不能让每次内容任务都改生成器。`title-quality.md` 与 `impeccable-anti-patterns.md` 供深度精修/review 按需读取，基本要求已写入本契约。

已存在 BRIEF 时直接使用它。现有 deck 更换风格时仍须抽取 BRIEF 后 canonical render；同风格文案编辑保留 existing-deck guard。用户明确要求 eval 时继续输出正式 eval JSON。
