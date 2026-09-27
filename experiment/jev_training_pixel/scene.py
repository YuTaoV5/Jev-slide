"""Three training mechanisms, pixel-video v2, English, reproducible toy values."""
from pathlib import Path as FilePath
import sys
HERE=FilePath(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'jev_pixel_explainer/.vendor'))
sys.path.insert(0,'C:/Users/YuTao/.codex/skills/pixel-video')
import numpy as np
from pixelkit import PHOSPHOR,Scene,Path,seg
from pixelkit import chrome
from pixelkit.widgets import module,wire
P=PHOSPHOR
BOXES={'input':(12,46,94,65),'policy':(140,46,96,65),'output':(270,46,196,65),'feedback':(270,153,196,64),'score':(140,153,96,64),'update':(12,153,94,64)}
class Training(Scene):
 W,H,SCALE=480,270,4
 FPS,DURATION=60,32.
 PAL,LANG=P,'en'
 BLOOM=dict(strength=.5,sigma=2.6,threshold=20)
 KIND='RLHF'
 def setup(self):
  self.d=dict(np.load(HERE/'data/data.npz'))
  if self.KIND=='RLHF':
   self.labels=['DEMOS','POLICY','RESPONSES','HUMAN / RM','REWARD','UPDATE']
   caps=[('START FROM DEMONSTRATIONS AND A PRETRAINED MODEL.','CLASSIC RLHF: SUPERVISED FINE-TUNING FIRST'),('THE POLICY GENERATES CANDIDATE RESPONSES.','ILLUSTRATIVE RESPONSES; NO MODEL WAS RUN'),('COMPARE TWO RESPONSES TO THE SAME PROMPT.','THEY ARE TEXT SAMPLES, NOT CONFIDENCE ESTIMATES'),('A PERSON RANKS WHICH RESPONSE THEY PREFER.','TOY LABEL: A IS PREFERRED TO B'),('TRAIN A REWARD MODEL ON THE RANKED PAIRS.','TOY PAIRWISE FIT; PREFERENCE IS NOT CORRECTNESS'),('SCORE FRESH POLICY RESPONSES WITH THE REWARD MODEL.','SCALAR REWARD PROVIDES A TRAINING SIGNAL'),('UPDATE THE POLICY USING REWARD AND A KL CONSTRAINT.','CLASSIC PPO LOOP; THE REFERENCE LIMITS DRIFT'),('REPEAT SAMPLING, SCORING AND POLICY UPDATES.','AT INFERENCE THE CHAT POLICY GENERATES TEXT')]
   statuses=['DEMOS -> SFT','PROMPT -> POLICY','2 RESPONSES','A > B','FIT REWARD MODEL','REWARD FOR TEXT','PPO + KL','PREFERENCE OBJECTIVE']
  elif self.KIND=='RLVR':
   self.labels=['TASK','POLICY','SOLUTIONS','VERIFIER','REWARD','UPDATE']
   caps=[('CHOOSE A TASK WITH A CHECKABLE REFERENCE.','TOY ARITHMETIC: 2 + 3 = 5'),('THE POLICY GENERATES SOLUTIONS TO THE TASK.','THE TEXT IS GENERATED BEFORE IT IS VERIFIED'),('SAMPLE ANSWERS 5 AND 6 FOR THIS TOY TASK.','THE VERIFIER CHECKS THE RESULT, NOT THE TONE'),('COMPARE EACH ANSWER WITH THE REFERENCE.','A RULE OR TEST PROVIDES CHECKABLE FEEDBACK'),('ASSIGN THE CORRECTNESS REWARD TO EACH SAMPLE.','ANSWER 5: REWARD 1; ANSWER 6: REWARD 0'),('USE THE REWARDS TO FORM A POLICY UPDATE.','THIS FILM OMITS ALGORITHM-SPECIFIC NORMALIZATION'),('REPEAT WITH MORE CHECKABLE TASKS AND SAMPLES.','ACTUAL SYSTEMS MAY ALSO USE FORMAT REWARDS'),('THE OBJECTIVE REWARDS CORRECT GENERATED ANSWERS.','IT DOES NOT BY ITSELF CALIBRATE REPORTED CONFIDENCE')]
   statuses=['2 + 3 = ?','SAMPLE TEXT','ANSWERS: 5 / 6','REFERENCE: 5','REWARDS: 1 / 0','UPDATE POLICY','REPEAT','CORRECTNESS OBJECTIVE']
  else:
   self.labels=['STATE','DECIDER','FORECAST','OUTCOMES','TOY SCORE','UPDATE']
   caps=[('PRESENT A STATE AND A FINITE DECISION QUESTION.','JEV CALLS ITS TRAINING DIRECTION RLCD'),('OUTPUT A PROBABILITY DISTRIBUTION, NOT A REPLY.','TOY START: P(YES) = 0.90; P(NO) = 0.10'),('OBSERVE OUTCOMES FOR COMPARABLE TOY CASES.','6 YES AND 4 NO IN THIS FIXED TEACHING GROUP'),('COMPARE THE WHOLE FORECAST WITH THE OUTCOMES.','A WRONG HIGH-CONFIDENCE FORECAST GETS MORE LOSS'),('COMPUTE MEAN LOG LOSS FOR THE TOY GROUP.','P=.90: .984; P=.60: .673; LOWER IS BETTER'),('UPDATE THE TOY LOGIT TOWARD THE GROUP FREQUENCY.','SCALAR GRADIENT DESCENT; NOT THE JEV OPTIMIZER'),('A CALIBRATED GROUP FORECAST MATCHES ITS FREQUENCY.','P=.60 FOR THIS GROUP; NO SINGLE-CASE GUARANTEE'),('JEV AIMS AT CALIBRATED DECISIONS.','EXACT JEV LOSS AND TRAINING RECIPE ARE NOT PUBLIC')]
   statuses=['STATE + QUESTION','P(YES) = .90','6 / 10 YES','SCORE DISTRIBUTION','LOSS: .984 -> .673','TOY PARAMETER UPDATE','P(YES) -> .60','RLCD, NOT RLVR']
  self.stages=chrome.Stages([dict(name=['INPUT','MODEL','OUTPUT','CHECK','SCORE','LEARN','LOOP','RECAP'][i],t=4.*i,status=statuses[i],cap=caps[i]) for i in range(8)])
  self.paths=[Path([(106,78),(140,78)]),Path([(236,78),(270,78)]),Path([(368,111),(368,153)]),Path([(270,185),(236,185)]),Path([(140,185),(106,185)]),Path([(59,153),(59,131),(125,131),(125,78),(140,78)])]
  if self.KIND=='RLCD':self.paths[2]=Path([(300,111),(300,130),(188,130),(188,153)])
 def draw(self,cv,t):
  chrome.background(cv);stage,_=self.stages.at(t)
  active=[{'input'},{'policy'},{'output'},{'feedback'},{'feedback','score'},{'score','update'},{'update','policy'},set(BOXES)][stage]
  for (key,(x,y,w,h)),label in zip(BOXES.items(),self.labels):module(cv,x,y,w,h,'active' if key in active else 'idle',P,label=label,font=self.lf)
  for i,path in enumerate(self.paths):wire(cv,path,t,[4,8,12,16,20,24][i],.8,P,hold=1.1,n=5,gap=.12)
  cv.text(12,26,'TRAINING VIEW',P['label']);cv.text(466,26,'ILLUSTRATIVE',P['orange'],align='r')
  col=lambda s:P['text'] if stage>=s else P['idle']
  if self.KIND=='RLHF':
   cv.text(22,69,'PROMPT',col(0));cv.text(22,87,'DEMO',col(0))
   cv.text(150,69,'SFT MODEL',col(1));cv.text(150,87,'SAMPLE',col(1))
   cv.text(280,69,'A: CLEAR RESPONSE',col(2),n=max(0,int((t-8)*14)));cv.text(280,87,'B: VAGUE RESPONSE',col(2),n=max(0,int((t-8.8)*14)))
   cv.text(280,175,'RANK: A > B',col(3),n=max(0,int((t-12)*9)));cv.text(280,194,'FIT REWARD MODEL',col(4))
   prob=float(self.d['preference_fit'][min(7,max(0,int((t-16)*2)))])
   cv.text(150,175,'R(A), B=0' if stage>=5 else 'P(A > B)',col(4));value=float(np.log(prob/(1-prob))) if stage>=5 else prob;cv.text(150,194,f'{value:.2f}' if stage>=4 else '...',P['orange'] if stage>=4 else P['idle'])
   cv.text(22,175,'PPO + KL',col(5));cv.text(22,194,'POLICY',col(5))
   cv.text(12,228,'PREFERENCE LABELS GUIDE TRAINING',P['label'])
  elif self.KIND=='RLVR':
   cv.text(22,69,'2 + 3 = ?',col(0));cv.text(22,87,'TASK ONLY',col(0))
   cv.text(150,69,'GENERATE',col(1));cv.text(150,87,'TEXT',col(1))
   cv.text(280,69,'SAMPLE A: 5',col(2),n=max(0,int((t-8)*9)));cv.text(280,87,'SAMPLE B: 6',col(2),n=max(0,int((t-8.8)*9)))
   cv.text(280,170,'REFERENCE: 5',col(3));cv.text(280,185,'5 == 5 : TRUE',col(3));cv.text(280,200,'6 == 5 : FALSE',col(3))
   cv.text(150,175,'A -> 1',col(4));cv.text(150,194,'B -> 0',col(4))
   cv.text(22,175,'POLICY',col(5));cv.text(22,194,'GRADIENT',col(5))
   cv.text(12,228,'ANSWER CORRECTNESS IS CHECKED IN CODE',P['label'])
  else:
   cv.text(22,69,'CONTEXT',col(0));cv.text(22,87,'YES / NO',col(0))
   cv.text(150,69,'DIRECT',col(1));cv.text(150,87,'SCORES',col(1))
   index=min(60,max(0,int((t-20)*15)));p=float(self.d['calibration_path'][index]) if stage>=5 else .9
   for k,(label,val) in enumerate([('YES',p),('NO',1-p)]):
    y=69+k*18;cv.text(280,y,label,col(1));cv.fill(311,y,102,7,P['blue_dk']);cv.fill(311,y,round(102*val*seg(t,4.4,5.5)),7,P['fwd']);cv.text(453,y,f'{val:.2f}' if stage>=1 else '...',col(1),align='r')
   cv.text(280,172,'OBSERVED: 6 YES / 4 NO',col(2))
   for i,v in enumerate(self.d['outcomes']):
    c=P['fwd'] if v else P['orange'];cv.fill(282+i*16,192,10,10,c if t>=8+i*.18 else P['idle'])
   cv.text(150,175,'LOG LOSS',col(4));loss=-(.6*np.log(p)+.4*np.log(1-p));cv.text(150,194,f'{loss:.3f}' if stage>=4 else '...',col(4))
   cv.text(22,175,'TOY LOGIT',col(5));cv.text(22,194,'UPDATE',col(5))
   cv.text(12,228,'TOY LOSS, NOT JEV RECIPE',P['orange'])
  cv.text(466,228,'NO MODEL RUN',P['label'],align='r')
  # Training loop phase travels continuously without displacing the fixed map.
  cv.fill(16+int((t%4)*26),124,3,2,P['orange'])
  self.stages.draw(cv,t,self.KIND,P)
 def sfx(self):return []
class RLHF(Training):KIND='RLHF';TITLE='RLHF'
class RLVR(Training):KIND='RLVR';TITLE='RLVR'
class RLCD(Training):KIND='RLCD';TITLE='RLCD'
