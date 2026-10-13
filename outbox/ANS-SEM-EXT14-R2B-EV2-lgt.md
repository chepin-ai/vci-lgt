CLASSIFY: L2(lgt SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-EXT14-R2B-EV2-lgt.md

应卡: inbox/EXT14-R2B-EV2-lgt.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 443, "completion_tokens": 1491, "total_tokens": 1934, "prompt_tokens_details": {"cached_tokens": 256}, "prompt_cache_hit_tokens": 256, "prompt_cache_miss_tokens": 187}

这份证据包 2/3 延续了 1/3 的字段级比对思路，把 v1.0.0(@2053f49c) → v1.0.1（包A）的差异收敛到了一个**可审计的最小集**。以下是关键点归档与判读：

## 一、字段级 diff 判读

**核心结论：44 个数学字段零改动，全部变更都是元数据/披露/见证类字段。**

| 样本 | 变更字段数 | 数学字段 | 变更性质 |
|---|---|---|---|
| iso100 | 3 | 17/17 同 | disclosure / generator.sha256 / witness_sha256 |
| iso1000 | 6 | 16/16 同 | +completeness/status、blocked_subcode、retry_budget（+上面类） |
| psi-trunc | 4 | 11/11 同 | disclosure / zero_source.sha256 / generator.sha256 / witness_sha256 |

三点值得记录：

1. **数学字段逐位同（bit-identical）**，不是“等价”而是“位同”——这是比容差比对更强的断言，排除了浮点重排、编译器优化、mpmath 版本漂移等一切潜在扰动。
2. **iso1000 的 6 字段变化是唯一带“语义增量”的**：completeness/status、blocked_subcode、retry_budget 属于**结果状态元数据**，不是数值结果。也就是说 iso1000 的“结论变了”是披露层/状态层变了，不是数学层变了。这一点需要在 3/3 里和 iso1000 的 verify 输出对齐确认（包A 实跑显示 iso1000 ok=true，说明新状态元数据与旧数学结论一致）。
3. **sha256 三处齐变（generator + witness + zero_source）**符合“产物自指哈希”的传递性：任何一处上游字节变动都会穿透到 witness_sha256。这正是设计意图——哈希链把非数学字段的改动也钉死了。

## 二、跨环境重放判读

**envA（重置前容器#1）↔ envB（重置后容器#2），python3.12.12 + mpmath1.3.0 + Linux5.10 lifsea，x86_64。**

- iso100 Backlund 拒证区间 N_B = [29.09812430226496, 29.09812430426496]，两环境逐位相同；
- trunc 残差 r ∈ [−3365.36, 3142.19] ⊆ Dudek 界 ±5195860.44，两环境逐位相同。

判读：

- **“逐位相同”是本次重放的最强断言**，等价于跨容器的**字节级可复现性（bit-reproducibility）**。这排除了：FPU 微码差异、线程调度对归约顺序的影响、mpmath 内部缓存态差异、locale/时区泄漏进计算路径。
- N_B 区间宽度 = 2.0e-9，仍不含唯一整数 → 拒证结论**在两环境同时成立**，说明 KI-EXT11-1 的钉档行为不是单环境偶发，而是可复现的确定性行为。
- trunc 残差落在 Dudek 界内且两环境同值 → **零源残差是环境无关的**，不是重置后被“修好”了。

## 三、包A 核验判读（envB 实跑）

```
verify iso1000  ok=true
verify trunc    ok=true
verify iso100   ok=false, failed 唯一项 = Backlund 异常「N_B 区间不含唯一整数——拒证」
pytest 尾行: 41 passed in 1497.81s (0:24:57)
```

- **ok=false 的 iso100 是设计内行为**，不是回归：failed 集合大小=1，且唯一项就是 KI-EXT11-1 钉档的 Backlund 拒证。这与上一节“两环境 N_B 逐位相同”形成闭环——**拒证是可重放的确定性拒证**。
- **41 passed / 24:57**：pytest 全绿，耗时约 25 分钟，属于可接受的资源包级别。若 3/3 里有 per-test 时间拆解，可用来定位是否某条 ζ 相关用例占据了主时长。

## 四、双跑闸判读

三证书重签时**进程内同代码连跑两次，字节级一致**，run-log 落在 `包A artifacts/witnesses-zeta/run-log-sup01.json`。

- 这是**进程内确定性**证据，与第二节的**跨容器确定性**互补：一个排除了“同进程内状态污染”，另一个排除了“容器环境漂移”。
- 两者联合起来，把“数学字段为什么能逐位相同”的因果解释逼到唯一路径：**计算路径本身是确定的，非确定性只存在于披露/元数据层**。

## 五、与 1/3、3/3 的衔接点

- **对 1/3**：1/3 里若已有 v1.0.0 的字段清单与哈希，本节可直接套用“3/6/4 字段变更 + 44 数学字段零改动”作为差异摘要。
- **对 3/3**：需要核验三件事——
  1. iso1000 的 `completeness/status`、`blocked_subcode`、`retry_budget` 新值是否与 ok=true 一致（即“状态变了但结论没变”）；
  2. `witness_sha256` / `generator.sha256` / `zero_source.sha256` 三处 sha 是否在 v1.0.1 内部自洽（哈希链闭合）；
  3. run-log-sup01.json 的双跑记录是否含**时间戳外的全字节比对**（只排除时间戳字段，还是全字节含时间戳？需明确）。

## 六、可直接入档的三条结论

1. **数学不变量已建立**：44 个数学字段跨 3 样本、跨 2 版本、跨 2 环境逐位同。
2. **变更面已收敛**：全部 diff 落在 disclosure / provenance / witness_sha256 / 状态元数据，无一进入计算路径。
3. **拒证行为已钉档**：iso100 Backlund ok=false 是 KI-EXT11-1 设计内行为，可重放、可解释、唯一项。

如果需要，我可以把上面这套判读整理成**审计员视角的一页式 attestation**（含字段计数、环境指纹、哈希链闭合点、open items），作为 3/3 的封面页。

——lgt SI1语义轨·20261013T125541Z
