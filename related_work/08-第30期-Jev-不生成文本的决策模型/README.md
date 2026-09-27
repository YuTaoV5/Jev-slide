# Jev：完整原理、训练动画与实战

当前版：2026-09-27 v4。根据用户纠正，恢复原版介绍与原理内容，不再以精简版替代完整讲解。

- [完整 slide：60 页](slides/deck.html)：背景、接口、动机、架构解释、训练、合成数据、评测 → NanoJev → kernel 方案 → 未来观点。
- [逐页演讲稿与领导问答](演讲稿与领导问答.md)：与60页同步，含操作建议、依据和讨论记录表。
- [原版恢复映射与术语校正](notes/原版恢复与术语校正.md)：原1–29页与40–42页的全部主题恢复，记录哪些表述补了限定。
- [页码与操作](slides/使用说明.md) · [全页预览](slides/预览-全部页面.png)。
- [NanoJev独立7页](slides/deck-practice.html)：对应完整版40–46页，仍只包含NanoJev实战。
- [kernel方案与证据](notes/kernel定位方案与证据.md) · [交接记录](../../handoff.md)。

## 三段训练流程动画

第25页：RLHF，示范/SFT → 回答 → 人类偏好 → 奖励模型 → PPO + KL。

第26页：RLVR，生成答案 → 独立验证器 → 1/0正确性奖励 → 策略更新；参考答案只给验证器，不作为策略输入。

第27页：Jev的RLCD，概率 → 结果反馈 → 校准目标；采用可复算的log loss教学例，明确不是已公开的Jev损失或优化器。官方称Jev路线为RLCD，RLVR作为对照。

三段均32秒、1920×1080、60fps、静音，中文流程标签、阶段说明与像素字幕，配中文slide和讲稿。翻到自动播、离开暂停、回到该页重播；文件位于slides/media/jev-training-*-zh.mp4（默认中文版；英文历史版本保留）。

## 保留与边界

原版42页文件deck.before-practice.html未修改；上一轮23页版备份为deck.before-v4.html。保留原背景数字和探针图，同时标明历史快照、来源及推断边界。新增解释训练/推理、群体校准、分支隔离、候选效应与合成数据假设。

原版其他应用与PaperDance实战30–38页继续由NanoJev唯一实战和kernel设计替代，遵循此前要求；原页39的过渡并入后段。原数据和旧deck均保留，不删除来源文件。

NanoJev225/Jev2738是尝试数，本地无模型对照162次；这些不是模型延迟。kernel部分仍为设计，未调用真实模型、未执行kernel收益评测。

## 重建

```powershell
python experiment/jev_practice/build_slides_v4.py
python experiment/jev_practice/verify_slides_v4.py
```

双击HTML离线打开；可选localhost:8766。旧demo.html现在转入完整主版，避免误进仅7页的实战版。动画源与重跑说明在experiment/jev_training_pixel/。
