"""Assemble the Aplevia "Sofia" storytelling ad (voice-over only). Run from the v3/ directory."""
import json, subprocess, sys, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

TOOLS = __file__.rsplit('/', 1)[0]
sys.path.insert(0, TOOLS)
from script_v3 import CUTS, SEGMENTS, MIRROR, LABEL_SHOTS
from clean_v3 import remove_text, remove_label

FONTS = TOOLS.rsplit('/', 1)[0] + '/fonts/'
W, H, FPS = 1080, 1920, 30
SW, SH, SFPS = 720, 1280, 30
PAUSE = 0.30
CARD_DUR_PAD = 0.6
OUT = sys.argv[1] if len(sys.argv) > 1 else 'aplevia_sofia_v1.mp4'

def font(name, size): return ImageFont.truetype(FONTS + f'Montserrat-{name}.ttf', size)
def smooth(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)

# ---------------------------------------------------------------- timing from the voice-over
vo = [json.load(open(f'vo/{i:02d}.json')) for i in range(len(SEGMENTS))]
speech = [d['al']['character_end_times_seconds'][-1] for d in vo]
clips, audio, t = [], [], 0.0      # clip: (out_start, dur, shot, src_start, speed)
for i, (shots, _) in enumerate(SEGMENTS):
    dur = speech[i] + PAUSE + (CARD_DUR_PAD if shots == ['card'] else 0)
    audio.append((i, t + 0.05))
    if shots == ['card']:
        clips.append((t, dur, 'card', 0, 1)); t += dur; continue
    lens = {k: CUTS[k + 1] - CUTS[k] - 0.1 for k in shots}
    for k in shots:
        d, L = dur * lens[k] / sum(lens.values()), lens[k]
        a = CUTS[k] + 0.05
        clips.append((t, d, k, a + (L - d) / 2, 1.0) if d <= L else (t, d, k, a, L / d))
        t += d
TOTAL = t + 0.8
print(f'total {TOTAL:.1f}s, {len(clips)} clips')

# ---------------------------------------------------------------- words
CARD_SEG = next(i for i, s in enumerate(SEGMENTS) if s[0] == ['card'])
DEG_SEG = next(i for i, s in enumerate(SEGMENTS) if '360' in s[1])
GLOBAL_DISPLAY = {'aplévia': 'APLEVIA', 'benkoung': 'BENGKUNG', 'mille': '1000', 'cinq': '5', 'trente': '30', 'vingt-neuf': '29'}
SEG_DISPLAY = {CARD_SEG: {'deux': '2', 'achetées': 'ACHETÉES =', 'une': '1'},
               DEG_SEG: {'trois': '360', 'cent': '', 'soixante': ''}}
words = []
for i, out_t in audio:
    al = vo[i]['al']; cur, ws, we = '', None, None
    for c, s, e in zip(al['characters'] + [' '], al['character_start_times_seconds'] + [0], al['character_end_times_seconds'] + [0]):
        if c.isspace():
            if cur.strip(): words.append([out_t + ws, out_t + we, cur, i])
            cur, ws = '', None
        else:
            if ws is None: ws = s
            cur += c; we = e
def display(w, seg):
    core = w.strip('«»"').rstrip(',.:;')
    key = core.lower().rstrip('…')
    rep = SEG_DISPLAY.get(seg, {}).get(key, GLOBAL_DISPLAY.get(key))
    if rep == '': return ''
    out = (rep or core).upper()
    return out
for w in words: w[2] = display(w[2], w[3])
words = [w for w in words if w[2]]
def cue(seg, word): return next(w[0] for w in words if w[3] == seg and w[2].startswith(word))

# ---------------------------------------------------------------- subtitles (same band as the erased captions)
def ass_time(x):
    x = max(x, 0); return f'{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}'
groups, g = [], []
for w in words:
    if g and (len(g) == 3 or len(' '.join(x[2] for x in g + [w])) > 20 or w[3] != g[-1][3] or w[0] - g[-1][1] > 0.35):
        groups.append(g); g = []
    g.append(w)
    if w[2][-1] in '?!…:': groups.append(g); g = []
if g: groups.append(g)
GOLD = '&H006BC3F5&'
lines = ['[Script Info]', 'ScriptType: v4.00+', f'PlayResX: {W}', f'PlayResY: {H}', 'WrapStyle: 2', '', '[V4+ Styles]',
         'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
         'Style: Sub,Montserrat ExtraBold,74,&H00FFFFFF,&H00FFFFFF,&H00141822,&H8C000000,0,0,0,0,100,100,1,0,1,5,3,5,40,40,0,1',
         '', '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
for gi, g in enumerate(groups):
    g_end = g[-1][1] + 0.3
    if gi + 1 < len(groups): g_end = min(g_end, groups[gi + 1][0][0])
    y = 1720 if g[0][3] == CARD_SEG else 1385
    for wi, w in enumerate(g):
        s = w[0]; e = g[wi + 1][0] if wi + 1 < len(g) else g_end
        txt = ' '.join((f'{{\\c{GOLD}}}{x[2]}{{\\c&H00FFFFFF&}}' if k == wi else x[2]) for k, x in enumerate(g))
        pop = '\\alpha&H60&\\t(0,120,\\alpha&H00&)' if wi == 0 else ''
        lines.append(f'Dialogue: 0,{ass_time(s)},{ass_time(e)},Sub,,0,0,0,,{{\\pos(540,{y}){pop}}}{txt}')
open('subs.ass', 'w').write('\n'.join(lines) + '\n')

# ---------------------------------------------------------------- audio
inputs, filt = [], []
for k, (i, at) in enumerate(audio):
    inputs += ['-i', f'vo/{i:02d}.mp3']; ms = int(at * 1000)
    filt.append(f'[{k}:a]aresample=48000,adelay={ms}|{ms}[a{k}]')
filt.append(''.join(f'[a{k}]' for k in range(len(audio))) + f'amix=inputs={len(audio)}:normalize=0,apad,atrim=0:{TOTAL:.3f},'
            'highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,loudnorm=I=-14:TP=-1.5:LRA=9[out]')
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(filt), '-map', '[out]', '-ac', '2', 'voice.wav'], check=True)

# ---------------------------------------------------------------- footage
cache = {}
def load_shot(k):
    if k not in cache:
        a, b = CUTS[k], CUTS[k + 1]
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{a:.3f}', '-t', f'{b - a:.3f}', '-i', 'src.mp4', '-vf', 'hqdn3d=1.5:1.5:3:3',
                              '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True, check=True).stdout
        cache.clear(); cache[k] = np.frombuffer(raw, np.uint8).reshape(-1, SH, SW, 3)
    return cache[k]
def enhance(f):
    f = cv2.resize(f, (W, H), interpolation=cv2.INTER_LANCZOS4)
    return cv2.addWeighted(f, 1.3, cv2.GaussianBlur(f, (0, 0), 1.4), -0.3, 0)
def shot_frame(k, ts):
    fr = load_shot(k); i = min(max(int(round((ts - CUTS[k]) * SFPS)), 0), len(fr) - 1)
    f = remove_text(fr[i].copy(), labels=False)
    if k in LABEL_SHOTS: f = remove_label(f)
    if k in MIRROR: f = np.ascontiguousarray(f[:, ::-1])
    return enhance(f)

# ---------------------------------------------------------------- overlays
def rgba(img): a = np.asarray(img.convert('RGBA')).astype(np.float32); return a[..., [2, 1, 0]], a[..., 3:] / 255.0
def comp(frame, ov, xy=(0, 0)):
    col, a = ov; x, y = xy; h, w = a.shape[:2]
    if x < 0: col, a, w, x = col[:, -x:], a[:, -x:], w + x, 0
    w = min(w, W - x); col, a = col[:, :w], a[:, :w]
    region = frame[y:y + h, x:x + w].astype(np.float32)
    frame[y:y + h, x:x + w] = (region * (1 - a) + col * a).astype(np.uint8)
    return frame
def scaled(im, s, alpha=1.0):
    if abs(s - 1) > 1e-3: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    col, a = rgba(im); return (col, a * alpha), im.width, im.height

NAVY, CORAL, PINK = (26, 34, 84), (226, 72, 62), (246, 223, 220)
def text_img(text, f, fill, pad=10):
    w = int(f.getlength(text)) + 2 * pad; im = Image.new('RGBA', (w, f.size + 2 * pad + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((w / 2, im.height / 2), text, font=f, fill=fill, anchor='mm'); return im
def pill(text, f, bg, fg, icon=None):
    tw = f.getlength(text); h = int(f.size * 1.9); w = int(tw + h * 1.0 + (h if icon else 0))
    im = Image.new('RGBA', (w + 30, h + 30), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((15, 21, 15 + w, 21 + h), h // 2, fill=(80, 30, 30, 60))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(im); d.rounded_rectangle((15, 15, 15 + w, 15 + h), h // 2, fill=bg)
    tx = 15 + w / 2
    if icon == 'swiss':
        cx, cy, r = 15 + h * 0.62, 15 + h / 2, h * 0.3
        d.rounded_rectangle((cx - r, cy - r, cx + r, cy + r), 8, fill=(218, 41, 28)); a, b = r * 0.22, r * 0.68
        d.rectangle((cx - a, cy - b, cx + a, cy + b), fill='white'); d.rectangle((cx - b, cy - a, cx + b, cy + a), fill='white')
        tx += h / 2
    elif icon == 'check':
        cx, cy, r = 15 + h * 0.62, 15 + h / 2, h * 0.3
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill='white')
        d.line([(cx - r * .45, cy), (cx - r * .1, cy + r * .38), (cx + r * .5, cy - r * .35)], fill=(40, 150, 80), width=6, joint='curve')
        tx += h / 2
    d.text((tx, 15 + h / 2), text, font=f, fill=fg, anchor='mm'); return im
def stars(text):
    f = font('SemiBold', 40); tw = f.getlength(text); im = Image.new('RGBA', (int(tw + 360), 90), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(5):
        cx, cy, r = 34 + k * 62, 45, 26
        pts = [(cx + (r if j % 2 == 0 else r * .45) * math.sin(j * math.pi / 5), cy - (r if j % 2 == 0 else r * .45) * math.cos(j * math.pi / 5)) for j in range(10)]
        d.polygon(pts, fill=(245, 175, 30))
    d.text((340, 45), text, font=f, fill=NAVY, anchor='lm'); return im

# offer card base: pink background, wordmark, the product row from the original card, title
src_card = cv2.cvtColor(cv2.imread('offer.png'), cv2.COLOR_BGR2RGB)
row = Image.fromarray(src_card[285:472]).resize((W, int(187 * W / SW)), Image.LANCZOS)
base = Image.new('RGBA', (W, H), PINK + (255,))
base.alpha_composite(text_img('APLEVIA', font('Black', 120), NAVY), ((W - text_img('APLEVIA', font('Black', 120), NAVY).width) // 2, 150))
base.paste(row, (0, 360))
ti = text_img('OFFRE SPÉCIALE', font('ExtraBold', 64), NAVY); base.alpha_composite(ti, ((W - ti.width) // 2, 690))
st = stars('+1000 clientes satisfaites'); base.alpha_composite(st, ((W - st.width) // 2, 1300))
CARD_BASE = cv2.cvtColor(np.asarray(base.convert('RGB')), cv2.COLOR_RGB2BGR).astype(np.float32)
CARD_ITEMS = [(text_img('2 ACHETÉES = 1 OFFERTE', font('Black', 66), CORAL), cue(CARD_SEG, '2'), 830),
              (pill('Livraison gratuite en Suisse', font('ExtraBold', 44), (255, 255, 255, 255), NAVY, 'swiss'), cue(CARD_SEG, 'LIVRAISON'), 985),
              (pill('30 jours satisfaite ou remboursée', font('ExtraBold', 44), (46, 160, 90, 255), (255, 255, 255), 'check'), cue(CARD_SEG, '30'), 1135)]
def zoom(img, z):
    M = np.float32([[z, 0, W / 2 * (1 - z)], [0, z, H / 2 * (1 - z)]])
    return np.clip(cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT), 0, 255).astype(np.uint8)
def card_frame(tt, lt, dur):
    f = zoom(CARD_BASE, 1.0 + 0.035 * lt / dur)
    for im, at, y in CARD_ITEMS:
        if tt < at: continue
        k = smooth((tt - at) / 0.25); ov, w, h = scaled(im, 0.8 + 0.2 * k, k)
        f = comp(f, ov, ((W - w) // 2, y - h // 2))
    return f

CTA = pill('EN SAVOIR PLUS  ›', font('Black', 52), (226, 72, 62, 255), (255, 255, 255))
CTA_AT = cue(len(SEGMENTS) - 1, 'CLIQUE')

# ---------------------------------------------------------------- render
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-i', 'voice.wav', '-vf', f'ass=subs.ass:fontsdir={FONTS}', '-map', '0:v', '-map', '1:a',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                        '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
ci = 0
for fi in range(int(round(TOTAL * FPS))):
    tt = fi / FPS
    while ci + 1 < len(clips) and tt >= clips[ci + 1][0]: ci += 1
    o, d, k, s0, sp = clips[ci]; lt = min(tt - o, d - 1e-3)
    frame = card_frame(tt, lt, d) if k == 'card' else shot_frame(k, s0 + lt * sp)
    if tt >= CTA_AT - 0.1:
        kk = smooth((tt - CTA_AT + 0.1) / 0.3); pulse = 1 + 0.03 * math.sin(max(tt - CTA_AT, 0) * 2 * math.pi * 1.3)
        ov, w, h = scaled(CTA, (0.85 + 0.15 * kk) * pulse, kk)
        frame = comp(frame.copy(), ov, ((W - w) // 2, 1640 - h // 2))
    assert frame.dtype == np.uint8 and frame.shape == (H, W, 3)
    enc.stdin.write(np.ascontiguousarray(frame).tobytes())
    if fi % 600 == 0: print(f'{tt:6.1f}s / {TOTAL:.1f}s', flush=True)
enc.stdin.close(); enc.wait()
print('done', OUT)
