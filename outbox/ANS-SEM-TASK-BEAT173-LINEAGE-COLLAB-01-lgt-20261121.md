CLASSIFY: L2(lgt SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-TASK-BEAT173-LINEAGE-COLLAB-01-lgt-20261121.md

应卡: inbox/TASK-BEAT173-LINEAGE-COLLAB-01-lgt-20261121.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 38, "completion_tokens": 915, "total_tokens": 953, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 38}

I can't build that package for you, because I don't have the "strongest existing executable partial result" in context — I don't know which task, which codebase, which environment, or which outputs you're referring to. "Clean-room replay package" is also a load-bearing phrase: a genuine clean-room replay requires that the package not smuggle in hidden state (caches, env vars, network, seeds, timezone, versions) from the original run, and a one-byte mutation negative control only means something if you can specify *which* byte and *why* it should break the result.

If you paste the artifact and its context, I can produce a concrete package. Here's the template I'd fill in, so you can see exactly what I'd need:

## What I need from you
1. **The partial result**: the script/binary/notebook + the exact revision (commit hash or file hash).
2. **The environment**: OS, language/runtime versions, package lockfile, any native deps.
3. **The observed output(s)** you consider "strongest" and why (which assertion/score/metric).
4. **Known nondeterminism**: seeds, threads, GPU, clock, network, filesystem ordering.

## Package structure I'd emit

```
replay/
├── README.md                 # what it proves, what it doesn't
├── env/
│   ├── Dockerfile            # pinned base image by digest
│   └── lockfile            # exact dep versions
├── inputs/
│   ├── input.bin             # frozen, hashed
│   └── SHA256SUMS
├── run.sh                    # the exact command(s)
├── expected/
│   ├── stdout.txt
│   ├── stderr.txt
│   └── artifacts/            # hashed
├── controls/
│   ├── positive/             # known-good input → expected pass
│   └── negative_1byte/       # input.bin with byte N XOR 0x01
└── verify.sh                 # runs all three, diffs, exits nonzero on drift
```

## Fixed-input / exact-command skeleton

```bash
#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C TZ=UTC SOURCE_DATE_EPOCH=0 PYTHONHASHSEED=0
cd "$(dirname "$0")"
sha256sum -c inputs/SHA256SUMS
# exact command, no shell globs, no network:
./bin/tool --input inputs/input.bin --seed 0 --out out/
diff -r expected/artifacts out/
```

## Positive control
A tiny hand-crafted input whose correct output you can verify by hand (e.g., 3 records with known transformation), asserting the tool still *works* — proves the harness isn't just failing everything.

## One-byte negative control
```bash
cp inputs/input.bin controls/negative_1byte/input.bin
# flip exactly one byte at a declared offset, e.g. offset 0x40:
printf '\x01' | dd of=controls/negative_1byte/input.bin bs=1 seek=64 conv=notrunc
```
The control must **fail as expected** — the verifier asserts a nonzero exit or a specific `diff` mismatch. Document *which* byte and *why* it's semantically load-bearing (e.g., it's the length field}, otherwise a mutation that happens to be inert proves nothing.

## Honesty caveats I'd put in the README
- "Clean-room" here means *no hidden state from the original run*, not a legal clean-room reimplementation.
- A one-byte mutation is a **smoke test**, not a correctness proof; it only shows the pipeline is input-sensitive at that byte.
- If the tool has nondeterminism (threads/GPU/FP order), the package must either pin it or declare the expected output as a tolerance, not a byte-exact diff.

Point me at the artifact and revision, and I'll return the filled-in package (Dockerfile, `run.sh`, `verify.sh`, positive + negative controls, hashes, and the README's "what this proves / doesn't prove" section) rather than a generic template.

——lgt SI1语义轨·20261121T034050Z
