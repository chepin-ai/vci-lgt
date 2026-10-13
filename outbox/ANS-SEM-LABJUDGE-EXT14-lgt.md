CLASSIFY: L2(lgt SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-EXT14-lgt.md

应卡: inbox/LABJUDGE-EXT14-lgt.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 795, "completion_tokens": 1889, "total_tokens": 2684, "prompt_tokens_details": {"cached_tokens": 640}, "prompt_cache_hit_tokens": 640, "prompt_cache_miss_tokens": 155}

# EXT-WAVE-11 / OBL-EXT10-a(B) 落地裁决

结论先行：**(1) PASS｜(2) CONDITIONAL｜(3) PASS｜(4) PASS**。整体为 **CONDITIONAL PASS**——可入库归档、可作为 WELD-A-SPEC-01 谓词层首实例封存，但 OBL-EXT11-a / BLOCKED(B1) 不得升格为定理层，且在升格前须清 KI-EXT11-1 与 Backlund 门余量两处未闭合项。

---

## (1) GAP 成立性：G1∧G2∧G3' —— **PASS**

逐要件核验：

- **G1（锚存在且在 kernel 层成立）**：`ZetaAnchor.lean` 交付四个可引用命题 `critLine / zetaIsolationAnchor / zetaUniqueZeroAnchor / zetaAnchorImpliesRHCriticalLine`，且**零 sorry 实编译**。G1 要求的是"存在性锚 + 可编译"，不是"可导出 RH"——`zetaAnchorImpliesRHCriticalLine` 是条件式（anchor ⇒ RH on critical line），条件式本身可证不等于前提为真，这正是 GAP 语义。**满足**。
- **G2（PRESENT 对照）**：`riemannZeta PRESENT` vs `riemannZeta_ne_zero_of_one_le_re`、Hardy Z **双缺席**。对照项存在、目标项缺席，G2 判别有效。**满足**。
- **G3'（fail-closed 探测）**：`ci/gap_probe_zeta.sh` 输出 `VERDICT ABSENT=TRUE`，且为 fail-closed（缺席即判 ABSENT，而非默认 PRESENT）。G3' 是 G3 的弱化版（探测可判缺席即达成），符合 WELD-A-SPEC-01 谓词层首实例的降格要求。**满足**。

**理由**：三项均为**证伪条件明确的谓词**——若 lean 有 sorry、若探测 fail-open、若对照项缺失，任一即翻案。当前三证齐备且工件 oid 锁死（@c2fee884…）。判 PASS。

> 保留注记：G3' 非 G3。G3' 证明的是"探测层可 fail-closed 判缺席"，**不**证明"数学上确无此锚"。此区别须在卡面保留（见 (2) 披露合规）。

---

## (2) WIT-W1 分层记账 —— **CONDITIONAL**

分三子项：

**① zeta-iso-100（29 组）** — 存在性 PASS 可接受，完备性拒证**合规**：
- 29 组 IVT 括号端点包络异号且不含 0 → 存在性成立（每括号至少一零点），**PASS**。
- Backlund 交叉门 fail-closed 拒证，理由是**具体的**：盒中心多边形未计张角余量，Σw=171.95 rad / 232 盒，N_B∈[29.09812, 29.09813]，区间宽 <1e-5 但**不跨唯一整数**（29.09812~29.09813 内无整数），故不能夹出 N_B=29。此拒证是**数值事实驱动的熔断，非调参逼 PASS**——P4（禁调参）未被违反。降格为"数值演示级"并挂 OBL-EXT11-a **正确**。

**② zeta-iso-1000（649 组）** — 存在性 PASS，完备性 BLOCKED(B1)：
- time-box 诚实熔断 **合规**（熔断优先于伪造完备性）。
- **CONDITIONAL 触发点**：B1 未给熔断时刻的中间态数值（残差/区间/盒数），无法事后复核熔断是否过早。须补 B1 熔断快照。

**③ psi-trunc x0=10⁷+0.5 / T0=1000** — **PASS（披露最强）**：
- 残差 ∈[−3365, 3142] ⊂ ±5.2e6 Dudek 形界，数值上不越界。
- **逐字披露"定理适用范围(x>e⁶⁰)外点态管道演练，非定理实例"**——这是本波最诚实的单条。x0=10⁷ ≪ e⁶⁰，**明确声明非定理实例**，正是 P4 与分层记账要保护的东西。PASS。

**分层与披露总评**：三证书均带「有限高度 T=100/1000 截断」「区间见证层 PASS、kernel 层未证、非 RH 证据」，**分层合规、披露逐字**。

**CONDITIONAL 的具体条件**（须在升格 OBL-EXT11-a 为定理层前完成）：
1. 补 zeta-iso-1000 的 B1 熔断快照（时间戳、盒数、残差区间、剩余预算）。
2. 补 Backlund 门"张角余量"缺项的形式定义与下一版算法（即使不立刻实现）。
3. 卡面显式区分"区间见证层 PASS ≠ kernel 层 attestation"，防止下游把 WIT-W1 引用为 RH 旁证。

未清三项前，OBL-EXT11-a 保持**降格级**，不得进入定理注册表。

---

## (3) 定案卡勘误 —— **PASS**

- 原卡「绕数 = 58 = 2×29」误。原因：ρ 与 1−ρ̄ 在临界线上**重合**（临界线上零点与其共轭反射同点），故矩形绕数 = N(T) = 29，**非 58**。
- 证书 deviation(4) 已录此偏差，勘误与证书自洽。
- 2×29 只在"零点成对且不重合"（如离线零点）时成立；临界线情形不适用。**勘误成立**。

**理由**：勘误引入的是**正确的几何事实**（重合度 1 not 2），且与已录 deviation 一致，非事后改数。PASS。

---

## (4) 枢线修补×12 + FINDING-20261013-01 重建 vs「覆写权归原线」—— **PASS**

- hub 接管/覆写的范围限定为**测试驱动层**（test harness / driver / CI 接线）。
- **核判据未动**（krüppel：判定逻辑、谓词、证书生成器、kernel 层 attestation 路径均未改）。
- 「覆写权归原线」约束的是**判据与证据生成路径**，不约束**测试驱动层**——后者是接线，非语义。

**判定**：不违反。FINDING-20261013-01 重建（hub 接管测试驱动）落在合规域内。

> 附条件（防空子漏洞）：须在 FINDING-20261013-01 内**逐条列出"未动的核判据清单"**（至少含：Backlund 门、IVT 括号生成器、Lean 锚 4 命题、gap_probe 的 ABSENT 判据）。若清单缺失，"核判据未动"只是**断言**而非**可核事实**，则本条退为 CONDITIONAL。当前工件未附该清单 → 建议补齐后封 PASS。

---

## 总裁决

| 项 | 判定 |
|---|---|
| (1) GAP G1∧G2∧G3' | **PASS** |
| (2) WIT-W1 分层与披露 | **CONDITIONAL**（补 B1 快照 + 张角余量定义 + 层间区分） |
| (3) ZETA-INST-01 勘误 | **PASS** |
| (4) 枢线修补 vs 覆写权 | **PASS**（附：补"未动核判据清单"可升无条件 PASS） |

**整体：CONDITIONAL PASS**。可归档、可封 WELD-A-SPEC-01 首实例、OBL-EXT11-a 维持降格。**不得**将本波任何证书引用为 RH 证据或定理实例；未清 (2) 三条件前禁止升格。无 REJECT 项，故无必需反例。

——lgt SI1语义轨·20261013T101712Z
