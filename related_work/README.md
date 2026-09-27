> 当前讲解材料（2026-09-27 v4）：[Jev 完整主版60页](08-第30期-Jev-不生成文本的决策模型/slides/deck.html) · [NanoJev独立7页](08-第30期-Jev-不生成文本的决策模型/slides/deck-practice.html) · [演讲稿与领导问答](08-第30期-Jev-不生成文本的决策模型/演讲稿与领导问答.md)。kernel 部分是拟议设计，正式研究协议仍待确定。

# Jev 相关文献

## 开源项目与教学实战（2026-09-27 新增）

用户提供的五个 ZIP 保留原样，源码展开在 `projects/`。逐项源码分析、实现门槛和实战取舍见 [开源项目分析](开源项目分析.md)；离线案例及重跑命令见 [实战 README](../experiment/jev_practice/README.md)。此次教学扩展不改变下述文献来源和研究范围。

新增实战的讲解入口是 [14页独立 slide](08-第30期-Jev-不生成文本的决策模型/slides/deck-practice.html)，包含 pixel-video 机制动画；完整 deck 共56页。当前计划与交接见 [handoff.md](../handoff.md)。

## 收录范围

工作目录原本没有论文或参考文献文件。本目录按 TypeSafe 的 Jev 决策模型整理：收录官方 arXiv 上可核验的 Jev/typed-decision 研究，并以 Jev 与语言模型的法律文档评测（arXiv:2609.27678）作为比较模型清单的锚点。

arXiv 论文目录中，`paper.pdf` 是论文 PDF，`source.tar.gz` 是 arXiv 原始 LaTeX 源包，`source/` 是解包后的文件（包括拆分的 `.tex`、`.bib` 和插图）。模型卡/system card 目录里的文件由模型提供方发布；这些文档只提供 PDF，未提供 LaTeX 源码。

## Jev 与 typed-decision 研究

| arXiv | 论文 | 相关性 | 本地文件 |
|---|---|---|---|
| [2609.27678](https://arxiv.org/abs/2609.27678) | Same Scores, Different Decisions: Evaluating JEV and Language Models for Legal Document Understanding | Jev 与 9 个语言模型在 ContractNLI 上的主要比较研究；基准模型清单据此整理 | [PDF](jev_papers/2609.27678_same_scores_different_decisions/paper.pdf) · [LaTeX 源码](jev_papers/2609.27678_same_scores_different_decisions/source/) |
| [2609.26550](https://arxiv.org/abs/2609.26550) | JEV-as-a-Judge: Accept When Confident, Escalate When Unsure | Jev 作为评审模型及置信度路由 | [PDF](jev_papers/2609.26550_jev_as_a_judge/paper.pdf) · [LaTeX 源码](jev_papers/2609.26550_jev_as_a_judge/source/) |
| [2609.26758](https://arxiv.org/abs/2609.26758) | Type-Safe Is Not Error-Free: A Constrained Decision Head Follows the Option Name, Not the Rubric Bound to It | 研究选项命名对 Jev 类 typed decision 的影响 | [PDF](jev_papers/2609.26758_type_safe_is_not_error_free/paper.pdf) · [LaTeX 源码](jev_papers/2609.26758_type_safe_is_not_error_free/source/) |
| [2609.28940](https://arxiv.org/abs/2609.28940) | Calibrated Decision Models for Autonomous Penetration-Testing Harnesses | Jev/Laya 在自动化渗透测试决策层的探索性评测 | [PDF](jev_papers/2609.28940_calibrated_decisions_pentest/paper.pdf) · [LaTeX 源码](jev_papers/2609.28940_calibrated_decisions_pentest/source/) |
| [2609.24965](https://arxiv.org/abs/2609.24965) | Jev for Scientific Decisions: Evaluating Semantic Choices and Their Consequences | 科学工作流中的语义选择、下游计算与结果 | [PDF](jev_papers/2609.24965_jev_scientific_decisions/paper.pdf) · [LaTeX 源码](jev_papers/2609.24965_jev_scientific_decisions/source/) |
| [2609.24574](https://arxiv.org/abs/2609.24574) | Evaluating Decision Models for Text Annotation in Computational Social Science | 社会科学文本标注；比较 Jev、开放决策模型和语言模型 | [PDF](jev_papers/2609.24574_decision_models_social_science/paper.pdf) · [LaTeX 源码](jev_papers/2609.24574_decision_models_social_science/source/) |
| [2609.23886](https://arxiv.org/abs/2609.23886) | this-that-model-1.0: A typed decision model that decides in 30 ms, for a millionth of a cent | 直接与 Jev 对比的 typed-decision 替代模型 | [PDF](jev_papers/2609.23886_this_that_model/paper.pdf) · [LaTeX 源码](jev_papers/2609.23886_this_that_model/source/) |
| [2609.24052](https://arxiv.org/abs/2609.24052) | Calibrated Decisions at Scale: Converting Police Crash Narratives into Probabilistic Crash Variables with a System One Model (Jev) | 大规模事故叙述结构化与概率校准 | [PDF](jev_papers/2609.24052_calibrated_decisions_crash_narratives/paper.pdf) · [LaTeX 源码](jev_papers/2609.24052_calibrated_decisions_crash_narratives/source/) |
| [2609.23986](https://arxiv.org/abs/2609.23986) | Jev-Mem: System-One-Controlled Agentic Memory for Efficient AI Agents | 将 Jev 用作智能体记忆系统的决策控制层 | [PDF](jev_papers/2609.23986_jev_mem/paper.pdf) · [LaTeX 源码](jev_papers/2609.23986_jev_mem/source/) |
| [2609.23959](https://arxiv.org/abs/2609.23959) | Open-Jev Judgments on CallScreenBench: Calibrated One-Pass Scam Screening with a Small Language Model | 开放权重 Jev-style 小模型；相关替代方向，不是 TypeSafe 托管 Jev | [PDF](jev_papers/2609.23959_open_jev_callscreenbench/paper.pdf) · [LaTeX 源码](jev_papers/2609.23959_open_jev_callscreenbench/source/) |
| [2609.23136](https://arxiv.org/abs/2609.23136) | Fast Intent-Driven Service Orchestration with Jev for 6G Edge Networks | Jev 在 6G 边缘服务编排中的端到端应用 | [PDF](jev_papers/2609.23136_jev_6g_edge_orchestration/paper.pdf) · [LaTeX 源码](jev_papers/2609.23136_jev_6g_edge_orchestration/source/) |
| [2609.22753](https://arxiv.org/abs/2609.22753) | Replacing Large Language Models with Jev Decision Models for Low-Latency Edge Service Orchestration | Jev 与结构化输出语言模型在边缘编排中的比较 | [PDF](jev_papers/2609.22753_jev_edge_service_orchestration/paper.pdf) · [LaTeX 源码](jev_papers/2609.22753_jev_edge_service_orchestration/source/) |

## 比较模型与任务的资料

主比较论文报告的对比语言模型为 Qwen3.5-4B/9B、Gemini 3.5 Flash-Lite、Gemini 3.1 Pro、GPT-5.6 Luna/Terra、GPT-6 Astra、Claude Haiku 4.5 和 Claude Sonnet 5。

| 模型/任务 | 资料 | 本地文件 |
|---|---|---|
| ContractNLI 任务及其基线 | [ContractNLI: A Dataset for Document-level Natural Language Inference for Contracts (arXiv:2110.01799)](https://arxiv.org/abs/2110.01799) | [PDF](comparison_models/2110.01799_contractnli/paper.pdf) · [LaTeX 源码](comparison_models/2110.01799_contractnli/source/) |
| Qwen 系列 | [Qwen3 Technical Report (arXiv:2505.09388)](https://arxiv.org/abs/2505.09388) | [PDF](comparison_models/2505.09388_qwen3_technical_report/paper.pdf) · [LaTeX 源码](comparison_models/2505.09388_qwen3_technical_report/source/) |
| Gemini 3.1 Pro | [Google DeepMind Model Card](https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-1-Pro-Model-Card.pdf) | [PDF](comparison_models/model_cards/google_gemini_3_1_pro_model_card.pdf) |
| Gemini 3.5 Flash-Lite | [Google DeepMind Model Card](https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-5-Flash-Lite-Model-Card.pdf) | [PDF](comparison_models/model_cards/google_gemini_3_5_flash_lite_model_card.pdf) |
| GPT-5.6 Luna/Terra | [OpenAI System Card](https://deploymentsafety.openai.com/gpt-5-6) | [PDF](comparison_models/model_cards/openai_gpt_5_6_system_card.pdf) |
| GPT-6 Astra | [OpenAI System Card](https://deploymentsafety.openai.com/gpt-6-astra) | [PDF](comparison_models/model_cards/openai_gpt_6_astra_system_card.pdf) |
| Claude Sonnet 5 | [Anthropic System Card](https://www.anthropic.com/news/claude-sonnet-5) | [PDF](comparison_models/model_cards/anthropic_claude_sonnet_5_system_card.pdf) |
| Claude Haiku 4.5 | [Anthropic System Card](https://www.anthropic.com/news/claude-haiku-4-5) | [PDF](comparison_models/model_cards/anthropic_claude_haiku_4_5_system_card.pdf) |

厂商对 GPT、Gemini 和 Claude 闭源模型发布的是 model/system card，而非带 LaTeX 的学术论文；因此这些条目只有官方 PDF。Qwen3 报告是 Qwen 家族的技术论文，主比较论文使用的是 Qwen3.5-4B/9B；未找到 Qwen3.5 这两个精确基座版本单独发布的 LaTeX 技术报告。

## 清单

- [arXiv 下载清单与官方 PDF/source 地址](arxiv_manifest.tsv)
- 所有条目均为预印本、技术报告或厂商 model/system card；引用和结论应以各来源页面的当前版本为准。
