import cv2, numpy as np
BAND = (895, 1005)        # burned-in subtitle rows
TOP = 196                 # bottom edge of old red banner area
K5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))

def remove_subs(f):
    y0, y1 = BAND
    roi = f[y0:y1]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    white = ((hsv[..., 2] > 200) & (hsv[..., 1] < 60)).astype(np.uint8)
    # keep only blobs that are surrounded by dark outline (the caption style)
    dark = (hsv[..., 2] < 60).astype(np.uint8)
    near_dark = cv2.dilate(dark, K5)
    text = white & near_dark
    if text.sum() < 30: return f
    # merge glyphs into a word box then grow over outline + drop shadow
    m = cv2.dilate(text, cv2.getStructuringElement(cv2.MORPH_RECT, (25, 9)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    keep = np.zeros_like(m)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if h >= 18 and w >= 20: keep[lab == i] = 1
    if keep.sum() == 0: return f
    keep = cv2.dilate(keep, cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15)))
    full = np.zeros(f.shape[:2], np.uint8); full[y0:y1] = keep * 255
    return cv2.inpaint(f, full, 7, cv2.INPAINT_TELEA)

def remove_banner(f):
    # replace the old banner area with a soft colour wash stretched from the picture just below it
    edge, feather = 190, 30
    row = f[edge:edge + 12].mean(0, keepdims=True)
    row = cv2.GaussianBlur(row.astype(np.float32), (0, 0), sigmaX=22, sigmaY=0.1)
    fill = np.repeat(row, edge + feather, 0)
    out = f.copy()
    out[:edge] = fill[:edge].astype(np.uint8)
    a = np.linspace(1, 0, feather)[:, None, None]
    out[edge:edge + feather] = (fill[edge:] * a + f[edge:edge + feather] * (1 - a)).astype(np.uint8)
    return out
