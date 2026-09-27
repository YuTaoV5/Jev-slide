# Jev 项目常识与协作约定

本文件记录项目已确认的背景和长期目录约定。新任务开始时先读本文件，再读相关目录中的说明。只把已确认的信息写成项目事实；未定研究设计要明确标为待确认。

## 项目背景

- 本项目讨论的是 TypeSafe 的 Jev typed decision model；“Jev”不是本项目自定义缩写。避免与其他领域同名词混淆。
- `related_work/README.md` 和 `related_work/arxiv_manifest.tsv` 是当前本地文献集的入口。`related_work/` 中的论文 PDF、`source.tar.gz` 和解包后的 LaTeX 源码来自对应 arXiv 页面；模型/system card 来自模型提供方。
- `arXiv:2609.27678`《Same Scores, Different Decisions: Evaluating JEV and Language Models for Legal Document Understanding》是当前比较文献的锚点之一，不等于已经确定本项目要复现该论文或采用其协议。
- 该比较论文评测 Jev 1.13.0，并比较 Qwen3.5-4B/9B、Gemini 3.5 Flash-Lite、Gemini 3.1 Pro、GPT-5.6 Luna/Terra、GPT-6 Astra、Claude Haiku 4.5 和 Claude Sonnet 5。引用或复用时以论文和对应厂商资料为准。
- Qwen3 技术报告是 Qwen 系列参考资料，并非 Qwen3.5-4B/9B 的精确技术报告。闭源模型的相关厂商资料是 PDF model/system card，没有对应的 LaTeX 源码。

## 目录约定

- `related_work/`：保存文献、原始论文源包、解包源码及索引。保留论文来源和版本信息；不要把解包源码误当成本项目代码。
- `DataSet/`：数据工作区，目录名大小写固定为 `DataSet`；`raw/`、`interim/`、`processed/`、`splits/` 分别用于原始数据、中间处理数据、实验数据和数据划分。
- `DataSet/raw/` 中的原始文件保持不变。为数据记录来源、引用、许可/限制、版本或校验值及处理步骤。不要提交敏感或未经许可的数据；必要时只保留获取说明和处理脚本。
- `experiment/`：实验配置、脚本、探索性 notebook、结果和日志。正式结果应能由明确的配置和脚本重跑；保留模型版本、数据/划分版本、提示词、运行参数、时间、种子（适用时）、费用、延迟和指标。
- 不要把 API key、访问 token 或其他密钥写入仓库、配置、日志或结果。

## 已确认的教学实战任务（2026-09-27）

- 当前用户目标：分析 `related_work/` 提供的五个 Jev 相关开源项目 ZIP，并给 `related_work/08-第30期-Jev-不生成文本的决策模型/slides/deck.html` 添加易实现的实战内容。
- 用户选择先完成离线实战。项目源码快照在 `related_work/projects/`；分析见 `related_work/开源项目分析.md`；本项目演示代码与结果在 `experiment/jev_practice/`。
- 人工概率 / logprob 夹具与上游轨迹回放必须明确标注，不作为本机模型推理、校准或性能结论。该教学任务不等于确定正式论文复现协议。
- 后续用户明确要求可翻页的新 slide 使用 kelip-slide，并用 pixel-video 制作机制动画。当前生成器在 `experiment/jev_practice/build_slides_v4.py`；像素视频项目在 `experiment/jev_pixel_explainer/`。工作计划与当前进度见根目录 `handoff.md`，开始接续前先读。
- 用户最新要求：实战只保留 NanoJev，去掉可lip品牌，重排整体讲解；只读分析 `X:/Items/1_AI4-Loc` 并提出 kernel 定位建议；输出逐页演讲稿和领导问答。
- 用户再次明确：原版Jev介绍与原理不能删除，必须讲得更明白；增加RLHF与Jev训练流程像素演示。官方路线名是RLCD，RLVR作为对照，不能混称。
- 用户要求像素动画改为中文：默认使用中文流程标签、步骤与字幕，保留必要缩写、公式和教学边界；英文历史视频保留。中文源代码为 experiment/jev_training_pixel/scene_zh.py。
- v4当前产物：完整主版60页（minecraft-agent 反例下移到 06 实验章节末第39页、删除 0.60 vs 0.90 log loss 表、前 29 页 source-badge 全部移除对齐 deck.before-practice.html 原版风格）；原版1–29及40–42页主题恢复；三段32秒RLHF/RLVR/RLCD动画位于25、26、28页；NanoJev独立7页对应主版40–46页。演讲稿新增"演讲稿-逐页详细版.md"（每页800–1500字、反例在第39页）。源动画在experiment/jev_training_pixel，恢复映射在results/original-restoration-map.json。32项浏览器检查通过、布局溢出0，三视频5760帧全部解码；verify_slides_v4.py 的 EXPECTED 已对齐60页。
- 已离线核验：上游 Jev / NanoJev 轨迹为2738 / 225次尝试；NanoJev 572个方向概率全通过0.5门槛。同一控制器常数0.5对照162次到达、34次碰撞。不能宣称推理快12倍或判断更准。
- kernel 接入仅为设计：AI4-Loc 现有分析入口仍是 runMockAnalysis，固定报告/分数不是实测；不把本次方案同步为该项目已实现能力。

## 研究设计尚待确定

研究问题、数据集及许可、实验基线、实验协议、评价指标、运行环境和依赖目前都没有经项目文档确认。不要只根据文献目录自行断定项目要复现哪篇论文、使用哪个数据集或采用什么结论。

项目启动时未找到 `handoff.md` 和 `brainstorm.md`；2026-09-27 已按用户要求新增 `handoff.md`。`brainstorm.md` 仍未找到。接续时应先阅读交接文件，并同步已确认决策；遇到研究范围冲突时保留冲突并请用户确认，不要静默改写。
