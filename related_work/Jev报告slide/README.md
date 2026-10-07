# Jev 原理、替代实现与实验分析

当前版本：2026-10-06，**65页**。按用户要求移除AI4-Loc相关方案；保留Jev原理、上游回放，聚焦NanoJev、SGLang Jev-like与Chat的实验分析。

- [完整网页报告](slides/deck.html)：实验第47–62页，未来与收尾第63–65页。
- [Markdown 博客：Jev 原理与开源替代实验](博客-Jev原理与开源替代实验.md)：同主题长文，包含 Mermaid 流程图、实验表格与复现入口。
- [实验说明与证据](notes/服务器实验更新.md)
- [实验讲稿与问答](演讲稿-服务器实验补充.md)
- [全页预览](slides/预览-全部页面.png)

核心结论：NanoJev更贴合参考目标，校准贡献待验证；输出预算影响接口延迟；同Qwen完整任务质量一致，复跑累计模型耗时约低11%。

构建：`python experiment/nanojev_compare/update_report_slides.py`

验证：`python experiment/nanojev_compare/verify_report_slides.py`

原版与76页版本均保留为历史HTML备份，当前讲稿已同步65页。
