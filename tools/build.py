"""Assemble the Aplevia version of the ad. Run from the work/ directory."""
import json, subprocess, sys, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

TOOLS = __file__.rsplit('/', 1)[0]
sys.path.insert(0, TOOLS)
from script_fr import SEGMENTS, OUTRO
from clean import remove_subs, remove_banner
import banner as banner_mod

FONTS = TOOLS.rsplit('/', 1)[0] + '/fonts/'
W, H, FPS = 1080, 1920, 30
SW, SH, SFPS = 716, 1276, 30
MIRROR_END = 14.3                      # first six shots
BRAND = (47.9667, 50.8667)             # 3D product shot replaced by the Aplevia render
MAIN_END = 75.84                       # source time where the original reviews screenshots start
OFFER_SRC = (78.15, 83.37)             # product handling footage reused under the offer lines (reviews end ~78.0)
OFFER_SPEED = 0.72                     # slowed a little so it covers most of the offer lines
OUT = sys.argv[1] if len(sys.argv) > 1 else 'aplevia_v1.mp4'
PREVIEW = len(sys.argv) > 2            # any extra arg: render a few seconds only

def font(name, size): return ImageFont.truetype(FONTS + f'Montserrat-{name}.ttf', size)
def smooth(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)

# ---------------------------------------------------------------- voice-over timing
vo = []
for i in range(len(SEGMENTS) + len(OUTRO)):
    d = json.load(open(f'vo/{i:02d}.json'))
    vo.append(d)
speech = [d['al']['character_end_times_seconds'][-1] for d in vo]

timeline = []   # (out_start, out_dur, kind, payload)
audio = []      # (file, out_time)
t = 0.0
starts = [s[0] for s in SEGMENTS] + [MAIN_END]
for i in range(len(SEGMENTS)):
    span = starts[i + 1] - starts[i]
    dur = max(speech[i] + 0.10, span * 0.82)
    dur = min(dur, span * 1.45)
    timeline.append((t, dur, 'main', (starts[i], span)))
    audio.append((i, t))
    t += dur
MAIN_OUT_END = t
n = len(SEGMENTS)
# rating card
a_dur = 0.15 + speech[n] + 0.30
audio.append((n, t + 0.15)); timeline.append((t, a_dur, 'rating', None)); t += a_dur
# offer lines over product footage
off0 = t
b1 = t + 0.05; b2 = b1 + speech[n + 1] + 0.15
b_dur = (b2 - t) + speech[n + 2] + 0.30
audio += [(n + 1, b1), (n + 2, b2)]
timeline.append((t, b_dur, 'offer', None)); t += b_dur
# end card
c_dur = 0.2 + speech[n + 3] + 1.4
audio.append((n + 3, t + 0.2)); timeline.append((t, c_dur, 'end', None)); t += c_dur
TOTAL = t
print(f'main {MAIN_OUT_END:.2f}s, total {TOTAL:.2f}s')

# ---------------------------------------------------------------- words (subtitles + badge cues)
GLOBAL_DISPLAY = {'aplévia': 'APLEVIA', 'benkoung': 'BENGKUNG', 'mille': '1000', 'cinq': '5', 'trente': '30'}
SEG_DISPLAY = {n + 1: {'deux': '2', 'achetées': 'ACHETÉES =', 'une': '1'}}
words = []      # (start, end, display, seg)
for i, out_t in audio:
    al = vo[i]['al']; chars = al['characters']
    cur, ws, we = '', None, None
    for c, s, e in zip(chars + [' '], al['character_start_times_seconds'] + [0], al['character_end_times_seconds'] + [0]):
        if c.isspace():
            if cur.strip():
                words.append([out_t + ws, out_t + we, cur, i])
            cur, ws = '', None
        else:
            if ws is None: ws = s
            cur += c; we = e
def display(w, seg):
    core = w.strip('«»"').rstrip(',.:;…')
    key = core.lower()
    rep = SEG_DISPLAY.get(seg, {}).get(key) or GLOBAL_DISPLAY.get(key)
    out = (rep or core).upper()
    return out
for w in words: w[2] = display(w[2], w[3])
words = [w for w in words if w[2] and w[2] not in ('«', '»')]

def cue(seg, word):
    for w in words:
        if w[3] == seg and w[2].startswith(word): return w[0]
    raise KeyError(word)

# ---------------------------------------------------------------- subtitles (ASS)
def ass_time(x):
    x = max(x, 0); h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f'{h}:{m:02d}:{s:05.2f}'
groups, g = [], []
for w in words:
    if g and (len(g) == 3 or len(' '.join(x[2] for x in g + [w])) > 20 or w[3] != g[-1][3] or w[0] - g[-1][1] > 0.35):
        groups.append(g); g = []
    g.append(w)
    if w[2][-1] in '?!' : groups.append(g); g = []
if g: groups.append(g)
YEL = '&H004DE1FF&'
lines = ['[Script Info]', 'ScriptType: v4.00+', f'PlayResX: {W}', f'PlayResY: {H}', 'WrapStyle: 2', '',
         '[V4+ Styles]',
         'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
         'Style: Sub,Montserrat Black,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,7,4,5,40,40,0,1',
         '', '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
for gi, g in enumerate(groups):
    g_end = g[-1][1] + 0.25
    if gi + 1 < len(groups): g_end = min(g_end, groups[gi + 1][0][0])
    for wi, w in enumerate(g):
        s = w[0]; e = g[wi + 1][0] if wi + 1 < len(g) else g_end
        txt = ' '.join((f'{{\\c{YEL}}}{x[2]}{{\\c&H00FFFFFF&}}' if k == wi else x[2]) for k, x in enumerate(g))
        pop = '\\fscx88\\fscy88\\t(0,90,\\fscx100\\fscy100)' if wi == 0 else ''
        lines.append(f'Dialogue: 0,{ass_time(s)},{ass_time(e)},Sub,,0,0,0,,{{\\pos(540,1432){pop}}}{txt}')
open('subs.ass', 'w').write('\n'.join(lines) + '\n')

# ---------------------------------------------------------------- audio
inputs, filt = [], []
for k, (i, at) in enumerate(audio):
    inputs += ['-i', f'vo/{i:02d}.mp3']
    ms = int(at * 1000); filt.append(f'[{k}:a]aresample=48000,adelay={ms}|{ms}[a{k}]')
filt.append(''.join(f'[a{k}]' for k in range(len(audio))) + f'amix=inputs={len(audio)}:normalize=0,apad,atrim=0:{TOTAL:.3f},'
            'highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,loudnorm=I=-14:TP=-1.5:LRA=9[out]')
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(filt), '-map', '[out]', '-ac', '2', 'voice.wav'], check=True)

# ---------------------------------------------------------------- static overlays
banner_mod.make('banner.png')
def rgba(img): a = np.asarray(img.convert('RGBA')).astype(np.float32); return a[..., [2, 1, 0]], a[..., 3:] / 255.0
BAN = rgba(Image.open('banner.png'))

def comp(frame, ov, alpha=1.0, xy=(0, 0)):
    col, a = ov; x, y = xy; h, w = a.shape[:2]
    if x < 0: col, a, w, x = col[:, -x:], a[:, -x:], w + x, 0
    w = min(w, W - x); col, a = col[:, :w], a[:, :w]
    region = frame[y:y + h, x:x + w].astype(np.float32)
    aa = a * alpha
    frame[y:y + h, x:x + w] = (region * (1 - aa) + col * aa).astype(np.uint8)
    return frame

def fit916(img):
    h, w = img.shape[:2]; tw = int(round(h * 9 / 16))
    if tw < w: x = (w - tw) // 2; img = img[:, x:x + tw]
    return cv2.resize(img, (W, H), interpolation=cv2.INTER_LANCZOS4)
brand_on = fit916(cv2.imread('brand_a_0.png')).astype(np.float32)
brand_dim = fit916(cv2.imread('brand_dim.png')).astype(np.float32)

def zoom(img, z, cy=0.5):
    if abs(z - 1) < 1e-4: return np.clip(img, 0, 255).astype(np.uint8)
    M = np.float32([[z, 0, W / 2 * (1 - z)], [0, z, H * cy * (1 - z)]])
    return np.clip(cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT), 0, 255).astype(np.uint8)

rng = np.random.default_rng(7)
P = 160
px = rng.uniform(0.18, 0.82, P) * W; py = rng.uniform(0.30, 0.78, P) * H
pv = rng.uniform(40, 120, P); pr = rng.uniform(1.5, 4.5, P); pph = rng.uniform(0, 6.28, P)
def sparkles(u):
    layer = np.zeros((H, W), np.float32)
    env = smooth(u / 0.4) * (1 - smooth((u - 1.6) / 1.0))
    if env <= 0: return None
    for i in range(P):
        a = env * (0.55 + 0.45 * math.sin(pph[i] + u * 9))
        cv2.circle(layer, (int(px[i]), int(py[i] - pv[i] * u)), int(pr[i]), float(a), -1, cv2.LINE_AA)
    return cv2.GaussianBlur(layer, (0, 0), 2.2) * 1.6 + layer
GOLD = np.array([90, 200, 255], np.float32)
def brand_frame(u):
    a = smooth((u - 0.45) / 1.25)
    img = brand_dim * (1 - a) + brand_on * a
    sp = sparkles(u)
    if sp is not None: img = img + sp[..., None] * GOLD
    return zoom(np.clip(img, 0, 255), 1.0 + 0.07 * (u / (BRAND[1] - BRAND[0])), 0.45)

# rating card
def rating_card():
    cw, ch = 900, 470
    im = Image.new('RGBA', (cw + 80, ch + 80), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((40, 52, 40 + cw, 52 + ch), 48, fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(im); d.rounded_rectangle((40, 40, 40 + cw, 40 + ch), 48, fill=(255, 255, 255, 250))
    def star(cx, cy, r):
        pts = [(cx + (r if k % 2 == 0 else r * 0.45) * math.sin(k * math.pi / 5), cy - (r if k % 2 == 0 else r * 0.45) * math.cos(k * math.pi / 5)) for k in range(10)]
        d.polygon(pts, fill=(255, 190, 40))
    for k in range(5): star(40 + cw / 2 + (k - 2) * 112, 150, 46)
    d.text((40 + cw / 2, 270), 'Plus de 1000 clientes', font=font('Black', 66), fill=(30, 20, 30), anchor='mm')
    d.text((40 + cw / 2, 345), 'satisfaites', font=font('Black', 66), fill=(201, 24, 74), anchor='mm')
    d.text((40 + cw / 2, 425), "l'ont notée 5 étoiles", font=font('SemiBold', 42), fill=(90, 80, 90), anchor='mm')
    return im
CARD = rating_card()
rating_bg = cv2.GaussianBlur(brand_on, (0, 0), 22) * 0.55

def badge(text, icon):
    f = font('ExtraBold', 40); tw = f.getlength(text); h = 96; w = int(tw + 150)
    im = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((20, 28, 20 + w, 28 + h), h // 2, fill=(0, 0, 0, 110))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im); d.rounded_rectangle((20, 20, 20 + w, 20 + h), h // 2, fill=(255, 255, 255, 250))
    cx, cy, r = 20 + 58, 20 + h // 2, 34
    if icon == 'gift':
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(201, 24, 74))
        d.text((cx, cy + 1), '+1', font=font('Black', 34), fill='white', anchor='mm')
    elif icon == 'swiss':
        d.rounded_rectangle((cx - r, cy - r, cx + r, cy + r), 10, fill=(218, 41, 28))
        a, b = 7, 22
        d.rectangle((cx - a, cy - b, cx + a, cy + b), fill='white'); d.rectangle((cx - b, cy - a, cx + b, cy + a), fill='white')
    else:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(34, 170, 90))
        d.line([(cx - 15, cy + 1), (cx - 4, cy + 13), (cx + 17, cy - 12)], fill='white', width=8, joint='curve')
    d.text((20 + 108, cy + 1), text, font=f, fill=(30, 20, 30), anchor='lm')
    return im
BADGES = [(badge('2 achetées = 1 offerte', 'gift'), cue(n + 1, '2')),
          (badge('Livraison gratuite en Suisse', 'swiss'), cue(n + 1, 'LIVRAISON')),
          (badge('30 jours satisfaite ou remboursée', 'check'), cue(n + 2, 'GARANTIE'))]

def cta():
    text = 'EN SAVOIR PLUS  ›'; f = font('Black', 54); tw = f.getlength(text); h = 128; w = int(tw + 140)
    im = Image.new('RGBA', (w + 60, h + 60), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((30, 42, 30 + w, 42 + h), h // 2, fill=(0, 0, 0, 140))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    grad = np.zeros((h, w, 4), np.uint8); tt = np.linspace(0, 1, w)[None, :]
    for i, (a, b) in enumerate(zip((255, 77, 109), (201, 24, 74))): grad[..., i] = (a + (b - a) * tt).astype(np.uint8)
    grad[..., 3] = 255
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=255)
    p = Image.fromarray(grad, 'RGBA'); p.putalpha(m); im.alpha_composite(p, (30, 30))
    ImageDraw.Draw(im).text((30 + w / 2, 30 + h / 2), text, font=f, fill='white', anchor='mm')
    return im
CTA = cta()

def pil_scaled(im, s, alpha=1.0):
    if abs(s - 1) > 1e-3: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    col, a = rgba(im); return (col, a * alpha), im.width, im.height

# ---------------------------------------------------------------- footage
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', 'src.mp4', '-vf', 'hqdn3d=2.5:2:5:4', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'],
                       stdout=subprocess.PIPE)
cur_idx, cur_frame = -1, None
def src_frame(ts):
    global cur_idx, cur_frame
    idx = min(int(round(ts * SFPS)), 2510)
    while cur_idx < idx:
        buf = dec.stdout.read(SW * SH * 3)
        if len(buf) < SW * SH * 3: break
        cur_idx += 1; cur_frame = np.frombuffer(buf, np.uint8).reshape(SH, SW, 3)
    return cur_frame

LUT = np.clip((np.arange(256) - 128) * 1.05 + 128 + 2, 0, 255).astype(np.uint8)
def enhance(f):
    f = cv2.resize(f, (W, H), interpolation=cv2.INTER_LANCZOS4)
    blur = cv2.GaussianBlur(f, (0, 0), 1.6)
    f = cv2.addWeighted(f, 1.4, blur, -0.4, 0)
    f = cv2.LUT(f, LUT)
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV); hsv[..., 1] = cv2.multiply(hsv[..., 1], 1.07)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def footage(ts):
    f = remove_banner(remove_subs(src_frame(ts).copy()))
    if ts < MIRROR_END: f = f[:, ::-1]
    return enhance(np.ascontiguousarray(f))

# ---------------------------------------------------------------- render
total_frames = int(round(TOTAL * FPS)) if not PREVIEW else int(3 * FPS)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-i', 'voice.wav', '-vf', f"ass=subs.ass:fontsdir={FONTS}", '-map', '0:v', '-map', '1:a',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                        '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
seg_i = 0
for fi in range(total_frames):
    tt = fi / FPS
    while seg_i + 1 < len(timeline) and tt >= timeline[seg_i + 1][0]: seg_i += 1
    o, dur, kind, pl = timeline[seg_i]; lt = tt - o
    if kind == 'main':
        s0, span = pl; ts = s0 + lt / dur * span
        frame = brand_frame(ts - BRAND[0]) if BRAND[0] <= ts < BRAND[1] else footage(ts)
        frame = comp(frame.copy(), BAN)
    elif kind == 'rating':
        frame = zoom(rating_bg, 1.0 + 0.03 * lt / dur)
        k = smooth(lt / 0.3)
        ov, w, h = pil_scaled(CARD, 0.86 + 0.14 * k, k)
        frame = comp(frame.copy(), ov, 1.0, ((W - w) // 2, 860 - h // 2))
    elif kind == 'offer':
        l1 = (OFFER_SRC[1] - OFFER_SRC[0]) / OFFER_SPEED
        prod = zoom(brand_on, 1.0 + 0.02 * max(lt - l1 + 0.4, 0), 0.45).astype(np.float32) * 0.82
        if lt < l1:
            foot = footage(OFFER_SRC[0] + lt * OFFER_SPEED).astype(np.float32) * 0.82
            k = smooth((lt - (l1 - 0.4)) / 0.4)
            frame = (foot * (1 - k) + prod * k).astype(np.uint8)
        else:
            frame = prod.astype(np.uint8)
        for bi, (im, at) in enumerate(BADGES):
            if tt < at: continue
            k = smooth((tt - at) / 0.22)
            ov, w, h = pil_scaled(im, 0.8 + 0.2 * k, k)
            frame = comp(frame, ov, 1.0, ((W - w) // 2, 400 + bi * 135 - h // 2))
    else:
        l1 = (OFFER_SRC[1] - OFFER_SRC[0]) / OFFER_SPEED
        z0 = 0.02 * max(timeline[seg_i - 1][1] - l1 + 0.4, 0)
        frame = zoom(brand_on, 1.0 + z0 + 0.05 * lt / dur, 0.45)
        frame = (frame.astype(np.float32) * (0.82 + 0.18 * smooth(lt / 0.5))).astype(np.uint8)
        k = smooth((lt - 0.15) / 0.3); pulse = 1 + 0.035 * math.sin(max(lt - 0.45, 0) * 2 * math.pi * 1.4)
        ov, w, h = pil_scaled(CTA, (0.85 + 0.15 * k) * pulse, k)
        frame = comp(frame.copy(), ov, 1.0, ((W - w) // 2, 1680 - h // 2))
    assert frame.dtype == np.uint8 and frame.shape == (H, W, 3), (kind, frame.dtype, frame.shape)
    enc.stdin.write(np.ascontiguousarray(frame).tobytes())
    if fi % 300 == 0: print(f'{tt:6.1f}s / {TOTAL:.1f}s', flush=True)
enc.stdin.close(); enc.wait(); dec.kill()
print('done', OUT)
