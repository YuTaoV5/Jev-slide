"""Build Chinese scene from retained English scene; geometry/math stay traceable."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=(HERE/'scene.py').read_text(encoding='utf-8')
s=s.replace('English, reproducible','Chinese, reproducible')
s=s.replace("PAL,LANG=P,'en'", "PAL,LANG=P,'zh'")
s=s.replace('P=PHOSPHOR', 'from chinese_font import ZH, text, Stages\nP=PHOSPHOR')
s=s.replace(" KIND='RLHF'", " @property\n def lf(self):return ZH\n KIND='RLHF'")
s=s.replace('chrome.Stages(', 'Stages(').replace('cv.text(', 'text(cv,')
s=s.replace('12,228,', '12,220,').replace('466,228,', '466,220,')
translations={
'DEMOS':'人工示范','POLICY':'策略模型','RESPONSES':'候选回答','HUMAN / RM':'人类 / 奖励模型','REWARD':'奖励','UPDATE':'参数更新',
'TASK':'问题','SOLUTIONS':'候选答案','VERIFIER':'验证器','STATE':'状态与问题','DECIDER':'决策模型','FORECAST':'预测分布','OUTCOMES':'真实结果','TOY SCORE':'示例评分',
'INPUT':'输入','MODEL':'模型','OUTPUT':'输出','CHECK':'反馈','SCORE':'评分','LEARN':'学习','LOOP':'循环','RECAP':'小结',
'TRAINING VIEW':'训练流程','ILLUSTRATIVE':'教学示意','NO MODEL RUN':'未运行真实模型',
'PROMPT':'提示词','DEMO':'示范回答','SFT MODEL':'监督微调','SAMPLE':'采样回答','A: CLEAR RESPONSE':'回答 A：清楚具体','B: VAGUE RESPONSE':'回答 B：含糊笼统','RANK: A > B':'人工排序：A 优于 B','FIT REWARD MODEL':'拟合奖励模型','PREFERENCE LABELS GUIDE TRAINING':'人类偏好提供训练信号',
'TASK ONLY':'只给问题','GENERATE':'生成','TEXT':'文本答案','SAMPLE A: 5':'答案 A：5','SAMPLE B: 6':'答案 B：6','REFERENCE: 5':'参考答案：5','5 == 5 : TRUE':'5 等于 5：正确','6 == 5 : FALSE':'6 不等于 5：错误','GRADIENT':'梯度更新','ANSWER CORRECTNESS IS CHECKED IN CODE':'用规则或测试验证答案',
'CONTEXT':'上下文','YES / NO':'是 / 否','DIRECT':'直接输出','SCORES':'概率分数','YES':'是','NO':'否','OBSERVED: 6 YES / 4 NO':'同类样本：6 是 / 4 否','LOG LOSS':'对数损失','TOY LOGIT':'示例参数','TOY LOSS, NOT JEV RECIPE':'教学损失；非 Jev 训练配方',
'DEMOS -> SFT':'示范 → 监督微调','PROMPT -> POLICY':'提示词 → 策略模型','2 RESPONSES':'两个候选回答','A > B':'偏好 A 胜过 B','REWARD FOR TEXT':'为新回答评分','PREFERENCE OBJECTIVE':'目标：符合人类偏好',
'SAMPLE TEXT':'采样文本答案','ANSWERS: 5 / 6':'候选答案：5 / 6','REWARDS: 1 / 0':'奖励：1 / 0','UPDATE POLICY':'更新策略模型','REPEAT':'重复训练','CORRECTNESS OBJECTIVE':'目标：答案正确',
'STATE + QUESTION':'状态 + 决策问题','P(YES) = .90':'是的概率 = .90','6 / 10 YES':'10 次中 6 次为是','SCORE DISTRIBUTION':'评价整个概率分布','LOSS: .984 -> .673':'损失：.984 → .673','TOY PARAMETER UPDATE':'调整示例参数','P(YES) -> .60':'是的概率 → .60','RLCD, NOT RLVR':'Jev 路线：RLCD',
'START FROM DEMONSTRATIONS AND A PRETRAINED MODEL.':'先用人工示范，对预训练模型做监督微调。','CLASSIC RLHF: SUPERVISED FINE-TUNING FIRST':'经典 RLHF：先学会如何回答，再学习偏好。',
'THE POLICY GENERATES CANDIDATE RESPONSES.':'策略模型针对同一个提示词，生成候选回答。','ILLUSTRATIVE RESPONSES; NO MODEL WAS RUN':'回答是教学示意，本次未运行真实模型。',
'COMPARE TWO RESPONSES TO THE SAME PROMPT.':'把两个候选回答放在一起，供人比较。','THEY ARE TEXT SAMPLES, NOT CONFIDENCE ESTIMATES':'这里输出的是文本，不是置信概率。',
'A PERSON RANKS WHICH RESPONSE THEY PREFER.':'人类标注者选出自己更偏好的回答。','TOY LABEL: A IS PREFERRED TO B':'本例标注：回答 A 优于回答 B。',
'TRAIN A REWARD MODEL ON THE RANKED PAIRS.':'用偏好排序训练奖励模型。','TOY PAIRWISE FIT; PREFERENCE IS NOT CORRECTNESS':'数值来自成对偏好算例；偏好不等于正确。',
'SCORE FRESH POLICY RESPONSES WITH THE REWARD MODEL.':'奖励模型为策略模型生成的新回答打分。','SCALAR REWARD PROVIDES A TRAINING SIGNAL':'一个奖励分数，成为更新策略的训练信号。',
'UPDATE THE POLICY USING REWARD AND A KL CONSTRAINT.':'用奖励更新策略，并用 KL 约束偏离程度。','CLASSIC PPO LOOP; THE REFERENCE LIMITS DRIFT':'经典 PPO 流程：避免过度偏离参考策略。',
'REPEAT SAMPLING, SCORING AND POLICY UPDATES.':'反复进行采样、评分和策略更新。','AT INFERENCE THE CHAT POLICY GENERATES TEXT':'训练后，聊天模型在推理时仍然生成文本。',
'CHOOSE A TASK WITH A CHECKABLE REFERENCE.':'选择能用规则或测试验证结果的任务。','TOY ARITHMETIC: 2 + 3 = 5':'算术示例：2 + 3 = 5；答案交给验证器。',
'THE POLICY GENERATES SOLUTIONS TO THE TASK.':'策略模型先根据问题生成答案。','THE TEXT IS GENERATED BEFORE IT IS VERIFIED':'先生成文本，再验证；模型输入不含参考答案。',
'SAMPLE ANSWERS 5 AND 6 FOR THIS TOY TASK.':'本例采样得到两个答案：5 和 6。','THE VERIFIER CHECKS THE RESULT, NOT THE TONE':'验证器检查答案对错，不评价语气是否讨喜。',
'COMPARE EACH ANSWER WITH THE REFERENCE.':'验证器把候选答案与参考答案比较。','A RULE OR TEST PROVIDES CHECKABLE FEEDBACK':'用规则、标准答案或测试提供可验证反馈。',
'ASSIGN THE CORRECTNESS REWARD TO EACH SAMPLE.':'为每个候选答案分配正确性奖励。','ANSWER 5: REWARD 1; ANSWER 6: REWARD 0':'答案 5 得 1 分；答案 6 得 0 分。',
'USE THE REWARDS TO FORM A POLICY UPDATE.':'根据奖励，计算并执行策略更新。','THIS FILM OMITS ALGORITHM-SPECIFIC NORMALIZATION':'本片省略不同算法中的归一化等细节。',
'REPEAT WITH MORE CHECKABLE TASKS AND SAMPLES.':'换更多可验证任务，重复采样和更新。','ACTUAL SYSTEMS MAY ALSO USE FORMAT REWARDS':'实际系统还可能加入输出格式奖励。',
'THE OBJECTIVE REWARDS CORRECT GENERATED ANSWERS.':'训练目标：让生成的答案更正确。','IT DOES NOT BY ITSELF CALIBRATE REPORTED CONFIDENCE':'仅奖励答对，并不自动保证置信度校准。',
'PRESENT A STATE AND A FINITE DECISION QUESTION.':'输入当前状态，以及一个有限选项的决策问题。','JEV CALLS ITS TRAINING DIRECTION RLCD':'Jev 官方将这条训练路线称为 RLCD。',
'OUTPUT A PROBABILITY DISTRIBUTION, NOT A REPLY.':'模型直接输出各选项的概率分布。','TOY START: P(YES) = 0.90; P(NO) = 0.10':'示例初值：是 0.90；否 0.10。',
'OBSERVE OUTCOMES FOR COMPARABLE TOY CASES.':'观察一组可比较样本的真实结果。','6 YES AND 4 NO IN THIS FIXED TEACHING GROUP':'固定教学样本：10 次里有 6 是、4 否。',
'COMPARE THE WHOLE FORECAST WITH THE OUTCOMES.':'比较预测的概率分布和实际结果。','A WRONG HIGH-CONFIDENCE FORECAST GETS MORE LOSS':'越自信地预测错误，受到的损失越大。',
'COMPUTE MEAN LOG LOSS FOR THE TOY GROUP.':'计算这组教学样本的平均对数损失。','P=.90: .984; P=.60: .673; LOWER IS BETTER':'概率 .90：损失 .984；概率 .60：损失 .673。',
'UPDATE THE TOY LOGIT TOWARD THE GROUP FREQUENCY.':'调整示例参数，让概率接近这组样本的频率。','SCALAR GRADIENT DESCENT; NOT THE JEV OPTIMIZER':'这里用简单梯度下降，不是 Jev 的真实优化器。',
'A CALIBRATED GROUP FORECAST MATCHES ITS FREQUENCY.':'群体校准：预测概率与实际发生频率相符。','P=.60 FOR THIS GROUP; NO SINGLE-CASE GUARANTEE':'本组概率趋近 .60；不保证单次判断正确。',
'JEV AIMS AT CALIBRATED DECISIONS.':'Jev 的目标是输出经过校准的决策概率。','EXACT JEV LOSS AND TRAINING RECIPE ARE NOT PUBLIC':'Jev 的精确损失与完整训练配方尚未公开。',
}
for en,zh in translations.items():
    token=repr(en)
    assert token in s, en
    s=s.replace(token,repr(zh))
(HERE/'scene_zh.py').write_text(s,encoding='utf-8')
r=(HERE/'render_windows.py').read_text(encoding='utf-8').replace('import scene as scenes','import scene_zh as scenes')
r=r.replace("{kind.lower()}.mp4", "{kind.lower()}-zh.mp4").replace("{kind.lower()}-render-verification.json", "{kind.lower()}-zh-render-verification.json")
(HERE/'render_zh.py').write_text(r,encoding='utf-8')
print('Chinese scene and renderer generated')
