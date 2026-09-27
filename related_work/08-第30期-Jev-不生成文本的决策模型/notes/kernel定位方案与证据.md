# kernel 定位：Jev 接入方案与依据

日期：2026-09-27。此文件记录只读核查和本次设计建议；未修改 `X:/Items/1_AI4-Loc`，未执行其上传、模型或分析 API。方案不等于已确认研究协议。

## 现状核查

| 依据 | 实际观察 | 设计含义 |
|---|---|---|
| server/index.js:84–88 | 上传日志与可选符号包，创建任务，调用 runMockAnalysis | 可以保留入口，在后端换入真实 worker |
| server/index.js:91–101 | 定时器推进步骤，写固定报告与 92.4 等示例分数 | UI 状态和分数不能作为真实定位性能 |
| server/index.js:110–123 | 门禁状态顺序存在，benchmark 分数固定赋值 | 需要可执行 benchmark、真实结果与版本记录 |
| docs/IMPLEMENTATION_PLAN.md | 规划 worker、evidence.json、版本与输入哈希 | 这些是计划中的接口方向，不能当成已完成能力 |
| kernel_linux_6.6/ | 当前工作目录仅见 .git 元数据，没有源码文件 | 接入前补齐实际版本源码与匹配符号；本次没有进行内核函数级分析 |

## 接入范围与分工

首选候选：从已闭环、可授权的 panic 或 hung task 案例中选择一个故障族，先做证据候选排序。下一步取证选择是后续闭环能力，不与首个试点同时承诺。

建议链路：本地解析与版本校验 → 证据 / 代码候选召回 → Jev 对有限命题判断 → 代码策略验收 → 工具取证 → 状态更新 → 工程师确认。生成模型可负责提出假设和撰写报告；所有根因结论仍需原始证据和工程验证。

确定性部分：解包、日志解析、时间与数值计算、符号/构建匹配、文件哈希、检索过滤、调用预算、去重与输出格式校验。

语义判断候选：证据与当前故障的相关性、某段证据对具体命题的支持与冲突、有限检查项的优先顺序。模型不得凭空增加文件、行号或未召回的候选。

## 建议的应用契约（非官方 API 原始请求）

```json
{
  "schema": "kernel-investigation-proposal-v1",
  "case_id": "synthetic-hung-task-001",
  "input_manifest": {
    "kernel_commit": "TO_BE_PROVIDED",
    "build_id": "TO_BE_PROVIDED",
    "symbol_match": "unknown"
  },
  "evidence": [
    {"id": "E1", "source_hash": "TO_BE_PROVIDED", "line_range": [1, 3], "kind": "hung_task", "text": "SYNTHETIC EXAMPLE"}
  ],
  "hypotheses": [{"id": "H1", "claim": "lock-related wait"}, {"id": "H2", "claim": "I/O-related wait"}],
  "allowed_actions": ["inspect_lock_owner", "inspect_wait_stack", "request_matching_symbols", "escalate"],
  "checked_actions": [],
  "missing_evidence": ["matching symbols", "owner stack"]
}
```

适配器将契约转换为 TypeSafe typed questions；当前没有实现或调用该适配器。本轮不造一个看似真实的 Jev 响应。引用 E-ID / H-ID 的存在性、符号匹配和必要字段由代码检查，不能交给模型概率保证。

建议新增输出：

- `input-manifest.json`：文件哈希、源码 / 构建 / 符号版本、抽取器版本。
- `evidence.json`：片段、位置、时间关系、反证、缺失字段。
- `decision_trace.json`：题目版本、候选、模型固定版本、响应、策略版本、是否采纳、工具结果、费用与延迟。
- `report.md`：明确已证实事实、待验证假设、缺失证据、已执行检查与工程师确认状态。

这些是建议文件，不声明 AI4-Loc 已具备这些真实产物。给未知项保留 `unknown`，不能用 0 分代替“未测量”。

## 控制器策略

1. 先检查关键输入与版本是否可用，不匹配就补资料。
2. 保留多种候选及 OTHER 出口；低分证据仍可回查，关键反证不被摘要抹掉。
3. 模型建议只改变调查顺序；精确工具反馈可否定建议。
4. 以输入与环境版本为缓存键，避免重复检查；版本变化后重新核验。
5. 设调用预算、超时和连续无新信息的退出条件，默认回原流程。
6. 根因状态升级需要该故障族的证据标准与工程验证，不能由最高分直接触发。

## 如何证明价值

建立工程师复核的已闭环案例集，记录数据来源、许可、问题家族、构建版本、根因与证据。按故障家族分组，并留出更新版本；同一故障的重复日志不可跨集合。

对同一案例和预算做配对评估：规则 + 检索、现有 Agent、加 Jev 的流程；必要时增加本地小模型。先测候选召回，再测排序，否则会掩盖候选遗漏。报告 Top-k 命中、严重误导率、拒答/扩检比例、有效取证次数、人工确认时间、端到端墙钟 p50/p95、总费用，以及失败样本。

校准集用于选择阈值，留出测试集用于验收。质量和收益门槛需要团队依据误导与漏报成本确定；这里不预填 90% 等无依据承诺。影子运行先只记录，不改变现有任务结果。

## 与 NanoJev 实战的联系

225 对 2738 的尝试数展示了系统行为差异。记录中 NanoJev 572 个概率全部通过门槛；同一控制器用常数概率只需 162 次。由此得到的设计观点是：模型价值必须与控制器、检索和规则的贡献分开评估。游戏地图、动作反馈与 kernel 因果证据不同，不能把该结果作为定位收益的实验证明。

## 待确认清单

故障族、数据授权与可用规模、kernel 源码和符号、标注规则、评估预算、部署与外发条件、模型版本、验收门槛、人员与周期均待确认。本轮已确认的只有离线讲解与方案材料。

## 来源

- 本地 `X:/Items/1_AI4-Loc/server/index.js`、`docs/IMPLEMENTATION_PLAN.md` 与目录实际状态。
- [TypeSafe Introduction](https://docs.typesafe.ai/introduction)：输入输出与题型，2026-09-27 核查。
- NanoJev 本地源码及 `experiment/jev_practice/results/nano-maze-audit.json`：只支撑游戏控制机制和离线计数，不支撑 kernel 能力。
