"""Local 12-pixel Chinese bitmap font; no changes to the installed skill.

SimSun is read from Windows only at render time. Videos contain rasterized pixels
and need no fonts at playback. ASCII math uses the original LCD glyphs.
"""
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pixelkit.fonts import FONT57
from pixelkit import chrome as base

class ChineseFont:
    cap = height = 12
    spacing = 1
    def __init__(self):
        self.font = ImageFont.truetype('C:/Windows/Fonts/simsun.ttc', 12)
    @lru_cache(maxsize=2048)
    def glyph(self, ch):
        if ch in FONT57.glyphs:
            g = FONT57.glyph(ch)
            return np.pad(g, ((2, max(0, 10-g.shape[0])), (0, 0)))
        img = Image.new('1', (12, 12))
        ImageDraw.Draw(img).text((0, 0), ch, font=self.font, fill=1, anchor='lt')
        return np.array(img, dtype=bool)
    def width(self, s):
        return sum(self.glyph(c).shape[1]+self.spacing for c in s)-self.spacing if s else 0
    def missing(self, s):
        return sorted(set(c for c in s if not c.isspace() and not self.glyph(c).any()))

ZH = ChineseFont()
base.LAYOUT['zh'] = dict(font=ZH, head_y=4, rule_y=236, y1=239, y2=254, cps=35)
_original_font = base._font
base._font = lambda spec: ZH if spec is ZH else _original_font(spec)

def text(cv, x, y, s, c, **kwargs):
    return cv.text(x, y, s, c, font=ZH, **kwargs)

class Stages(base.Stages):
    """Chinese caption band at y=239/254; measured using the rendered font."""
    def __init__(self, stages):
        super().__init__(stages, lang='zh')
    def check(self, title=None):
        bad=[]
        x_sq=467-(len(self.stages)-1)*7-5+1
        for s in self.stages:
            for value in (s['name'],s['status'],*s['cap']):
                if ZH.missing(value): bad.append(('missing Chinese glyph', value))
            for value in s['cap']:
                if ZH.width(value)>460: bad.append(('caption too wide', value))
            w=ZH.width(s['status'])
            if 240-w//2 < 10+ZH.width(title or '')+12 or 240+w//2 > x_sq-7-ZH.width(s['name'])-12:
                bad.append(('header collision', s['status']))
        return bad
