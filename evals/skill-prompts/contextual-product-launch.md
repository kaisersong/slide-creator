请基于以下研究笔记生成一份 HTML 产品发布演示稿，面向产品和工程负责人。需要适合现场讲解，不要做研究报告。

输出要求：
- 保存到 `evals/artifacts/current/skill-runs/contextual-product-launch/`。
- 使用产品发布感更强的视觉风格。
- 不要把没有数字的观点包装成 KPI。

研究笔记：
- 用户真正需要的是在生成前锁定结构，而不是生成后反复重试。
- 观察 1：当内容在长对话末尾才被要求转成 slides，模型更容易遗漏风格和标题约束。
- 观察 2：当 deck 先落成 BRIEF.json，再渲染 HTML，失败更容易定位到路由、压缩、渲染或 polish。
- 观察 3：最稳定的输出会把标题、叙事角色、版式和严格校验分成可复查的中间层。
- 建议：发布重点放在 IR-first workflow 和 strict pre-write gate。
