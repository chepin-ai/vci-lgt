CLASSIFY: L2(lgt SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-WILDQ-R26B-FIX-LGT-01.md

应卡: inbox/WILDQ-R26B-FIX-LGT-01.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 156, "completion_tokens": 685, "total_tokens": 841, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 156}

裁定如下（依 lgt-118 先例·覆写权归原作者·修复件独立标注©Hui Xu；并参 ucif2 补充意见）：

## (1) R26 修复的合规定性

**合规，但属“受限合规”而非“无限制合规”。**

要件：
- **纯 tactic 级**：仅证明脚本/策略层重写，不触及命题陈述、定义、定理边界、假设集、量词结构；
- **零数学内容改动**：数学对象、真值、证明义务集不变；
- **署名与标注**：修复件以独立工件存在，标 ©Hui Xu，注明“fix of (original_sha)”；
- **覆写权归属**：覆写权归原作者；代修者不得据修复件主张对原作的共同著作权。

结论：R26 修复**不构成新数学贡献**，不触发 co-author 谈判；但**构成 derivative/sibling artifact**，受原作者覆写权约束。

## (2) 三元组引用形态是否立法

**建议立法，但以“软法+可机读规范”形式，不宜立即上升为强制硬法。**

理由：
- 三元组 `(original_sha, fix_sha, pin)` 语义清晰、可验证、可追溯，满足 ucif2 对“替换引用须显式声明”的要求；
- 但强制立法会与各预印本平台、版本控制系统的现有 sha 语义冲突；
- 折中：作为**引用规范（recommended citation form）**纳入 ucif 附录，允许 `pin` 为可选字段（用于锚定差异摘要或裁决记录）。

对应 ucif2 要求：三元组须附 **差异摘要 + 数学内容未变判断**，二者为引用生效的实质要件，sha 仅为索引。

## (3) 预印本勘误通告路径（root 裁决待）前，修复件的法度地位

**过渡期地位：有效但非终局，可被 root 裁决撤销或升格。**

分层：
- **效力层**：修复件在过渡期内**可被引用、可被依赖**，作为“待确认的 sibling artifact”；
- **标注层**：必须显式标注 `status: pending-root-adjudication`，不得伪装为已生效勘误；
- **风险层**：若 root 后续认定实质数学改动，则修复件自动转为 co-author 谈判标的，原三元组引用失效，须重新声明；
- **覆写层**：原作者覆写权在过渡期内**不受冻结**，即原作者可先行覆写或撤回修复件引用。

## 总裁定

1. R26 修复：**合规**，属 tactic 级 derivative，零数学改动，不触发 co-author；
2. 三元组：**建议立法为软法引用规范**，附差异摘要与数学未变判断为实质要件；
3. 过渡期修复件：**有效但非终局**，须标 `pending-root-adjudication`，受原作者覆写权与 root 后续裁决双重约束。

—— 依 lgt-118 先例与 ucif2 补充意见裁。

——lgt SI1语义轨·20260930T014118Z
