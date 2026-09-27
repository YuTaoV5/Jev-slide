# 中文训练像素动画验收

2026-09-27：RLHF、RLVR、RLCD三段中文版，每段32秒、1920×1080、60fps、静音，合计5760帧全部解码通过。

- 流程模块、步骤状态和双行字幕改为中文；保留必要缩写、公式。全部262个中文字形经字体cmap检查覆盖，代表全尺寸帧可读。
- scene.py与scene_zh.py数值常量对照通过；只调整页脚坐标，数据、时间与数学计算未改变。见zh-source-check.json。
- pixel-video每0.25秒采样检查三段：无字形缺失、重叠、越界错误；每段有4条初始阅读停留提示（同一0秒起始段），人工已查看三套8帧联系表与全尺寸帧。中文chrome布局在当前进程扩展，未修改已安装skill。
- 第25–27页已引用带-zh的视频及封面。浏览器32项功能/逐页渲染检查通过，布局问题0、页面/资源错误0、外网请求0；HTTP与file均验证播放、拖动、暂停、返回重播。
- 原完整60页与60页讲稿、32个原版section保留，NanoJev独立7页不变。内容覆盖报告见../../jev_practice/results/zh-content-check.json。

日志：*-zh-layout-check.txt；视频参数与逐帧结果：*-zh-render-verification.json；页面验收：../../jev_practice/results/slides-zh-check.json。

中文字体仅渲染时读取本机Windows宋体，视频本身不依赖字体安装。英文版本保留。数学仍是教学算例，无模型调用/真实训练；RLCD算例不是Jev公开训练配方。
