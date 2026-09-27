"""Restore every original introductory/mechanism section, add training explainers."""
from pathlib import Path
import html,json,re,shutil
import slides_v3_content as v3
H=Path(__file__).resolve().parent;ROOT=H.parents[1];DEST=ROOT/'related_work/08-第30期-Jev-不生成文本的决策模型';S=DEST/'slides'

def plain(s):return html.unescape(re.sub('<[^>]+>',' ',s))
def new(title,sub,body,speech,q,a,sec='04 训练 · 逐步解释',source='官方概念 + 本地可复算教学示意'):
 return dict(title=title,sub=sub,body=body,sec=sec,speech=speech,question=q,answer=a,source=source,action='停留约45–60秒；先指明输入，再讲反馈和输出。')
def movie(kind,title,sub,speech):
 p=new(title,sub,f'<div class="fig card"><video muted loop autoplay playsinline controls preload="auto" src="media/jev-training-{kind.lower()}-zh.mp4" poster="media/jev-training-{kind.lower()}-zh.png"></video></div>',speech,'这段展示的是正式模型训练实测吗？','不是。流程依据公开材料，数值由小规模教学计算生成；没有训练或调用真实模型。',source='experiment/jev_training_pixel/FACTS.md；scene_zh.py；training-speaker-notes.md')
 p['action']='入页自动播放32秒中文动画；首次按下表短句跟讲，之后按建议时间暂停深讲，整页约90秒。拖动播放器进度条定位；离页暂停、返回重播。鼠标移出视频区域后，播放控件会收起，方便看底部字幕。'
 p['detail']=(H/'training-speaker-notes.md').read_text(encoding='utf-8').split('## '+kind+'\n',1)[1].split('\n## ',1)[0].strip()
 return p

ORIGINAL_TALKS={
1:'先用原版的定义建立直觉：输入材料与有限问题，输出供程序使用的答案和概率。发布热度是原稿的历史背景，不是能力证据。今天完整保留原理介绍，再补三条训练路线动画，最后看 NanoJev 实战与 kernel 定位设计。',
2:'原版介绍了团队背景、融资和合成数据投入。它解释为什么团队关注后训练，但履历与融资不能证明模型效果。页面保留原稿来源和历史口径；RLHF共同发明人是官网宣传写法，具体可核实的是相关论文作者身份。',
3:'这页保留发布时的热度快照，用来说明为什么值得关注。HN分数、社交浏览和接入比例都是原稿采集时的数字，会变化；热度不用于评价正确率，也不用于推出生产可用性。',
4:'先分清证据层次。接口、输出类型可查官方文档；采访是提供方口径；黑盒探针能观察行为，但不能唯一确定内部计算图。后面用分支、KV缓存和读出头帮助理解，始终把已知接口与架构假设分开。',
5:'进入第一个问题：Jev究竟提供什么。先理解材料、题目和答案的契约，再看模型怎么可能实现它；不要把概念上的不生成文本理解成模型内部完全没有计算。',
6:'这张原版演示强调程序不必等待一段文字再解析答案。图上的时延和费用来自原演示的一次设置，不是本机复测，也不是所有请求的承诺。不输出自然语言推理链，不等于不能做语义判断。',
7:'state放材料，questions放判断任务和允许答案。Choice在给定选项中选择，Score在有序等级上给分，Noul判断命题。选项值与概率是结构化数据，并非只返回裸数字；问题独立评估也不代表增加问题没有输入成本。',
8:'保留原稿的请求响应例子：将接口字段逐项对应到返回值。这里的原始记录来自已有材料，本轮没有重新调用API。让听众先看题目ID、类型和候选，再看答案、分布与confidence，避免只盯最高概率。',
9:'同一条工单能同时问部门、情绪和是否威胁投诉，这三道题是不同判断。部门分布加起来为一；情绪分数是等级期望；Noul是单命题数值。最高选项、期望分和confidence不是可以互换的量。',
10:'动机不只是少输出几个token。我们要讨论程序是否能对不确定性采取不同动作：自动处理、补充证据，或者转人工。训练目标、校准与应用策略会分别决定这些动作是否可信。',
11:'这页对照的是产品目标：偏好导向的文字，与用于代码决策的概率。它不是说所有聊天模型必须逐条人审，或Jev能够无条件自动化。概率诚实是目标，要在一批预测上测；实际阈值还取决于业务错误成本。',
12:'下面保留原版架构段。先记住边界：能观察到题目独立、结构化输出和延迟特征，但官方没有公开完整内部实现。图是与这些现象相容的一种解释，不是开源模型结构图。',
13:'原图用共享前缀和多个分支解释一次材料、多题判断：公共信息来自state，每题只应看到自己题干和选项。共享KV与特殊读出位置是实现假设；探针支持隔离行为，不能证明唯一的mask或缓存布局。',
14:'这页放大单个问题，解释读出位置可以聚合材料、题干与多个选项的信息。候选一起参与打分时，增加选项可能改变已有选项之间的比例。这样的行为与listwise模型相容，但不能据此排除所有其他内部设计。',
15:'保留三种读出解释：softmax将分数归一化，Score用等级概率求期望，sigmoid可表示单个布尔概率。这里区分数学上的实现示意与已知返回契约；官方并未凭这些公式公开权重形状或所有头的结构。',
16:'原图的关键趋势是输入长度和批量问题数会影响时延。一题与一百题在这组测量里相近，并不意味着任意数量问题都持平：一千五百题已经增长。测量是服务端上报值，客户端网络和排队还会增加耗时。',
17:'底座画像保留原稿全部线索，但证据强度不同。参数规模、MoE和分词器匹配属于探针推测，不能当成官方规格；跨论文的知识评测也未必同协议。接口上限与语言表现要按固定模型版本再核查。',
18:'训练段先回答三个问题：奖励是谁给的，奖励评估的对象是什么，训练后希望模型输出什么。RLHF、RLVR与RLCD是目标差异，不是从低级到高级的一条必然升级路线。',
19:'三条路线分别围绕偏好、可验证答案和校准概率。RLHF可以使用人类排序训练奖励模型；RLVR用规则或测试验证生成答案；官方称Jev采用RLCD。原图中的log/Brier是帮助理解校准目标的示例，并非已公开的Jev损失。',
20:'接下来讨论数据为什么重要。一个概率目标是否有意义，依赖样本怎样生成、标签从哪里来、训练环境是否覆盖部署环境，而不只是把模型输出层换成数字。',
21:'这页保留原采访关于合成训练数据和团队投入的说法。必须限定为这里讨论的训练数据口径，不能理解成预训练语言模型从未接触真实文本。客户请求不用于训练也不能推出产品没有其他改进或校准渠道。',
22:'原稿用“先抽潜在结果，再生成观测材料”解释一种可能的数据设计。这样可以知道模拟器里的真实状态，但把状态写成语言后可能丢失信息，也可能引入线索。流程是教学重构，提供方没有公开这条完整流水线。',
23:'四步依次是抽潜变量、生成文本、计算条件分布、形成训练行。0.036与0.028归一化得到约0.56与0.44，需要满足例子给定的先验、条件独立及其他类别似然假设。知道潜变量不代表观测文本必然能唯一推回它。',
24:'清楚、模糊和不可知样本，分别对应集中的分布、分散的分布和先验。模拟器可提供可控标签，但不自动代表真实世界。标签无噪声仅在生成规则与文本语义一致的假设下成立，跨域误差仍需要实测。',
25:'进入评测段。保留原版图表和来源，逐一分清官方工作流、第三方测试与作者实践；它们的数据、模型版本和计时方式不同，不汇成一个统一排行榜。',
26:'原版官方图展示特定工作流里准确率、费用与时延的权衡。图上前沿不是所有任务的性能保证；还要看题目分解方式、标签来源、推理配置与输入长度。实际落地要用自己的数据重测。',
27:'把平均分拆成工作流后，可以看到同一模型在客服、告警、轨迹和发票任务上的差异。比值看起来大，不意味着每个任务都更准；延迟和成本的优势也不能弥补关键任务错误。',
28:'保留原稿的校准结果，但“两端可信、中间不可信”只能概括这些被测样本。高置信也可能系统性出错，低频区间样本少时估计会不稳。要看分桶、覆盖率、样本量和分布变化。',
29:'这一页保留多个短文本与推理任务的结果，重点是适用边界。各研究协议不同，所以按任务阅读，不能简单平均。对复杂因果推理，有限判断接口也不会自动解决证据缺失。',
40:'原版提出一个有用的系统视角：智能体既有生成点，也有很多路由、筛选与验证点。蓝色位置可以尝试类型化判断，但每个判断的价值要单独评估；不是给所有节点再加一次模型调用就会变好。',
41:'保留“先发现任务”的核心观点，同时将“没人追平”“只有一家想到”改成待验证判断。可训练结构、数据质量和任务定义都影响效果。kernel试点应先明确什么样的错误最耗工程师时间。',
42:'回到原版的定义：材料与有限问题，返回类型化答案和概率。用自己的任务验证校准、正确率、端到端耗时和失败处理。完整原理介绍、训练动画与NanoJev对照最终都服务于这个判断。'
}

def restore(src,n):
 src=re.sub(r'<div class="brand">.*?</div>','',src,flags=re.S)
 src=re.sub(r'<div class="big" style="margin-top:70px">可lip</div>','',src)
 src=src.replace('可lip','')
 src=src.replace('不写字、不解释、不推理','不生成文字、不输出推理链')
 src=src.replace('输入：材料 + 三种题　<span class="thin">输出：只有数</span>','输入：材料 + 三种题　<span class="thin">输出：类型化答案与概率</span>')
 src=src.replace('多问几道几乎不加钱','多题可并行；输入费用仍随题目增加')
 src=src.replace('说 0.8 就有 80% 对','校准良好的同组预测约 80% 成立')
 src=src.replace('每一条都要人看','需按任务判断是否复核')
 src=src.replace('≥ 0.9 自动 · &lt; 0.5 转人','示例策略：过线才自动，否则复核')
 src=src.replace('计算图证据充分','计算图是行为证据支持的假设')
 src=src.replace('复现印证','非官方实现示意')
 src=src.replace('100 道题和 1 道题延迟一样','原测量中 100 题与 1 题延迟接近')
 src=src.replace('255 个选项和 2 个选项延迟相同','原探针中 255 与 2 选项延迟接近')
 src=src.replace('Jev 不是这样','与原探针行为不符')
 src=src.replace('Jev 实测是这样','与原探针行为相容')
 src=src.replace('→ 选项在同一行，是算法 B','→ 支持联合打分假设，不能唯一确定计算图')
 src=src.replace('三种原语的读出 · 官方文档给出的公式','返回值公式 + 读出头实现示意（架构未公开）')
 src=src.replace('与 choice 不是同一个头：','接口不同；以下为实现示意：')
 src=src.replace('没有一个复现追平','是否追平需同协议验证')
 src=src.replace('这一步之前没人当成产品做','将这一需求产品化')
 src=src.replace('兴趣过滤（PaperDance）','兴趣过滤')
 src=src.replace('一个真实样本都没有','采访中的训练数据口径；不指预训练语料')
 src=src.replace('客户数据不进训练，没有回流来修','不使用客户请求训练；仍需独立跨域验证')
 src=src.replace('标签零噪声','规则一致时标签可控')
 src=src.replace('答案天生正确','潜在标签已知')
 if n==16:
  src=src.replace('延迟随 state 线性，','state 变长会增加延迟，').replace('随问题数持平','大批量题目也会增加延迟')
 if n==22:src=src.replace('官方：训练数据 100% 合成 · 一半员工在一个合成数据实验室','采访：合成训练数据 · 以下生成流程是教学重构')
 if n==19:
  src=src.replace('同一个框架，只差奖励','目标与反馈不同；Jev 路线是 RLCD，不是 RLVR')
  src=src.replace('期望奖励最大时 p 的形状','目标倾向（有条件）').replace('收窄到高分模式（mode dropping）','提高偏好响应的概率；可能收窄模式').replace('会讨好的生成器','偏好对齐的生成器').replace('全部质量压到 argmax','纯0/1目标倾向奖励高的答案').replace('会做题，不会说「不知道」','提高可验证任务正确率').replace('proper scoring rule（log / Brier）','校准目标；log / Brier 为教学示例').replace('p = 真实条件概率','理想充分条件下 p 接近真实比例').replace('概率诚实的判断器','以校准为目标的判断器')
 if n==42:src=src.replace('一次前向 · 100 毫秒 · 输出免费 · 两端可信，中间不可信 · 用之前拿自己的数据验一遍','结构化接口 · 时延、费用、校准都要按任务验证 · 用自己的数据验一遍')
 # Trace every restored section; a small page badge marks the historical source, not a new benchmark.
 src=src.replace('<section ',f'<section data-origin-page="{n}" ',1)
 badge='架构推断 · 非官方实现' if n in [13,14,15,17] else '原版资料 · 数字为历史快照' if n in [1,2,3,6,7,8,9,16,21,26,27,28,29] else '保留原版主题 · 补充边界说明'
 src=src.replace('</section>',f'<div class="source-badge">原版 {n:02d} · {badge}</div></section>')
 return src

def main():
 old=(S/'deck.before-practice.html').read_text(encoding='utf-8');original=re.findall(r'<section\b.*?</section>',old,re.S)
 assert len(original)==42
 vpages=v3.main(emit=False)
 extra={
 7:[new('训练改参数，推理用参数','先分清两个时间尺度，后面三段动画讲的都是训练',v3.flow([('训练阶段','样本 → 反馈 → 更新参数'),('保存模型','参数固定下来'),('推理阶段','新材料 → 类型化答案')],'线上请求通常不在现场重新训练奖励模型'), '训练是根据许多样本和反馈调整参数；推理是使用已保存的参数处理新输入。像素动画里的反馈回路发生在训练阶段，不能理解成每次Jev请求都等待人工标签或验证答案。应用的核验、回退与模型训练是另外两层。','线上是否每次都要奖励模型？','经典RLHF奖励模型用于训练；本页不假设生产推理调用它。Jev公开接口也没有这样的调用契约。',sec='01 接口 · 先分清阶段')],
 11:[new('“报 0.8”描述一组预测的可靠性','校准概念 · 不是对某一条答案的保证',v3.big('<span>80 / 100</span>','同一概率组中，约 80 次事件实际成立','理想教学例；实际需足够样本、区间估计与分布稳定'), '把许多报出0.8的判断放在一起，再看约有多少成立，才是在检验校准。这与这一个答案有没有八成可靠的证明不同。校准好也不必然更准确，例如总报基准发生率就可能校准但区分能力很弱。','校准好是否代表能力强？','不一定，还要看区分能力、准确率及应用后的错误成本。',sec='02 动机 · 校准是什么')],
 13:[new('共享的是材料，每道题仍有自己的条件','接口独立评估可以确认；KV cache / mask 图是解释性假设',v3.flow([('公共 state','所有题都需要的事实'),('各题条件','题干 + 本题候选'),('独立输出','不能偷看另一题的答案')],'跨题依赖要由应用分轮组织，不能期待题目自行串成推理链'), '原图的读法是先看公共材料，再看每道题自己的条件。若第二题需要第一题答案，应用应该先拿到答案，再把经验证的结果写入下一轮state。黑盒行为只能约束可能实现，不能告诉我们每层缓存的真实布局。','既然分支隔离，能否多步推理？','可以由外部流程组合多轮判断，但单次多题并行不是串行推理。',sec='03 架构 · 读图辅助')],
 14:[new('改变选项，也改变了模型面对的问题','联合候选效应 · 不应把黑盒现象当作唯一架构证明',v3.flow([('原候选','计费 / 技术 / 销售'),('加入新候选','其他 / 无法判断'),('分布变化','已有选项的比例也可能变')],'固定选项说明与顺序做评测；记录候选集版本'), '候选描述给出了任务语义。新增其他选项可能改变比较边界，所以分布会变。原稿观察到这种效应，将其与listwise读出联系起来；这是一种解释，不足以唯一证明特殊token和头结构。工程上最直接的行动是固定候选版本，并测试顺序敏感性。','概率变化是否就是错误？','未必，题目本身变了；但不必要的顺序敏感和描述冲突需要回归检查。',sec='03 架构 · 候选语义')],
 18:[new('RLHF、RLVR、RLCD：差别在优化目标','官方明确：Jev / TypeSafe 的训练路线是 RLCD',v3.flow([('RLHF','人更偏好哪个回答'),('RLVR','生成的答案能否验证'),('RLCD','报出的概率是否可靠')],'三者可在复杂训练流程里组合，不是简单的替代关系'), 'RLHF是人类反馈强化学习，RLVR是可验证奖励强化学习，RLCD是TypeSafe对校准决策训练路线的命名。因此本次把用户提到的“Jev RLVR”准确展开为RLVR对照与Jev RLCD。下面三个动画分别跟踪反馈从哪里来，不把它们混为一个算法。','RLCD就是换个名字的RLVR吗？','二者可以都使用结果反馈，但这里强调的输出与优化目标不同；仅知道名称不能推出完整训练算法。',source='https://docs.typesafe.ai/introduction/machine-learning-primer')],
 19:[movie('RLHF','RLHF：人类排序，训练奖励，再更新策略','经典 InstructGPT 流程示意 · SFT → 偏好 → reward model → PPO + KL', '先用示范做SFT，策略模型生成回答，人对回答做偏好排序。奖励模型学会预测这种偏好，再给新采样的回答提供训练信号；经典PPO流程还通过参考策略约束限制偏移。动画的A、B是教学样例，偏好分不等于事实正确率。'),movie('RLVR','RLVR：答案先生成，再由规则验证','可验证奖励示意 · 2 + 3 = 5 · 正确性奖励 1 / 0', '输入一个可核验的问题，模型生成两个候选解，再用规则比较答案或运行测试。得到的奖励用于更新策略，让后续生成更容易通过验证。实际算法还可能含格式奖励和归一化。这个目标可以改善正确率，但不会自动要求模型如实报告不确定性。'),movie('RLCD','Jev 的 RLCD：让概率接受结果检验','官方路线 + 教学数学示意 · 具体损失和优化器未公开', '模型输出概率分布，反馈用于检验这些概率与结果是否匹配。这里构造同一信息条件下六个正例、四个反例，演示log loss如何把过度自信的0.90拉向0.60。这是可复算的单参数教学模型，不是Jev真实训练流水线，更不是证明其实现使用了这个损失或梯度更新。'),new('为什么 0.60 比 0.90 更诚实？','同一信息条件：60% 正例、40% 反例 · 玩具二分类',v3.table(['预测 p(正例)','平均 log loss ↓','含义'],[['0.60','0.673','匹配此玩具分组的发生率'],['0.90','0.984','遇到40%的反例时损失更大'],['0.99','1.848','错误的高度自信受到更大惩罚']]),'平均损失等于−0.6 ln p−0.4 ln(1−p)，在p等于0.6时最小。它要求概率整体合理，而不是只看这次采样有没有答对。极小值结论成立于给定的真实比例和损失假设；有限数据、分布偏移与优化误差仍会影响结果。','是不是应该所有问题都报0.6？','不是。这里只固定一个信息条件和分组；换一组信息，真实条件概率可能完全不同。',source='experiment/jev_training_pixel/prep.py；data/provenance.json')],
 24:[new('模拟器知道标签，模型未必看见全部信息','保留原版“倒果为因”示例，同时区分潜在状态与可见文本',v3.flow([('潜在状态','生成时已知'),('观测材料','可能丢信息、引入噪声'),('条件分布','根据可见信息评估')],'合成数据可以控制规则；仍需验证语言生成和真实分布的差异'), '先抽标签并不意味着写出的文本只有一个正确解释。文本会遮掉潜在信息，生成模型也可能写错约束。因此要验证生成器是否遵循规则，并在真实数据上测试校准。0.56与0.44只是在原稿模拟器假设下计算出的比例。','怎样知道合成数据没有偷偷泄漏答案？','分离生成与审计，检查标签线索、模板重复、语义一致性，并用独立真实样本检验。',sec='05 数据 · 信息边界')]
 }
 pages=[];mapping=[]
 def append_original(n):
  raw=restore(original[n-1],n);title=re.search(r'data-title="(.*?)"',raw).group(1);sec=re.search(r'data-sec="(.*?)"',raw).group(1)
  if n==16:title='输入长度与问题批量都会影响延迟';raw=re.sub('data-title=".*?"','data-title="'+title+'"',raw,count=1)
  pages.append(dict(raw=raw,title=title,sec=sec,speech=ORIGINAL_TALKS[n],question='这一页哪些内容不能直接当作已验证事实？',answer=('架构图、参数规模和内部实现是原稿探针推断，尚非官方披露。' if n in [13,14,15,17] else '历史数字保留原来源与时间口径；教学例和推断不是本轮真实模型实测，应用效果需独立评估。'),source=f'原版第{n}页；notes/技术事实核查.md对应条目；notes/原版恢复与术语校正.md',action='先讲主结论，再解释图中证据；原密集页可停留60–90秒。',origin=n))
  mapping.append(dict(original=n,current=len(pages),title=title))
 for n in range(1,30):
  append_original(n);pages.extend(extra.get(n,[]))
 # Preserve the accepted NanoJev practice and kernel proposal after the full primer.
 pages.extend(vpages[4:22])
 for n in [40,41,42]:append_original(n)
 assert len(pages)==60
 for f in [S/'deck.html',DEST/'演讲稿与领导问答.md']:
  b=f.with_name(f.stem+'.before-v4'+f.suffix)
  if f.exists() and not b.exists():shutil.copy2(f,b)
 # Use the v3 document shell and inline navigation, without reusing its reduced body.
 current=(S/'deck.html').read_text(encoding='utf-8')
 if 'data-origin-page=' in current:current=(S/'deck.before-v4.html').read_text(encoding='utf-8')
 start=current.index('<section ');end=current.rindex('</section>')+len('</section>')
 prefix=current[:start]
 # Scope the spacious v3 table typography to newly authored pages.
 prefix=prefix.replace('.tbl.left td{font-size:30px','.practice-v2 .tbl.left td{font-size:30px').replace('.tbl.left th{font-size:25px','.practice-v2 .tbl.left th{font-size:25px')
 prefix=prefix.replace('</head>','<style>.source-badge{position:absolute;left:128px;bottom:62px;font-size:18px;color:#86868b}.slide:not(.practice-v2) h1{line-height:1.28}.slide:not(.practice-v2){padding-bottom:104px}.cover .p{font-size:33px;line-height:1.65}.slide.cover h1{line-height:1.32}.cover .source-badge{bottom:350px}.slide[data-origin-page="19"] .tbl td{font-size:25px;padding:18px 12px}.slide[data-origin-page="19"] .tbl th{font-size:22px}.slide[data-origin-page="42"] .big{font-size:37px}</style></head>')
 chunks=[]
 for p in pages:
  if 'raw' in p:chunks.append(p['raw'])
  else:chunks.append(f'<section class="slide practice-v2" data-sec="{html.escape(p["sec"])}" data-title="{html.escape(p["title"])}"><div class="kicker">{p["sec"]}</div><h1>{p["title"]}</h1><div class="sub">{p["sub"]}</div>{p["body"]}</section>')
 result=prefix+'\n'.join(chunks)+current[end:]
 result=re.sub(r'<title>.*?</title>','<title>Jev · 完整原理、训练动画与实战</title>',result)
 assert '可lip' not in result
 assert {int(x) for x in re.findall('data-origin-page="(\\d+)"',result)}==set(range(1,30))|{40,41,42}
 (S/'deck.html').write_text(result,encoding='utf-8')
 (H/'results/original-restoration-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
 plan='# v4：完整原理恢复与训练动画\n\n原版介绍、原理、训练、数据和评测均保留；共60页。原版应用30–38页继续由NanoJev唯一实战与kernel方案替代。原页39为未来过渡，内容并入后段。\n\n|新页|来源|段|标题|\n|---|---|---|---|\n'
 for i,p in enumerate(pages,1):plan+=f'|{i}|'+(f'原版{p["origin"]}' if 'origin'in p else '新增 / v3保留')+f'|{p["sec"]}|{p["title"]}|\n'
 (H/'slides-v4-plan.md').write_text(plan,encoding='utf-8')
 script='# Jev 完整原理、训练动画与实战：逐页演讲稿\n\n2026-09-27 v4，对应主版60页。建议45–60分钟；原过渡页可快速带过。独立NanoJev版仍为7页，对应主版40–46页。问答是预判，会议结论表保持待确认。\n\nRLHF：人类反馈；RLVR：可验证奖励；Jev官方路线RLCD：校准决策。三段动画各32秒，中文流程标签与像素字幕配套讲解，数学样例均为教学计算。\n\n'
 script+='本稿已按当前中文版逐页核对。第25–27页增加视频时间轴、短句口播、暂停深讲、术语解释和追问回答；时间轴对应视频时间，可暂停展开。三段视频静音，由演讲者讲解。\n\n'
 for i,p in enumerate(pages,1):
  script+=f'## 第 {i:02d} 页｜{p["title"]}\n\n**画面操作**：{p["action"]}\n\n**讲述**：{p["speech"]}\n\n'
  if p.get('detail'):script+=p['detail']+'\n\n'
  script+=f'**可能追问**：{p["question"]}\n\n**建议回答**：{p["answer"]}\n\n**依据**：{p["source"]}\n\n'
 appendix=(H/'leadership-appendix.md').read_text(encoding='utf-8');appendix=appendix[:appendix.index('主版页码与独立版对应：')]
 script+=appendix+'主版40–46页，对应NanoJev独立版1–7页。原版恢复映射见 notes/原版恢复与术语校正.md。\n'
 (DEST/'演讲稿与领导问答.md').write_text(script,encoding='utf-8')
 (S/'使用说明.md').write_text(plan+'\n## 播放\n\n主版deck.html为完整60页。NanoJev独立deck-practice.html仍7页。RLHF/RLVR/RLCD视频在主版25/26/27页，各32秒，流程、步骤和字幕已中文化（保留必要英文缩写与公式）。双击可离线使用；滚轮、触控、方向键、G目录、数字跳页、F全屏。视频入页重播，离页暂停；拖动进度条不翻页。\n\n原稿历史数字与架构推断保留来源标签，不能当成本轮实测。原始42页备份没有修改。\n\n重建：python experiment/jev_practice/build_slides_v4.py；验收：python experiment/jev_practice/verify_slides_v4.py。\n',encoding='utf-8')
 print('Built',len(pages),'pages. Videos:',[(i+1,p['title']) for i,p in enumerate(pages) if '<video' in p.get('body','')]);print('Nano starts',next(i+1 for i,p in enumerate(pages) if p['title']==vpages[4]['title']))
if __name__=='__main__':main()
