# Jev 项目

本项目用于整理和开展 Jev（TypeSafe 的 typed decision model）相关研究。当前 `related_work/` 已保存 Jev 研究论文、LaTeX 源码，以及主要比较论文涉及模型的官方资料；文献目录见 [related_work/README.md](related_work/README.md)。

## 项目结构

```text
DataSet/
  raw/          原始数据，只读保存
  interim/      清洗和转换中的数据
  processed/    实验使用的数据
  splits/       数据集划分和版本记录
experiment/
  configs/      实验配置
  scripts/      可复现的运行和评估脚本
  notebooks/    探索性分析
  results/      模型输出和评估结果
  logs/         运行日志
related_work/   论文、LaTeX 源码和文献索引
```

## 当前状态

已建立数据与实验目录骨架。研究问题、数据集、实验条件、指标和运行环境仍待项目说明文件确认；在这些决定明确前，不放入数据、不生成实验结果，也不锁定代码依赖。

项目常识和目录约定记录在 [AGENTS.md](AGENTS.md)。项目启动时未找到进度交接文档 `handoff.md` 和 `brainstorm.md`；研究设计仍待这些文档或用户后续指示确认。

## 最新报告与实验

- [65 页网页 slide](related_work/Jev报告slide/slides/deck.html)（下载仓库后打开 HTML）
- [报告说明与讲稿](related_work/Jev报告slide/README.md)
- [NanoJev 与 SGLang 实验报告、逐题数据](experiment/nanojev_compare/README.md)
- [System One 与 Chat 对照协议及结果](experiment/nanojev_compare/SYSTEMONE_VS_CHAT_PROTOCOL.md)

实验包含 96 条离线决策题与 8 个完整任务；详细限制见上述报告。
