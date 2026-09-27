"""Brand-free Jev narrative: NanoJev evidence -> kernel investigation design."""
import html,json,re,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
DEST=ROOT/'related_work/08-第30期-Jev-不生成文本的决策模型'
SLIDES=DEST/'slides'
E=html.escape
PAGES=[]
def text(x,y,s,size=32,color='#1D1D1F',weight=400,anchor='start'):
 return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{E(str(s))}</text>'
def box(x,y,w,h,title,sub='',blue=False):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="{"#E8F0FE" if blue else "#F5F5F7"}"/>'+text(x+28,y+60,title,34,'#0071E3' if blue else '#1D1D1F',600)+(text(x+28,y+112,sub,25,'#6E6E73') if sub else '')
def arrow(a,b,c,d):return f'<path d="M{a} {b} L{c} {d}" stroke="#A1A1A6" stroke-width="4" fill="none" marker-end="url(#ar)"/>'
def diagram(s):return '<div class="diagbox pad"><svg class="sv" viewBox="0 0 1600 560">'+s+'</svg></div>'
def flow(items,caption=''):
 n=len(items);w=(1600-(n-1)*65)/n;s=''
 for i,(a,b) in enumerate(items):
  x=i*(w+65);s+=box(x,165,w,170,a,b,i==n-1)
  if i<n-1:s+=arrow(x+w+10,250,x+w+51,250)
 return diagram(s+text(800,440,caption,29,'#6E6E73',anchor='middle'))
def table(headers,rows):
 return '<div class="tblwrap"><table class="tbl left wrap"><thead><tr>'+''.join('<th>'+a+'</th>' for a in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+a+'</td>' for a in r)+'</tr>' for r in rows)+'</tbody></table></div>'
def big(a,b,c):return f'<div class="statement"><div>{a}</div><p>{b}</p><small>{c}</small></div>'
def add(title,sub,body,sec,speech,q,a,source,action='正常翻页，停留约 45 秒。'):
 PAGES.append(dict(title=title,sub=sub,body=body,sec=sec,speech=speech,question=q,answer=a,source=source,action=action))

def main(emit=True):
 PAGES.clear()
 nano=json.loads((ROOT/'related_work/projects/NanoJev-main/web/dev/side_by_side_results.json').read_text(encoding='utf-8'))['examples'][0]
 audit=json.loads((HERE/'results/nano-maze-audit.json').read_text(encoding='utf-8'))
 replay={'size':nano['size'],'initial':nano['initial'],'systems':[{'name':'Jev' if s['id']=='jev' else 'NanoJev','id':s['id'],'summary':s['summary'],'positions':[f['position'] for f in s['frames']]} for s in nano['systems'][:2]]}
 official='TypeSafe 官方 Introduction：https://docs.typesafe.ai/introduction（2026-09-27 核查）'
 ns='NanoJev README.md；scripts/evaluate_model_edges_maze.py；web/dev/side_by_side_results.json；本地 results/nano-maze-audit.json'
 ks='X:/Items/1_AI4-Loc/server/index.js:84–101；docs/IMPLEMENTATION_PLAN.md。后续设计均为本次建议，尚未接入。'
 add('Jev：让判断推动问题定位','机制 → NanoJev 离线实战 → kernel 定位方案',big('从<span>选择下一步</span><br>到缩短排查路径','让有限判断进入可验证的工程流程','第 30 期 · 离线讲解与方案讨论'), '01 为什么需要它',
 '今天围绕一个问题展开：能不能用一个不写长篇回答的模型，让定位过程少走弯路？先用四页说明 Jev 的输入输出，再通过 NanoJev 的迷宫轨迹拆解“更快到终点”的原因，最后落到 kernel 定位系统的接入设计。实战只有 NanoJev。游戏结果是上游录制，本轮做了控制器重放和无模型对照；kernel 部分是方案，不是已上线能力。',
 '这次汇报希望做什么决策？','先确认试点方向：证据候选排序与下一步取证建议。是否采购、部署和定性能目标，要等真实案例评估。',ns+'；'+ks)
 add('先把大问题，拆成有限判断','程序需要可执行的分支；工程师需要可核对的证据',flow([('当前材料','日志、候选、约束'),('有限问题','哪个相关？缺什么？'),('下一步','取证、继续、复核')],'判断模块的价值，用整条任务的结果衡量'), '01 为什么需要它',
 '定位不是一句“根因是什么”就结束。它是一连串判断：哪些证据相关、哪些假设值得先看、现在缺什么材料、什么时候必须交回工程师。Jev 的机会在这些小而明确的判断点。它能否有用，最终看整个排查过程，而不只看返回结果格式是否正确。',
 '规则也能做，为什么要模型？','精确匹配继续用规则；只有规则难覆盖的语义判断进入候选试点，并保留规则基线检验增益。',official)
 add('材料与题目进，类型化答案出','Jev 的接口契约 · Choice / Score 的 confidence 是独立字段',table(['问题','返回什么','定位场景中的拟用法'],[
 ['Choice','选项 + 概率分布 + confidence','从候选取证动作中选择一个'],['Noul','命题为真的程度（0–1）','证据是否支持某个具体判断'],['Score','等级期望 + 分布 + confidence','按明确定义的等级评估相关性']]),'02 模型机制',
 '输入包含 state 和 typed questions。Choice 用来在给定集合里选择；Noul 针对一个命题；Score 面向有明确文字描述的有序等级。输出给代码消费。Choice 和 Score 的 confidence 与最大选项概率不是同一个字段。多个问题独立评估，不意味着多道题能自行推导出一个没有提供证据的完整因果链。',
 '不生成文本，怎么说明为什么？','由程序绑定题目、候选与原始证据 ID；需要自然语言解释时另由工程师或生成模型撰写，并核验引用。',official)
 add('用 36 秒看清：判断怎样触发动作','像素机制示意 · 人工分数 · 不代表本轮调用 Jev', '<div class="fig card"><video muted loop autoplay playsinline controls preload="auto" poster="media/jev-decision-mechanism.png" src="media/jev-decision-mechanism.mp4"></video></div>','02 模型机制',
 '看动画中的四个位置：材料进入、有限题目形成、返回结构化分数、应用策略决定动作。这里保留的分数是人工示意，0.70 也只是示意阈值。它解释接口和业务代码的关系，不展示 Jev 内部架构，不作为另一个实战案例。真正的离线实战从下一页 NanoJev 开始。',
 '这个概率可以直接当成正确率吗？','不可以。应在真实业务标注集上检验校准与错误成本，再选择接受、补证据或拒答策略。',official+'；experiment/jev_pixel_explainer/FACTS.md','播放一轮约 36 秒；指向低分转人工的部分，随后翻页。')
 add('NanoJev 把“小判断”做成可训练模型','0.6B 开源实现 · 此图描述 NanoJev，不代表 Jev 的内部结构',flow([('局部状态 + 问题','给定候选方向'),('Qwen3-0.6B','编码候选路径'),('决策头','输出方向安全概率')],'迷宫里四个概率相互独立，不要求加起来等于 1'), '03 唯一实战 · NanoJev',
 'NanoJev 是一个基于 Qwen3-0.6B 的决策模型实现，使用决策头得到数值，而不逐字生成回答。在这个迷宫展示中，每到一个新位置，它针对四个方向给出独立的安全判断。这只是判断器，外面还有一个确定性的探索控制器。不能因为它复现类似接口，就把这个结构说成 Jev 的内部实现。',
 '本机真的跑了这个 0.6B 模型吗？','没有加载权重。本轮读取上游录制的概率与动作，逐步重放并核验控制器；另跑了完全不使用模型的对照。',ns)
 panels=''.join(f'<article class="maze-panel"><h2>{s["name"]}</h2><canvas width="440" height="440" aria-label="{s["name"]} 迷宫轨迹"></canvas><div class="maze-readout"></div></article>' for s in replay['systems'])
 add('同一张迷宫，NanoJev 先到终点','同一控制器 · 同一步数播放 · 上游录制轨迹', '<div class="maze-panels">'+panels+'</div><div class="maze-controls" data-interactive><button id="maze-play">播放轨迹</button><button id="maze-reset">从头开始</button><input id="maze-step" type="range" min="0" max="2738" step="1" value="225"><span id="maze-position"></span></div><p class="maze-note">蓝点：当前位置　黑点：终点　浅蓝线：已走路径　·　尝试包含撞墙</p>','03 唯一实战 · NanoJev',
 '这张 50×50 迷宫的起终点和探索代码一致。页面停在第 225 次尝试：NanoJev 已经到终点，Jev 还在探索。点击从头开始再播放，两边按动作尝试数同步；到终点的一方保持最终画面。这里的动画播放速度是展示设置，与真实 API 请求延迟无关。',
 '地图是不是完整给了模型？','展示的是完整地图，但模型通过 5×5 局部窗口观察；控制器只记住实际探索过的边，没有全图最短路兜底。',ns,'先解释第 225 次的静止画面，再从头播放约 15 秒；拖动滑块可复查。')
 add('少的是尝试次数：2,738 → 225','约为 1 / 12.17 · 没有测量推理延迟或端到端耗时', table(['所选轨迹','总尝试','撞墙','成功移动'],[['Jev','2,738','1,044','1,694'],['NanoJev','225','77','148']]),'03 唯一实战 · NanoJev',
 '一次尝试可能成功移动，也可能撞墙停在原地。Jev 的 2738 次由 1044 次撞墙和 1694 次成功移动组成；NanoJev 的 225 次由 77 次撞墙和 148 次移动组成。路径差异是累计形成的：每次分数都可能改变后续探索。12.17 是尝试数比值，不能写成吞吐、推理速度或费用提升倍数。',
 '是否说明 NanoJev 避障更准？','还不能。双方访问的位置不同，原子判断样本不一致；总撞墙数也受路径长度影响。需要固定相同状态的判断评测。',ns)
 add('控制器先过门槛，再优先靠近终点','原代码顺序 · 记录实际反馈，避免重复尝试已知墙壁',flow([('候选筛选','未试过且 p ≥ 0.5'),('方向排序','距离 → 访问次数 → p'),('实际尝试','记下通路或墙壁')],'没有方向过线就试低分方向；当前无新边就沿已知通路回退'), '03 唯一实战 · NanoJev',
 '理解结果的关键在控制器。先找未尝试且安全概率至少 0.5 的边，再优先选择曼哈顿距离更接近终点的方向，随后看访问次数、概率和固定方向顺序。全部低分时仍会探路，撞墙不是游戏立即失败。只有没有新边时，才在已验证的通路上用 BFS 返回探索前沿。因此模型和控制器共同决定行为。',
 '是不是模型直接规划了全局路线？','不是。模型给局部安全概率；目标距离、访问记忆、低分探路与已知通路回退都由代码完成。',ns)
 add('这次，NanoJev 把所有方向都放过了','143 个访问位置 × 4 个方向 · 最低概率仍为 0.688',big('<span>572 / 572</span>','记录中的方向概率全部超过 0.5','筛选不再排除方向；距离、访问记录和概率细微差异决定路线'),'03 唯一实战 · NanoJev',
 '复算结果很关键：NanoJev 在 143 个首次访问位置生成了 572 个概率，全部大于 0.5。控制器的门槛在这条轨迹上没有过滤掉任何方向，几何启发式因此能充分参与选路。Jev 则有更多方向落在门槛下，经历了 1216 次低分探路和 643 次已知通路回退；NanoJev 的这两项是 0 和 4。轨迹分布不同，这些数不能作为相同状态下的准确率比较。',
 '更快的主要原因到底是什么？','可核验的机制是：分数改变候选集合与排序，进而改变整条探索路径。这里表现出放行偏置与控制器的配合，不能归因为更准确的安全预测。',ns)
 add('移除模型判断，同一控制器只用 162 次','新增离线消融 · 所有方向固定 p = 0.5 · 同地图、同预算、同排序规则',table(['判断来源','尝试次数','撞墙次数'],[['Jev 上游录制','2,738','1,044'],['NanoJev 上游录制','225','77'],['本地常数对照：无模型','162','34']]),'03 唯一实战 · NanoJev',
 '为了确认功劳属于哪一层，我把判断器替换为常数 0.5，保留原始环境和控制器，实际离线执行。结果 162 次到达终点、撞墙 34 次。常数分数也全都过门槛，但平分时退回固定方向顺序；NanoJev 的细小概率差异仍会改变排序，所以两条路径不相同。这个对照说明该展示尚不能证明模型带来了增益，反而提醒我们必须保留无模型基线。',
 '是不是说明 Jev 没价值？','只能说明这一个迷宫上的控制器已很强。kernel 语义任务是否获益是另一项待验证问题，不能向两个方向过度推广。','experiment/jev_practice/analyze_nano_maze.py；results/nano-maze-audit.json；results/nano-maze-constant-trace.json')
 add('单条展示，不能替代成功率评估','上游独立 Maze test：10 个案例 · 与展示使用不同控制设置',big('<span>4 / 10</span>　vs　7 / 10','NanoJev　　　　　　　　　Jev','这页比较独立测试的成功数；不与前页的尝试次数混成一个排名'),'03 唯一实战 · NanoJev',
 '上游完整测试表里，Maze 十例成功数是 NanoJev 四例、Jev 七例。它采用测试协议的 seeded epsilon-greedy 控制器，与前面展示的局部边探索设置不同，不能直接合并。两个结果共同提醒我们：演示用来看机制，固定协议的测试用来看泛化；到达一次终点，也不等于系统整体更可靠。',
 '怎样公平比较？','固定观测、候选、控制器、预算、案例集与版本，同时报告成功率、失败、尝试数和墙钟时间，并保留无模型对照。','NanoJev README.md:54–63')
 add('迁移到定位：每一步都要减少无效排查','设计观点 · 把定位过程看成不断收集证据、修正候选的闭环',flow([('提出候选','保留多种可能'),('选择取证','优先能区分假设的证据'),('更新判断','验证、反驳、补缺')],'概率用于分配调查顺序；根因需要证据闭环'), '04 kernel 定位设计',
 '从游戏迁移到问题定位，值得保留的是分工方法：判断器给建议，工具返回实际反馈，控制器更新状态。我们希望降低重复查同一段日志、过早锁定假设和无效工具调用。终点不应定义为“模型给了最高分”，而是根因被证据与复现共同支持。',
 '为什么不直接让大模型一直分析？','保留其生成假设和解释的能力；针对频繁、边界明确的判断尝试更轻的组件，是否减少总成本要用配对实验确认。',ks)
 add('当前工作台已成形，分析核心仍是模拟','基于 AI4-Loc 实际代码核查 · 不是生产定位能力评测',table(['已经存在','当前实现','拟接入位置'],[['日志 / 符号包上传','/api/analyze 创建任务','上传后建立可追踪输入清单'],['任务进度与报告','runMockAnalysis 定时推进','替换为真实 worker + 证据链'],['评分与门禁界面','固定报告与示例分数','接真实 benchmark 与 evaluator']]),'04 kernel 定位设计',
 '现有工程具备工作台、上传、任务列表和报告展示。代码中的分析函数使用定时器推进阶段，并写入固定报告；92.4 之类的分数不是本轮分析结果。当前 kernel_linux_6.6 目录只见 Git 元数据，没有可直接使用的源码工作树。因此先把真实解析、版本绑定和 worker 接上，再讨论模型排序增益，避免把界面上的完成状态误认为定位已经完成。',
 '项目现在最缺什么？','真实 kernel 故障样本、匹配的源码和符号、可执行取证链，以及独立标注与评估；模型只是其中一个可替换环节。',ks+'；kernel_linux_6.6 目录只读检查')
 add('Jev 放在取证之后、动作之前','拟议接入：研发分析 worker；先以影子建议运行',flow([('本地取证','解析 / 符号 / 检索'),('Jev 判断','相关性 / 支持度'),('代码策略','校验 / 预算 / 路由'),('工具与工程师','取证 / 复现 / 审核')],'生成模型负责假设与报告；原始证据始终可追溯'), '04 kernel 定位设计',
 '建议采用可替换决策适配器。日志解析、地址符号化、时间窗口和版本过滤由确定性工具完成；Jev 仅处理已经整理好的证据和有限题目；代码层校验输出并决定是否采纳。复杂假设、解释和修复建议仍由工程师或生成模型负责。这样模型不可用时，现有流程能够继续。',
 '要改前端和接口吗？','优先保留上传与报告接口，在 runMockAnalysis 对应位置接真实 worker，增加输入清单、decision_trace.json 和 evidence.json；这是拟实施设计。',ks)
 add('先把证据变成“可定位、可核对”的状态','建议 state 契约 · 原始日志与关键上下文保持关联',table(['字段组','必须回答的问题'],[['版本','kernel commit / build ID / config / 模块符号是否匹配？'],['现场','故障类型、时间窗、CPU / 任务、调用栈来自哪里？'],['证据','每个 E-ID 是否带文件哈希、行号、抽取器版本？'],['上下文','已做哪些检查？哪些假设被否定？还缺什么？']]),'04 kernel 定位设计',
 '定位输入首先要可靠。相同地址在不同构建里可能指向不同代码；缺符号和符号不匹配也不应混为一谈。建议每个证据片段绑定来源哈希、行号和抽取步骤，state 保留已检查项与已否定假设。精确数值计算和版本一致性由代码做。给模型的不是整包日志，而是可追踪的必要片段。',
 '长日志压缩会不会丢关键证据？','保留原件与索引，保留支持证据、反证、未决项和关键约束；模型只消费当前窗口，可按 ID 补取原文，不能只留摘要。',ks)
 add('候选要先找全，再让模型调整顺序','拟议候选集 · 栈帧、相关代码、变更、历史问题分别召回',diagram(box(0,30,440,145,'符号与调用栈','精确映射')+box(0,215,440,145,'代码与变更','版本约束检索')+box(0,400,440,145,'历史故障','相似现场')+arrow(470,280,595,280)+box(630,175,450,205,'候选池 + OTHER','去重，保留来源')+arrow(1110,280,1210,280)+box(1240,175,360,205,'优先调查列表','不删除低分原件',True)),'04 kernel 定位设计',
 '让 Jev 从空白材料中发现全新的根因，难度和边界都很大。更可控的办法是先用精确符号映射和检索建立候选集合，再做相关性排序。候选包含代码片段、变更和历史案例，并始终保留 OTHER 或候选不足出口。候选本身漏掉真实根因，排序器无法把它凭空选出来，因此候选召回率必须单独评估。',
 '候选没有真因怎么办？','触发扩检或人工调查；测试里单独统计候选召回。禁止把最高分候选自动写成已确认根因。',ks)
 add('把“谁是根因”改成三类可核验小问题','题目设计草案 · 每题只问一个判断，保留“不足以判断”',table(['判断','题目示例','应用动作'],[['相关性','E17 是否与当前故障时间窗和调用路径相关？','排序证据'],['支持 / 冲突','这段持锁记录是否支持 H1 中的具体命题？','补支持证据或寻找反证'],['下一步','查持锁者、查 I/O 栈、补符号，先做哪项？','从允许的取证动作中选择']]),'04 kernel 定位设计',
 '不一次问“根因到底是什么”，而是拆成能通过材料复查的问题。对于支持与冲突，分别问支持某一个具体命题、是否存在某类反证，避免一个分数混合多个含义。缺材料时由前置检查或明确选项返回不足。Choice 结果附候选 ID，证据 ID 由题目上下文绑定，应用适配器校验它们存在。',
 '多个概率能直接相乘得到根因概率吗？','不能。题目之间可能相关，独立提问不代表统计独立；策略分数必须经过验证，也不应命名为因果概率。',ks+'；'+official)
 add('每次取证后更新状态，避免原地打转','拟议 worker 循环 · 工具反馈优先于模型建议',diagram(box(70,45,600,155,'证据状态 vN','已验证 / 已否定 / 待补充')+arrow(700,120,880,120)+box(925,45,600,155,'选择下一个检查','受预算和工具能力约束',True)+arrow(1225,220,1225,345)+box(925,365,600,155,'工具执行并留痕','带参数、输入版本与输出 ID')+arrow(900,442,720,442)+box(70,365,600,155,'核对新证据','没有新信息就补证据或退出')+arrow(370,345,370,220)),'04 kernel 定位设计',
 '这对应迷宫中的记忆与反馈。每次只读取证完成后更新证据状态。相同输入和版本下已经验证的检查应缓存，避免反复调用；环境变化后不能沿用过期结论。设置调用预算和无新增证据的停止条件。工具不可用、证据互相冲突或候选不在集合里时，直接保留未决状态交回工程师。',
 '模型会不会反复推荐同一检查？','代码维护已执行集合、证据版本和预算，并拒绝无意义重复；这不依赖模型记忆是否可靠。',ks)
 add('例如：hung task，先区分等待发生在哪里','合成教学示例 · 没有真实模型分数，不对应实际客户故障',diagram(box(0,60,455,175,'E1：任务等待超时','现场尚缺持锁者信息')+arrow(480,145,605,145)+box(640,60,450,175,'H1 锁等待 / H2 I/O','两种假设都保留')+arrow(1115,145,1230,145)+box(1260,60,340,175,'建议补取证据','锁 / 等待队列',True)+text(60,345,'新增 E2：记录持锁者身份、相关栈与时间关系',38)+text(60,425,'若仍无法排除 I/O → 保留并行假设，继续取证',32,'#6E6E73')+text(60,500,'证据支持假设 ≠ 已证明缺陷起因',31,'#0071E3',600)),'04 kernel 定位设计',
 '假设当前只看到任务等待超时。它还不足以区分锁竞争、I/O 等待或更早的异常。候选模块先保留两种假设，决策模块建议一项能够区分假设的取证任务。得到持锁者和时间关系后，再判断哪些命题获得支持、哪些仍未解决。这个例子没有伪造模型概率，也不暗示某条通用超时信息能直接定位具体驱动缺陷。',
 '什么时候才能对外说根因确定？','要满足该故障族预先约定的证据标准，并有复现、反事实对照或修复回归等验证，再由工程师确认。',ks)
 add('高分只是建议，停止条件由代码定义','拟议策略 · 证据不足、候选缺失、服务失败均有明确出口',table(['情形','系统行为'],[['证据充分且判断一致','推荐候选与下一步，展示证据链'],['支持与反证冲突 / 缺关键材料','扩检或补取证据，标为待确认'],['预算耗尽 / 超时 / 输出异常','保留现场，回退原流程并转人工'],['需要复现、修改或修复','走工程验证流程，确认后再形成结论']]),'04 kernel 定位设计',
 '阈值只控制采纳建议的范围，不授予结论真实性。阈值选择要同时看误导调查的代价和自动处理覆盖率。建议先影子运行，不改变现有任务结果；保留明确超时和失败出口。定位工具是研发侧流程组件，不能因为模型号称快，就把它放入内核运行时的调度或故障处理路径。',
 '能不能自动改代码并关闭问题？','这不是本轮接入范围。该方案先辅助排查与取证；修改、回归与问题关闭仍需要原有验证流程。',ks)
 add('是否值得接入，用整条定位流程验收','建议评估协议 · 案例、标注、预算与目标阈值仍待确定',table(['对照 / 指标','要证明什么'],[['规则 + 检索 / 现有 Agent / 加 Jev','Jev 在相同输入与预算下有净增益'],['候选召回、Top-k 命中、严重误导率','更快找到正确方向，且不漏掉关键问题'],['取证次数、人工确认耗时、总成本 p50 / p95','少走弯路，而非只减少一条 API 延迟'],['按故障家族和版本留出，统计失败与拒答','重复样本不泄漏，跨版本结果可复核']]),'05 验证与推进',
 '测试应使用已闭环的历史故障，由工程师核验根因和证据。按故障家族分组、时间和版本留出，不能把同一问题的重复日志分到训练和测试两边。对相同案例配对比较规则检索、现有 Agent 与加入 Jev 的流程，必要时加入本地小模型。报告全部案例、失败和拒答，不只展示成功案例。先量基线，再由团队设定误导率和时间收益门槛。',
 '能承诺节省百分之多少吗？','目前没有真实 kernel 测量，不能承诺。先明确人工确认起止点、模型与工具墙钟耗时、请求成本和失败代价，再给置信区间。',ks)
 add('先把“候选排序”做成最小试点','建议顺序 · 每一阶段都有可以退出的判断依据',flow([('准备','真实 worker + 案例'),('离线','固定输入配对评估'),('影子','只记录建议与反馈'),('有限采纳','质量达标再接动作')],'首个落点：panic / hung task 的证据候选排序；下一步取证随后评估'), '05 验证与推进',
 '范围先收窄到一个数据可获得的故障族：例如 panic 或 hung task 的证据候选排序，实际选择由样本决定。先补真实 worker 和可追溯证据，再做离线配对，随后影子运行。只有质量和错误成本达标才有限采纳。下一步取证选择更接近闭环控制，应放在排序验证之后，不必一次重构整个工作台。',
 '需要哪些角色和交付？','kernel 工程师负责标签与证据标准，平台开发负责抽取和 worker，评测负责人维护留出集。交付数据清单、适配器、评估报告和回退方案；人天待盘点后估算。',ks)
 add('让定位更有效，先证明每个判断有用','本轮结论 · NanoJev 是机制窗口，kernel 方案需要自己的证据',big('值得试的，是<span>有限判断</span><br>能否减少无效调查','先验收增益，再扩大自动化范围','已完成：离线复算与讲解材料　·　待验证：真实 kernel 任务收益'),'05 验证与推进',
 '最后收束三点。第一，Jev 的接口适合代码消费的小判断。第二，NanoJev 这条轨迹确实更少尝试，但常数对照更短，说明必须分清模型和控制器贡献。第三，kernel 定位可以先试证据排序和取证建议，关键是可追溯输入、反馈闭环和真实案例评估。希望本次确认的是可验证的试点范围，而不是未经测量的性能承诺。',
 '如果 Jev 没有提升怎么办？','停用该判断环节，保留已经建设的证据索引、评估集和 worker。适配器可替换，试点失败也不应破坏现有流程。',ns+'；'+ks)
 assert len(PAGES)==23
 if not emit:return PAGES
 # Write the page plan before materializing the HTML.
 plan='# v3 页面计划（2026-09-27）\n\n主版 23 页；独立 NanoJev 实战为主版 5–11 页，共 7 页。\n\n|页|段|结论|画面|\n|---|---|---|---|\n'
 for i,p in enumerate(PAGES,1):plan+=f'|{i}|{p["sec"]}|{p["title"]}|'+('视频' if '<video' in p['body'] else '轨迹互动' if '<canvas' in p['body'] else '数据或机制图')+'|\n'
 (HERE/'slides-v3-plan.md').write_text(plan,encoding='utf-8')
 base=(SLIDES/'deck.before-practice.html').read_text(encoding='utf-8')
 prefix=base[:base.index('<!-- 1 封面 -->')]
 css=(HERE/'slides-v2.css').read_text(encoding='utf-8')+'''\n.statement{flex:1;display:flex;flex-direction:column;justify-content:center;gap:38px}.statement>div{font-size:98px;line-height:1.38;font-weight:600;letter-spacing:-2px}.statement span{color:var(--accent)}.statement p{font-size:37px;color:var(--muted)}.statement small{font-size:26px;color:var(--muted);line-height:1.6}.maze-panels{padding:0 145px;gap:40px}.maze-panel{padding:20px 45px}.tbl.left td{font-size:30px;line-height:1.65;padding:24px 20px}.tbl.left th{font-size:25px;padding:15px 20px}.practice-v2 h1{font-size:64px}.sub{line-height:1.6}.sv{font-family:var(--font)}\n'''
 prefix=re.sub(r'<title>.*?</title>','<title>Jev · NanoJev 实战与 kernel 定位方案</title>',prefix)
 prefix=prefix.replace('</head>','<style>'+css+'</style></head>')
 controls='<div id="deck-controls" data-interactive><button id="deck-prev" aria-label="上一页">‹</button><span id="deck-count"></span><button id="deck-next" aria-label="下一页">›</button><button id="deck-menu" aria-expanded="false">☰ 目录</button><button id="deck-fullscreen">全屏</button></div><nav id="deck-toc" hidden></nav><div id="deck-hint">滚轮 / 滑动 / ← → 翻页 · G 目录 · F 全屏</div>'
 old=(HERE/'slides-v2-interactions.js').read_text(encoding='utf-8')
 interaction='(() => {\n'+old[old.index('  const replay='):]
 interaction=interaction.replace("if(event.detail.slide.querySelector('[data-mechanism]')){step=0;renderStep();}",'')
 interaction=interaction.replace(' 步',' 次尝试')
 # Coordinates in upstream recordings are [row, column]. Match the simulator.
 interaction=interaction.replace('([x,y])','([y,x])').replace('([x,y],i)','([y,x],i)').replace('const [gx,gy]','const [gy,gx]').replace('const [x,y]','const [y,x]')
 (HERE/'slides-v3-interactions.js').write_text(interaction,encoding='utf-8')
 data='<script id="maze-data" type="application/json">'+json.dumps(replay,ensure_ascii=False,separators=(',',':'))+'</script>'
 scripts=data+'<script>'+(HERE/'slide-navigation.js').read_text(encoding='utf-8')+'</script><script>'+interaction+'</script>'
 for name,pages in [('deck.html',PAGES),('deck-practice.html',PAGES[4:11])]:
  f=SLIDES/name;b=SLIDES/(f.stem+'.before-v3.html')
  if f.exists() and not b.exists():shutil.copy2(f,b)
  body='\n'.join(f'<section class="slide practice-v2" data-sec="{E(p["sec"])}" data-title="{E(p["title"])}"><div class="kicker">{E(p["sec"])}</div><h1>{p["title"]}</h1><div class="sub">{p["sub"]}</div>{p["body"]}</section>' for p in pages)
  result=prefix+body+'</div>'+controls+scripts+'</body></html>'
  assert '可lip' not in result and '可Lip' not in result
  f.write_text(result,encoding='utf-8')
 script='# Jev：NanoJev 实战与 kernel 定位方案 — 演讲稿\n\n版本：2026-09-27 v3。对应 slides/deck.html 23 页，建议 18–22 分钟，另留 10 分钟讨论。独立 NanoJev 版对应主版 5–11 页。\n\n口径：官方接口事实、上游录制、本地离线复算、拟议设计分开讲。没有真实 Jev API 调用，没有 kernel 定位收益实测。以下问题是根据材料预判的领导提问，不是假称实际发生的会议记录。\n\n'
 for i,p in enumerate(PAGES,1):
  script+=f'## 第 {i:02d} 页｜{p["title"]}\n\n**画面操作**：{p["action"]}\n\n**讲述**：{p["speech"]}\n\n**可能追问**：{p["question"]}\n\n**建议回答**：{p["answer"]}\n\n**依据**：{p["source"]}\n\n'
 script+=(HERE/'leadership-appendix.md').read_text(encoding='utf-8')
 (DEST/'演讲稿与领导问答.md').write_text(script,encoding='utf-8')
 (SLIDES/'使用说明.md').write_text(plan+'\n## 使用\n\n双击 deck.html 讲完整方案；deck-practice.html 仅为 NanoJev 七页。离线使用；视频在主版第 4 页，迷宫在主版第 6 页 / 独立版第 2 页。滚轮、触控、方向键、空格、PageUp/Down 翻页；数字跳页；G 目录，F 全屏。\n\n演讲稿在上一级 `演讲稿与领导问答.md`。没有品牌标签；灰底黑字与蓝色强调。两份旧 deck 保存在 `*.before-v3.html`。\n\n重建：`python experiment/jev_practice/analyze_nano_maze.py`，然后 `python experiment/jev_practice/build_slides_v3.py`；验收：`python experiment/jev_practice/verify_slides_v3.py`。\n',encoding='utf-8')
 (SLIDES/'实战说明.md').write_text('# NanoJev 唯一实战\n\n独立版 7 页，对应主版 5–11 页。\n\n'+ '\n'.join(f'{i}. {p["title"]}' for i,p in enumerate(PAGES[4:11],1))+'\n\n其他旧实验保留在 experiment 中作历史记录，不再进入当前演示。\n\n源轨迹未修改；本地审计重放 Jev / NanoJev 的原动作、反馈与终点，常数 0.5 对照实际执行。详见 `results/nano-maze-audit.json`。不得把尝试数解释为墙钟时间，不得把游戏结果当作 kernel 任务验证。\n',encoding='utf-8')
 print('Built 23-page main, 7-page NanoJev, synchronized speech and page map.')
if __name__=='__main__':main()
