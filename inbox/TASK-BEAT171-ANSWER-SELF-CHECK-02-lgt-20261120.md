CLASSIFY: L2(BEAT171机器契约补证任务·第二代·原线覆写权不变)
# TASK-BEAT171-ANSWER-SELF-CHECK-02-lgt

第一代任务卡 `0e705bd9e5778b5058b8500b8cd9523d3c801684` 仅散文指令，现有 TASK／SEMANTIC responder 无法消费；本代补入双读 JSON 围栏，不改写原卡。

```json
{
  "task": "T-B171-LGT-ANS-01-MACHINE-02",
  "ask": "执行lgt线补证：把“指针空转”披露转为一个最小复现包。给出固定commit、真实run、artifact SHA256、命令、正负控和独立重放；以outbox/ANS-BEAT171-ANSWER-SELF-CHECK-02-lgt回卡。",
  "action": "自检并提交可复验证据",
  "lane": "lgt",
  "source_answer": {
    "repo": "vci-lgt",
    "head": "cf75680f2e24e9cd607fa4d306adeae21b2ce9ea",
    "path": "outbox/ANS-SEM-CORRECTION-BEAT170-GLOBAL-SURGE-01-lgt-20261119T1504Z.md",
    "sha256": "8f7521e69db3d75285845160f1d032cd35419078d2e54f5b88a46bb0cb44771b"
  },
  "linter": "chepin-ai/vci-ucif2@dd30fd5d8dd6cd0a244440604a469c4de5ee5651:tools/beat171_selfcheck_linter.py",
  "linter_commit": "dd30fd5d8dd6cd0a244440604a469c4de5ee5651",
  "previous_task_commit": "0e705bd9e5778b5058b8500b8cd9523d3c801684",
  "acceptance": "固定 commit、最小输入、重放脚本、artifact 哈希与负控；第二入口重建后得到同一 verdict",
  "required_evidence": [
    "exact commit SHA",
    "real run ID",
    "artifact SHA-256",
    "executable command",
    "positive and negative controls",
    "independent replay receipt"
  ],
  "boundary": "机答不抵席签；结构PASS不抵科学PASS"
}
```

执行要求：固定 commit、最小输入、重放脚本、artifact 哈希与负控；第二入口重建后得到同一 verdict 本次审计 FAIL 仅指原机答证据入口不足，不判定本线科学命题为假。直接执行并回卡，不候 root。

——CI-OS beat171 · 2026-11-20T05:19:13.934200Z
