CLASSIFY: L2(lgt SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-T03R-lgt-SEG1.md

应卡: inbox/LABJUDGE-T03R-lgt-SEG1.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 270, "completion_tokens": 820, "total_tokens": 1090, "prompt_tokens_details": {"cached_tokens": 128}, "prompt_cache_hit_tokens": 128, "prompt_cache_miss_tokens": 142}

SEG 1/7 已接收。  
聚合ID：**OMNIBUS-01-T03R-20261009**  
前段指纹：**GENESIS**  
本段指纹：**9e20d96c**  
状态：**SEG头确认，按“全量清账波板文逐段移送”继续。**

下面把你这段 **§1 POLICY-01存量锚盘点** 按“硬截止第2波次到期”做结构化归并，不改判据、不升格结论：

---

## §1 POLICY-01 存量锚盘点

### 锚1：circulant 闭式锚
**处置：原临时锚 → 升认证锚**  
**认证号：CERT-CIRC-01**

**闭式：**
- \(f^* = \mathbf{0}\) 向量  
- \(g^* = (-\varepsilon \ln k - \varepsilon \,\mathrm{lse}(-c/\varepsilon)) \cdot \mathbf{1}\)

其中：
- \(\mathrm{lse}(\cdot)\)：log-sum-exp
- \(\mathbf{1}\)：全 1 向量

**验证覆盖：**
- \(\varepsilon \in \{1.0,\ 0.5,\ 0.2\}\)
- \(k \in \{6,\ 10\}\)
- 种子 \(\in \{20261009,\ 777\}\)

**结果：**
- Krawczyk 严格内包：**全过**
- K 宽：\(\le 1.78\times 10^{-14}\)
- 残差：\(\le 3.5\times 10^{-16}\)
- 负面对照：\(g^* + 1\times 10^{-9}\) **拒证**

**认证结论：**
> CERT-CIRC-01 成立。  
> circulant 闭式锚由临时锚升为认证锚。  
> 判据为 Krawczyk 严格内包，覆盖指定 \(\varepsilon\)、\(k\)、种子组合；负面对照拒绝。

---

### 锚2：f80 锚
**处置：f80 锚 → 认证锚（相对精度型）**

**认证依据：**
- F-X1 外向区间包含证书
- T4 E 层：30/30 含 f80 真值

**声明：**
- 非绝对真值
- 系 x87 80 位 63 尾数高精度参照
- 判据：\(\mathrm{lo} \le t_{80} \le \mathrm{hi}\)，按位

**认证结论：**
> f80 锚升为认证锚，但认证类型为相对精度型。  
> 其有效性来自 F-X1 外向区间包含证书与 T4 E 层 30/30 覆盖。  
> 不声明为绝对真值，仅声明为 x87 80 位 63 尾数高精度参照，并按位满足区间包含判据。

---

## 当前 SEG 1/7 小结

| 锚 | 原状态 | 新状态 | 认证号/类型 | 关键判据 | 结果 |
|---|---|---|---|---|---|
| 锚1 circulant 闭式锚 | 临时锚 | 认证锚 | CERT-CIRC-01 | Krawczyk 严格内包 | 全过，K宽≤1.78e-14，残差≤3.5e-16，负面对照拒证 |
| 锚2 f80 锚 | f80 锚 | 认证锚 | 相对精度型 | F-X1 + T4 E层30/30 + 按位 lo≤t80≤hi | 成立，非绝对真值 |

---

**SEG 1/7 移送状态：已归并，等待下一段。**  
下一段请继续发送。

——lgt SI1语义轨·20261009T091200Z
