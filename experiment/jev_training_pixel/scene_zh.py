"""Three training mechanisms, pixel-video v2, Chinese, reproducible toy values."""
from pathlib import Path as FilePath
import sys
HERE=FilePath(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'jev_pixel_explainer/.vendor'))
sys.path.insert(0,'C:/Users/YuTao/.codex/skills/pixel-video')
import numpy as np
from pixelkit import PHOSPHOR,Scene,Path,seg
from pixelkit import chrome
from pixelkit.widgets import module,wire
from chinese_font import ZH, text, Stages
P=PHOSPHOR
BOXES={'input':(12,46,94,65),'policy':(140,46,96,65),'output':(270,46,196,65),'feedback':(270,153,196,64),'score':(140,153,96,64),'update':(12,153,94,64)}
class Training(Scene):
 W,H,SCALE=480,270,4
 FPS,DURATION=60,32.
 PAL,LANG=P,'zh'
 BLOOM=dict(strength=.5,sigma=2.6,threshold=20)
 @property
 def lf(self):return ZH
 KIND='RLHF'
 def setup(self):
  self.d=dict(np.load(HERE/'data/data.npz'))
  if self.KIND=='RLHF':
   self.labels=['人工示范','策略模型','候选回答','人类 / 奖励模型','奖励','参数更新']
   caps=[('先用人工示范，对预训练模型做监督微调。','经典 RLHF：先学会如何回答，再学习偏好。'),('策略模型针对同一个提示词，生成候选回答。','回答是教学示意，本次未运行真实模型。'),('把两个候选回答放在一起，供人比较。','这里输出的是文本，不是置信概率。'),('人类标注者选出自己更偏好的回答。','本例标注：回答 A 优于回答 B。'),('用偏好排序训练奖励模型。','数值来自成对偏好算例；偏好不等于正确。'),('奖励模型为策略模型生成的新回答打分。','一个奖励分数，成为更新策略的训练信号。'),('用奖励更新策略，并用 KL 约束偏离程度。','经典 PPO 流程：避免过度偏离参考策略。'),('反复进行采样、评分和策略更新。','训练后，聊天模型在推理时仍然生成文本。')]
   statuses=['示范 → 监督微调','提示词 → 策略模型','两个候选回答','偏好 A 胜过 B','拟合奖励模型','为新回答评分','PPO + KL','目标：符合人类偏好']
  elif self.KIND=='RLVR':
   self.labels=['问题','策略模型','候选答案','验证器','奖励','参数更新']
   caps=[('选择能用规则或测试验证结果的任务。','算术示例：2 + 3 = 5；答案交给验证器。'),('策略模型先根据问题生成答案。','先生成文本，再验证；模型输入不含参考答案。'),('本例采样得到两个答案：5 和 6。','验证器检查答案对错，不评价语气是否讨喜。'),('验证器把候选答案与参考答案比较。','用规则、标准答案或测试提供可验证反馈。'),('为每个候选答案分配正确性奖励。','答案 5 得 1 分；答案 6 得 0 分。'),('根据奖励，计算并执行策略更新。','本片省略不同算法中的归一化等细节。'),('换更多可验证任务，重复采样和更新。','实际系统还可能加入输出格式奖励。'),('训练目标：让生成的答案更正确。','仅奖励答对，并不自动保证置信度校准。')]
   statuses=['2 + 3 = ?','采样文本答案','候选答案：5 / 6','参考答案：5','奖励：1 / 0','更新策略模型','重复训练','目标：答案正确']
  else:
   self.labels=['状态与问题','决策模型','预测分布','真实结果','示例评分','参数更新']
   caps=[('输入当前状态，以及一个有限选项的决策问题。','Jev 官方将这条训练路线称为 RLCD。'),('模型直接输出各选项的概率分布。','示例初值：是 0.90；否 0.10。'),('观察一组可比较样本的真实结果。','固定教学样本：10 次里有 6 是、4 否。'),('比较预测的概率分布和实际结果。','越自信地预测错误，受到的损失越大。'),('计算这组教学样本的平均对数损失。','概率 .90：损失 .984；概率 .60：损失 .673。'),('调整示例参数，让概率接近这组样本的频率。','这里用简单梯度下降，不是 Jev 的真实优化器。'),('群体校准：预测概率与实际发生频率相符。','本组概率趋近 .60；不保证单次判断正确。'),('Jev 的目标是输出经过校准的决策概率。','Jev 的精确损失与完整训练配方尚未公开。')]
   statuses=['状态 + 决策问题','是的概率 = .90','10 次中 6 次为是','评价整个概率分布','损失：.984 → .673','调整示例参数','是的概率 → .60','Jev 路线：RLCD']
  self.stages=Stages([dict(name=['输入','模型','输出','反馈','评分','学习','循环','小结'][i],t=4.*i,status=statuses[i],cap=caps[i]) for i in range(8)])
  self.paths=[Path([(106,78),(140,78)]),Path([(236,78),(270,78)]),Path([(368,111),(368,153)]),Path([(270,185),(236,185)]),Path([(140,185),(106,185)]),Path([(59,153),(59,131),(125,131),(125,78),(140,78)])]
  if self.KIND=='RLCD':self.paths[2]=Path([(300,111),(300,130),(188,130),(188,153)])
 def draw(self,cv,t):
  chrome.background(cv);stage,_=self.stages.at(t)
  active=[{'input'},{'policy'},{'output'},{'feedback'},{'feedback','score'},{'score','update'},{'update','policy'},set(BOXES)][stage]
  for (key,(x,y,w,h)),label in zip(BOXES.items(),self.labels):module(cv,x,y,w,h,'active' if key in active else 'idle',P,label=label,font=self.lf)
  for i,path in enumerate(self.paths):wire(cv,path,t,[4,8,12,16,20,24][i],.8,P,hold=1.1,n=5,gap=.12)
  text(cv,12,26,'训练流程',P['label']);text(cv,466,26,'教学示意',P['orange'],align='r')
  col=lambda s:P['text'] if stage>=s else P['idle']
  if self.KIND=='RLHF':
   text(cv,22,69,'提示词',col(0));text(cv,22,87,'示范回答',col(0))
   text(cv,150,69,'监督微调',col(1));text(cv,150,87,'采样回答',col(1))
   text(cv,280,69,'回答 A：清楚具体',col(2),n=max(0,int((t-8)*14)));text(cv,280,87,'回答 B：含糊笼统',col(2),n=max(0,int((t-8.8)*14)))
   text(cv,280,175,'人工排序：A 优于 B',col(3),n=max(0,int((t-12)*9)));text(cv,280,194,'拟合奖励模型',col(4))
   prob=float(self.d['preference_fit'][min(7,max(0,int((t-16)*2)))])
   text(cv,150,175,'R(A), B=0' if stage>=5 else 'P(A > B)',col(4));value=float(np.log(prob/(1-prob))) if stage>=5 else prob;text(cv,150,194,f'{value:.2f}' if stage>=4 else '...',P['orange'] if stage>=4 else P['idle'])
   text(cv,22,175,'PPO + KL',col(5));text(cv,22,194,'策略模型',col(5))
   text(cv,12,220,'人类偏好提供训练信号',P['label'])
  elif self.KIND=='RLVR':
   text(cv,22,69,'2 + 3 = ?',col(0));text(cv,22,87,'只给问题',col(0))
   text(cv,150,69,'生成',col(1));text(cv,150,87,'文本答案',col(1))
   text(cv,280,69,'答案 A：5',col(2),n=max(0,int((t-8)*9)));text(cv,280,87,'答案 B：6',col(2),n=max(0,int((t-8.8)*9)))
   text(cv,280,170,'参考答案：5',col(3));text(cv,280,185,'5 等于 5：正确',col(3));text(cv,280,200,'6 不等于 5：错误',col(3))
   text(cv,150,175,'A -> 1',col(4));text(cv,150,194,'B -> 0',col(4))
   text(cv,22,175,'策略模型',col(5));text(cv,22,194,'梯度更新',col(5))
   text(cv,12,220,'用规则或测试验证答案',P['label'])
  else:
   text(cv,22,69,'上下文',col(0));text(cv,22,87,'是 / 否',col(0))
   text(cv,150,69,'直接输出',col(1));text(cv,150,87,'概率分数',col(1))
   index=min(60,max(0,int((t-20)*15)));p=float(self.d['calibration_path'][index]) if stage>=5 else .9
   for k,(label,val) in enumerate([('是',p),('否',1-p)]):
    y=69+k*18;text(cv,280,y,label,col(1));cv.fill(311,y,102,7,P['blue_dk']);cv.fill(311,y,round(102*val*seg(t,4.4,5.5)),7,P['fwd']);text(cv,453,y,f'{val:.2f}' if stage>=1 else '...',col(1),align='r')
   text(cv,280,172,'同类样本：6 是 / 4 否',col(2))
   for i,v in enumerate(self.d['outcomes']):
    c=P['fwd'] if v else P['orange'];cv.fill(282+i*16,192,10,10,c if t>=8+i*.18 else P['idle'])
   text(cv,150,175,'对数损失',col(4));loss=-(.6*np.log(p)+.4*np.log(1-p));text(cv,150,194,f'{loss:.3f}' if stage>=4 else '...',col(4))
   text(cv,22,175,'示例参数',col(5));text(cv,22,194,'参数更新',col(5))
   text(cv,12,220,'教学损失；非 Jev 训练配方',P['orange'])
  text(cv,466,220,'未运行真实模型',P['label'],align='r')
  # Training loop phase travels continuously without displacing the fixed map.
  cv.fill(16+int((t%4)*26),124,3,2,P['orange'])
  self.stages.draw(cv,t,self.KIND,P)
 def sfx(self):return []
class RLHF(Training):KIND='RLHF';TITLE='RLHF'
class RLVR(Training):KIND='RLVR';TITLE='RLVR'
class RLCD(Training):KIND='RLCD';TITLE='RLCD'
