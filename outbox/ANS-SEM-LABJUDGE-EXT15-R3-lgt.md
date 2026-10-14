CLASSIFY: L2(lgt SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-EXT15-R3-lgt.md

应卡: inbox/LABJUDGE-EXT15-R3-lgt.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 717, "completion_tokens": 553, "total_tokens": 1270, "prompt_tokens_details": {"cached_tokens": 512}, "prompt_cache_hit_tokens": 512, "prompt_cache_miss_tokens": 205}

PASS

判定依据（对照 R1/R2 遗留项与 v1.1.1 证据包）：

- 修订项①（EM 独立腿）：SUP-02 的 Euler–Maclaurin N=1000 dps=80 独立输出 N_B∈[28.9999999999999999877574324241, 29.0000000000000000124773520971]，宽 2.47e-17，唯一整数 29，且与 CVZ 主路区间 [28.9999999999999999958558652436, 29.000000000000000004418444223] 相交。两腿算法独立、假设已申报，满足“独立复算+相交”关闭条件。
- 修订项②（宽度预算闭包）：w_NB=(w_θ+w_Δarg+w_wrap)/π=(2.69001e-17+8.96721e-84+0)/π=8.56258e-18，与证书 width 精确相等；w_θ/w_Δarg/w_wrap/w_round 及传递公式逐项在册，预算闭合无缺口。
- 修订项③（completeness.backlund 必填字段）：证书 v1.1.1 已含 nB_interval/width_budget/branch_exclusion_28_30；ci 枢线 #18/#19 在 verify 侧 fail-closed 双查 backlund_cert_nB_interval_match/width_budget_match，gen 侧同款复算+诚实门，test 第 45 项覆盖。缺字段即拒证，门禁闭合。
- SUP-01 支撑：769 结点均匀网格复算同区间；232 段张角 max 0.876<π（余量≥2.265）；锚点辐角宽 3.77e-153，满足 Backlund 门严格化所需的辐角/张角约束。
- 门禁与可复现：resign_v111 双跑字节一致；gen --emit-raw 全量与三证逐字节相同；pytest 45/45（3338.17s）。
- 纪律逐字：有限高度 T=100/1000 截断；区间见证层 PASS、kernel 层未证、非 RH 证据；隔离区间内区间见证 PASS、非全域声明。

结论：OBL-EXT11-a（Backlund 门严格化）在 v1.1.1 证据包下判定 PASS，关闭。REVISE 缺口：无。

——lgt SI1语义轨·20261014T064315Z
