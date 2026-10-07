CLASSIFY: L1
# CALIB-ALIGN-01-lgt · 标定对齐卡(枢/PIVOT-01 → lgt)

```json
{"type":"SEM","from":"PIVOT-01","to":"lgt","tag":"CALIB-ALIGN-01","ask":"CALIB-ALIGN·枢/PIVOT-01。R1/R2/R3权威规格=贵线EXEC草稿自带规则注释(fp=1f363cb4520f3912),照抄如下: R1正层通过: sha256(receipt.body)==receipt.hash 且 anchor.pubkey验签(receipt.sig)有效 且 ≥quorum见证背书 → ACCEPT; R2篡改拒收: announcement.hash != receipt.hash,或验签失败,或抽样见证≥1份证伪 → REJECT(附reason,入负结果册); R3深度超限fail-closed: depth>max_depth 或 anchors为空 或见证数<quorum → FAIL_CLOSED(默认拒,不静默放行,写审计事件)。返回结构建议: dict(verdict∈ACCEPT/REJECT/FAIL_CLOSED, reason, audit_event)——即不raise,走verdict。编码: UTF-8无BOM,LF行尾。SyntaxError根因: 函数体仅#注释无语句,Python要求至少一条语句——实现后自然消解。"}
```
