CLASSIFY: L2(lgt SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-WILDQ-EXEC-LGT-01.md

应卡: inbox/WILDQ-EXEC-LGT-01.md
引擎: KIMI_API_KEY/kimi-k3 usage={"prompt_tokens": 342, "completion_tokens": 1493, "total_tokens": 1835, "completion_tokens_details": {"reasoning_tokens": 883}, "prompt_tokens_details": {"cache_write_tokens": 256}}

【互锚验】本run所收链尖fp=81a9234bdff61b99(源:TIP-349-81a9234bdff61b99.json)。两点诚实缺口:①本人未亲读该json,fp系转述;②来卡WILDQ-EXEC-LGT-01.md未附fp,无法比对——不作一致声明,记缺口,待补验。

## v1交付物(骨架+三段核心规则+判据段)

**接口定义**
```python
def verify_layer(receipt: dict, announcement: dict, depth: int,
                 anchors: list, witnesses: list, quorum: int = 2,
                 max_depth: int = 3) -> dict:
    # 返回 {"verdict": ACCEPT|REJECT|FAIL_CLOSED, "reason": str, "fp": sha256}
```

**三段核心规则**
```python
# R1 正层通过: sha256(receipt.body)==receipt.hash 且
#    anchor.pubkey验签(receipt.sig)有效 且 ≥quorum见证背书 → ACCEPT
# R2 篡改拒收: announcement.hash != receipt.hash,或验签失败,
#    或抽样见证中≥1份证伪 → REJECT(附reason,入负结果册)
# R3 深度超限fail-closed: depth > max_depth 或 anchors为空
#    或见证数<quorum → FAIL_CLOSED(默认拒,不静默放行,写审计事件)
```

**trust_anchor.json(最小可信锚)**
```json
{
  "anchor_id": "lgt-si1-root-0",
  "pubkey": "ed25519:BASE64_PLACEHOLDER",
  "chain_tip_fp": "81a9234bdff61b99",
  "witnesses": ["w1", "w2", "w3"],
  "quorum": 2,
  "max_depth": 3,
  "policy": "fail-closed"
}
```

**验证判据段**
- C1 合法三层样本(depth≤3,签验/hash/见证齐)→ACCEPT
- C2 篡改样本(hash不符、签名无效、见证证伪任一)→REJECT
- C3 depth=4或锚缺失→FAIL_CLOSED,无静默放行路径
- C4 所有拒绝路径须落负结果册(级名不滥用:REJECT≠FAIL_CLOSED)

**自验声明**
判据在纸面逻辑上满足C1–C4,但点名未满足处:①互锚亲读未完成,fp一致性未证;②代码未执行,无测试日志,判据未实证;③见证抽样仅接口声明,随机选取逻辑未实现;④pubkey为占位符。以上为负结果,入册待补。

——lgt SI1语义轨·20261003T160745Z
