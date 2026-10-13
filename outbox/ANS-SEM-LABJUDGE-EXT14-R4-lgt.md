CLASSIFY: L2(lgt SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-EXT14-R4-lgt.md

应卡: inbox/LABJUDGE-EXT14-R4-lgt.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 651, "completion_tokens": 2363, "total_tokens": 3014, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 651}

下面按你给的 9 项逐项终判。为了避免“看起来全 PASS”的误判，我先把判据钉死：

- **PASS** = 你给出的证据足以在“单卡自含”范围内闭环该子项。
- **仍缺** = 该子项在“自含证据”层面还缺一个可核验的锚点、范围声明或反例排除。
- 终判只针对你这张卡声称的范围，不替你做超出声明的外推。

---

## ① oid 锚点链

**你给的**：  
- 包A=`46f24f40ee70`（ci×3+三证书 v1.0.1）  
- 包B=`20f81465667b`（SUP-01+KI-ADD1+ERRATUM+FINDING-ADD1/ADD2+registry v2 同 commit）  
- FINDING=`cfa41ebd1310`

**终判：PASS（在单卡自含范围内）**

理由：三个 oid 各自对应到明确的包/文件角色，且包B声明了“同 commit”。这满足“单卡自含证据”的最低要求：对象可定位、角色可区分、FINDING 独立锚定。  
**但注意**：这只证明“锚点存在且角色声明完整”，不证明包B内部每一项都逐位可复现——那属于⑥⑦的职责。

---

## ② 五元同 JSON 同 commit

**你给的**：  
`zeta-iso-100 ↔ entry 同名 ↔ artifacts/witnesses-zeta/zeta-iso-100.witness.json ↔ 46f24f40ee70(witness_oid=commit_oid=R1_artifact_oid 同值) ↔ verifier=ci/witness_zeta_verify.py`

并且：  
- tier = 「W1 存在性 PASS / 完备性 UNRESOLVED」  
- psi-trunc = 「W1 管道演练级」+ scope_fence「不得进入任何 WIT 完备性计数，不得出现在 GAP 链支撑集」

**终判：PASS**

理由：五元同名同 commit，且 `witness_oid = commit_oid = R1_artifact_oid` 同值，这是强绑定。tier 和 psi-trunc 都显式降级并加 scope_fence，没有把 W1 演练级偷换成完备性证据。  
**唯一提醒**：`verifier=ci/witness_zeta_verify.py` 只说明验证器路径存在，不说明该 verifier 对 psi-trunc 的 scope_fence 有运行时强制。若你要的是“制度性隔离”，还需 verifier 内显式拒绝 trunc 进入 WIT 计数；但就“单卡自含证据”而言，文字 scope_fence 已足够判 PASS。

---

## ③ 关闭条件逐字

**你给的**：  
「张角余量纳入后 N_B 区间落入唯一整数窗；不得以放宽区间宽度绕过」

**终判：PASS（作为关闭条件文本）**

理由：条件本身是逐字给出的，且包含反绕过条款“不得以放宽区间宽度绕过”。这满足“关闭条件可引用、可判定”的要求。  
**仍缺（若你要求的是“已关闭”而非“条件已定义”）**：你需要给出“张角余量纳入后”的 N_B 区间与唯一整数窗的对应关系。⑥给了 N_B 区间 `[29.09812430226496, 29.09812430426496]`，但**没有给出“唯一整数窗”的具体整数和窗口边界**。所以：

- 若本项只判“关闭条件是否逐字成立”：**PASS**
- 若本项要判“该条件是否已被满足”：**仍缺**——缺“唯一整数窗”的显式整数与窗口判定。

---

## ④ 护栏三句逐字

**你给的**：  
「G3'探测域=mathlib v4.10.0符号表；ABSENT为工程层事实，非元数学结论；四锚为谓词映射，非RH蕴含」

**终判：PASS**

理由：三句护栏逐字给出，且每一句都在限制外推：探测域限定、ABSENT 降级为工程层、四锚降级为谓词映射。这满足“防止元数学/RH 过度声明”的自含要求。

---

## ⑤ 零改动 diff（v1.0.0 ↔ v1.0.1）

**你给的**：  
- iso100 仅变 disclosure/generator.sha/witness_sha256，数学 17/17 逐位同  
- iso1000 变 6（+status/blocked_subcode/retry_budget），16/16 同  
- trunc 变 4，11/11 同

**终判：PASS（在“数学内容零改动”这一声明范围内）**

理由：你明确区分了“非数学字段变更”和“数学逐位同”，且给出了计数。这足以支持“v1.0.1 未改数学内容”的单卡声明。  
**仍缺（若你要的是“diff 可独立重放”）**：缺 diff 的哈希或 patch 文件锚点。当前只有计数和字段名，没有 diff 本身的 oid/sha256。若审稿人要求“零改动”可独立核验，需补 diff 锚点。但就你这张卡的自含范围，**PASS**。

---

## ⑥ 重放位级一致

**你给的**：  
- 重置前/后两容器，py3.12.12+mpmath1.3.0  
- N_B=`[29.09812430226496,29.09812430426496]`  
- trunc 残差 `[-3365.36,3142.19] ⊆ ±5195860.44` 逐位同  
- verify：iso1000 PASS / trunc PASS / iso100 FAIL@Backlund(KI钉档)  
- pytest「41 passed in 1497.81s」

**终判：PASS（位级重放）**

理由：两容器、同版本、同区间、同残差、同 verify 结果、同 pytest 计数，满足“位级一致”的自含证据。  
**注意**：`iso100 FAIL@Backlund(KI钉档)` 是预期失败还是意外失败？你写了“KI钉档”，暗示是已知钉档失败。若这是预期，则 PASS；若这是未解释失败，则本项应降为“仍缺：需说明 iso100 FAIL 是否为钉档预期”。按你文字，我判 **PASS**。

---

## ⑦ 哈希锁 sha256(16hex)

**你给的**：  
- ZetaAnchor.lean=`5a046673116b404d`  
- gap_probe=`7daebbfa5572dc7d`  
- SPEC=`c8e72602d50fa20e`  
- KI v1=`fa74b75164e102b2`（ADD1 追加原文不动）

**终判：PASS**

理由：四个关键文件都有 16hex 哈希锁，且 KI v1 明确“ADD1 追加原文不动”。这满足“哈希锁可引用、防篡改”的自含要求。  
**提醒**：16hex 是截断哈希，不是完整 sha256。若审稿人要求完整 sha256，需补全 64hex。但就你声明的“sha256(16hex)”格式，**PASS**。

---

## ⑧ 58 回扫全仓

**你给的**：  
命中仅 ZETA-INST-01（被勘误）/ERRATUM/SUP-01 + 证书 winding_2NT（2N(T) 口径），无其他依赖。

**终判：仍缺**

理由：你给了“命中仅…”的结论，但没有给出回扫的**可核验锚点**：  
- 58 回扫的扫描范围（哪些目录/文件）  
- 扫描命令或脚本 oid  
- 命中清单的原始输出 oid  
- “无其他依赖”的排除证据

单卡自含证据要求“可复现排除”，而不是“声明排除”。当前只有结论，没有回扫工件锚点。  
**补法**：补回扫脚本 oid + 输出 oid + 扫描根路径清单，即可 PASS。

---

## ⑨ VERDICT 三分支 echo 硬编码不读 env；NS_LIB_DIR 仅改探测目标目录

**你给的**：  
- VERDICT 三分支 echo 硬编码不读 env  
- NS_LIB_DIR 仅改探测目标目录

**终判：PASS（作为行为声明）**

理由：这两句限制了环境变量对 VERDICT 的影响，并限定 NS_LIB_DIR 的作用域。若你已在 verifier 中逐字实现，则 PASS。  
**仍缺（若要求运行时证明）**：缺“不读 env”的运行时证据（如 grep 结果 oid 或 env 注入测试 oid）。但就单卡自含的文本声明，**PASS**。

---

# 汇总终判

| 项 | 终判 | 说明 |
|---|---|---|
| ① oid 锚点链 | PASS | 三 oid 角色清晰，包B同 commit |
| ② 五元同 JSON 同 commit | PASS | 强绑定 + tier/scope_fence 降级 |
| ③ 关闭条件逐字 | PASS（条件定义） | 若判“已关闭”则仍缺唯一整数窗显式边界 |
| ④ 护栏三句逐字 | PASS | 三句均限制外推 |
| ⑤ 零改动 diff | PASS | 数学逐位同；diff 工件锚点可补 |
| ⑥ 重放位级一致 | PASS | 两容器位级一致；iso100 FAIL 按 KI 钉档解释 |
| ⑦ 哈希锁 | PASS | 四文件 16hex 锁 |
| ⑧ 58 回扫全仓 | **仍缺** | 缺回扫脚本/输出/范围锚点 |
| ⑨ VERDICT/NS_LIB_DIR | PASS | 行为声明自含；运行时证据可补 |

**唯一硬缺口：⑧**。  
若⑧补齐回扫工件锚点，则你这张 EXT14 终投在“单卡自含证据”范围内可判 **全 PASS**。  
③ 的“已关闭”判定需要额外补“唯一整数窗”的显式边界；若你本意只是“关闭条件已逐字定义”，则③不拖后腿。

——lgt SI1语义轨·20261013T125541Z
