"""Windows adapter for pixel-video's scene renderer (pxv hard-codes Unix fork).

Uses exactly Scene.frame(), with a bounded producer and the imageio FFmpeg binary.
No changes to the installed skill. No audio. Decode every final frame for verification.
"""
from pathlib import Path
import sys
import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent / 'jev_pixel_explainer/.vendor'))
import cv2
import imageio_ffmpeg
import scene_zh as scenes
from pixelkit import ensure_setup

def render(kind):
    cv2.setNumThreads(1)
    scene = ensure_setup(getattr(scenes,kind)())
    out = HERE / 'out' / f'jev-training-{kind.lower()}-zh.mp4'
    n = round(scene.DURATION * scene.FPS)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    proc = subprocess.Popen([ffmpeg,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
        '-s','1920x1080','-r',str(scene.FPS),'-i','-','-an','-c:v','libx264',
        '-preset','medium','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],
        stdin=subprocess.PIPE)
    begin=time.monotonic()
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            for start in range(0,n,24):
                for buf in pool.map(lambda i: scene.frame(i/scene.FPS).tobytes(), range(start,min(start+24,n))):
                    proc.stdin.write(buf)
                if start%120==0: print(f'frame {min(start+24,n)}/{n}; {time.monotonic()-begin:.1f}s',flush=True)
        proc.stdin.close()
        if proc.wait()!=0: raise RuntimeError('FFmpeg encode failed')
    except Exception:
        proc.kill()
        raise
    cap=cv2.VideoCapture(str(out))
    width,height=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps=cap.get(cv2.CAP_PROP_FPS)
    decoded=0
    while True:
        ok,frame=cap.read()
        if not ok: break
        decoded+=1
    cap.release()
    assert (width,height)==(1920,1080)
    assert abs(fps-60)<.001 and decoded==n
    report=dict(output=str(out),width=width,height=height,fps=fps,decoded_frames=decoded,
        duration_seconds=decoded/fps,silent=True,native_canvas=[480,270],integer_scale=4,
        fixture_model_run=False,render_seconds=round(time.monotonic()-begin,2))
    (HERE/'out'/f'{kind.lower()}-zh-render-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    for kind in (sys.argv[1:] or ['RLHF','RLVR','RLCD']): render(kind)
