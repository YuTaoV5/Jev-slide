"""Add measured server experiments to the user's Jev report deck.

Preserves the pre-existing Jev explanation and replay controls byte-for-byte.
Read data from saved experiment artifacts, never from a live model service.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "related_work/Jev报告slide"
DECK = REPORT / "slides/deck.html"
BACKUP = Path(__file__).resolve().parent / "report_source/base-deck.html"
RESULTS = Path(__file__).resolve().parent / "results"


def esc(value):
    return html.escape(str(value))


def cards(items):
    return '<div class="exp-cards">' + ''.join(f'<article><small>{esc(k)}</small><h2>{v}</h2><p>{d}</p></article>' for k, v, d in items) + '</div>'


def table(headers, rows, note=""):
    return '<div class="exp-table"><table><thead><tr>' + ''.join(f'<th>{esc(x)}</th>' for x in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in row) + '</tr>' for row in rows) + '</tbody></table>' + (f'<p class="exp-note">{note}</p>' if note else '') + '</div>'


def flow(items, note):
    return '<div class="exp-flow">' + ''.join(f'<article><small>{i+1:02}</small><h2>{a}</h2><p>{b}</p></article>' for i, (a, b) in enumerate(items)) + f'</div><p class="exp-note">{note}</p>'


def bars(items, max_value, unit, note):
    return '<div class="exp-bars">' + ''.join(f'<div><label>{name}<b>{value:.1f} {unit}</b></label><div class="exp-track"><i style="width:{100*value/max_value:.2f}%"></i></div><p>{desc}</p></div>' for name, value, desc in items) + f'<p class="exp-note">{note}</p></div>'


def main():
    focused_backup=DECK.with_name('deck.before-experiment-focus.html')
    if not focused_backup.exists():focused_backup.write_bytes(DECK.read_bytes())
    if not BACKUP.exists():
        BACKUP.write_bytes(DECK.read_bytes())
    original = BACKUP.read_text(encoding="utf-8")
    for before,after in [('03 唯一实战 · NanoJev','07 上游回放 · NanoJev'),
                         ('04 kernel 定位方案','09 kernel 定位方案'),
                         ('05 验证与推进','10 验证与推进'),('09 未来','11 未来')]:
        original=original.replace(before,after)
    sections = list(re.finditer(r'<section\b[^>]*class="slide\b.*?</section>', original, re.S))
    assert len(sections) == 60
    cross = json.loads((RESULTS / "summary.json").read_text(encoding="utf-8"))
    matched = json.loads((RESULTS / "matched/systemone_chat_summary.json").read_text(encoding="utf-8"))
    online = json.loads((RESULTS / "rollout_repeat/manifest.json").read_text(encoding="utf-8"))["summary"]
    pages = []

    def add(title, sub, body, speaker):
        pages.append((title, sub, body, speaker))

    add("从原理走向可部署实验", "2026-10-06 · 两种替代实现，三层实验问题", cards([
        ("模型", "NanoJev", "训练一个小型决策模型<br>检验任务专门化后的表现"),
        ("接口", "SGLang Jev-like", "让原有聊天模型直接读出候选概率<br>检验接口变化的收益"),
        ("对照", "标准会话 API", "同一个 Qwen、同一个任务<br>检验速度与长程结果")]),
        "前面的 Jev 原理和上游回放继续保留。接下来切换到本次服务器实测：先区分训练模型和包装接口，再讨论证据。Jev 是原始参照，本次不具备新的 Jev 在线调用结果。")
    add("本次账号尚未获得 Jev API 权限", "访问限制是本次实验条件，不代表所有用户都无法申请", cards([
        ("Jev", "公开资料 + 上游记录", "介绍原理与官方训练目标<br>不把历史轨迹当成新的 Jev 推理"),
        ("NanoJev", "源码与权重可本地运行", "固定发布 checkpoint<br>在 A100 上加载并实际推理"),
        ("SGLang", "兼容接口可部署", "同一 Qwen 服务同时支持<br>System One 与聊天接口")]),
        "用户当前账号尚未获得 Jev API 权限，因此本轮不做 Jev 的实时性能排名。原始 Jev 的结构和训练说明来自官方公开资料；历史概率和轨迹属于上游记录。NanoJev 和 SGLang 则确实在新服务器上运行。")
    add("共性在决策契约，差异在如何得到概率", "输入状态和候选问题，输出可供程序选择的类型化答案", flow([
        ("公开状态", "材料、观察、已知记忆"), ("问题与候选", "Choice / Boolean / Score"),
        ("候选概率", "模型读出或标签评分"), ("程序行动", "选动作、执行、更新状态")],
        "三者都可服务决策流程；概率归一化不等于校准，接口相似也不能证明内部实现相同。"),
        "共同点是把小判断交给模型、把行动与状态更新交给程序。这个契约可以支持同一个决策控制器。它没有要求模型必须采用同一架构，也没有承诺概率天然可靠。")
    add("NanoJev：训练底座与决策读出", "本次模型基于 Qwen3-0.6B，使用发布的 unified checkpoint", flow([
        ("候选路径", "状态 + 问题 + 每个候选"), ("共享底座", "候选表示由 backbone 编码"),
        ("决策头", "集合交互与共享评分"), ("概率分布", "本次 Choice 经 softmax 输出")],
        "有额外训练和决策头；本次直接加载已发布权重，没有重新训练。不是 Jev 的官方权重或完整训练配方。"),
        "NanoJev 是社区实现，约 0.6B 底座，源码能核验候选路径和决策头。发布 unified 权重接受过游戏任务监督，其中包含专家标签和 Jev 教师概率。它的专门训练可能使它更贴合这些目标，但不能据此称为复现了 Jev 的 RLCD。")
    add("SGLang：用原聊天模型评分候选标签", "本次 Qwen3.8-27B 权重不变，System One 接口不增加决策训练", flow([
        ("选择题提示", "候选映射为 A、B、C…"), ("一次 prefill", "关闭 thinking，不生成答复"),
        ("标签分数", "读取回答位置的 next-token logits"), ("候选分布", "对给定标签归一化")],
        "API：/v1/systemone · 输出 token 为 0；省掉生成并不自动增加规划能力或概率校准。"),
        "这条路线保留原模型的词表输出头，在回答位置读取候选标签分数。它是推理接口适配，而不是额外训练出来的 Jev 模型。label mass 反映词表概率有多少落在候选标签上，也不是事件正确率。")
    add("三者不能被写成同一种模型", "原理参照、社区训练实现、通用模型接口适配", table(
        ["维度", "TypeSafe Jev", "NanoJev", "SGLang Jev-like"], [
        ["实现来源", "官方模型服务", "社区开源决策模型", "SGLang 推理接口"],
        ["训练", "官方称 RLCD", "任务监督与教师目标", "本轮未新增训练"],
        ["本轮权重", "未在线调用", "Qwen3-0.6B + 决策头", "Qwen3.8-27B 原权重"],
        ["校准", "官方目标；需按任务验证", "本轮未验证校准", "标签分布；不默认校准"],
        ["可核验范围", "公开契约与官方资料", "本地源码、权重与推理", "服务源码与 API 响应"]],
        "Jev 的完整内部架构和训练配方未公开；不能把 NanoJev 或 SGLang 的实现反推为 Jev 的事实。"),
        "这张表把能力契约和实现事实分开。原理相通不等于参数、训练或校准能力相同。Jev 的官方目标可以说明，但本轮既没有 API 实测，也没有获得其内部完整配方。")
    add("三组实验，回答三个不同的问题", "A100 80GB ×1 · SGLang 0.5.21 · 固定模型与数据版本", cards([
        ("01 · 跨模型", "NanoJev vs SGLang", "96 个相同离线状态<br>专家动作匹配 / 教师一致性"),
        ("02 · 同模型", "System One vs Chat", "96 个相同提示与候选<br>动作一致性 / HTTP 耗时"),
        ("03 · 完整任务", "执行真实 episode", "8 个配对初始任务，独立复跑<br>环境成功率 / 行动成本")]),
        "跨模型实验混合了训练、容量和编码方式，只能评价这两个部署实例。同模型接口实验把权重与提示固定。完整任务则让两种接口各自控制环境，真实的成功由模拟器判断。这三类结果不能互相替代。")
    add("96 条离线题，参考目标并不相同", "按 ID 的 SHA-256 排序，每个任务/划分最多取 30 个不同 episode", table(
        ["任务", "test / OOD", "参考目标", "指标含义"], [
        ["射击", "30 / 30", "专家策略最大概率动作", "匹配参考动作，不是通关率"],
        ["迷宫", "10 / 10", "上游 Jev 概率", "接近教师，不代表真实正确"],
        ["贪吃蛇", "8 / 8", "上游 Jev 概率", "接近教师，不代表真实正确"]],
        "不同 episode 不足 30 时全部纳入；不是全量 4,438 条数据。教师概率没有作为模型输入。"),
        "一共 96 条题目。射击数据中的 gold 明确标为 reference_argmax_compatibility，是与专家首选动作的匹配。迷宫和贪吃蛇没有独立正确动作标签，只能比较 Jev 教师一致性。这是离线测试，不是让模型重新玩一局。")
    groups = cross["by_split_task"]
    rows = []
    for split, task, name in [("test","shooting","射击"),("ood","shooting","射击"),("test","maze","迷宫"),("ood","maze","迷宫"),("test","snake","贪吃蛇"),("ood","snake","贪吃蛇")]:
        g=groups[f"{split}/{task}"]; metric="expert_argmax_match" if task=="shooting" else "jev_teacher_top1_match"
        rows.append([f'{split.upper()} / {name}',str(g['n']),f"{g['nano_'+metric]*100:.1f}%",f"{g['sglang_'+metric]*100:.1f}%","专家动作匹配" if task=="shooting" else "Jev 教师一致"])
    add("NanoJev 更贴合这批参考目标", "小样本离线对照 · 两模型不同，不能把差异归因于接口", table(
        ["划分 / 任务", "题数", "NanoJev", "SGLang", "比较口径"], rows,
        "射击合计 47/60 vs 12/60；教师首选动作合计 27/36 vs 19/36。OOD 贪吃蛇上 SGLang 为 8/8。"),
        "多数分组中 NanoJev 更贴合专家或教师目标，但不是所有任务都领先。OOD 贪吃蛇上 SGLang 与教师首选动作全部一致。NanoJev 的发布模型针对相应任务训练过，这支持任务适配的价值，不能推出它普遍优于 Jev 或通用大模型。")
    overall=cross["overall"]
    add("35.4 ms 与 158.2 ms 描述两套部署", "跨模型延迟：NanoJev 同进程调用，SGLang 经 localhost HTTP", cards([
        ("NanoJev · 中位数", f'{overall["nano_latency_s_median"]*1000:.1f} ms', "0.6B 底座 + 决策头<br>FP32 驻留，BF16 autocast"),
        ("SGLang · 中位数", f'{overall["sglang_latency_s_median"]*1000:.1f} ms', "27B 聊天模型，BF16<br>System One HTTP 请求"),
        ("解释边界", "不作公平速度排名", "模型规模、路径、编码不同<br>没有排除这些混杂因素")]),
        "这是部署观察而非公平吞吐量排名。NanoJev 首次加载 11.39 秒不计入单题延迟，且客户端调用方式不同。不能把比值写成模型普遍快多少倍。为了判断 API 的收益，下一项必须保持同一个 Qwen。")
    add("同一 Qwen，才能检验接口变化", "三组采用同一 renderer、候选顺序与关闭 thinking 的模板", table(
        ["组", "路径", "输出预算", "96 题相对 A 的动作一致"], [
        ["A · System One", "候选标签评分", "0 生成 token", "参照"],
        ["B · Chat", "贪心生成一个字母", "最多 1 token", "96 / 96"],
        ["C · Chat", "常规短答并结束", "最多 32；实际均值 2", "95 / 96"]],
        "96 题输入 token 数逐题相同；代表样本完整 token ID 序列相同。C 的一题差异尚待确定性复查。"),
        "不是让聊天模型先写一段长解释再比速度；那样会夸大不生成文字的优势。B 是最强的短输出基线，C 允许正常终止答复。A/B 全部同动作，C 有一条差异，但汇总的专家/教师匹配数恰好相同。")
    mo=matched["overall"]
    add("不生成文本，不保证判断普遍更快", "同提示的 96 题 HTTP 耗时中位数 · 小规模 pilot", bars([
        ("System One",mo["systemone"]["latency_median_s"]*1000,"0 个生成 token"),
        ("Chat · 1 token",mo["chat_1token"]["latency_median_s"]*1000,"优化的单字母回答"),
        ("Chat · 最多 32 token",mo["chat_32tokens"]["latency_median_s"]*1000,"实际输出均值 2 token")],150,"ms","未清空 prefix cache；每题一次测量。计时至响应 JSON 读取完成，不能推广为稳定性能排名。"),
        "这里 System One 处于两种会话设置之间：比一个 token 的优化基线慢，比允许正常结束的短答快。速度依赖输出预算、缓存、调度和输入长度。仅用输出 token 为零这一事实，不能推出全场景更快。")
    add("完整任务中，两种接口的轨迹一致", "迷宫与贪吃蛇 · 8 个相同初始世界与种子 · 关闭 thinking、贪心选动作", cards([
        ("真实环境成功", "6 / 8 = 6 / 8", "System One 与 1-token Chat<br>逐局独立 reset，相同物理预算"),
        ("动作序列一致", "8 / 8 对", "每组物理步骤总计 555<br>每组实际模型调用 460 次"),
        ("最长成功实例", "149 个物理步骤", "16×16 迷宫，两组都到达<br>含已知边上的代码重定位")]),
        "成功率由环境终止结果给出，不再借用教师动作。8 对轨迹全部一致，两次运行均为 6/8。这里最多 160 步预算；没有运行 800 步迷宫。重复同一组种子不能算成 16 个独立 case。")
    add("长程耗时约降 11%，任务结果一致", "独立复跑期间未发送其他模型请求 · 两组各 460 次请求", bars([
        ("System One",online["systemone"]["model_latency_s"],"6/8 成功，555 个物理步骤"),
        ("Chat · 1 token",online["chat_1token"]["model_latency_s"],"6/8 成功，555 个物理步骤")],140,"秒","单位：累计模型 HTTP 秒数；System One 低约 11.0%。8 个 case、缓存未严格控制，不是稳定速度结论。"),
        "在线复跑中 System One 累计请求耗时为 107.71 秒，Chat 为 120.99 秒。这里的请求序列和固定状态测试不同，因此速度结论也不同。首轮受到一次审计请求重叠影响的 194.45 秒不用于宣传。本页只使用无其他模型请求的复跑数据。")
    add("NanoJev 的优势，尚不能归因于校准", "本次是 0.6B 底座，不是 0.5B；动作匹配与概率校准是不同指标", cards([
        ("数据观察", "专家匹配 78.3%", "NanoJev 47/60，SGLang 12/60<br>这是参考动作匹配，非通关率"),
        ("合理解释", "任务监督与适配", "NanoJev 接受专家/教师目标训练<br>通用 Qwen 仅换评分接口"),
        ("待检验假设", "校准带来优势？", "缺少训练前后与校准消融<br>未测独立结果上的可靠性")]),
        "用户提出校准可能是关键因素，这可以保留为研究假设。Jev 官方强调校准目标，但本轮没有 Jev 在线数据，也没有对 NanoJev 做独立结果的校准评价。NanoJev 比通用 Qwen 更贴合任务目标，任务监督和训练适配是合理解释；模型容量、输入编码、决策头也不同，不能确认唯一原因。要隔离校准作用，需要同底座、同数据、同训练预算的目标消融，以及独立结果的 Brier/log loss 和可靠性图。单纯事后温度缩放通常不会改变同题 argmax，所以更可靠的概率与更高的动作匹配率不能直接画等号。")
    add("输出预算影响速度，长程质量未变", "把数据观察、机制解释与待验证假设分开", cards([
        ("NanoJev vs Jev-like", "适配值得研究", "0.6B 专门训练更贴合参考目标<br>校准贡献尚未被独立验证"),
        ("短输出 · 同 Qwen", "收益取决于基线", "85.7 ms < 常规短答 119.7 ms<br>但 > 1-token Chat 57.5 ms"),
        ("完整任务 · 同 Qwen", "质量相同，耗时有差", "两组均 6/8，8 对轨迹一致<br>107.7 vs 121.0 秒：约降 11%")]),
        "用户关于接口不一定改善长程判断的分析与这批实测一致，但应表述为这8个任务没有显示质量提升。107.7秒与121秒不是完全没有差异，累计模型HTTP耗时低约11%，只是样本小、缓存未严格控制，不能称为稳定收益。短输出的85.7与119.7毫秒支持特定常规短答设置下更快，不支持比最优化1-token会话更快；32是上限，实际平均只生成2个token。校准是否让NanoJev受益需要消融，不把合理猜测写成实验结论。")

    assert len(pages)==16
    plan = "# 2026-10-06 服务器实验更新\n\n当前共65页：原理1–39页、上游回放40–46页、实验47–62页、未来与收尾63–65页。按用户要求删除此前11页AI4-Loc/kernel方案与验证内容；历史备份保留但不进入当前报告。\n\n|页|主题|\n|---|---|\n"
    plan += '\n'.join(f'|{47+i}|{t}|' for i,(t,_,_,_) in enumerate(pages))
    plan += "\n\n数据入口：`experiment/nanojev_compare/README.md`、`SYSTEMONE_VS_CHAT_PROTOCOL.md`、`results/interface_validation.json`。\n\n来源：本地 NanoJev 源码 README 与固定权重；https://docs.sglang.io/docs/supported-models/decision_models；https://typesafe.ai/blog/introducing-system-one-models-and-jev；原官方训练资料的本地核查笔记。\n\n权限说明来自本次用户账号情况；没有独立验证所有用户的申请渠道。未宣称开源方案的热度排名。\n\n复建：`python experiment/nanojev_compare/update_report_slides.py`。旧v4生成器写入另一份历史目录，不是本报告的当前生成入口。\n"
    (REPORT / "notes/服务器实验更新.md").write_text(plan,encoding="utf-8")
    chapter='\n<!-- SERVER EXPERIMENTS 2026-10-06 -->\n'+ '\n'.join(
        f'<section class="slide exp-v5" data-sec="08 服务器实测" data-title="{esc(t)}"><div class="kicker">08 服务器实测 · {i+1:02} / 16</div><h1>{t}</h1><div class="sub">{s}</div>{b}</section>' for i,(t,s,b,_) in enumerate(pages))
    cut=sections[46].start()
    # Drop old pages 47–57 completely; keep only the general future/end pages.
    updated=original[:cut]+chapter+'\n'+original[sections[57].start():]
    css='''<style id="server-experiments-style">
.exp-v5 h1{font-size:62px;line-height:1.25}.exp-v5 .sub{font-size:28px;line-height:1.5}
.exp-cards{flex:1;min-height:0;display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-top:44px}
.exp-cards article{background:white;border-radius:26px;padding:40px 34px;display:flex;flex-direction:column;justify-content:center}
.exp-cards small,.exp-flow small{font-size:22px;color:var(--muted);letter-spacing:.05em}.exp-cards h2{font-size:43px;line-height:1.4;margin:28px 0;color:var(--accent);font-weight:600}.exp-cards p{font-size:29px;line-height:1.8;color:var(--muted)}
.exp-flow{flex:1;display:grid;grid-template-columns:repeat(4,1fr);gap:24px;align-content:center;margin-top:35px}
.exp-flow article{background:white;border-radius:26px;padding:38px 28px;min-height:270px}.exp-flow h2{font-size:38px;margin:22px 0;color:var(--accent)}.exp-flow p{font-size:27px;line-height:1.6;color:var(--muted)}
.exp-note{font-size:24px;line-height:1.6;color:var(--muted);margin-top:28px}
.exp-table{flex:1;min-height:0;margin-top:36px;background:white;border-radius:26px;padding:34px 38px;display:flex;flex-direction:column;justify-content:center}
.exp-table table{width:100%;border-collapse:collapse;table-layout:auto;text-align:left}.exp-table th{font-size:23px;font-weight:500;color:var(--muted);padding:16px 14px;border-bottom:2px solid var(--line)}.exp-table td{font-size:27px;padding:19px 14px;line-height:1.55;border-bottom:1px solid var(--line)}.exp-table td:first-child{font-weight:600}.exp-table tr:last-child td{border-bottom:0}.exp-table .exp-note{font-size:23px}
.exp-bars{flex:1;background:white;border-radius:26px;margin-top:40px;padding:42px 55px;display:flex;flex-direction:column;justify-content:center;gap:30px}.exp-bars label{display:flex;justify-content:space-between;font-size:30px;line-height:1.5}.exp-bars b{font-size:43px;color:var(--accent);font-weight:600}.exp-track{height:30px;border-radius:8px;background:var(--bg);margin-top:14px;overflow:hidden}.exp-track i{display:block;height:100%;background:var(--accent);border-radius:8px}.exp-bars p{font-size:24px;color:var(--muted);line-height:1.5;margin-top:12px}.exp-bars .exp-note{margin-top:0}
</style>'''
    updated=updated.replace('</head>',css+'</head>',1)
    DECK.write_text(updated,encoding="utf-8")
    notes='# 服务器实验章节讲稿（第47–62页）\n\n'+ '\n\n'.join(f'## 第 {47+i} 页｜{t}\n\n{n}' for i,(t,_,_,n) in enumerate(pages))
    notes+='\n\n## 领导问答补充\n\n**能说复现了 Jev 吗？** 共用类型化决策思路，但没有 Jev 官方权重、完整架构或训练配方。\n\n**NanoJev 更高的匹配率是因为校准吗？** 尚不能归因；任务监督和适配是合理解释，必须用同底座消融与独立结果验证校准贡献。\n\n**短时更快、长程没有差别吗？** 相对常规短答设置更快，相对1-token优化基线更慢；完整任务结果相同，但累计模型耗时约低11%，样本小、缓存未严格控制。\n\n**NanoJev 是不是胜过了 Jev？** 本次没有新的 Jev 在线评测；教师一致性不是实际正确率。\n'
    (REPORT / '演讲稿-服务器实验补充.md').write_text(notes,encoding='utf-8')
    # Renumber the existing scripts using immutable backups. Insert new content
    # before old page 47, retaining the original discussion and all later pages.
    for name in ('演讲稿-逐页详细版.md','演讲稿与领导问答.md'):
        target=REPORT/name
        backup=Path(__file__).resolve().parent / 'report_source' / name
        if not backup.exists():backup.write_bytes(target.read_bytes())
        old=backup.read_text(encoding='utf-8')
        headings=list(re.finditer(r'^## 第\s*(\d+)\s*页.*$',old,re.M))
        retained=[]
        for index,m in enumerate(headings):
            n=int(m.group(1))
            if 47<=n<=57:continue
            end=headings[index+1].start() if index+1<len(headings) else len(old)
            block=old[m.start():end]
            if index==len(headings)-1:
                extra=re.search(r'\n## (?!第)',block)
                if extra:block=block[:extra.start()]
            if n>=58:block=re.sub(r'(^## 第\s*)\d+(\s*页)',lambda x:x.group(1)+str(n+5)+x.group(2),block,count=1,flags=re.M)
            retained.append((n,block))
        prefix='# Jev 原理与服务器实验：65页讲稿\n\n当前已移除AI4-Loc方案，聚焦NanoJev、SGLang Jev-like及Chat实验分析。第47–62页为实验，63–65页为未来与收尾。历史版本保存在备份。\n\n'+''.join(b for n,b in retained if n<=46)
        tail=''.join(b for n,b in retained if n>=58)
        insertion='\n'.join(f'## 第 {47+i} 页｜{t}\n\n{n}\n' for i,(t,_,_,n) in enumerate(pages))
        target.write_text(prefix+insertion+'\n'+tail,encoding='utf-8')
    (REPORT/'slides/使用说明.md').write_text('# 当前报告：65页\n\n第47–62页为实验分析，未来与收尾为63–65页。\n\n方向键/空格翻页，G打开目录，数字键跳页；实验从 `deck.html#47` 开始。原迷宫回放和三段训练视频保留。全部素材本地，断网可用。\n\n'+plan,encoding='utf-8')
    readme=REPORT/'README.md'
    old='# Jev 原理、替代实现与实验分析\n\n当前版本：2026-10-06，**65页**。按用户要求移除AI4-Loc相关方案；保留Jev原理、上游回放，聚焦NanoJev、SGLang Jev-like与Chat的实验分析。\n\n- [完整网页报告](slides/deck.html)：实验第47–62页，未来与收尾第63–65页。\n- [实验说明与证据](notes/服务器实验更新.md)\n- [实验讲稿与问答](演讲稿-服务器实验补充.md)\n- [全页预览](slides/预览-全部页面.png)\n\n核心结论：NanoJev更贴合参考目标，校准贡献待验证；输出预算影响接口延迟；同Qwen完整任务质量一致，复跑累计模型耗时约低11%。\n\n构建：`python experiment/nanojev_compare/update_report_slides.py`\n\n验证：`python experiment/nanojev_compare/verify_report_slides.py`\n\n原版与76页版本均保留为历史HTML备份，当前讲稿已同步65页。\n'
    readme.write_text(old,encoding='utf-8')
    print('Updated',DECK,'pages',49+len(pages))


if __name__=='__main__':main()
