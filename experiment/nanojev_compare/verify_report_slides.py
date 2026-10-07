"""Render and validate the updated report deck, offline and at 1920x1080."""
import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
SLIDES = ROOT / "related_work/Jev报告slide/slides"
OUT = Path(__file__).resolve().parent / "results/report-slides"


def contact(paths, target):
    cols, w, h, gap = 4, 480, 270, 12
    canvas = Image.new("RGB", (cols*(w+gap)+gap, math.ceil(len(paths)/cols)*(h+gap+22)+gap), "#d2d2d7")
    draw = ImageDraw.Draw(canvas)
    for i,p in enumerate(paths):
        x,y=gap+(i%cols)*(w+gap),gap+(i//cols)*(h+gap+22)
        with Image.open(p) as source:canvas.paste(source.convert("RGB").resize((w,h),Image.Resampling.LANCZOS),(x,y))
        draw.text((x,y+h+3),p.stem,fill="#1d1d1f")
    canvas.save(target)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    current=(SLIDES/'deck.html').read_text(encoding='utf-8')
    old=(Path(__file__).resolve().parent/'report_source/base-deck.html').read_text(encoding='utf-8')
    for before,after in [('03 唯一实战 · NanoJev','07 上游回放 · NanoJev'),
                         ('04 kernel 定位方案','09 kernel 定位方案'),
                         ('05 验证与推进','10 验证与推进'),('09 未来','11 未来')]:
        old=old.replace(before,after)
    pattern=r'<section\b[^>]*class="slide\b.*?</section>'
    before=re.findall(pattern,old,re.S)
    after=re.findall(pattern,current,re.S)
    assert len(after)==65 and len(before)==60
    assert after[:46]==before[:46] and after[62:]==before[57:], 'Retained original slide body changed'
    assert not re.search(r'ai4[- ]?loc|kernel|runMockAnalysis', ''.join(after),re.I), 'Removed subject remains in active deck'
    report={'count':65,'retained_49_original_sections_preserved':True,'ai4loc_removed':True,'page_errors':[],'layout_issues':[],'external_requests':[]}
    shots=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='chrome',headless=True,args=['--force-device-scale-factor=1'])
        page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
        page.on('pageerror',lambda e:report['page_errors'].append(str(e)))
        def block(route):
            report['external_requests'].append(route.request.url)
            route.abort()
        page.route(re.compile(r'^https?://'),block)
        page.goto((SLIDES/'deck.html').as_uri(),wait_until='load')
        page.wait_for_function('window.jevDeck && window.jevDeck.count===65')
        page.evaluate('document.fonts.ready')
        for index in range(65):
            page.evaluate('(i)=>window.jevDeck.show(i)',index)
            page.wait_for_timeout(80)
            page.evaluate("document.querySelectorAll('video').forEach(v=>v.pause())")
            issues=page.evaluate('''() => {
              const s=document.querySelector('.slide.active'); const out=[];
              const r=s.getBoundingClientRect();
              for(const e of s.querySelectorAll('h1,.sub,.exp-cards article,.exp-table,.exp-bars,.exp-flow article,.exp-note')){
                const b=e.getBoundingClientRect();
                if(b.bottom>r.bottom-30||b.right>r.right-40||b.left<r.left)out.push({kind:'bounds',text:e.textContent.slice(0,60),bottom:b.bottom});
                if(e.scrollHeight>e.clientHeight+3||e.scrollWidth>e.clientWidth+3)out.push({kind:'overflow',text:e.textContent.slice(0,60)});
              }
              for(const img of s.querySelectorAll('img'))if(!img.complete||img.naturalWidth===0)out.push({kind:'image',src:img.getAttribute('src')});
              return out;
            }''')
            report['layout_issues'].extend({'page':index+1,**x} for x in issues)
            shot=OUT/f'slide-{index+1:02}.png';page.screenshot(path=str(shot));shots.append(shot)
        page.keyboard.press('Home');assert page.evaluate('window.jevDeck.current')==0
        page.keyboard.press('End');assert page.evaluate('window.jevDeck.current')==64
        page.evaluate('window.jevDeck.show(46)');page.keyboard.press('ArrowRight');assert page.evaluate('window.jevDeck.current')==47
        page.keyboard.press('g');assert page.locator('#deck-toc button').count()==65
        report['navigation_passed']=True
        browser.close()
    contact(shots,SLIDES/'预览-全部页面.png')
    contact(shots[46:62],SLIDES/'预览-服务器实验.png')
    (OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
    if report['page_errors'] or report['layout_issues'] or report['external_requests']:raise SystemExit(1)


if __name__=='__main__':main()
