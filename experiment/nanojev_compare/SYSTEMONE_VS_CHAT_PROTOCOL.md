# 同模型 System One 与标准会话接口实验

日期：2026-10-06。范围：用户指定的 SGLang Qwen3.8-27B 服务。下面包含已执行的小规模验证和正式实验设计；不能扩展为原版 Jev 的训练或性能结论。

## 要检验的两个问题

1. **判断延迟**：相同权重、相同观察、相同候选动作、相同提示 token、相同并发与缓存条件下，System One 的“可执行动作就绪时间”是否更短？
2. **长程任务表现**：相同初始世界、随机种子、观察权限、控制器与行动预算下，System One 是否有更高任务成功率、更少碰撞或更低步骤成本？

两者分别检验。减少文本生成不意味着改进规划能力；长上下文也不等于长程任务。服务器的 System One 从答复位置的候选标签 next-token 分数选动作，关闭 thinking；标准会话若用同一提示、关闭 thinking 并贪心生成首个标签，通常会得到同一动作。原始来源：[SGLang decision models](https://docs.sglang.io/docs/supported-models/decision_models)。提供候选概率不代表它们是任务成功概率。

## 实验组

| 组 | API | 提示 | thinking | 输出预算 | 用途 |
|---|---|---|---|---|---|
| A | `/v1/systemone` | 服务内部的固定选择题提示 | 关闭 | 0 生成 token | Jev-like 方案 |
| B | `/v1/chat/completions` | 复用 A 的原版 renderer | 关闭 | 1 token、温度 0 | 主要接口对照，优化后的会话决策 |
| C | `/v1/chat/completions` | 与 A 相同 | 关闭 | 最多 32 token、温度 0 | 普通常规短回答，需要完整返回和解析 |
| D（正式扩展） | `/v1/chat/completions` | 同样的公开状态和选项 | 开启 | 固定推理 token 预算 | 质量/时间取舍，不纳入“只有接口不同”的比较 |

B/C 输出选项字母后按同一顺序映射动作；解析只接受单个有效选项字母（可带句点）。无效输出计为失败，并单列失败率，不能静默改为正确动作。A 取最高概率候选。所有组在仅有一个合法动作时由同一代码直接执行并标记为 forced，不混入模型调用延迟。对 D 要明确最终动作与 reasoning 的解析、总 token 预算和超时；本次未运行 D。

## 已执行的单步验证

固定样本是此前 96 个不同 episode 的离线状态，共享源数据 ID。三组逐题调用顺序轮转，先做一次 warmup。第一轮提示只在语义上相同；第二轮 B/C 直接调用服务器安装版 `_render_question`，与 A 共用 renderer。

pilot 的计时终点为 HTTP 响应 JSON 读取完成；其后的本地字母解析/动作映射没有计入。因此它是动作就绪延迟的近似，正式版应包含这部分客户端处理。

| 验证条件 / 组 | 延迟中位数 | 延迟均值 | 输出 token 均值 | 无效动作 |
|---|---:|---:|---:|---:|
| 语义相同提示 / A | 167.5 ms | 185.4 ms | 0 | 0/96 |
| 语义相同提示 / B | 136.0 ms | 140.0 ms | 1 | 0/96 |
| 语义相同提示 / C | 121.3 ms | 154.6 ms | 2 | 0/96 |
| renderer 相同 / A | 85.7 ms | 122.3 ms | 0 | 0/96 |
| renderer 相同 / B | 57.5 ms | 100.3 ms | 1 | 0/96 |
| renderer 相同 / C | 119.7 ms | 147.2 ms | 2 | 0/96 |

renderer 相同的三组，射击专家动作匹配均为 12/60；对迷宫/贪吃蛇 Jev 教师首选动作匹配均为 19/36。完整概率和响应存于 `results/matched/systemone_chat_predictions.jsonl`；逐任务统计存于 `results/matched/systemone_chat_summary.json`。

A/B 的 96 个 top-1 动作全部一致；A/C 一致 95/96。C 有 1 题选择不同，但没有改变上述汇总匹配数，不能把“指标相等”写成“三组每题都相等”。这一差异在当前服务条件下尚未定位，需要在固定调度和确定性设置下复查。96 题的三组输入 token 数逐题相等；另对一条 455-token 输入将本地 chat 模板的完整 token ID 序列与服务器 `/v1/decisions` 返回的序列比较，完全相同，记录在 `results/matched/prompt_audit.json`。System One 与 decisions 共用同一 `_encode_question` 实现，安装版源码快照已保存。

**当前证据不支持 A 普遍比会话判断快。** A 比只输出一个 token 的 B 慢，比生成字母及终止 token 的 C 快。服务没有清空 prefix cache；第二轮共享提示、第一轮运行顺序与既存缓存均会影响结果，不能将两轮耗时差归因于 renderer。每题只有一次测量，这是可行性 pilot，不是稳定性能排名。

## 正式延迟实验

- 保持模型修订、权重、精度、SGLang 版本、启动参数、GPU 和模板不变。使用同一服务，测试期间只运行这一项负载；并发主实验为 1，扩展为 4，与当前 `max-running-requests=4` 一致。
- 预先固定样本和随机化顺序。每个输入重复 5 次；按输入长度、任务、候选数分层。A/B 为主要比较，C 为实际应用补充。
- 冷缓存和暖缓存分开：独占测试时，冷缓存每次调用前执行服务的 cache flush；暖缓存先预热当前输入，再随机顺序调用各组。GPU kernel warmup 不计入样本。必须记录 flush 是否成功，不把网络客户端冷启动与 GPU 冷启动混在一起。
- 客户端计时从发送请求前至完整响应解析并获得有效动作，三组均使用 HTTP。报告配对的中位数、P95、均值、超时/格式失败、输入/输出 token、吞吐。聊天 TTFT 可另报，但不能用 TTFT 替代可执行动作就绪时间。
- 校验 A/B 的模板 kwargs、候选顺序、prompt token 数和 token ID；保存 prompt hash。B 与 A 的动作不一致时，检查候选外最高词、近似平局、模板差异和运行非确定性，不能直接称为准确率差。
- 按状态（或 episode）聚类 bootstrap 95% 区间，重复测量不能当作独立题目。预先约定：只有配对延迟比的区间整体低于 1，才称 A 更快。

## 正式长程实验

复用 NanoJev 的 `unified_grid_envs.py`、`scaled_maze.py`、`snake_game.py`，冻结源码 hash。原版公开状态渲染提供近期事件及观察到的记忆，控制器不额外替任一组规划。每组重新 reset 相同 seed；后续观察由各自动作产生，所以不同策略可以走出不同轨迹。环境隐藏地图和评估 oracle 不进入请求。

| 任务分层 | 环境和预算 | 主要成功标准 | 补充指标 |
|---|---|---|---|
| 短迷宫 | 8×8，32 次物理尝试 | 预算内到达目标 | 碰撞、物理步骤、模型决策数 |
| 中程迷宫 | 16×16，160 次物理尝试 | 预算内到达目标 | 同上，累计模型耗时 |
| 长迷宫 | 50×50，800 次物理尝试 | 预算内到达目标 | 同上，失败/超时原因 |
| 贪吃蛇 | 8×8/12×12，96/160 步，2/3 个食物 | 预算内完成食物目标 | 碰撞/死亡、存活步数、食物数 |

迷宫自动沿已经走过的边移动的 macro 步骤同样消耗物理预算；报告物理步骤与模型决策数，不能把一次模型调用等同于一次游戏移动。原版不同规模也改变任务难度；比较应在每个分层内做配对，不将规模间差直接解释为纯粹的 horizon 效应。长迷宫的 tree/corridor 拓扑分别报告。

先跑每个划分/变体 1 个 episode 的 pilot 检查执行器；正式版建议每个预先定义难度层使用至少 100 个新 seed 的配对 episode。正式 seed 清单在模型调用前生成并冻结，记录生成器版本；去重依据初始世界 hash，不能根据模型结果挑选关卡。当前上游 test/OOD 名称仅表示它的发布划分，不能宣称 Qwen 的训练分布已知。

主实验保持**相同行动预算**，用于判断策略质量。另设相同墙钟时间预算，测量低延迟能否带来更高完成率；当前游戏物理时钟按 action 前进，网络等待不会消耗物理步骤，因此两类预算必须独立报告。

主指标为逐难度层配对成功率差和聚类 bootstrap 95% 区间，并用 McNemar 检查两组不一致的成功/失败 episode。附报全样本物理步数、碰撞、模型调用数、累计耗时；只对成功 episode 计算的路径效率单独标记，以免成功率不同产生选择偏差。独立 episode 是统计单位，连续状态不是独立样本。A/B 的动作和完整轨迹都一致时，可直接报告“这组条件下任务质量一致”，不能靠增加状态条数获得显著性。

## 已执行的完整 episode pilot

8 个配对 case，A/B 各执行 8 局，均完整终止，没有外部截断。两组初始观察 hash 逐 case 相同，8 对动作序列全部一致；每组成功 6/8，物理步骤总计 555，非 forced 模型调用 460。这里已经实测任务结果，无需依赖 Jev 教师标签。

| case | A/B 成功 | A/B 物理步骤 | 物理预算 |
|---|---|---:|---:|
| ood-maze16-7840001 | 失败 / 失败 | 160 / 160 | 160 |
| ood-maze8-408001 | 失败 / 失败 | 160 / 160 | 160 |
| ood-snake12-7842000 | 成功 / 成功 | 17 / 17 | 160 |
| ood-snake8-418005 | 成功 / 成功 | 13 / 13 | 160 |
| test-maze16-7830001 | 成功 / 成功 | 149 / 149 | 160 |
| test-maze8-308040 | 成功 / 成功 | 23 / 23 | 32 |
| test-snake12-7832000 | 成功 / 成功 | 24 / 24 | 160 |
| test-snake8-318000 | 成功 / 成功 | 9 / 9 | 96 |

上游 OOD 的 maze8/snake8 预算也是 160；执行时保留每个 case 的原始规格。该 pilot 包含最多 160 步的完整任务，没有运行 800 步 maze50。8 个 case 不足以推广到其他难度或全部长程任务。

第一轮累计模型 HTTP 时间为 A 107.62 秒、B 194.45 秒。其中一次提示 token 审计请求与在线任务有过重叠，且 B 的一个 maze8 episode 出现较大耗时；这一轮延迟仅供诊断，不用于性能结论。全部逐步动作、观察 hash、延迟和最终环境信息存于 `results/rollout_pilot/episodes.jsonl`，初始案例和源码 hash 存于该目录 `manifest.json`。

相同 8 个 case 的独立复跑已经完成，期间没有发送其他模型请求。两组仍成功 6/8、物理步骤总计 555、模型调用各 460；A/B 每个配对 episode 的动作序列全部相同。累计模型 HTTP 耗时为 A **107.71 秒**、B **120.99 秒**；按这些请求的均值为 234.2 ms 和 263.0 ms，累计时间 A 比 B 低约 11.0%。这说明该在线请求场景与固定状态的单步 pilot 不同，不能用“输出 token 为零”直接推导普遍更快。复跑数据在 `results/rollout_repeat/`；两个复跑不是 16 个不同 case，统计时仍只有 8 个独立初始任务。正式速度结论仍需按上述冷/暖缓存与重复测量协议取得。

## 脚本和复现

离线脚本：`compare_systemone_chat.py`。服务器命令：

```bash
cd /root/gpufree-data/nanojev_compare
/root/systemone-venv/bin/python compare_systemone_chat.py \
  --data data/NanoJev-unified/unified/hard \
  --output results/matched_reproduction --per-task 30 --matched-prompt
```

在线脚本：`compare_rollouts.py`。本轮 pilot 使用上游固定 test/OOD、maze8/maze16/snake8/snake12，每个划分/变体最多 1 个固定 hash 排序的 case，A/B 两组：

```bash
/root/systemone-venv/bin/python compare_rollouts.py \
  --source source/NanoJev-main \
  --cases source/NanoJev-main/configs/unified_games_v1_cases.jsonl \
  --output results/rollout_reproduction --limit-per-variant 1
```

`--limit-per-variant 0` 运行所选变体全部已有 test/OOD cases；`--variants` 可调整变体；使用新 output 目录避免覆盖已保存轨迹。D、冷/暖缓存重复、并发负载以及新增正式 seed 队列属于待执行的扩展设计，不是本轮已经完成的实验。
