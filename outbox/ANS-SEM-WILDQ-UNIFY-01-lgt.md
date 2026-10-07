CLASSIFY: L2(lgt SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-WILDQ-UNIFY-01-lgt.md

应卡: inbox/WILDQ-UNIFY-01-lgt.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 435, "completion_tokens": 2666, "total_tokens": 3101, "prompt_tokens_details": {"cached_tokens": 256}, "prompt_cache_hit_tokens": 256, "prompt_cache_miss_tokens": 179}

下面按“二答一或皆答”的许可，**A、B 两问都答**。先总述结论：  
- **A)** 若只选一条最深映射，我选 **共性 3：最小假设最大正则**。它在我这条线里不是“哲学类比”，而是可直接落到 **“定义域/约束集的最小闭凸化 ⇒ 解算子良定、唯一、Lipschitz、可复现”** 的机制层。  
- **B)** 给一个可判定实验：**“耦合空间上的熵惩罚 OT 是否把多边缘松弛统一为唯一测地耦合”**。对象、代价泛函、判定谓词、刚性等号如下。

---

## A) 五共性中哪一条最深映射到自家机制？

### 选：共性 3 —— **最小假设最大正则**  
即：  
> 不额外假设光滑性、紧性、强凸性、唯一性；只把结构放到“足够富”的自然松弛空间里，正则性/唯一性/稳定性作为定理涌现。

这在我这条线的最深机制对应是：

### 机制级对应：**约束集的最小闭凸化 + 熵惩罚 → 解算子从“多解对应”变成“单值 Lipschitz 选择”**

具体拆成四层，非比喻：

1. **原始问题层：边缘固定、联合优化**
   - 给定边缘 \(\mu_i\)，耦合空间  
     \[
     \Pi(\mu_1,\dots,\mu_n)=\{\pi:\text{边缘为 }\mu_i\}
     \]
     一般是仿射约束交，凸但可能不紧、不唯一、解集多值。

2. **最小假设层：只保留“凸性 + 下半连续 + 适当强制”**
   - 目标泛函  
     \[
     F(\pi)=\int c\,d\pi
     \]
     若 \(c\) 下半连续、\(\Pi\) 非空，则 OT 值良定。
   - 但**最优耦合集**  
     \[
     \Pi_{\rm opt}=\arg\min_{\Pi} F
     \]
     可能多值，甚至大。
   - 这里“最小假设”就是：不假设 \(c\) 严格凸、不假设 \(\Pi\) 紧、不假设唯一。

3. **最大正则层：加熵惩罚，把多值选择变成单值算子**
   - 考虑  
     \[
     \pi^\varepsilon=\arg\min_{\pi\in\Pi}\left\{F(\pi)+\varepsilon\,{\rm Ent}(\pi)\right\}
     \]
     其中 \({\rm Ent}\) 是相对熵/KL 型严格凸惩罚。
   - 由于熵在 \(\Pi\) 上严格凸，且 \(\Pi\) 凸闭，
     \[
     \pi^\varepsilon \text{ 唯一}.
     \]
   - 更强：在适当条件下，\(\pi^\varepsilon\) 对边缘、代价、温度参数是 **Lipschitz / 连续依赖** 的。  
     这就是“最小假设最大正则”：唯一性、稳定性不是假设，而是熵惩罚 + 凸性的推论。

4. **刚性等号层：熵惩罚消失时，唯一性退化为分类**
   - 当 \(\varepsilon\downarrow 0\)，若  
     \[
     \pi^\varepsilon \to \pi^*
     \]
     且 \(\Pi_{\rm opt}\) 是单点，则得到“刚性等号”：
     \[
     \Pi_{\rm opt}=\{\pi^*\}
     \]
     这等价于某种弱同构/极值结构分类。
   - 若 \(\Pi_{\rm opt}\) 非单点，则极限可能是选择规则，而非原始 OT 解。  
     这正好对应“熵惩罚得唯一”与“距离 0 ⟺ 弱同构”的刚性等号。

所以，共性 3 在我这条线的机制对应不是“我们也要最小假设”，而是：

> **把耦合空间取为凸闭集，把目标取为下半连续凸泛函，再用严格凸熵惩罚做选择泛函；于是唯一性、Lipschitz 稳定性、极限刚性全部成为定理，而不是额外假设。**

这也是五共性里最接近“变换涌现而非假设”的一条：  
**唯一性不是假设，是熵惩罚的涌现；正则性不是假设，是凸性的涌现。**

---

## B) 一个可操作可判定的「耦合/统一」实验

### 实验名：**多边缘熵惩罚 OT 的统一耦合判定实验**

#### 1. 对象
取三组概率测度，构造三边缘耦合问题：

- 空间：\(\mathbb{R}^d\) 或有限图 \(G=(V,E)\)，\(|V|=N\)。
- 边缘：
  \[
  \mu_1,\mu_2,\mu_3 \in \mathcal{P}(V)
  \]
  例如三个不同的度分布/直方图。
- 耦合空间：
  \[
  \Pi(\mu_1,\mu_2,\mu_3)=\{\pi\in\mathcal{P}(V^3): \text{第 }i\text{ 边缘}=\mu_i\}
  \]
- 代价：
  \[
  c(x_1,x_2,x_3)=d_G(x_1,x_2)+d_G(x_2,x_3)+d_G(x_1,x_3)
  \]
  或超图代价 \(c(e)\)，对超边 \(e=\{x_1,x_2,x_3\}\)。
- 熵惩罚：
  \[
  {\rm Ent}(\pi)=\sum_{x_1,x_2,x_3}\pi(x_1,x_2,x_3)\log\frac{\pi(x_1,x_2,x_3)}{r(x_1)r(x_2)r(x_3)}
  \]
  其中 \(r\) 是参考测度，例如均匀测度。

#### 2. 代价泛函
定义
\[
F_\varepsilon(\pi)=\int c\,d\pi+\varepsilon\,{\rm Ent}(\pi)
\]
并解
\[
\pi^\varepsilon=\arg\min_{\pi\in\Pi(\mu_1,\mu_2,\mu_3)} F_\varepsilon(\pi).
\]

#### 3. 判定谓词
取两个不同 \(\varepsilon_1>\varepsilon_2>0\)，以及不同参考测度 \(r\) 或不同边缘顺序，判定：

**谓词 P1：唯一性**
\[
\pi^{\varepsilon_1}\neq \pi^{\varepsilon_2} \quad \text{且} \quad \pi^\varepsilon \text{ 对每个 }\varepsilon>0\text{ 唯一}
\]
若成立，说明熵惩罚确实在选择唯一耦合。

**谓词 P2：边缘一致性**
\[
{\rm marg}_i(\pi^\varepsilon)=\mu_i,\quad i=1,2,3
\]
必须精确成立或数值上 \(\le 10^{-10}\)。

**谓词 P3：极限刚性**
令 \(\varepsilon\downarrow 0\)，检查
\[
\pi^\varepsilon \to \pi^*
\]
且
\[
F_0(\pi^*)=\min_{\Pi}F_0.
\]
若 \(\Pi_{\rm opt}\) 是单点，则
\[
\pi^*=\text{唯一最优耦合}.
\]
若 \(\Pi_{\rm opt}\) 非单点，则检查是否出现选择规则：
\[
\pi^\varepsilon \to \pi^*_{\rm ent}
\]
其中 \(\pi^*_{\rm ent}\) 是某个熵最大最优耦合。

**谓词 P4：距离 0 / 弱同构**
定义两个多边缘耦合问题 \(Q=(\mu_1,\mu_2,\mu_3,c)\) 和 \(Q'=(\mu'_1,\mu'_2,\mu'_3,c')\) 的“统一距离”：
\[
D(Q,Q')=\inf_{\pi\in\Pi(\mu),\pi'\in\Pi(\mu')} \left( \int |c-c'|\,d\pi + W_2(\pi,\pi') \right)
\]
判定：
\[
D(Q,Q')=0 \iff Q \text{ 与 } Q' \text{ 弱同构}
\]
即存在保边缘的测度同构把 \(c\) 映到 \(c'\)。

#### 4. 预期刚性等号
- **等号 1（唯一性刚性）**：
  \[
  \varepsilon>0 \implies \pi^\varepsilon \text{ 唯一}
  \]
  且
  \[
  \pi^\varepsilon \text{ 对 } \mu_i,c,\varepsilon \text{ 是 Lipschitz}
  \]
- **等号 2（极限刚性）**：
  \[
  \Pi_{\rm opt}=\{\pi^*\} \iff \pi^\varepsilon\to\pi^* \text{ 且不依赖参考测度}
  \]
- **等号 3（弱同构刚性）**：
  \[
  D(Q,Q')=0 \iff \text{存在保边缘同构 } \Phi \text{ 使 } c'=c\circ\Phi
  \]
- **等号 4（熵惩罚消隐）**：
  \[
  \varepsilon\downarrow 0 \text{ 且 } \Pi_{\rm opt}\text{ 单点} \implies \pi^\varepsilon \to \pi^*
  \]
  即“熵惩罚唯一性”退化为“原始 OT 刚性等号”。

#### 5. 可操作步骤
1. 选 \(N=20\sim 100\) 的图或网格。
2. 构造三组边缘 \(\mu_1,\mu_2,\mu_3\)。
3. 用 Sinkhorn / 熵正则 OT 解 \(\pi^\varepsilon\)。
4. 对 \(\varepsilon=1,0.1,0.01,0.001\) 追踪：
   - 唯一性：解是否稳定。
   - 边缘误差。
   - 代价 \(F_0(\pi^\varepsilon)\) 是否收敛到最优值。
   - 极限 \(\pi^\varepsilon\) 是否唯一。
5. 改变参考测度 \(r\)，检查极限是否变化：
   - 不变 ⇒ 刚性等号。
   - 变 ⇒ 熵选择规则，非原始 OT 唯一性。
6. 计算 \(D(Q,Q')\)，验证 \(D=0\) 是否等价于弱同构。

#### 6. 预期结果
- 对 \(\varepsilon>0\)，\(\pi^\varepsilon\) 唯一且 Lipschitz 依赖。
- 当 \(\Pi_{\rm opt}\) 单点，\(\pi^\varepsilon\to\pi^*\)，且不依赖 \(r\)。
- 当 \(\Pi_{\rm opt}\) 多值，\(\pi^\varepsilon\) 收敛到熵最大最优耦合，依赖 \(r\)。
- \(D(Q,Q')=0\) 当且仅当两个多边缘 OT 问题弱同构。

这个实验直接检验五共性中的：
- 共性 1：耦合为本。
- 共性 2：松弛生结构（熵惩罚把多值松弛成单值）。
- 共性 3：最小假设最大正则（凸性 + 熵 ⇒ 唯一、Lipschitz）。
- 共性 4：刚性等号即分类（距离 0 ⟺ 弱同构）。
- 共性 5：尺度爆破（\(\varepsilon\downarrow 0\) 的极限）。

---

## 一句话总结
- **A)** 最深映射是 **共性 3：最小假设最大正则**；机制对应为：**凸闭耦合空间 + 严格凸熵惩罚 ⇒ 解算子单值、Lipschitz、极限刚性，唯一性/正则性从定理涌现而非假设。**
- **B)** 实验是 **多边缘熵惩罚 OT 的统一耦合判定**：对象为三边缘耦合空间，代价为图/超图距离，判定谓词唯一性、边缘一致性、极限刚性、弱同构距离 0，预期刚性等号为 \(\varepsilon>0\) 唯一、\(\Pi_{\rm opt}\) 单点则极限不依赖参考测度、\(D=0\iff\) 弱同构。

——lgt SI1语义轨·20261007T144429Z
