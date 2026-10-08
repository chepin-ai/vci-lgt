CLASSIFY: L2(lgt SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-E04-lgt.md

应卡: inbox/LABJUDGE-E04-lgt.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 664, "completion_tokens": 2309, "total_tokens": 2973, "prompt_tokens_details": {"cached_tokens": 512}, "prompt_cache_hit_tokens": 512, "prompt_cache_miss_tokens": 152}

```json
{
  "verdict": "APPROVE_PROMOTION_CANDIDATE_TO_FORMAL_WITH_SCOPE_LIMITS",
  "promotion": {
    "from": "candidate_v4",
    "to": "formal_law_with_declared_domain",
    "status": "有条件升格",
    "condition": "仅限退火族/Sinkhorn-Greenkhorn暖启动路径且随判定强制申报 path+budget；naive路径不得套用预算界律，只能标为表示界"
  },
  "questions": {
    "q1": {
      "question": "六项否决理由已逐项实测闭环后，v4是否满足候选→正式的不滥升格条件？",
      "answer": "满足，但为有条件正式化：①已不是空泛口号，而由E4-1至E4-6形成跨实现、表示界排除、消融、显式上界、预算尾和外推、schema回填的闭环；②E4-1仍存在诚实缺口：跨实现只到算法族级独立，不是作者级独立，因此不能升为“普适律/跨作者定律”；③E4-3表明无路径申报时不可复现，故正式律必须把path+budget作为判定必填项，而不是注记；④E4-4上界只覆盖退火族/R∈[1,4]/ε∈[3e-3,1e-1]，外推须声明；⑤因此可升格为正式候选域内定律，不得升为无条件全局律。"
    },
    "q2": {
      "question": "E4-2双控制实验设计是否足以支撑“退火路径非表示界”？",
      "answer": "足以支撑“在f64与f80双控制下，annealing实例的gap不归因于表示界”的结论；但不足以单独支撑“所有退火路径永久且普适地非表示界”。证据强度：naive C∈[1,10]在f64全下溢NaN而f80 gap=0.0，说明naive可由表示精度解释；annealing同实例f64 +1.28e-11≈f80 +1.29e-11，且tol伪影被双控制排除，说明该实例中观测gap不由f64表示下限主导。结论应表述为：退火路径的预算界机制已获强证据，但适用域仍受实例、ε范围、R范围和实现族限制。"
    },
    "q3": {
      "question": "E4-3“预测不需要路径/复现必须有路径”二元性是否成立？",
      "answer": "成立，但需精确化为：预测模型可在不读取path因子的条件下获得可泛化误差上界/趋势预测；而任何具体数值复现声明必须包含path+budget，否则同一(k,R,B)跨factor展布达中位2.72 dex、最大9.06 dex，不可复现。factor无可泛化预测信号(-7.3%)支持“预测不依赖path因子”；跨factor巨大展布支持“复现必须有path申报”。二者不矛盾：前者是统计预测层，后者是判定审计层。"
    }
  },
  "findings": [
    {
      "id": "F1",
      "finding": "六项否决已闭环，但闭环强度不均衡。",
      "evidence": [
        "E4-1：Greenkhorn vs Sinkhorn三档gap逐位一致 +2.31e-02/+7.59e-03/+1.96e-03，两族预算有界。",
        "E4-2：naive f64下溢NaN vs f80 gap=0.0，annealing f64 +1.28e-11≈f80 +1.29e-11。",
        "E4-3：36跑消融，factor无可泛化预测信号(-7.3%)，但同(k,R,B)跨factor展布中位2.72/最大9.06 dex。",
        "E4-4：log10(gap)=-0.405+1.594logε+0.879logR，R2=0.949，保守上界覆盖15/15点。",
        "E4-5：截断区me 5.9e-3→6e-15超幂律尾，外推保守。",
        "E4-6：eps-decl-schema v1必填eps_rel+scale+path+budget+err_metric，5/5回填通过，缺eps_rel正确拒绝。"
      ],
      "impact": "支持升格，但只支持带适用域和申报义务的正式律。"
    },
    {
      "id": "F2",
      "finding": "诚实缺口必须随正式律入册：跨实现仅到算法族级独立，非作者级独立。",
      "evidence": [
        "E4-1指出：两族皆预算有界，但诚实缺口=算法族级独立作者级不独立。"
      ],
      "impact": "禁止把v4表述为跨作者普适定律；只能表述为算法族级已验证律。"
    },
    {
      "id": "F3",
      "finding": "“预测不需要路径”成立，但“判定与复现必须有路径”更强且必须强制化。",
      "evidence": [
        "E4-3：factor无可泛化预测信号(-7.3%)，但同(k,R,B)跨factor展布中位2.72/最大9.06 dex。",
        "v4第③条：路径+预算必须随判定申报，无路径则不可复现，不可降级为注记。"
      ],
      "impact": "schema必须把path+budget设为判定必填，不得仅作注记。"
    },
    {
      "id": "F4",
      "finding": "表示界与预算界已按路径分野，但边界是“已测路径域”，不是“所有可能路径”。",
      "evidence": [
        "E4-2：naive=表示界；annealing=预算界。",
        "E4-4：上界适用域退火族/R∈[1,4]/ε∈[3e-3,1e-1]，外推须声明。"
      ],
      "impact": "正式律必须携带适用域和越域外推声明要求。"
    },
    {
      "id": "F5",
      "finding": "显式上界可作为预算证书签发基础，但必须按保守上界签发。",
      "evidence": [
        "E4-4：保守上界gap≲10^0.122·ε^1.594·R^0.879覆盖15/15点。",
        "v4第⑤条：预算证书按保守上界签发。"
      ],
      "impact": "允许在适用域内作为证书依据；越域只能作外推假设并标注。"
    }
  ],
  "candidate_law_v4_assessment": {
    "law_1": {
      "text": "界性随路径分野：naive=表示界；退火+暖启动=算力预算界且固定判据下表示无关。",
      "status": "接受为正式律，但限已测路径与适用域。"
    },
    "law_2": {
      "text": "ε按eps_rel相对申报尺度定义。",
      "status": "接受，schema已强制eps_rel+scale。"
    },
    "law_3": {
      "text": "路径+预算必须随判定申报，无路径则不可复现，不可降级为注记。",
      "status": "接受，且应设为硬性审计规则。"
    },
    "law_4": {
      "text": "误差可引显式上界gap≲10^0.122·ε^1.594·R^0.879，适用域退火族/R∈[1,4]/ε∈[3e-3,1e-1]，外推须声明。",
      "status": "接受为域内正式上界，越域不得默认引用。"
    },
    "law_5": {
      "text": "预算证书按保守上界签发。",
      "status": "接受。"
    }
  },
  "rejection_if_any": {
    "still_reject_full_unconditional_promotion": true,
    "reason": "若将v4升格为无条件、跨作者、全路径普适律，则应否决。具体可检验否定理由如下：",
    "falsifiable_reasons": [
      "若在退火族/R∈[1,4]/ε∈[3e-3,1e-1]之外，同一path+budget申报下实测gap超过10^0.122·ε^1.594·R^0.879且稳定复现，则上界律越域失效。",
      "若发现naive路径在更高精度或补偿求和下不再下溢/NaN，并呈现与退火同量级预算界，则“naive=表示界”的分野需修正。",
      "若缺少path+budget时仍能跨实现逐位复现同一判定，则“复现必须有路径”被否定。",
      "若出现作者级独立实现中Greenkhorn/Sinkhorn分族行为不一致且超出算法族级差异，则E4-1的跨实现支持降级。"
    ]
  },
  "json_schema_note": {
    "schema": "eps-decl-schema v1",
    "required_fields": [
      "eps_rel",
      "scale",
      "path",
      "budget",
      "err_metric"
    ],
    "backfill": "5/5历史回填通过",
    "negative_control": "缺eps_rel反例正确拒绝"
  },
  "final_decision": {
    "promote": true,
    "scope": "退火族/暖启动路径/R∈[1,4]/ε∈[3e-3,1e-1]/算法族级独立",
    "must_declare": [
      "path",
      "budget",
      "eps_rel",
      "scale",
      "err_metric",
      "是否外推及外推域"
    ],
    "forbidden": [
      "无条件全局律",
      "跨作者普适律",
      "无path复现声明",
      "把预算界套用于naive表示界"
    ]
  }
}
```

——lgt SI1语义轨·20261008T061504Z
