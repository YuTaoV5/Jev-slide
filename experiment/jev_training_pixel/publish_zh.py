"""Verify completed Chinese renders, generate posters, then publish local media."""
from pathlib import Path
import json
import shutil
from PIL import Image
import scene_zh
from pixelkit import ensure_setup

HERE=Path(__file__).resolve().parent
MEDIA=HERE.parents[1]/'related_work/08-第30期-Jev-不生成文本的决策模型/slides/media'
for kind in ('RLHF','RLVR','RLCD'):
    report=json.loads((HERE/'out'/f'{kind.lower()}-zh-render-verification.json').read_text())
    assert report['decoded_frames']==1920 and report['fps']==60
    assert report['width']==1920 and report['height']==1080
    scene=ensure_setup(getattr(scene_zh,kind)())
    stem=f'jev-training-{kind.lower()}-zh'
    Image.fromarray(scene.frame(29.5)).save(HERE/'out'/f'{stem}.png')
    for ext in ('mp4','png'):
        shutil.copy2(HERE/'out'/f'{stem}.{ext}',MEDIA/f'{stem}.{ext}')
print('Published 3 Chinese videos and posters; English files retained.')
