"""Assemble the Aplevia storytelling ad (voice-over only). Run from the v2/ directory."""
import json, subprocess, sys, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

TOOLS = __file__.rsplit('/', 1)[0]
sys.path.insert(0, TOOLS)
from script_v2 import CUTS, SEGMENTS, OUTRO
import card

FONTS = TOOLS.rsplit('/', 1)[0] + '/fonts/'
W, H, FPS = 1080, 1920, 30
SW, SH, SFPS = 720, 1264, 29.993
TEMPO = 1.05                     # slight speed-up of the voice-over
PAUSE = 0.30                     # breath between lines
MIN_DUR = {26: 2.6, 38: 4.2}     # product cards stay on screen long enough to read
OUT = sys.argv[1] if len(sys.argv) > 1 else 'aplevia_histoire_v1.mp4'

def font(name, size): return ImageFont.truetype(FONTS + f'Montserrat-{name}.ttf', size)
def smooth(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)

# ---------------------------------------------------------------- voice-over timing
vo = [json.load(open(f'vo/{i:02d}.json')) for i in range(len(SEGMENTS) + len(OUTRO))]
speech = [d['al']['character_end_times_seconds'][-1] / TEMPO for d in vo]

clips = []        # (out_start, out_dur, shot, src_start, speed, pingpong)
audio = []        # (vo index, out_time)
t = 0.0
for i, (shots, _) in enumerate(SEGMENTS):
    dur = speech[i] + PAUSE
    audio.append((i, t + 0.05))
    lens = {k: CUTS[k + 1] - CUTS[k] - 0.1 for k in shots}       # drop a few frames at each cut
    fixed = {k: MIN_DUR[k] for k in shots if k in MIN_DUR}
    rest = dur - sum(fixed.values())
    free = [k for k in shots if k not in fixed]
    alloc = dict(fixed)
    for k in free: alloc[k] = rest * lens[k] / sum(lens[x] for x in free)
    if not free: alloc = {k: dur * alloc[k] / sum(alloc.values()) for k in shots}
    for k in shots:
        d, L = alloc[k], lens[k]
        a = CUTS[k] + 0.05
        if d <= L: clips.append((t, d, k, a + (L - d) / 2, 1.0, False))
        elif L / d >= 0.6: clips.append((t, d, k, a, L / d, False))
        else: clips.append((t, d, k, a, 0.8, True))
        t += d
MAIN_END = t
n = len(SEGMENTS)
end_dur = 0.4 + speech[n] + 0.25 + speech[n + 1] + 1.4
audio += [(n, t + 0.4), (n + 1, t + 0.4 + speech[n] + 0.25)]
TOTAL = t + end_dur
print(f'main {MAIN_END:.1f}s, total {TOTAL:.1f}s, {len(clips)} clips')

# ---------------------------------------------------------------- words
GLOBAL_DISPLAY = {'aplévia': 'APLEVIA', 'benkoung': 'BENGKUNG', 'trente': '30'}
SEG_DISPLAY = {n: {'deux': '2', 'achetées': 'ACHETÉES =', 'une': '1'}}
words = []
for i, out_t in audio:
    al = vo[i]['al']; cur, ws, we = '', None, None
    for c, s, e in zip(al['characters'] + [' '], al['character_start_times_seconds'] + [0], al['character_end_times_seconds'] + [0]):
        if c.isspace():
            if cur.strip(): words.append([out_t + ws / TEMPO, out_t + we / TEMPO, cur, i])
            cur, ws = '', None
        else:
            if ws is None: ws = s
            cur += c; we = e
def display(w, seg):
    core = w.strip('«»"').rstrip(',.:;')
    key = core.lower().rstrip('…')
    rep = SEG_DISPLAY.get(seg, {}).get(key) or GLOBAL_DISPLAY.get(key)
    return (rep or core).upper()
for w in words: w[2] = display(w[2], w[3])
words = [w for w in words if w[2]]
def cue(seg, word): return next(w[0] for w in words if w[3] == seg and w[2].startswith(word))

# ---------------------------------------------------------------- subtitles
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
         'Style: Sub,Montserrat ExtraBold,70,&H00FFFFFF,&H00FFFFFF,&H00141822,&H8C000000,0,0,0,0,100,100,1,0,1,5,3,5,40,40,0,1',
         '', '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
for gi, g in enumerate(groups):
    g_end = g[-1][1] + 0.3
    if gi + 1 < len(groups): g_end = min(g_end, groups[gi + 1][0][0])
    shot = next((c[2] for c in reversed(clips) if c[0] <= g[0][0]), None)
    y = 1330 if g[0][0] >= MAIN_END else (125 if shot == 38 else 1480)
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
    filt.append(f'[{k}:a]aresample=48000,atempo={TEMPO},adelay={ms}|{ms}[a{k}]')
filt.append(''.join(f'[a{k}]' for k in range(len(audio))) + f'amix=inputs={len(audio)}:normalize=0,apad,atrim=0:{TOTAL:.3f},'
            'highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,loudnorm=I=-14:TP=-1.5:LRA=9[out]')
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(filt), '-map', '[out]', '-ac', '2', 'voice.wav'], check=True)

# ---------------------------------------------------------------- source frames (random access, cached per shot)
cap_cache = {}
def load_shot(k):
    if k not in cap_cache:
        a, b = CUTS[k], CUTS[k + 1]
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{a:.3f}', '-t', f'{b - a:.3f}', '-i', 'src.mp4', '-vf', 'hqdn3d=1.5:1.5:3:3',
                              '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True, check=True).stdout
        fr = np.frombuffer(raw, np.uint8).reshape(-1, SH, SW, 3)
        cap_cache.clear(); cap_cache[k] = fr
    return cap_cache[k]

GLOW = card.wordmark(SW, SH, 1082, 'glow')
INK = card.wordmark(SW, SH, 962, 'ink', ['Trente jours pour essayer.', 'Satisfaite ou remboursée.'], size=90)
def brand_fix(k, f):
    if k == 26: return card.apply(card.bg_fill(f, 1022, 1192), GLOW)
    if k == 38: return card.apply(card.bg_fill(f, 900, 1212), INK)
    return f

def enhance(f):
    tw = int(round(SH * 9 / 16)); x = (SW - tw) // 2
    f = cv2.resize(f[:, x:x + tw], (W, H), interpolation=cv2.INTER_LANCZOS4)
    blur = cv2.GaussianBlur(f, (0, 0), 1.4)
    return cv2.addWeighted(f, 1.3, blur, -0.3, 0)

def shot_frame(k, ts):
    fr = load_shot(k); i = int(round((ts - CUTS[k]) * SFPS)); i = min(max(i, 0), len(fr) - 1)
    return enhance(brand_fix(k, fr[i]))

# ---------------------------------------------------------------- end card
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

INKC = (74, 32, 26)
def badge(text, icon):
    f = font('ExtraBold', 38); tw = f.getlength(text); h = 88; w = int(tw + 140)
    im = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((20, 26, 20 + w, 26 + h), h // 2, fill=(60, 30, 20, 70))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im); d.rounded_rectangle((20, 20, 20 + w, 20 + h), h // 2, fill=(255, 251, 245, 255), outline=(225, 200, 175, 255), width=2)
    cx, cy, r = 20 + 52, 20 + h // 2, 30
    if icon == 'gift':
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(150, 52, 40)); d.text((cx, cy + 1), '+1', font=font('Black', 30), fill='white', anchor='mm')
    elif icon == 'swiss':
        d.rounded_rectangle((cx - r, cy - r, cx + r, cy + r), 9, fill=(218, 41, 28)); a, b = 6, 19
        d.rectangle((cx - a, cy - b, cx + a, cy + b), fill='white'); d.rectangle((cx - b, cy - a, cx + b, cy + a), fill='white')
    else:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(60, 150, 90))
        d.line([(cx - 13, cy + 1), (cx - 3, cy + 11), (cx + 15, cy - 10)], fill='white', width=7, joint='curve')
    d.text((20 + 96, cy + 1), text, font=f, fill=INKC, anchor='lm')
    return im
BADGES = [(badge('2 achetées = 1 offerte', 'gift'), cue(n, '2')),
          (badge('Livraison gratuite en Suisse', 'swiss'), cue(n, 'LIVRAISON')),
          (badge('30 jours satisfaite ou remboursée', 'check'), MAIN_END + 0.2)]
def cta():
    text = 'EN SAVOIR PLUS  ›'; f = font('Black', 50); tw = f.getlength(text); h = 116; w = int(tw + 130)
    im = Image.new('RGBA', (w + 60, h + 60), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((30, 40, 30 + w, 40 + h), h // 2, fill=(60, 20, 10, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    grad = np.zeros((h, w, 4), np.uint8); tt = np.linspace(0, 1, w)[None, :]
    for i, (a, b) in enumerate(zip((176, 72, 52), (120, 36, 30))): grad[..., i] = (a + (b - a) * tt).astype(np.uint8)
    grad[..., 3] = 255
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=255)
    p = Image.fromarray(grad, 'RGBA'); p.putalpha(m); im.alpha_composite(p, (30, 30))
    ImageDraw.Draw(im).text((30 + w / 2, 30 + h / 2), text, font=f, fill='white', anchor='mm')
    return im
CTA = cta()
CTA_AT = cue(n + 1, 'CLIQUE')

def end_frame(lt):
    # shot 26 (rebranded) plays back and forth, scaled into the upper part over a soft backdrop of itself
    L = CUTS[27] - CUTS[26] - 0.1; u = (lt * 0.7) % (2 * L); u = u if u < L else 2 * L - u
    f = shot_frame(26, CUTS[26] + 0.05 + u)
    s = 0.64; fw, fh = int(W * s), int(H * s); x0, y0 = (W - fw) // 2, 20
    small = cv2.resize(f, (fw, fh), interpolation=cv2.INTER_AREA)
    inner = small[6:-6, 6:-6]
    ext = cv2.copyMakeBorder(inner, y0 + 6, H - y0 - fh + 6, x0 + 6, W - x0 - fw + 6, cv2.BORDER_REPLICATE)
    back = cv2.GaussianBlur(ext, (0, 0), 40)
    m = np.zeros((H, W), np.float32); m[y0 + 6:y0 + fh - 6, x0 + 6:x0 + fw - 6] = 1
    m = cv2.GaussianBlur(m, (0, 0), 10)[..., None]
    out = (ext * m + back * (1 - m)).astype(np.uint8)
    tt = MAIN_END + lt
    for bi, (im, at) in enumerate(BADGES):
        if tt < at: continue
        k = smooth((tt - at) / 0.25); ov, w, h = scaled(im, 0.85 + 0.15 * k, k)
        out = comp(out, ov, ((W - w) // 2, 1450 + bi * 108 - h // 2))
    if tt >= CTA_AT - 0.2:
        k = smooth((tt - CTA_AT + 0.2) / 0.3); pulse = 1 + 0.03 * math.sin(max(tt - CTA_AT, 0) * 2 * math.pi * 1.3)
        ov, w, h = scaled(CTA, (0.85 + 0.15 * k) * pulse, k)
        out = comp(out, ov, ((W - w) // 2, 1800 - h // 2))
    return out

# ---------------------------------------------------------------- render
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-i', 'voice.wav', '-vf', f'ass=subs.ass:fontsdir={FONTS}', '-map', '0:v', '-map', '1:a',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                        '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
ci = 0; last_main = None
for fi in range(int(round(TOTAL * FPS))):
    tt = fi / FPS
    if tt < MAIN_END:
        while ci + 1 < len(clips) and tt >= clips[ci + 1][0]: ci += 1
        o, d, k, s0, sp, pp = clips[ci]; lt = tt - o
        if pp:
            L = CUTS[k + 1] - CUTS[k] - 0.1; u = (lt * sp) % (2 * L); u = u if u < L else 2 * L - u
            frame = shot_frame(k, s0 + u)
        else:
            frame = shot_frame(k, s0 + lt * sp)
        last_main = frame
    else:
        lt = tt - MAIN_END
        frame = end_frame(lt)
        if lt < 0.4: frame = (last_main * (1 - smooth(lt / 0.4)) + frame * smooth(lt / 0.4)).astype(np.uint8)
    assert frame.dtype == np.uint8 and frame.shape == (H, W, 3)
    enc.stdin.write(np.ascontiguousarray(frame).tobytes())
    if fi % 300 == 0: print(f'{tt:6.1f}s / {TOTAL:.1f}s', flush=True)
enc.stdin.close(); enc.wait()
print('done', OUT)
