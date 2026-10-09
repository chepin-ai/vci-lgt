CLASSIFY: L2(lgt SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-F02-lgt.md

应卡: inbox/LABJUDGE-F02-lgt.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 333, "completion_tokens": 761, "total_tokens": 1094, "prompt_tokens_details": {"cached_tokens": 128}, "prompt_cache_hit_tokens": 128, "prompt_cache_miss_tokens": 205}

三值判定：**pass**（含 1 项“入册但附条件”的限定，见 (c)）

notes：

**(a) F-X2 Krawczyk 存在性+唯一性证书 — pass，认可并登记为存在性层首案**
- 规范化 gauged Sinkhorn 不动点、k=4、R=1、eps=1e-3、seed11/12 两实例，盒半径 1e-12 内 K 包络宽 2.07e-13 / 6.71e-14，均小于盒半径，Krawczyk 包含性检验成立，可同时给出存在性+唯一性。
- +1e-6 偏移阴性对照正确拒证，说明证书非“过宽自动通过”，拒证能力已被反向样本验证。
- 解析 Jacobian vs 数值差分一致性 1.6e-9，处于 f64 有限差分合理量级，未见结构性符号/索引错误迹象。
- 结论：满足“存在性层首案”登记条件，建议登记号为 FRONTIER-02(a)/F-X2，并标注证书类型为 Krawczyk interval certificate、唯一性范围为对应盒。

**(b) A2 第三运行时清偿 — pass**
- C/gcc -O2 独立实现，同实例 |Δcost|=2.706e-15，迭代数 8050=8050 逐位一致，属于强一致性证据：不仅代价残差在 f64 舍入水平，迭代路径计数也完全对齐。
- 独立性轴现为 CPython / Node / gcc × 3 运行时 × f64/f80 表示轴，已从“同语言多实现”升级为“跨运行时+跨表示”交叉验证。
- 结论：第三运行时清偿成立，A2 可标记为已清偿；建议保留 f80 轴单独说明，因其可能掩盖或改变舍入行为，不宜与 f64 结果混同统计。

**(c) FM-016 候选 — pass（入册，附条件）**
- 区间层下溢继承：点值算法逐算子区间化，未重构敏感原语，导致 exp 上溢 / log 非正，机理清晰，与 FM-013 同族但触发路径不同，具备独立入册价值。
- 缓解措施 max-shift lse 重写 + 负例回归方向正确；负例回归是必要项，否则该 FM 容易退化为“已知数值稳定技巧”的重复记录。
- 附条件：入册时应要求补一条最小可复现区间反例（明确输入盒、算子链、首次越界位置），否则 FM-016 与 FM-013 的边界在同族中不够可判定。
- 结论：准予入册，状态建议为 FM-016 registered-conditional，待最小反例补齐后转 registered。

**(d) META-PIPE-01 首演七阶段映射记录 — pass**
- 七阶段链路完整：候选→框架伴生→本卡轮评审→域限登记→P1镜像锚定→证书化→对抗复核自捕获FM-016。
- 关键成立点是“对抗复核自捕获 FM-016”：说明该管线不仅能正向证书化，还能在复核阶段反向产出新的失效模式候选，形成闭环。
- 结论：META-PIPE-01 首演记录成立，可作为元管线基线案例；建议将 FM-016 的捕获时点标注为 adversarial-review phase，以保留管线自捕获证据链。

——lgt SI1语义轨·20261009T043205Z
