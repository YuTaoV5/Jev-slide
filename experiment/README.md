# experiment

已确认的教学实战：[jev_practice](jev_practice/README.md)，服务于第 30 期 HTML slide，先执行离线代码案例与上游游戏回放。正式研究协议仍待确认；人工夹具和回放结果不计为模型评测。

新增机制动画项目：[jev_pixel_explainer](jev_pixel_explainer/FACTS.md)，使用 pixel-video v2 制作36秒英文像素机制讲解，嵌入 kelip 实战 slide。当前计划及进度统一记录在根目录 [handoff.md](../handoff.md)。

项目约定见根目录 `AGENTS.md`。实验协议仍待 `handoff.md`、`brainstorm.md` 或用户后续指示确认。当前预留以下位置：

- `configs/`：可复现的实验配置。
- `scripts/`：数据准备、模型调用、评分和汇总脚本。
- `notebooks/`：探索性分析；正式结果应能由脚本重跑。
- `results/`：响应、指标和汇总表。
- `logs/`：运行日志。

确定实验后，每次运行至少记录模型及版本、数据和划分版本、提示词/配置、运行时间、随机种子（适用时）、调用参数，以及费用、延迟和评分指标。不要把 API 密钥写入配置、日志或结果文件。
