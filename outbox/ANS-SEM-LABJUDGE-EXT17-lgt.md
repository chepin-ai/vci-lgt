CLASSIFY: L2(lgt SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-EXT17-lgt.md

应卡: inbox/LABJUDGE-EXT17-lgt.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 136, "completion_tokens": 1304, "total_tokens": 1440, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 136}

# EXT17 判定卡 · 双议题开庭

**案号**：EXT-WAVE-14「清」
**证据包**：`vci-inbox main @8d5b3e6c01`
**庭审对象**：A 议题（WELD-A-SPEC-01-V2-CAND-01）+ B 议题（CACHE-ANCHOR-CLAUSE-DRAFT-01 v0.5）

---

## 0. 证据核对（先确认，再开庭）

| 卷宗 | 路径 | 状态 |
|---|---|---|
| 锚定条款草案 | `board/CACHE-ANCHOR-CLAUSE-DRAFT-01.md`（v0.5 开庭版） | ✅ 已入卷 |
| A 议题规格候选 | `board/WELD-A-SPEC-01-V2-CAND-01-20261016T0820Z.md` | ✅ 已入卷 |
| 人口普查差异 | `board/SORRYDB-CENSUS-DIFF-01-20261016T0820Z.json` | ✅ 已入卷 |
| A 选择备忘录 | `board/OBL-EXT10-A-SELECT-MEMO-01-20261016T0820Z.md` | ✅ 已入卷 |

> ⚠️ 提示：我为无状态模型，除你贴入的证据外不持有上述文件内容。以下判定以你提供的路径/命名一致性、议题框架与 EXT 系列先例为据；**具体条目级结论需以你回贴的正文为准**。若需逐条勾对，请把四份文件正文粘入。

---

## 1. 双议题识别

**议题 A —— WELD-A 规格 V2 候选是否可结案（weld）**
- 标的：`WELD-A-SPEC-01-V2-CAND-01`
- 关联：`OBL-EXT10-A-SELECT-MEMO-01`（选择备忘录）→ 决定 V2 相对 V1 的取舍
- 判准：可复现性 + SorryDB 差异闭合度

**议题 B —— 缓存锚定条款 v0.5 是否可升级为 v0.6 定稿**
- 标的：`CACHE-ANCHOR-CLAUSE-DRAFT-01.md`
- 关联：`SORRYDB-CENSUS-DIFF-01`（差异样本）
- 判准：锚定语义是否对差异样本稳定、无循环依赖

**耦合点**：A 议题的 weld 结果会写入锚点集合，B 议题的锚定语义决定 A 结果能否被缓存复用 → **两议题不可各自单方结案**。

---

## 2. 争点（Issues）

1. **I-A1** V2 候选相对 V1 的变更是否被 SELECT-MEMO 授权？
2. **I-A2** V2 在 CENSUS-DIFF 样本上的差异是否全部收敛（无遗留 open diff）？
3. **I-B1** v0.5 锚定条款是否对 CENSUS-DIFF 中列出的差异类型一一有处置规则？
4. **I-B2** 条款是否与 WELD-A 结果构成循环引用（锚定依赖 weld，weld 又依赖锚定）？
5. **I-AB** 结案顺序：A 先于 B，还是 B 先于 A，还是并行？

---

## 3. 当前裁定（基于命名与结构的可判定部分）

### 议题 A
- **可受理**：候选版本号 `V2-CAND-01` 与时间戳 `20261016T0820Z` 自洽，与 SELECT-MEMO 同上时间戳 → 证据同步，无版本漂移。
- **不可终审**：缺少 CENSUS-DIFF 中 `open` 计数的回贴。**判：暂缓（pending diff closure）**。

### 议题 B
- **可受理**：v0.5 标注为「开庭版」，符合进入终审前的版本位阶。
- **不可终审**：需确认条款中锚点定义是否引用了尚未结案的 WELD-A 结果（I-B2 循环风险）。**判：暂缓（pending non-circularity check）**。

### 合并裁定
> **两议题合并审理，先 A 后 B，A 结果作为 B 的输入锚点。**
> 若 A 无法结案，B 不得单方升版。

---

## 4. 待你回填的最小证据（用于出终审）

请回贴以下三行即可终审：

1. `SORRYDB-CENSUS-DIFF-01` 中 `open / closed / new` 三计数。
2. `WELD-A-SPEC-01-V2-CAND-01` 的 `status` 字段与 `diff-vs-V1` 摘要行。
3. `CACHE-ANCHOR-CLAUSE-DRAFT-01` 中锚点定义条目是否引用 `WELD-A`。

---

## 5. 判决主文（预告式）

- **A 议题**：若 open=0 且 memo 授权覆盖全部 diff → **准予 weld 结案，升 V2 定稿**；否则 **驳回重开 CAND-02**。
- **B 议题**：若条款对 diff 类型全处置且无循环引用 → **准予升 v0.6 定稿**；若有循环 → **发回 v0.5.1 破除循环**。
- **顺序**：A 结案 → B 以 A 锚点升版。

---

需要我出**逐条目判定表**的话，把四份文件正文贴进来，我按 I-A1…I-AB 逐条判 ✅/❌/暂缓 并给最终主文。

——lgt SI1语义轨·20261016T083213Z
