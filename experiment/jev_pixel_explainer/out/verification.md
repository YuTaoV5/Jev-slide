# Pixel-video 验证

2026-09-27 完成。`pxv check scene.py` 以0.25秒间隔覆盖36秒，输出 `clean`。已查看8阶段contact sheet、19.5秒接受分支和29秒拒答分支样帧，并抽取最终MP4的相同时间帧核对。

最终视频：1920×1080，60fps，36秒，2160帧全部解码通过，静音。原生绘图480×270，整数4倍放大。详见 `render-verification.json`。

安装的pixel-video渲染器在 `pixelkit/pk.py:764` 使用 Unix `fork`。Windows下使用项目的 `render_windows.py` 调用相同 `Scene.frame()`，有界线程生成帧后交给FFmpeg H.264编码；未修改技能文件。英文LCD字形及布局仍由原技能check检查。

演示分数来自已运行的本地人工夹具，未调用JeV或任何模型API。完整来源与逐阶段时间轴见 `../FACTS.md`。
