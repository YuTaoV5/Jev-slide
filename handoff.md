# Jev 项目交接

更新时间：2026-09-27。状态：v4与三段像素动画中文化均已完成；本轮重构 60 页顺序。

## 当前计划：完成 60 页结构对齐

按用户最新纠正——把 minecraft-agent 反例从原 27 页移到 06 实验章节末（第 39 页），删掉 0.60 比 0.90 更诚实的 log loss 表（第 29 页），前 29 页 source-badge 改为"原版 NN · 原版"（去掉我之前加的"原版资料"和"数字为历史快照"字样）；演讲稿从 61 页重新落到 60 页，跨页引用同步按 reverse order 处理。讲稿生成器、slides-v4-plan 已对齐 60 页。

## 最新完成：60 页顺序重构

1. 在 deck.html 第 27 页位置删除新增反例页（原 27-28 行间），把反例页移到 06 实验章节末：紧跟"短文本持平小模型"（原 38）之后、NanoJev 章节（原 40）之前；data-sec 改为"06 实验 · 营销演示 vs 代码"。
2. 删掉 deck.html 的 "为什么 0.60 比 0.90 更诚实" log loss 表（原第 29 页 practice-v2 块）。
3. 前 29 页 source-badge 全部移除，对齐 deck.before-practice.html 风格（原版本来就没有这些 badge）；CSS 选择器保留以便未来复用。
4. 演讲稿同步：删原 27、29；按 old → new 映射（28→27、30→28、31→29、32→30、33→31、34→32、35→33、36→34、37→35、38→36、39→37、40→38、41→40、42→41、…、61→60）批量重写页号；从 演讲稿与领导问答.md 复制旧 31–33、57 节内容填补空缺，page 33 模型只知道标签 + page 52 把谁是根因按 deck 写新节。
5. verify_slides_v4.py 的 EXPECTED 计数从 61 改为 60。

## 最新完成：中文像素动画

1. 为RLHF、RLVR、RLCD三段增加中文字形，将模块、阶段、说明与字幕翻成中文；保留必要缩写和数学值。
2. 检查字形、边界与关键帧，重新导出1080p/60fps视频及封面；保留英文版本用于追溯。
3. 将主版第25、26、28页切换到中文视频，反例页位置从原 27 页下移到 06 实验章节末（第 39 页）。同步生成器、讲稿、使用说明与项目记录。
4. 验证完成：中文版总5760帧解码通过，262个中文字形覆盖完整；三段每0.25秒布局采样无错误（有静止阅读提示）。浏览器32项通过，布局溢出、页面错误、资源错误、外网请求均为0。完整60页、原版原理、NanoJev与kernel方案继续保留。
5. 中文构建：experiment/jev_training_pixel/localize_zh.py → scene_zh.py；render_zh.py → publish_zh.py → build_slides_v4.py。详见动画README。源数值与时间参数核对未改变；原英文视频及deck.before-zh.html保留。

## 最新用户纠正（优先级最高）

原版关于Jev介绍与原理的内容不能删除，必须讲得更明白；为RLHF与Jev训练做像素流程演示。已恢复完整原理版，不能再用上一轮23页精简稿替换。此前“实战只保留NanoJev”、kernel方案、去品牌和逐页讲稿要求继续有效。

官方AI primer明确Jev/TypeSafe路线是RLCD，RLVR单列为对照。现有材料正确展示RLHF、RLVR、RLCD三者，不称“Jev的RLVR”。

## 已执行计划

1. 原版恢复：从未修改的deck.before-practice.html提取原1–29及40–42页，共32个section；背景、接口、动机、架构、训练、数据、评测和未来观点全部保留。来源ID和原新页码映射可查。
2. 解释增强：新增10页（含3视频），说明训练与推理、群体校准、分支、选项变化、三训练目标、log loss算例和合成数据的信息边界。将架构推断与官方契约分开，修正绝对措辞而不删除主题。
3. 动画：pixel-video三段各32秒，480×270绘制、4倍到1080p、60fps、静音、中文流程标签/阶段/字幕；中文slide与讲稿解释。5760帧全部解码校验。RLVR参考答案只进入验证器；RLCD的log loss和梯度下降明确是教学示意，非公开Jev配方。
4. 整合：完整版60页；NanoJev独立7页不变，对应主版40–46。原应用30–38页继续由NanoJev实战和kernel方案替代，原39过渡并入后段。
5. 文稿：演讲稿同步60页，原每页有讲述、操作、依据和预判问答；附跨页问答和未决记录表。
6. 验收：32项浏览器功能/渲染检查全部通过，HTTP/file两入口、三视频、导航、目录、轮滚、触控、轨迹；布局溢出0、页面/资源错误0、外网请求0。逐页渲染并查看60页联系表、原密集页、封面和训练关键画面。
7. 入口：旧demo.html改为完整deck.html，避免误开7页独立实战；v2/v3旧构建命令均转调v4，防止删掉恢复的原理。

## 推荐产物

|路径（相对X:/Items/Jev-proj）|用途|
|---|---|
|related_work/08-第30期-Jev-不生成文本的决策模型/slides/deck.html|完整60页（反例在第39页06实验末），推荐入口|
|同目录 deck-practice.html|NanoJev独立7页|
|同目录 media/jev-training-rlhf-zh.mp4|第25页，RLHF流程|
|同目录 media/jev-training-rlvr-zh.mp4|第26页，RLVR流程|
|同目录 media/jev-training-rlcd-zh.mp4|第28页，Jev RLCD目标与玩具算例|
|第30期目录/演讲稿与领导问答.md|60页旧讲稿；新讲稿见演讲稿-逐页详细版.md（60页）|
|第30期目录/演讲稿-逐页详细版.md|60页同步讲稿（每页800–1500字，反例在第39页）|
|第30期目录/notes/原版恢复与术语校正.md|逐页恢复映射、措辞校正和来源|
|第30期目录/notes/kernel定位方案与证据.md|保留的kernel设计方案|
|experiment/jev_practice/build_slides_v4.py|恢复、整合和讲稿生成器|
|experiment/jev_practice/slides_v3_content.py|上一版页面数据供v4复用；不可独立覆盖主版|
|experiment/jev_practice/slides-v4-plan.md|全部页码施工表（已对齐61页）|
|experiment/jev_practice/results/original-restoration-map.json|32个原页到新页映射|
|experiment/jev_practice/results/v4-content-check.json|60页/60讲稿/32原页/3动画覆盖检查|
|experiment/jev_practice/results/minecraft-agent-debunk.md|minecraft-agent 仓库静态分析（commit 78b40ed）|
|experiment/jev_practice/verify_slides_v4.py|32项浏览器验收与渲染（EXPECTED 已更新为 60 页）|
|experiment/jev_practice/results/slides-v4-check.json|最终通过报告，零溢出|
|experiment/jev_training_pixel/|三动画源码、FACTS、数值、帧图及解码报告|

## 验证边界

- pixel-video每0.25秒采样无字形、文字重叠或越界错误；工具提示了静止阅读时间，已人工检查联系表与全尺寸帧。不要改写为“所有警告为0”。中文版见动画out/verification-zh.md（英文历史报告为verification.md）。
- 原版热度、价格和评测数字保留为历史资料，不是本轮重新测量。原架构探针没有证明唯一内部结构或参数规模。
- Jev精确损失、优化器、权重和完整训练配方未由所读官方材料披露。RLCD动画不是真实训练复现。
- 本轮无模型API调用、无权重训练；RLHF奖励与RLVR算术、RLCD比例均为标明的教学计算。
- NanoJev225/Jev2738为原录制尝试数；本地常数对照162，不能声称推理快12倍。完整审计脚本与结果保留。
- kernel仍是方案：AI4-Loc实际分析入口为mock，目录未见内核源码工作树，未修改该项目或运行真实性能实验。

## 重跑

```powershell
python experiment/jev_practice/build_slides_v4.py
python experiment/jev_practice/verify_slides_v4.py
```

动画先读experiment/jev_training_pixel/README.md和FACTS.md。当前中文版render_zh.py兼容Windows；英文历史版本使用render_windows.py，复用pixel-video Scene.frame。动画与posters发布到slides/media后再跑页面验收。

修改原理说明请改build_slides_v4.py；后段NanoJev/kernel正文来自slides_v3_content.py；跨页问答来自leadership-appendix.md。不要直接手改输出讲稿后再运行生成器，否则会被同源生成覆盖。

当前可选localhost服务在127.0.0.1:8766，支持媒体Range；离线双击HTML无需服务。此前PID116948仅作历史记录，接续时先核对进程，不可盲目终止。

## 备份与历史

原42页deck.before-practice.html保留未修改。v3主版保存在slides/deck.before-v4.html，旧讲稿在第30期目录演讲稿与领导问答.before-v4.md。旧README均另存before-v4；更早56页和14页保存在before-v3备份。先前交接记录在experiment/jev_practice/results/handoff-before-v4.md，其页码与状态由本文件替代。

本轮没有未完成必需项。项目未建立Git仓库，无commit。
