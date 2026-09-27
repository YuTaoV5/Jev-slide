"""Reproducible educational values; no pretrained model or Jev training run."""
from pathlib import Path
import json, numpy as np
H=Path(__file__).resolve().parent
q=.6
ps=np.array([.5,.6,.8,.9,.95,.99])
loss=-(q*np.log(ps)+(1-q)*np.log(1-ps))
z=np.log(.9/.1);path=[]
for _ in range(61):
 p=1/(1+np.exp(-z));path.append(p);z-=.8*(p-q)
outcomes=np.array([1]*6+[0]*4)
# A toy Bradley-Terry reward model: one scalar score gap, A preferred to B.
gap=0.;bt=[]
for _ in range(8):
 prob=1/(1+np.exp(-gap));bt.append(prob);gap+=1-prob
np.savez(H/'data/data.npz',p=ps,loss=loss,q=q,calibration_path=path,outcomes=outcomes,preference_fit=bt)
(H/'data/provenance.json').write_text(json.dumps(dict(kind='deterministic teaching calculation',model_run=False,api_calls=0,q=q,log_loss=dict(zip(map(str,ps),loss)),outcomes=outcomes.tolist(),calibration_start=path[0],calibration_end=path[-1],notes='Not the disclosed Jev loss. Scalar gradient descent illustrates proper-scoring optimum, not the actual RLCD optimizer.'),indent=2),encoding='utf-8')
print('Toy calculations saved; .90 loss',loss[3],'; .60 loss',loss[1])
