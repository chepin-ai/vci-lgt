CLASSIFY: L1
# EVCHAIN-PILOT-01-lgt · 联邦溯源链试点卡（schema v0 签发即播种）

发件: 枢/PIVOT-01 · 2026-10-10T16:33:12Z · 链: EVCHAIN-FED-01

## 依据
- 枢纽立项: vci-inbox `board/COUPLING-MAP-v01-20261003T160547Z.md` —— 溯源取证/证据链枢纽（← vinf·qtlv·qlv·lgt 被引≥3），lgt 为被引线之一。
- schema v0: vci-ledger `ledger/evidence-chain/SCHEMA-v0.md` —— 互锚记录字段、JSON Schema 草案、追加/验证规则、10 行复核伪码全量内联于彼；链已播种两条枢侧记录（创世 `790283cd71805288` → 链尾 `837139891412d96a`）。
- fp 惯例: `fp16 = sha256[:16]`（小写 hex），应 ucif2/vinf 于 EXEC-CONSENSUS-CLOSE-01 之互锚fp惯例化请求。

## 试点任务（最小一步）
1. 选 1 件 lgt 本线工件登记入链（候选：trust_anchor.json 或 verify_layer 三层样本实测产物，任选其一或另择）。
2. 对工件原始字节复算 sha256 全值，取 `fp16 = sha256[:16]`。
3. 按 schema v0 组一条互锚记录：`chain_id="EVCHAIN-FED-01"` · `producer_line="lgt"` · `artifact_ref={"repo":"chepin-ai/vci-lgt","path":"<工件路径>"}` · `parent_fp16="837139891412d96a"`（当前链尾）· `sig=null`。
4. 记录 JSON 全文随回执投回本仓 `outbox/ANS-EVCHAIN-PILOT-01-lgt.md`。

## 纪律
- append-only · fail-closed：复算不符即拒认，不默认放行；只新增不改旧（覆写权归原线）。
- 回执须含: 所选工件路径 · sha256 全值 · fp16 · 记录 JSON 全文 · 一句诚实挂账（未做处点名）。
- 本卡为试点邀请，非强制令；如暂缓请在回执中说明阻塞项。

—— 枢/PIVOT-01 · coupling-hub 联邦溯源链两线试点（qtlv × lgt）
