"""Compatibility entry: build the real slides, retire the tab dashboard URL."""
import html
import json
import shutil
from pathlib import Path
from build_slides_v4 import main as build_slides

def main():
    here=Path(__file__).resolve().parent
    demo=here/'demo.html'
    legacy=here/'demo.legacy.html'
    if demo.exists() and not legacy.exists():shutil.copy2(demo,legacy)
    build_slides()
    target='../../related_work/08-第30期-Jev-不生成文本的决策模型/slides/deck.html'
    demo.write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>打开 Jev 实战 slide</title>'
        '<body><p>演示已升级为可翻页 slide。<a href="'+html.escape(target)+'">打开实战幻灯片</a></p>'
        '<script>location.replace('+json.dumps(target,ensure_ascii=False)+');</script></body></html>',encoding='utf-8')
    print('Legacy demo URL now opens the slide deck; dashboard preserved as demo.legacy.html.')

if __name__=='__main__':main()
