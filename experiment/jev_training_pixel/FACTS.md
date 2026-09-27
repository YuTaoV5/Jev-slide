# Training animations: facts and limits

Verified 2026-09-27. Three distinct mechanisms; no model API, pretrained training, or Jev recipe reproduction.

## Primary sources

- TypeSafe AI primer: https://docs.typesafe.ai/introduction/machine-learning-primer — explicitly calls TypeSafe training RLCD and lists RLHF / RLVR separately. It describes group calibration, not a guarantee for one case. Exact optimizer and scoring loss are not disclosed here.
- Ouyang et al. (2022), https://arxiv.org/abs/2203.02155 — demonstrations / SFT, ranked model responses, reward model, PPO with a reference-policy constraint. The movie presents the classic pipeline, not every modern preference-training variant.
- DeepSeek-R1 report, https://arxiv.org/html/2501.12948v1 , section 2.2.2 — rule-based correctness and format rewards; code tests / verifiable math examples. Our binary arithmetic verifier is a toy, not a complete R1 reward specification.

## On-screen numbers

Every toy value is computed in prep.py and saved to data/data.npz.

- RLHF: two synthetic responses A / B, illustrative preference A>B. Reward-model toy uses a scalar Bradley-Terry score gap, trained by deterministic gradient descent; P(A>B) starts .50. These are preference probabilities, not objective correctness.
- RLVR: synthetic arithmetic 2+3 has reference 5; candidates 5 / 6 produce exact correctness rewards 1 / 0. The feedback is for a generated sampled answer; no calibrated confidence objective follows automatically.
- RLCD: illustrative hidden-outcome group has six positives and four negatives, q=.60. A Bernoulli prediction p=.90 has average natural-log loss .984; p=.60 gives .673. Gradient descent on one logit with learning rate .8 gives the displayed path toward .60. Log loss is ONE proper-scoring-rule demonstration, not confirmed Jev implementation.
- All frame counts / durations are presentation parameters: 480x270 grid, x4 to 1920x1080, 60fps, 32s each.

## Storyboards

Each film uses eight 4-second stages with fixed system modules and moving data/feedback signals; two Chinese captions per stage in the current deck (English historical source retained). Completed operations hold while the current stage progresses.

RLHF: demonstrations → policy → responses → human rank → reward model → fresh-response score → PPO/update loop → distinction between preference and correctness.
RLVR: task → policy → sampled solutions → verifier → exact reward → policy update → repeat → correctness reward is not calibration.
RLCD: state → forecast distribution → observed outcomes → compare complete forecast with outcomes → proper score → toy parameter update → group-frequency check → unknown Jev implementation caveat.

Persistent Chinese labels: 训练流程 / 教学示意 / 未运行真实模型. RLCD additionally marks 教学损失；非 Jev 训练配方. No animation claims a single outcome proves the correct probability, or that production inference calls a reward model.

## Chinese localization (2026-09-27)

Explicit user preference overrides the pixel-video skill default English language. localize_zh.py derives scene_zh.py from retained scene.py without changing formulas, timelines or fixtures. chinese_font.py rasterizes local Windows SimSun at 12 native pixels and preserves LCD mathematical glyphs. Caption rows move to y=239/254. No font is bundled; MP4 playback needs no fonts. The reference answer is only fed to the RLVR verifier.
