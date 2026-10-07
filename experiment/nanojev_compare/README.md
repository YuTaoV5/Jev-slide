# NanoJev 与 SGLang System One 的同题离线对照

同模型 System One / 标准会话接口的后续实验设计与实测 pilot 见 [SYSTEMONE_VS_CHAT_PROTOCOL.md](SYSTEMONE_VS_CHAT_PROTOCOL.md)。它包含 96 题同提示对照和完整游戏 episode 对照，与下面的 NanoJev / Qwen 跨模型对照分开。

## 结论与边界

2026-10-06 在用户指定的 A100 80GB 服务器上，运行了 NanoJev 发布的 unified checkpoint，并调用已有的 SGLang `Qwen3.8-27B-SystemOne` 服务。两者读取完全相同的 `state`、`questions` 和动作候选项。共完成 96 条逐题配对推理，全部返回有效候选概率；逐题数据见 [paired_predictions.jsonl](results/paired_predictions.jsonl)，机器汇总见 [summary.json](results/summary.json)。

这是**离线决策题对照**，并未让两种策略重新执行完整游戏。因此下面的专家动作匹配率、Jev 教师一致率均不是任务成功率，也不能证明概率校准。NanoJev 是专门训练的决策模型；SGLang 方案是通用 Qwen3.8-27B 的 System One 兼容接口，**不是原版 TypeSafe Jev**。

## 环境与版本

- 服务器：`120.209.70.195:30113`；Ubuntu 24.04；NVIDIA A100-SXM4-80GB ×1。
- SGLang：0.5.21，`Qwen3.8-27B-SystemOne`，本机 `127.0.0.1:30000/v1/systemone`；具体部署见 [现有部署记录](../sglang_systemone/README.md)。测试前 `/ready` 返回 HTTP 200；测试期间没有替换或停掉服务。
- NanoJev：`related_work/projects/NanoJev-main` 源码快照，发布的 `NanoJev-unified` checkpoint；权重 `best.safetensors` SHA-256 `f68c47d66998231b86b7e91b4ed5e82ae23acf104c8b7cd6d165c3ac7b7ffe1b`，发布修订 `047b927b30882a1138fc504821b82ac145a4b81a`。
- 数据：`NanoJev-unified/unified/hard/test.jsonl` 和 `ood.jsonl`，发布修订 `7afc5257c0f3ff0ba08512729888a51d94b40e7e`。原始数据没有写回仓库。测试集 2496 条，OOD 集 1942 条。
- 运行环境：Python venv 中 PyTorch `2.13.0+cu130`、Transformers `5.12.1`。NanoJev 权重以 FP32 驻留，用 BF16 autocast；`temperature=1`、关闭 native Triton。与项目 `requirements-toy.txt` 的版本不完全一致，须将此视为复现差异。

## 取样、指标和结果

固定算法：按 `SHA256(id)` 排序，每个划分、任务取最多 30 个**不同 episode** 的第一条记录。三个任务的不同 episode 数不足 30 时全部纳入，所以最终是 96 条，而非计划的 180 条；同一 episode 的多个连续状态不会重复计入。`test` 和 `ood` 均在模型调用前固定。源码 [run_paired.py](run_paired.py) 实现选择、推理和汇总。

| 划分 / 任务 | 配对数 | NanoJev 专家动作匹配 | SGLang 专家动作匹配 | NanoJev 对 Jev 教师 top-1 一致 | SGLang 对 Jev 教师 top-1 一致 | NanoJev / SGLang 延迟中位数 |
|---|---:|---:|---:|---:|---:|---:|
| test / 射击 | 30 | 22/30 (73.3%) | 4/30 (13.3%) | — | — | 34.9 / 135.7 ms |
| OOD / 射击 | 30 | 25/30 (83.3%) | 8/30 (26.7%) | — | — | 34.3 / 135.8 ms |
| test / 迷宫 | 10 | — | — | 7/10 (70.0%) | 1/10 (10.0%) | 44.4 / 230.6 ms |
| OOD / 迷宫 | 10 | — | — | 6/10 (60.0%) | 5/10 (50.0%) | 44.4 / 245.7 ms |
| test / 贪吃蛇 | 8 | — | — | 7/8 (87.5%) | 5/8 (62.5%) | 33.3 / 137.4 ms |
| OOD / 贪吃蛇 | 8 | — | — | 7/8 (87.5%) | 8/8 (100.0%) | 35.7 / 161.6 ms |

射击任务的参考标签为数据集的 `reference_argmax_compatibility`：与上游专家策略的最大概率动作是否一致，**不是环境成功判定**。迷宫、贪吃蛇没有对应 `gold`；仅能与上游 Jev 教师的概率分布比较。该教师输出也不是实测正确答案。全部 96 条中两模型 top-1 动作相同 34/96 (35.4%)；射击专家匹配为 NanoJev 47/60 (78.3%)、SGLang 12/60 (20.0%)；带 Jev 教师的 36 条中 top-1 一致为 27/36 (75.0%) 和 19/36 (52.8%)。对教师概率的交叉熵分别为 0.7453 和 1.0264，越低表示越接近教师，**并不等于校准或任务表现**。

NanoJev 为同进程 Python 调用，SGLang 为 localhost HTTP 调用，且模型规模不同；延迟中位数 35.4 ms 与 158.2 ms 只描述这套实现和负载，不应当作公平的模型吞吐量排名。NanoJev 首次加载耗时 11.39 秒，没有计入逐题延迟。SGLang 返回的 `x_label_mass` 范围为 0.99908–0.99999；所有配对概率和与 1 的最大偏差为 `1.02e-7`。

## 服务器复现

服务器文件分别位于 `/root/gpufree-data/nanojev_compare/source/NanoJev-main`、`models/NanoJev-unified`、`data/NanoJev-unified/unified/hard` 和 `results`。在 SGLang `/ready` 正常时执行：

```bash
cd /root/gpufree-data/nanojev_compare
/root/systemone-venv/bin/python run_paired.py \
  --source source/NanoJev-main \
  --data data/NanoJev-unified/unified/hard \
  --checkpoint models/NanoJev-unified \
  --output results --per-task 30
```

`paired_predictions.jsonl` 每行包括原始数据 ID、划分/任务/episode、可用参考标签、两模型候选概率与 top-1、两次延迟及 SGLang `x_label_mass`，不含原始状态文本或密钥。要评估真正的游戏任务成功率，下一步需要将两模型接到**同一**环境执行器，固定关卡、随机种子、行动预算和终止条件，再运行在线 episode；不能由本次离线结果推出通关率。
