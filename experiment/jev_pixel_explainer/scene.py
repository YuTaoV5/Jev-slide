"""Jev public interface plus application policy; no model inference or internal architecture."""
from pathlib import Path as FilePath
import math
import sys
HERE = FilePath(__file__).resolve().parent
sys.path.insert(0, str(HERE / '.vendor'))
sys.path.insert(0, 'C:/Users/YuTao/.codex/skills/pixel-video')
import numpy as np
from pixelkit import PHOSPHOR, Scene, Path, seg
from pixelkit import chrome
from pixelkit.widgets import module, wire, rbox

P = PHOSPHOR
TITLE = 'JEV'
T = [0., 4., 8., 12., 16., 21., 26., 31.]
DURATION = 36.
STAGES = [
    dict(name='STATE', t=T[0], status='STATE + QUESTIONS', cap=(
        'START WITH A SYNTHETIC SUPPORT TICKET.',
        'PUBLIC INTERFACE VIEW; THE MODEL WAS NOT RUN')),
    dict(name='TYPE', t=T[1], status='CHOICE: 3 OPTIONS', cap=(
        'DEFINE THE QUESTION AND ITS ALLOWED ANSWERS.',
        'BILLING / TECHNICAL / UNKNOWN: LOCAL EXAMPLE')),
    dict(name='ASK', t=T[2], status='STATE + CHOICE', cap=(
        'SEND CONTEXT AND TYPED QUESTIONS TO THE INTERFACE.',
        'SCHEMATIC REQUEST; NO INTERNAL ARCHITECTURE SHOWN')),
    dict(name='ANSWER', t=T[3], status='CHOICE + SCORES', cap=(
        'JEV RETURNS TYPED DATA, NOT GENERATED PROSE.',
        'ILLUSTRATIVE SCORES; THE MODEL WAS NOT RUN')),
    dict(name='GATE', t=T[4], status='0.82 >= 0.70', cap=(
        'THE APPLICATION ACCEPTS THIS SCORE AND ROUTES THE TICKET.',
        'LOCAL POLICY ON P(MAX); NOT TYPESAFE CONFIDENCE')),
    dict(name='CHECK', t=T[5], status='0.36 / 0.34 / 0.30', cap=(
        'NOW LOAD A SECOND, MORE EVEN SCORE FIXTURE.',
        'ILLUSTRATIVE SCORES; THE MODEL WAS NOT RUN')),
    dict(name='HOLD', t=T[6], status='0.36 < 0.70', cap=(
        'THE SAME RULE WITHHOLDS AUTOMATIC ROUTING.',
        'EXAMPLE FALLBACK: SEND THE TICKET TO A PERSON')),
    dict(name='RECAP', t=T[7], status='TYPED DATA -> ACTION', cap=(
        'MODEL OUTPUTS FEED POLICY; YOUR CODE CHOOSES THE ACTION.',
        'SOURCE: TYPESAFE DOCS + LOCAL ARTIFICIAL FIXTURES')),
]

MODULES = {
    'state': (13, 44, 91, 81, 'STATE'),
    'question': (13, 149, 91, 69, 'QUESTION'),
    'jev': (126, 80, 87, 96, 'JEV'),
    'answer': (237, 44, 111, 174, 'TYPED ANSWER'),
    'gate': (374, 57, 91, 58, 'APP POLICY'),
    'action': (374, 145, 91, 73, 'ACTION'),
}
PATHS = [
    ('state', 'jev', [(104, 89), (116, 89), (116, 113), (126, 113)]),
    ('question', 'jev', [(104, 180), (116, 180), (116, 144), (126, 144)]),
    ('jev', 'answer', [(213, 127), (237, 127)]),
    ('answer', 'gate', [(348, 86), (374, 86)]),
    ('gate', 'action', [(419, 115), (419, 145)]),
]

class Explainer(Scene):
    W, H, SCALE = 480, 270, 4
    FPS, DURATION = 60, DURATION
    PAL, LANG, TITLE = P, 'en', TITLE
    BLOOM = dict(strength=.5, sigma=2.6, threshold=20)

    def setup(self):
        self.stages = chrome.Stages(STAGES)
        self.d = dict(np.load(HERE / 'data' / 'data.npz'))
        self.paths = [(a, b, Path(points)) for a,b,points in PATHS]

    def box_state(self, key, stage):
        active = [ {'state'}, {'question'}, {'state','question','jev'}, {'answer'},
                   {'gate','action'}, {'answer'}, {'gate','action'}, {'jev','answer','gate','action'} ][stage]
        begun = dict(state=0, question=1, jev=2, answer=3, gate=4, action=4)
        return 'active' if key in active else ('done' if stage >= begun[key] else 'idle')

    def draw(self, cv, t):
        chrome.background(cv)
        stage, _ = self.stages.at(t)
        accent = P['orange']
        cv.text(13, 25, 'PUBLIC INTERFACE', P['label'])
        cv.text(465, 25, 'OFFLINE EXPLAINER', P['label'], align='r')
        for key, (x,y,w,h,label) in MODULES.items():
            module(cv,x,y,w,h,self.box_state(key,stage),P,label=label,font=self.lf)
        # Whole map persists; particles traverse the same connections.
        triggers = [8., 8.3, 12., 16., 17.5]
        if stage == 5: triggers = [8.,8.3,21.,23.,99.]
        if stage == 6: triggers = [8.,8.3,21.,26.,27.5]
        if stage == 7: triggers = [31.,31.25,31.7,32.3,32.9]
        for j,(a,b,p) in enumerate(self.paths):
            wire(cv,p,t,triggers[j],.75,P,hold=1.1,n=5,gap=.10)
        # Context words type into the fixed state panel.
        for i,s in enumerate(['DOUBLE', 'CHARGED', 'REFUND?']):
            cv.text(22, 66+i*16, s, P['text'] if t>.45+i*.42 else P['idle'],
                    n=max(0,int((t-.45-i*.42)*17)))
        # Allowed answers are the explicit contract.
        cv.text(22,165,'CHOICE',P['orange'] if stage>=1 else P['idle'])
        for i,s in enumerate(['BILLING','TECHNICAL','UNKNOWN']):
            cv.text(22,178+i*11,s,P['text2'] if t>4.6+i*.45 else P['idle'])
        cv.text(169,110,'TYPED',P['text2'] if stage>=2 else P['idle'],align='c')
        cv.text(169,122,'DECISION',P['text2'] if stage>=2 else P['idle'],align='c')
        cv.text(169,151,'MODEL',P['label'],align='c')
        cv.text(169,161,'NOT RUN',P['orange'],align='c')
        # Fixture A then B, with bar lengths calculated from source JSON.
        which = 0 if t<21 else 1
        vals = self.d['scores'][which]
        data_start = 12.5 if which==0 else 21.3
        for i,label in enumerate(['BILLING','TECHNICAL','UNKNOWN']):
            y = 103+i*30
            cv.text(245,y,label,P['text2'] if stage>=3 else P['idle'])
            cv.fill(245,y+11,74,7,P['blue_dk'])
            if stage>=3:
                f = seg(t, data_start+i*.3, data_start+1.15+i*.3)
                cv.fill(245,y+11,int(round(74*float(vals[i])*f)),7,accent if i==0 else P['fwd'])
                cv.text(340,y+11,f'{vals[i]:.2f}',P['text2'],align='r')
        cv.text(245,66,'CHOICE:',P['label'])
        cv.text(245,79,'BILLING' if stage>=3 else '...',P['text'] if stage>=3 else P['idle'])
        cv.text(245,198,'PROBABILITIES',P['label'])
        cv.text(382,80,'P(MAX)',P['text2'])
        cv.text(382,96,'>= 0.70',accent)
        # Two outcomes always visible; highlight only the active branch.
        accepted = stage==4
        rejected = stage>=6
        for yy,label,on,col in [(169,'BILLING',accepted,P['fwd']), (196,'HUMAN',rejected,P['orange'])]:
            rbox(cv,382,yy-4,75,17,col if on else P['idle'])
            cv.text(419,yy,label,col if on else P['label'],align='c')
        if stage==4:
            cv.text(419,126,'ACCEPT',P['fwd'],align='c')
        elif stage>=6:
            cv.text(419,126,'ABSTAIN',P['orange'],align='c')
        # Footer caveat remains visible regardless of stage.
        cv.text(13,228,'ILLUSTRATIVE SCORES',P['orange'])
        cv.text(465,228,'THE MODEL WAS NOT RUN',P['label'],align='r')
        # A small scan marker reinforces the active module without moving the map.
        scan_x = 130 + int((math.sin(t*2.0)+1)*35)
        cv.fill(scan_x,185,3,2,P['orange'] if stage==2 else P['dim2'])
        self.stages.draw(cv,t,TITLE,P)

    def sfx(self):
        return []
