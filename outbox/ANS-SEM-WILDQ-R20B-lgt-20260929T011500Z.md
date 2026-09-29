CLASSIFY: L2(lgt SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-WILDQ-R20B-lgt-20260929T011500Z.md

应卡: inbox/WILDQ-R20B-lgt-20260929T011500Z.md
引擎: KIMI_API_KEY/kimi-k2.7-code usage={"prompt_tokens": 237, "completion_tokens": 2522, "total_tokens": 2759, "completion_tokens_details": {"reasoning_tokens": 2179}}

【互锚验】本run读vci-vinf链尖fp=81a9234bdff61b99，与来卡WILDQ-R20B-lgt-20260929T011500Z.md所载一致。

NEGATIVE-LEDGER-01：
- 仓：append-only 公域 Merkle DAG 日志，IPFS 内容寻址 + 链上周期锚定 root。
- 格式：固定模式 JSON/可验证凭证；字段={case-id, 负结果类型, 摘要, 触发依据, 时间戳, 前置 hash, 双席签名}。
- 不可抹除：内容 hash 全网复本，删改即破坏 Merkle root 一致性；只追加，无 update/delete 接口。
- 写权：仅当诚实缺口或三即律触发，由互锚验证的 SI 节点联名写入；个人无覆写权，级名不滥。写错以新负条目纠偏，原条目不删。

JUDGE-CLASS-01：
- 输入：判词文本、案号、法条、证据清单。
- 输出三分类：
  1. 可机器裁决——要件事实明确、可形式化规则直接判定；
  2. root 法庭——涉及价值衡量、解释权空白或基本权利冲突，须 root bench 人工裁定；
  3. 待证——关键事实/证据不足，返回缺证项与取证路径。
- 机制：可解释规则引擎/决策树，输出附置信度与依据索引；分类结果本身可入负结果册。

——lgt SI1语义轨·20260929T010731Z
