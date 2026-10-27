from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
FONTS = '/tmp/claude-0/-home-user-mes-videos-amine-ia/1b0ba2e1-ad98-558e-ab91-a164b7df65af/scratchpad/fonts/'
W, H = 1080, 1920

def make(path, text="Ton ventre, ce n'est pas du gras…"):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    # dark header gradient hides the wash left where the old banner was
    g = np.zeros((420, W, 4), np.uint8); g[..., :3] = (18, 8, 14)
    g[..., 3] = (np.clip(1 - np.linspace(0, 1, 420) ** 1.6, 0, 1) * 215)[:, None].astype(np.uint8)
    img.alpha_composite(Image.fromarray(g, 'RGBA'))
    font = ImageFont.truetype(FONTS + 'Montserrat-ExtraBold.ttf', 50)
    tw = font.getlength(text); ph = 104; pw = int(tw + 84)
    x0, y0 = (W - pw) // 2, 104
    # soft shadow
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
    d.rounded_rectangle((x0, y0 + 10, x0 + pw, y0 + ph + 10), ph // 2, fill=(0, 0, 0, 140))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    # pill with horizontal coral → raspberry gradient
    grad = np.zeros((ph, pw, 4), np.uint8); t = np.linspace(0, 1, pw)[None, :]
    for i, (a, b) in enumerate(zip((255, 77, 109), (201, 24, 74))): grad[..., i] = (a + (b - a) * t).astype(np.uint8)
    grad[..., 3] = 255
    mask = Image.new('L', (pw, ph), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw - 1, ph - 1), ph // 2, fill=255)
    pill = Image.fromarray(grad, 'RGBA'); pill.putalpha(mask)
    # thin light rim on top for a glossy feel
    rim = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
    ImageDraw.Draw(rim).rounded_rectangle((1, 1, pw - 2, ph - 2), ph // 2, outline=(255, 255, 255, 90), width=3)
    pill.alpha_composite(rim)
    img.alpha_composite(pill, (x0, y0))
    d = ImageDraw.Draw(img)
    d.text((W // 2, y0 + ph // 2 + 3), text, font=font, fill=(0, 0, 0, 70), anchor='mm')
    d.text((W // 2, y0 + ph // 2), text, font=font, fill='white', anchor='mm')
    img.save(path)

if __name__ == '__main__':
    import sys; make(sys.argv[1])
