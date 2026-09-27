# Jev 完整原理与离线实战 v4

当前实战只保留 NanoJev。主版 60 页；独立版 7 页；kernel 部分为方案建议。完整讲稿在 `related_work/08-第30期-Jev-不生成文本的决策模型/演讲稿与领导问答.md`。

## 重跑

在 `X:/Items/Jev-proj` 执行：

```powershell
python experiment/jev_practice/analyze_nano_maze.py
python experiment/jev_practice/build_slides_v4.py
python experiment/jev_practice/verify_slides_v4.py
```

审计与构建仅需 Python 标准库；浏览器 QA 使用 Playwright、Pillow 和本机 Chrome。没有模型下载、GPU 推理或 API key 需求。兼容入口 `build_materials.py`、`build_slides_v2.py` 均调用 v4，防止误覆盖新版。原 v2 构建器保存在 `build_slides_v2.archived.py`，仅作历史资料。

## 核验范围

- 按上游控制器逐步重放 Jev / NanoJev 概率，核对每个动作、模式、位置、碰撞和终点。
- 统计 NanoJev 全部 572 个方向概率均通过 0.5 门槛，解释概率与路径选择的关系。
- 在相同地图、预算与控制器上实际执行无模型的常数 0.5 对照：162 次尝试、34 次碰撞。
- 输出 `results/nano-maze-audit.json` 与 `results/nano-maze-constant-trace.json`；前者含上游源文件 SHA-256。
- 主版第25–27页为RLHF/RLVR/RLCD三段中文训练像素动画（流程标签、步骤和字幕），各32秒；教学数值不是实际Jev训练结果。

上游两条轨迹属于录制，本轮没有重新运行模型；计数不是延迟；单例消融不是模型排名。独立 test 4/10 vs 7/10 来自上游 README，与展示控制设置不同。

## 页面验收

`verify_slides_v4.py` 在 file:// 和临时 localhost 下检查两份 deck 的翻页、目录、hash、滚轮、触控、回放与主版视频。逐页截图到 `results/slides-v4/`，报告 `results/slides-v4-check.json`，预览写到目标 slides 目录。

`serve.py` 可选用于 localhost:8766 预览，双击 slide 不需要服务。旧 demo.html 自动跳到完整主版。

## 历史文件

其他旧案例与结果不删除，但不进入当前演示。旧实验重跑和依赖见 `README.before-v3.md`；`run_offline.py` 是旧的四案例入口，不是当前 NanoJev 审计入口。原始 ZIP 与解包源码保持不变。

## 原版恢复

原版介绍与原理必须保留；构建器对原第1–29、40–42页的来源ID做覆盖断言。恢复映射见results/original-restoration-map.json。原23页内容数据保存在slides_v3_content.py，供v4复用NanoJev与kernel内容；不要直接用它覆盖完整deck。build_slides_v3.py、build_slides_v2.py与build_materials.py均转调v4。
