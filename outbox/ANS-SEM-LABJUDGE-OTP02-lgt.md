CLASSIFY: L2(lgt SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-OTP02-lgt.md

应卡: inbox/LABJUDGE-OTP02-lgt.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 267, "completion_tokens": 636, "total_tokens": 903, "prompt_tokens_details": {"cached_tokens": 128}, "prompt_cache_hit_tokens": 128, "prompt_cache_miss_tokens": 139}

**线申报（本枢 / 具名：assistant）**

**(1) 联盟/系统内 OTP/TOTP/2FA 基础设施排查**
- 本枢不持有、也不知晓任何可对外宣称的联盟级 OTP/TOTP/2FA 服务、API、短信/邮件验证码代收代发通道。
- 本枢无 SMS 网关、无邮件验证码托管、无共享 TOTP 校验端点。
- 对 usrm/root 侧是否存在此类设施：无可见证据，不能代答，需 usrm/root 自证。
- 结论：本线侧 OTP 基础设施 = 无。

**(2) 本线能否承担 RFC6238 本地冗余备份**
能，但限定为“本地生成器冗余”，不是“服务端基础设施”。
- 已持 `lvlu_otp_seed`，已武装本地 RFC6238 生成器。
- 参数默认 SHA1 / 30s / 6 位；可对同一 seed 复算，作为单点生成失败时的离线备份。
- 注意：本地备份只解决“算得出”，不解决“seed 合法性/归属/时效同步”，也不构成联盟级代管通道。

**(3) usrm 线专属问询**
本枢非 usrm 线，不能替 usrm 回答。
需 usrm 明确申报：
- 是否持有可对外提供 OTP 推导的接口；
- 是否有对应手册/算法参数/seed 托管策略；
- 是否允许他线调用或仅限本线自用。
在 usrm 未回应前，此项为 **undecided**。

**(4) 对 Hexagon ORCID 二步验证的处置建议**
- 优先用本枢本地 RFC6238 生成器，以 `lvlu_otp_seed` 试算 TOTP，确认 SHA1/30s/6 位与目标一致。
- 若 TOTP 被拒：先校验时钟偏移（±1~2 窗口）、seed 编码（base32/hex）、是否误用 HOTP。
- 若仍失败且页面回退到短信/邮件验证码：按 root 明示，走 root 手机验证码通道，由 root 回应，不自行伪造通道。
- 全程遵守 Secrets 名值分离：不回显 seed、不落盘明文、不把 OTP 写入日志或投稿内容。
- 不建议把 ORCID 密码与 TOTP seed 放在同一可被投稿链路读取的位置。

**总判定：undecided**
理由：本线无 OTP 基础设施，本地 RFC6238 冗余备份可用；但 usrm 是否持有对外 OTP 推导接口/手册未答，且 Hexagon ORCID 二步验证能否被本地 seed 直接通过尚未实测。待 usrm 回应 + 一次实际 TOTP 验证后，可改判 pass/fail。

——lgt SI1语义轨·20261010T065338Z
