# RLHF / RLVR / Jev RLCD 像素训练讲解

主版slide第25–27页默认使用中文版，各32秒，模块、阶段、动态说明与双行字幕均为中文，保留RLHF/RLVR/RLCD、PPO/KL和必要公式。480×270绘制，整数4倍到1920×1080，60fps，静音。

中文版本在 `scene_zh.py`，由 `localize_zh.py` 从英文 `scene.py` 生成。修改翻译应改 `localize_zh.py` 后重新生成。`chinese_font.py` 使用本机 Windows 宋体生成12像素中文字形，字幕行重新排布；仅渲染需要字体，成品MP4离线播放不需要安装字体。没有修改已安装的skill文件。

先读FACTS.md。所有数字来自prep.py的确定性玩具计算，没有运行真实模型。Jev的具体损失与优化器未公开；不要把本片的log loss示例说成真实RLCD实现。RLVR参考答案只供验证器使用。

## 重跑（项目根目录）

```powershell
python experiment/jev_training_pixel/prep.py
$env:PYTHONPATH = 'X:\Items\Jev-proj\experiment\jev_pixel_explainer\.vendor'
Push-Location experiment/jev_training_pixel
python -X utf8 localize_zh.py
python -X utf8 C:/Users/YuTao/.codex/skills/pixel-video/pxv check scene_zh.py:RLHF
python -X utf8 C:/Users/YuTao/.codex/skills/pixel-video/pxv check scene_zh.py:RLVR
python -X utf8 C:/Users/YuTao/.codex/skills/pixel-video/pxv check scene_zh.py:RLCD
python -X utf8 render_zh.py
python -X utf8 publish_zh.py
Pop-Location
python experiment/jev_practice/build_slides_v4.py
python experiment/jev_practice/verify_slides_v4.py
```

Windows渲染适配器复用pixel-video的Scene.frame与FFmpeg，因技能默认渲染器使用Unix fork而单独适配；没有修改技能文件。依赖沿用jev_pixel_explainer/.vendor和当前Python环境。

out/包含MP4、poster、逐阶段联系表、像素检查日志与逐帧解码报告。中文文件名带 `-zh`，英文历史视频保留；英文重渲染仍用 `render_windows.py`。`publish_zh.py` 检查解码报告、生成中文封面，并同步MP4与PNG到slides/media。中文验收见out/verification-zh.md，英文历史验收见out/verification.md。
