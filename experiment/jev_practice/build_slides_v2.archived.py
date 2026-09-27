"""Build kelip-format standalone practice slides and integrate them into the main deck."""
import html
import json
import re
import shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SLIDES=ROOT/'related_work/08-第30期-Jev-不生成文本的决策模型/slides'
esc=html.escape

def text(x,y,value,size=30,color='#1D1D1F',weight=400,anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{esc(str(value))}</text>'
def box(x,y,w,h,title,subtitle='',blue=False):
    color='#0071E3' if blue else '#1D1D1F'
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="{"#E8F0FE" if blue else "#F5F5F7"}"/>'+text(x+28,y+54,title,32,color,600)+(text(x+28,y+101,subtitle,24,'#6E6E73') if subtitle else '')
def arrow(x1,y1,x2,y2,blue=False):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{"#0071E3" if blue else "#8E8E93"}" stroke-width="4" marker-end="url(#{"arB" if blue else "ar"})"/>'
def svg(content):
    return f'<div class="diagbox pad"><svg class="sv" viewBox="0 0 1600 560" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">{content}</svg></div>'
def slide(title,sub,body,sec='Jev 实战',extra=''):
    return f'<section class="slide practice-v2 {extra}" data-sec="{sec}" data-title="{esc(title)}"><div class="kicker"><b>实战</b>{sec}</div><h1>{title}</h1><div class="sub">{sub}</div>{body}</section>'
def card(label,title,detail):
    return f'<article><small>{label}</small><h2>{title}</h2><p>{detail}</p></article>'

def main():
    comp=json.loads((HERE/'results/compaction.json').read_text(encoding='utf-8'))
    before=comp['stats']['charsBefore'];after=comp['stats']['charsAfter'];ratio=comp['reduction_ratio']*100
    nano=json.loads((ROOT/'related_work/projects/NanoJev-main/web/dev/side_by_side_results.json').read_text(encoding='utf-8'))['examples'][0]
    replay={'size':nano['size'],'initial':nano['initial'],'systems':[{'name':s['name'],'id':s['id'],'summary':s['summary'],'positions':[f['position'] for f in s['frames']]} for s in nano['systems']]}
    pages=[]
    pages.append(slide('Jev，接进代码之后','第 30 期 · 机制动画与四个离线实践',
        '<div class="practice-hero"><div class="hero-line">把<span>判断</span><br>变成可执行的选择</div>'
        '<div class="hero-flow"><b>材料</b><i>→</i><b>有限问题</b><i>→</i><b>概率</b><i>→</i><b>代码分支</b></div>'
        '<p>滚轮 / 触控滑动 / ← → 翻页　·　G 目录　·　F 全屏</p></div>','00 从机制开始'))
    body=box(0,175,410,180,'一份 state','材料、约束、当前环境')+arrow(430,265,520,265)
    for y,title,sub in [(25,'Choice · 选择题','从给定选项中选一个'),(205,'Score · 评分题','按明确的尺度打分'),(385,'Noul · 是非题','判断一个命题为真的程度')]:
        body+=box(550,y,485,140,title,sub,True)+arrow(1055,y+70,1135,y+70)+box(1160,y,440,140,{'Choice · 选择题':'选项 + 分布','Score · 评分题':'分数 + 分布','Noul · 是非题':'0–1 数值'}[title], 'Choice / Score 另有 confidence' if y==25 else '')
    pages.append(slide('同一份材料，分别回答有限问题','TypeSafe 官方接口 · 各问题独立评估 · 返回值直接由程序消费',svg(body),'01 输入与输出'))
    pages.append(slide('从材料到动作，用像素动画走一遍','接口与应用机制示意 · 英文像素字幕 · 人工分数，未运行 Jev',
        '<div class="fig card"><video data-pixel-video muted loop autoplay playsinline controls preload="auto" poster="media/jev-decision-mechanism.png" src="media/jev-decision-mechanism.mp4"></video></div>','01 输入与输出'))
    body=''
    for i,(x,title,sub) in enumerate([(0,'输入材料','重复扣款，需要退款'),(405,'限定候选','billing / tech / unknown'),(810,'返回分布','0.82 / 0.12 / 0.06'),(1215,'执行策略','超过门槛才进入队列')]):
        body+=f'<g data-step-node="{i}">'+box(x,145,365,190,title,sub,i==3)+'</g>'
        if i<3:body+=arrow(x+374,240,x+395,240)
    body+=text(800,430,'阈值 0.70 是本例的应用策略；最大候选概率不等于 API confidence。',27,'#6E6E73',anchor='middle')
    pages.append(slide('模型给出分布，代码决定下一步','J / K 逐步讲解；蓝色框是当前讲解环节',
        '<div data-mechanism>'+svg(body)+'</div><div class="step-controls" data-interactive><button id="mechanism-back">上一步 K</button><span class="mechanism-counter">1 / 4</span><button id="mechanism-step">下一步 J</button><span id="mechanism-caption">先提供完整的当前材料</span></div>','01 输入与输出','mechanism-slide'))
    rows=[('awesome-jev','案例目录与标签工具','离线测试与源码阅读'),('fast-jev-compaction','从工具历史里选择保留项','实际调用原库'),('Jarvis','判断、生成、排序分工','构造原始题目'),('JEVfire','为有限候选打分并解码','阈值与拒答处理'),('NanoJev','训练式决策模型、游戏环境','播放已有轨迹')]
    table='<div class="tblwrap"><table class="tbl left wrap"><thead><tr><th>项目</th><th>落在系统的哪一层</th><th>这次可以运行什么</th></tr></thead><tbody>'+''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for a,b,c in rows)+'</tbody></table></div>'
    pages.append(slide('五个项目，选出最短的落地路径','本地 ZIP 源码快照 · 完整分析见《开源项目分析.md》',table,'02 选型'))
    body=text(0,45,'历史中的工具调用',28,'#6E6E73')+text(875,45,'对旧调用问两道 Noul',28,'#6E6E73')
    for i,(a,b) in enumerate([('t1 · 旧搜索','结果已失效'),('t2 · 读源文件','内容可重新读取'),('t3 · 测试报错','唯一错误证据'),('t4 · 最近读取','最近消息固定保留')]):
        body+=box(0,75+i*112,640,96,a,'',i==3)+text(300,135+i*112,b,27,'#6E6E73')
    body+=arrow(685,250,810,250)+box(860,90,700,150,'保留这个调用吗？','需要知道做过什么、输入是什么')+box(860,280,700,150,'保留完整结果吗？','完整内容是否仍然不可替代')
    pages.append(slide('先给工具历史编号，再问是否保留','fast-jev-compaction · 合成对话 · 发给判断器的 state 会省略结果正文',svg(body),'03 上下文裁剪'))
    body=''
    for i,(title,p,decision,detail) in enumerate([('t1 · Search','0.10 / 0.05','成对删除','调用和结果一起移除'),('t2 · Read','0.90 / 0.10','截短结果','保留调用 + 前 80 字符'),('t3 · Test','0.95 / 0.95','完整保留','唯一错误证据继续存在')]):
        x=i*545;body+=box(x,45,510,145,title,'P(调用) / P(结果)')+text(x+28,260,p,43,'#0071E3',600)+arrow(x+255,294,x+255,354)+box(x,384,510,145,decision,detail)
    pages.append(slide('两个概率，落到三种确定动作','人工固定概率 · 阈值 0.50 · 结果过线优先保留；t4 固定保留不参与判断',svg(body),'03 上下文裁剪'))
    pages.append(slide('原库已执行，关键证据仍然在','离线夹具实跑 · 输出原文未被摘要重写',
        f'<div class="result-hero"><div class="large-metric">{before:,}<span>→</span>{after:,}</div><div class="metric-caption">字符数 · 按上游库计数口径 · 缩短 {ratio:.2f}%</div>'
        '<div class="evidence-line"><b>用户约束保留</b><b>错误证据保留</b><b>调用 / 结果不孤立</b></div>'
        '<p>这组人工概率验证的是执行逻辑。真实效果还要看裁剪后的任务成功率。</p></div>','03 上下文裁剪'))
    pages.append(slide('概率不够高，就交回人工处理','JEVfire 原解码器已验证 · 人工分数 · 滑块演示同一门控公式',
        '<div class="gate-grid" data-interactive><div class="gate-chart"><div class="gate-choice"><button id="gate-high" class="selected">明确样例</button><button id="gate-low">模糊样例</button></div><div id="gate-bars"></div></div>'
        '<div class="gate-policy"><label for="gate-threshold">接受阈值 <b id="gate-number">0.70</b></label><input id="gate-threshold" type="range" min="0" max="1" step="0.01" value="0.70"><div id="gate-output" aria-live="polite">billing</div><pre id="gate-json"></pre><p>归一化分数不是经过验证的正确率。</p></div></div>','04 候选与拒答'))
    body=''
    for i,(title,sub) in enumerate([('聊天材料','最近 10 条'),('7 道判断题','choice / score / noul'),('生成模型','草拟 3 条候选'),('再做一次选择','候选回复排序')]):
        x=i*405;body+=box(x,165,365,180,title,sub,i in [1,3]);
        if i<3:body+=arrow(x+375,255,x+395,255)
    body+=text(800,435,'本轮：原题目构造代码已运行，三条回复由人工写好；未调用生成或排序模型。',27,'#6E6E73',anchor='middle')
    pages.append(slide('Jarvis：先判断，再起草，再选择','应用分工 · Jev 承担判断任务，生成模型负责文字',svg(body),'05 对话助手'))
    panels=''.join(f'<article class="maze-panel"><h2>{esc(s["name"])}</h2><canvas width="440" height="440" aria-label="{esc(s["name"])} 迷宫轨迹"></canvas><div class="maze-readout"></div></article>' for s in replay['systems'])
    pages.append(slide('把动作轨迹直接放进幻灯片','NanoJev 上游所选迷宫轨迹 · 回放，不是本机实时推理',
        '<div class="maze-panels">'+panels+'</div><div class="maze-controls" data-interactive><button id="maze-play">播放轨迹</button><button id="maze-reset">从头开始</button><input id="maze-step" type="range" min="0" max="4726" step="1" value="225"><span id="maze-position">225 / 4726</span></div>'
        '<p class="maze-note">三个系统共享探索代码；单条展示轨迹不能代表完整评测排名。</p>','06 游戏回放'))
    pages.append(slide('先验证能否执行，再评价是否判断正确','离线实战的证据范围',
        '<div class="practice-two">'+card('本轮已验证','结构与执行','原库能裁剪历史<br>分数能触发接受 / 拒答<br>题目能构造、轨迹能回放')+card('下一轮要测','模型与任务','选项是否选对<br>置信度是否校准<br>最终任务成功率与总耗时')+'</div>','07 如何评价'))
    pages.append(slide('重跑结果，再回到 slide 讲解','从项目根目录执行 · 依赖准备见 experiment/jev_practice/README.md',
        '<div class="command-board"><small>重新执行离线代码</small><code>python experiment/jev_practice/run_offline.py</code><small>重新生成这组 slide</small><code>python experiment/jev_practice/build_slides_v2.py</code></div>'
        '<p class="run-note">双击 slides/deck-practice.html 即可讲解。<br>视频与轨迹在本地，翻页不依赖 Python 服务。</p>','07 如何评价'))
    body=box(0,165,450,185,'限定问题','业务先定义选项与含义')+arrow(475,258,555,258)+box(585,165,450,185,'模型判断','返回可检查的数值')+arrow(1060,258,1140,258)+box(1170,165,430,185,'代码行动','记录、回退、评测',True)
    pages.append(slide('把有限决策，做成可测的模块','Jev 实战 · 机制可解释，执行可复现，边界可核验',svg(body),'08 收尾'))
    content='\n'.join(pages)
    css=(HERE/'slides-v2.css').read_text(encoding='utf-8')
    navigation=(HERE/'slide-navigation.js').read_text(encoding='utf-8')
    interactions=(HERE/'slides-v2-interactions.js').read_text(encoding='utf-8')
    data='<script id="maze-data" type="application/json">'+json.dumps(replay,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+'</script>'
    controls='''<div id="deck-controls" data-interactive><button id="deck-prev" title="上一页" aria-label="上一页">‹</button><span id="deck-count"></span><button id="deck-next" title="下一页" aria-label="下一页">›</button><button id="deck-menu" aria-expanded="false">☰ 目录</button><button id="deck-fullscreen">全屏</button></div><nav id="deck-toc" aria-label="全部页面" hidden></nav><div id="deck-hint">滚轮 / 滑动 / ← → 翻页 · G 目录 · F 全屏</div>'''
    scripts=data+'<script>'+navigation+'</script><script>'+interactions+'</script>'
    current=(SLIDES/'deck.html').read_text(encoding='utf-8')
    backup=SLIDES/'deck.before-practice-v2.html'
    if not backup.exists():shutil.copy2(SLIDES/'deck.html',backup)
    # Preserve user-owned original content; replace only our delimited practice block.
    base=re.sub(r'<!-- PRACTICE_START -->.*?<!-- PRACTICE_END -->\s*','',current,flags=re.S)
    base=re.sub(r'<!-- PRACTICE_V2_START -->.*?<!-- PRACTICE_V2_END -->\s*','',base,flags=re.S)
    base=re.sub(r'<style id="practice-v2-style">.*?</style>\s*','',base,flags=re.S)
    prefix=base[:base.index('<!-- 1 封面 -->')]
    prefix=prefix.replace('</head>',f'<style id="practice-v2-style">{css}</style>\n</head>')
    prefix=re.sub(r'<title>.*?</title>','<title>Jev · 实战与像素机制讲解</title>',prefix)
    standalone=prefix+content+'\n</div>'+controls+scripts+'</body></html>'
    (SLIDES/'deck-practice.html').write_text(standalone,encoding='utf-8')
    start=base.index('<!-- 1 封面 -->')
    if '<div id="nav-hot">' in base:
        original_body=base[start:base.index('<div id="nav-hot">')]
    else:
        original_body=base[start:base.index('<div id="deck-controls"')]
    marker='<!-- 39 过渡 -->'
    if marker not in original_body:raise RuntimeError('Original insertion marker not found')
    original_body=original_body.replace(marker,'<!-- PRACTICE_V2_START -->\n'+content+'\n<!-- PRACTICE_V2_END -->\n'+marker,1)
    (SLIDES/'deck.html').write_text(prefix+original_body+controls+scripts+'</body></html>',encoding='utf-8')
    print('Built standalone 14 slides + complete 56 slides; new practice at 39–52.')

if __name__=='__main__':main()
