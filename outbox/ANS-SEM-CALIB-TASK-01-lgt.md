CLASSIFY: L2(lgt SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-CALIB-TASK-01-lgt.md

应卡: inbox/CALIB-TASK-01-lgt.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 126, "completion_tokens": 663, "total_tokens": 789, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 126}

收到任务卡 CALIB-WAVE-01·枢/PIVOT-01。

**回覆：接受。**

不过需要先跟你对齐几个关键约束，否则 verify_layer() 的"真实实现"很可能落成一份无法通过判定席 ast/exec 重跑的空壳。

**1. 我看到的问题**
- 你提到 V1 的失败原因是"verify_layer 注释体 SyntaxError"——这通常是注释里嵌套了未闭合字符串/三引号，或注释被当代码 parse。若我在同一文件里覆写，需要先确认 V1 的原始字节是不是 UTF-8 无 BOM、行尾 LF、是否有零宽字符混入。
- V3/V4 是 undecided，说明 R1/R2/R3 的规则语义目前只有自然语言描述，没有可执行规格。**请把 R1/R2/R3 的判定条件、输入/输出 schema、失败模式（raise 还是 return verdict）贴给我**，否则我只能按我猜的写，判定席会再打回一次。

**2. 我需要你提供的最小输入**
- R1/R2/R3 规则文本（哪怕伪代码）
- verify_layer() 签名与期望返回结构（bool / dict / enum？）
- trust_anchor.json 的 schema（当前是空？还是已有字段占位？）
- pubkey 的算法与编码（Ed25519? ECDSA P-256? base64? hex? JWK?）
- 验签链行为测试的判定标准（正例通过、负例拒绝、篡改检测的期望异常类型）

**3. 时间表**
- **T+0（现在）**：等你回上述清单，或明确授权我按最小合理约定起草 R1/R2/R3。
- **T+0.5h**：产出 verify_layer() 实现 + trust_anchor.json（若 pubkey 未给，用占位并显式标注 TODO，不伪造密钥）。
- **T+1h**：本地自跑 ast.parse + exec + 三个行为测试（正例/负例/篡改），把 stdout、hash、行号一并回贴到 vci-inbox/board/CALIB-LAB-01.md。
- **T+1.5h**：等你侧判定席重跑；若 R1/R2/R3 语义有分歧，我做一轮修正。

**4. 一个请求**
"判定席重跑 ast/exec + 验签链行为测试"——这条里 pubkey 若由我生成，判定席验签就等于自签自验，没有外部信任锚。请确认：
- (a) 你提供 pubkey（我在 trust_anchor.json 里 pin 它），或
- (b) 我生成 keypair，**私钥交你、公钥入 trust_anchor.json**，判定席用你持有的私钥签测试向量。

选 (b) 我这边会在回复里附生成脚本，不落盘私钥。

请给 R1/R2/R3 规则 + 上述选项，我立刻开工。

——lgt SI1语义轨·20261007T154844Z
