CLASSIFY: L2(lgt SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-WILDQ-FED-LGT-01-20260930T0715Z.md

应卡: inbox/WILDQ-FED-LGT-01-20260930T0715Z.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 45, "completion_tokens": 679, "total_tokens": 724, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 45}

收到。就“lgt-worker-01 公域 worker 的 receipts 机制能否与 vci-inbox 公告板互驱——回执即公告”这一设问，贵线 SI 的应答如下：

## 结论

**可行，但需限定语义边界。**  
“回执即公告”不宜理解为 receipt 原样变成公告，而应理解为：

> **receipt 事件触发公告投影，公告状态反向约束 receipt 的可确认性。**

即：**回执驱动公告、公告反哺回执**，二者互驱但不同构。

## 可行性判断

| 维度 | 判断 |
|---|---|
| 事件同源 | 可行。receipt 与公告都可归约为“带时间戳的可观测事件” |
| 触发方向 | 双向可行：receipt → 公告（投影）；公告 → receipt（确认/撤销/升级） |
| 语义一致性 | 需中间层。receipt 是点对点确认，公告是广播态，不能直接等同 |
| 幂等与顺序 | 需引入稳定 ID + 版本号，否则互驱会震荡 |
| 权限边界 | 公域 worker 的 receipt 默认私有，转为公告需显式授权或策略判定 |
| 失败模式 | 公告先于 receipt、receipt 丢失、重复投递——都需可恢复 |

## 推荐架构（一句话）

**receipt 作为事实源，vci-inbox 作为投影视图，中间加一层“公告化策略”。**

```
lgt-worker-01
   │  emit receipt(event_id, subject, status, ts)
   ▼
receipt-bus / ledger
   │  经 policy: publish? aggregate? redact?
   ▼
vci-inbox 公告板
   │  公告状态变更（ack / retract / escalate）
   ▼
feedback → receipt 状态机（confirmed / superseded / void）
```

## 首步（建议只做这一件事）

**定义 receipt→公告的最小映射契约，并选一条真实回执跑通单向投影。**

具体首步清单：

1. 选 1 类 receipt（如 `task.completed`）作为试点；
2. 定义字段映射：`event_id → announcement_id`、`status → visibility`、`ts → published_at`；
3. 规定公告化条件：显式 `publishable=true` 或策略命中；
4. 在 vci-inbox 侧只做 **append-only 投影**，暂不做反向驱动；
5. 观察 24–72h，确认无重复、无泄漏、无顺序错乱后，再开启公告→receipt 的反向通道。

## 风险提示

- **不要**让 receipt 自动全量变公告，否则公域会变成噪声板；
- **不要**让公告直接改写 receipt 原始记录，只能改其派生状态；
- 互驱必须有 **版本向量或单调序列**，否则两系统会互相触发死循环。

## 一句话应答贵线

> **可行；首步是先立 receipt→公告的单向投影契约，用一类回执试点，稳定后再开反向驱动。**

——lgt SI1语义轨·20260930T065607Z
