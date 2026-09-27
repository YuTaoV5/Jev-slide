"""Render all slides and exercise offline demo/replay in local Chrome."""
import json
import math
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SLIDES=ROOT/'related_work/08-第30期-Jev-不生成文本的决策模型/slides'
OUT=HERE/'results/render'

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

def contact(paths,target,columns=4):
    w,h,gap=480,270,12
    sheet=Image.new('RGB',(columns*(w+gap)+gap,math.ceil(len(paths)/columns)*(h+gap+22)+gap),'#d2d2d7')
    draw=ImageDraw.Draw(sheet)
    for i,path in enumerate(paths):
        x=gap+(i%columns)*(w+gap); y=gap+(i//columns)*(h+gap+22)
        with Image.open(path) as im: sheet.paste(im.resize((w,h),Image.Resampling.LANCZOS),(x,y))
        draw.text((x+5,y+h+2),path.stem,fill='#1d1d1f')
    sheet.save(target)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}/'
    errors=[]; failed=[]; overflow=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='chrome',headless=True,args=['--no-proxy-server'])
        page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
        page.on('pageerror',lambda err:errors.append(str(err)))
        page.on('response',lambda res:failed.append({'url':res.url,'status':res.status}) if res.status>=400 else None)
        replay=base+'related_work/projects/NanoJev-main/web/dev/side-by-side.html#maze'
        page.goto(replay)
        page.wait_for_function('window.nanojevComparison?.ready === true')
        page.evaluate('window.nanojevComparison.setFrame(0,225)')
        snapshot=page.evaluate('window.nanojevComparison.getSnapshot()')
        page.locator('#modelPanels').screenshot(path=str(SLIDES/'media/practice-nanojev.png'))
        page.evaluate('window.nanojevComparison.setFrame(1,50)')
        snake=page.evaluate('window.nanojevComparison.getSnapshot()')
        page.screenshot(path=str(OUT/'nanojev-snake.png'))
        page.goto(base+'experiment/jev_practice/demo.html')
        assert '8,144' in page.locator('#charMetric').inner_text()
        page.locator('#toggleHistory').click()
        assert '唯一错误证据' in page.locator('#history').inner_text()
        page.screenshot(path=str(OUT/'demo-compaction.png'))
        page.locator('[data-tab="fire"]').click()
        page.locator('[data-score="1"]').click()
        assert '人工处理' in page.locator('#fireResult').inner_text()
        page.locator('#threshold').evaluate("e=>e.value='0.30'")
        page.locator('#threshold').dispatch_event('input')
        assert 'billing' in page.locator('#fireResult').inner_text()
        page.locator('#threshold').evaluate("e=>e.value='0.70'")
        page.locator('#threshold').dispatch_event('input')
        page.screenshot(path=str(OUT/'demo-abstention.png'))
        page.locator('[data-tab="jarvis"]').click()
        assert page.locator('#questionList .row').count()==7
        page.locator('[data-tab="nano"]').click()
        page.locator('#loadReplay').click()
        iframe=page.frame_locator('#replay')
        iframe.locator('#next').click()
        page.wait_for_timeout(200)
        # Render full deck: preserve actual page navigation and local image loading.
        deck=base+quote(str((SLIDES/'deck.html').relative_to(ROOT)).replace('\\','/'))
        page.goto(deck+'#1')
        count=page.locator('section.slide').count()
        paths=[]
        for n in range(1,count+1):
            if n>1: page.keyboard.press('ArrowRight')
            page.wait_for_timeout(90)
            assert page.locator('.slide.active').evaluate('(s)=>[...document.querySelectorAll("section.slide")].indexOf(s)+1')==n
            page.wait_for_function('Array.from(document.querySelectorAll(".slide.active img")).every(i=>i.complete && i.naturalWidth>0)')
            path=OUT/f'slide-{n:02d}.png';page.screenshot(path=str(path));paths.append(path)
            if 39<=n<=45:
                issue=page.evaluate('''() => {const s=document.querySelector('.slide.active');const b=s.getBoundingClientRect();return [...s.querySelectorAll('h1,.sub,article,pre,table')].filter(e=>{const r=e.getBoundingClientRect();return r.right>b.right+2||r.bottom>b.bottom+2||e.scrollWidth>e.clientWidth+3||e.scrollHeight>e.clientHeight+3}).map(e=>e.tagName+': '+e.textContent.slice(0,50));}''')
                if issue: overflow.append({'slide':n,'items':issue})
        contact(paths,SLIDES/'预览-全部页面.png')
        contact(paths[38:45],SLIDES/'预览-实战页面.png',columns=2)
        browser.close()
    server.shutdown();server.server_close()
    report={'slide_count':count,'console_errors':errors,'http_errors':failed,'practice_overflow':overflow,
            'demo_checks':['before/after','abstain at .70','accept at .30','7 questions','iframe replay'],
            'maze_snapshot':snapshot,'snake_snapshot':snake}
    (HERE/'results/browser-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'slides':count,'console_errors':errors,'http_errors':failed,'overflow':overflow},ensure_ascii=False))
    assert not errors and not failed and not overflow

if __name__=='__main__':main()
