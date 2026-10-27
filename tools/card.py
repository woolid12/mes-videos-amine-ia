"""Erase the Bengka wordmark on the product cards and draw the Aplevia one instead."""
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FONTS = __file__.rsplit('/', 2)[0] + '/fonts/'

def bg_fill(f, y0, y1):
    """Rebuild rows y0..y1 by blending, per column, the plain background just above and below."""
    top = cv2.GaussianBlur(f[y0 - 10:y0].astype(np.float32).mean(0, keepdims=True), (0, 0), sigmaX=25, sigmaY=0.1)
    bot = cv2.GaussianBlur(f[y1:y1 + 10].astype(np.float32).mean(0, keepdims=True), (0, 0), sigmaX=25, sigmaY=0.1)
    t = np.linspace(0, 1, y1 - y0)[:, None, None]
    out = f.copy()
    patch = top * (1 - t) + bot * t
    patch += np.random.default_rng(0).normal(0, 1.2, patch.shape)   # faint grain like the render
    out[y0:y1] = np.clip(patch, 0, 255).astype(np.uint8)
    return out

def font(name, size, wght=None):
    f = ImageFont.truetype(FONTS + name, size)
    if wght:
        try: f.set_variation_by_axes([wght])
        except Exception: pass
    return f

def wordmark(w, h, cy, style, sub=None, size=96):
    """RGBA layer (w x h) with APLEVIA wordmark; style 'glow' (light, golden glow) or 'ink' (dark brown)."""
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f = font('Cinzel.ttf', size, 500)
    text = 'APLEVIA'; sp = int(size * 0.16)
    widths = [f.getlength(ch) for ch in text]; tw = sum(widths) + sp * (len(text) - 1)
    x = (w - tw) / 2
    col = (255, 246, 228, 255) if style == 'glow' else (92, 38, 30, 255)
    if style == 'glow':
        g = Image.new('RGBA', (w, h), (0, 0, 0, 0)); gd = ImageDraw.Draw(g); xx = x
        for ch, cw in zip(text, widths): gd.text((xx, cy), ch, font=f, fill=(255, 190, 90, 255), anchor='lm'); xx += cw + sp
        lay.alpha_composite(g.filter(ImageFilter.GaussianBlur(10)))
        lay.alpha_composite(g.filter(ImageFilter.GaussianBlur(4)))
    xx = x
    for ch, cw in zip(text, widths): d.text((xx, cy), ch, font=f, fill=col, anchor='lm'); xx += cw + sp
    # ornament: thin rule with a small diamond, like the original card
    oy = cy + int(size * 0.72); lc = (150, 100, 70, 200) if style == 'ink' else (200, 160, 120, 200)
    d.line([(w / 2 - 110, oy), (w / 2 - 12, oy)], fill=lc, width=2); d.line([(w / 2 + 12, oy), (w / 2 + 110, oy)], fill=lc, width=2)
    d.polygon([(w / 2, oy - 7), (w / 2 + 7, oy), (w / 2, oy + 7), (w / 2 - 7, oy)], fill=lc)
    if sub:
        fs = font('Cormorant.ttf', 40, 500)
        for i, line in enumerate(sub):
            d.text((w / 2, oy + 80 + i * 46), line, font=fs, fill=(92, 38, 30, 255), anchor='mm')
    return lay

def apply(f, lay, alpha=1.0):
    a = np.asarray(lay).astype(np.float32); al = a[..., 3:] / 255 * alpha
    return np.clip(f * (1 - al) + a[..., [2, 1, 0]] * al, 0, 255).astype(np.uint8)
