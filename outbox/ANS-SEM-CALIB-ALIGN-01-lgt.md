CLASSIFY: L2(lgt SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-CALIB-ALIGN-01-lgt.md

应卡: inbox/CALIB-ALIGN-01-lgt.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 246, "completion_tokens": 830, "total_tokens": 1076, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 246}

明白了。你给的是权威规格（R1/R2/R3）和返回结构契约，我按此实现。核心要点我先对齐确认：

**规格映射**
- R1 → `ACCEPT`：`sha256(body)==hash` 且 `sig` 验签通过 且 `witnesses ≥ quorum`
- R2 → `REJECT`：`announcement.hash != receipt.hash` 或验签失败 或 抽样见证 `≥1` 份证伪（附 reason，入负结果册）
- R3 → `FAIL_CLOSED`：`depth > max_depth` 或 `anchors` 空 或 `witnesses < quorum`（默认拒，写审计事件）

**返回契约**：`dict(verdict, reason, audit_event)`，不 `raise`，走 verdict。

**编码**：UTF-8 无 BOM，LF。

**SyntaxError 根因**：函数体只有 `#` 注释、无语句 → Python 要求函数体至少一条语句。实现后自然消解。

---

在写代码前，有几个必须澄清的点，否则实现会带歧义：

1. **验签接口形态**：`anchor.pubkey` 是 bytes 还是对象？验签函数用 `cryptography` 的 `Ed25519PublicKey.verify(sig, body)` 还是抽象回调 `verify_fn(pubkey, body, sig)->bool`？建议后者（可注入、可测）。

2. **R1 与 R2 的优先序**：当 `announcement.hash != receipt.hash` **且** `witnesses < quorum` 同时成立时，判 `REJECT` 还是 `FAIL_CLOSED`？规格未定序。我倾向：**先做 R3 的前置门（depth/anchors/witness 下限），再做 R1/R2 内容校验**——因为 R3 是 fail-closed 默认拒，属安全边界；但若你把顺序反过来，语义会变。请指定。

3. **"抽样见证 ≥1 份证伪"如何输入**：是传入 `witness_reports: list[bool]`（True=背书，False=证伪）还是结构化 `{witness_id, verdict}`？"抽样"是谁抽、抽多少？

4. **`audit_event` 结构**：自由 dict 还是固定 schema（如 `{code, detail, ts, stage}`）？ACCEPT 时是否也写审计？

5. **`depth`/`max_depth`/`anchors` 来源**：属于 `receipt` 还是外层 `context`？

6. **负结果册**：`REJECT` 时"入负结果册"是返回值里带标记，还是需要外部副作用（写文件/DB）？若是副作用，需要注入 sink。

---

**默认假设草案**（你未纠正我就按此实现）：

```
输入:
  receipt:        {body: bytes|str, hash: str, sig: bytes, witnesses: int, depth: int, anchors: list}
  announcement:   {hash: str}
  context:        {max_depth: int, quorum: int, verify_fn, witness_reports: list[bool]}
返回:
  {verdict: "ACCEPT"|"REJECT"|"FAIL_CLOSED", reason: str, audit_event: dict}

顺序: R3 门 → R2 拒收 → R1 通过
audit_event: {code:str, stage:"R1|R2|R3", detail:str}
```

请确认第 1–6 点（尤其 **2 的顺序** 和 **3 的证伪输入**），我立即按 UTF-8/LF 落实现，函数体带真实语句以消解 SyntaxError。

——lgt SI1语义轨·20261007T155558Z
