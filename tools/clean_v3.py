import cv2, numpy as np
SUB = (860, 985)      # two-line burned-in captions
LABEL = (755, 850)    # "JOUR 1" / "SEMAINE n" labels

def text_mask(f, y0, y1, vmin=215, dark=130, near=4, grow=11):
    roi = f[y0:y1]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    white = ((hsv[..., 2] > vmin) & (hsv[..., 1] < 45)).astype(np.uint8)
    dk = (hsv[..., 2] < dark).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * near + 1, 2 * near + 1))
    glyph = white & cv2.dilate(dk, k)
    # keep only blobs that look like letters on a text line (small, many side by side)
    n, lab, st, _ = cv2.connectedComponentsWithStats(glyph)
    keep = np.zeros_like(glyph)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if 2 <= h <= 60 and w <= 60 and a >= 3: keep[lab == i] = 1
    line = cv2.dilate(keep, cv2.getStructuringElement(cv2.MORPH_RECT, (31, 5)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(line)
    m = np.zeros_like(keep)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if w >= 60 and keep[lab == i].sum() >= 40: m[lab == i] = 1
    m = cv2.dilate(m & cv2.dilate(keep, k), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (grow, grow)))
    full = np.zeros(f.shape[:2], np.uint8); full[y0:y1] = m * 255
    return full

def remove_text(f, labels=True):
    m = text_mask(f, *SUB)
    if labels: m |= text_mask(f, *LABEL, vmin=225, dark=90, near=6, grow=19)
    if m.any(): f = cv2.inpaint(f, m, 6, cv2.INPAINT_TELEA)
    return f

def remove_label(f, box=(150, 750, 570, 855)):
    """Static 'SEMAINE n' label: white heavy letters with a thick black outline inside a known box."""
    x0, y0, x1, y1 = box
    hsv = cv2.cvtColor(f[y0:y1, x0:x1], cv2.COLOR_BGR2HSV)
    m = (((hsv[..., 2] > 200) & (hsv[..., 1] < 60)) | (hsv[..., 2] < 55)).astype(np.uint8)
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    full = np.zeros(f.shape[:2], np.uint8); full[y0:y1, x0:x1] = m * 255
    return cv2.inpaint(f, full, 9, cv2.INPAINT_TELEA)
