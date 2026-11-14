"""Gaya contoh: text behind the speaker, word-by-word captions, word walls, dark info cards,
question bubble, product card and a blurred end card.  Usage: python3 gaya.py config.json"""
import json, os, sys, subprocess, numpy as np, onnxruntime as ort
from PIL import Image, ImageDraw, ImageFont, ImageFilter

C = json.load(open(sys.argv[1]))
W, H, FPS = 1080, 1920, 30
SRC, OUT, DUR, END = C["src"], C["out"], C["dur"], C.get("end_len", 3.5)
FD = "/usr/share/fonts/opentype/inter/"
BLK, XB, BD = FD + "InterDisplay-Black.otf", FD + "InterDisplay-ExtraBold.otf", FD + "InterDisplay-Bold.otf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
YEL, GRN, CREAM, WHITE, RED = (255, 214, 10), (40, 200, 110), (243, 214, 150), (255, 255, 255), (235, 70, 70)
COL = {"yellow": YEL, "green": GRN}
F = lambda p, s: ImageFont.truetype(p, s)
ease = lambda x: 1 - (1 - min(max(x, 0), 1)) ** 3

def paste(base, im, x, y):
    l, t = max(0, -x), max(0, -y); r, b = min(im.width, base.width - x), min(im.height, base.height - y)
    if r > l and b > t: base.alpha_composite(im.crop((l, t, r, b)), (x + l, y + t))
def paste_c(base, im, cx, cy, alpha=1.0, scale=1.0):
    if scale != 1.0: im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if alpha < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    paste(base, im, int(cx - im.width / 2), int(cy - im.height / 2))
def fade(t, a, b, fi=0.3, fo=0.2): return min(ease((t - a) / fi), ease((b - t) / fo))

def text_img(txt, font, fill, stroke=0, sfill=(0, 0, 0), shadow=False):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1))); l, t, r, b = d.textbbox((0, 0), txt, font=font, stroke_width=stroke)
    pad = 20; im = Image.new("RGBA", (r - l + pad * 2, b - t + pad * 2), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - l, pad - t + 3), txt, font=font, fill=(0, 0, 0, 200), stroke_width=3, stroke_fill=(0, 0, 0, 200))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(5)))
    ImageDraw.Draw(im).text((pad - l, pad - t), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill)
    return im

# ---------- product photo (white background is fine on a white tile) ----------
PROD = None
if C.get("product"):
    p = Image.open(C["product"]["img"]).convert("RGB"); a = np.asarray(p).min(2) < 235
    ys, xs = np.where(a); bx = (xs.min() - 20, ys.min() - 20, xs.max() + 20, ys.max() + 20)
    PROD = p.crop(bx).convert("RGBA")
def prod_tile(h):
    im = PROD.resize((int(PROD.width * h / PROD.height), h), Image.LANCZOS)
    tile = Image.new("RGBA", (im.width + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(tile)
    d.rounded_rectangle([0, 0, tile.width - 1, tile.height - 1], 26, fill=WHITE); tile.alpha_composite(im, (20, 20))
    return tile

# ---------- layers ----------
def wall(word, color, rows=10, size=150):
    f = F(BLK, size); fill = text_img(word + "  ", f, color); outl = text_img(word + "  ", f, (0, 0, 0, 0), stroke=3, sfill=WHITE)
    out = []
    for r in range(rows):
        s = Image.new("RGBA", (fill.width * 4, fill.height), (0, 0, 0, 0))
        for k in range(4): s.alpha_composite(fill if (k + r) % 2 == 0 else outl, (k * fill.width, 0))
        out.append(s)
    return out
def draw_wall(base, strips, t, a):
    base.alpha_composite(Image.new("RGBA", (W, H), (15, 15, 15, int(185 * a))))
    for r, s in enumerate(strips):
        step = s.width / 4; x = int(-step + (t * 220 * (1 if r % 2 else -1) + r * 137) % step)
        im = s if a >= 1 else s.copy()
        if a < 1: im.putalpha(s.getchannel("A").point(lambda v: int(v * a)))
        paste(base, im, x, int(r * 205 - 40))

def dark_card(title, items, shown):   # items: (icon, text, highlight)
    w, rh = 760, 66; h = 80 + rh * len(items)
    im = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([15, 18, w + 15, h + 15], 30, fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8))); d = ImageDraw.Draw(im)
    d.rounded_rectangle([15, 15, w + 15, h + 15], 30, fill=(22, 22, 22, 225))
    d.text((50, 42), title, font=F(XB, 26), fill=(200, 200, 200))
    for i, (ic, txt, hi) in enumerate(items[:shown]):
        y = 112 + i * rh
        if ic in ("x", "v"):
            d.ellipse([50, y - 19, 88, y + 19], fill=(225, 60, 60) if ic == "x" else (50, 190, 100))
            if ic == "v": d.line([(60, y + 1), (67, y + 9), (79, y - 8)], fill=WHITE, width=5)
            else: d.line([(61, y - 8), (77, y + 8)], fill=WHITE, width=5); d.line([(61, y + 8), (77, y - 8)], fill=WHITE, width=5)
        else:
            d.ellipse([50, y - 19, 88, y + 19], fill=YEL); d.text((69, y), ic, font=F(BLK, 26), fill=(20, 20, 20), anchor="mm")
        d.text((108, y), txt, font=F(XB, 38), fill=YEL if hi else WHITE, anchor="lm")
    return im

def bubble(label, q):
    fl, fq = F(BD, 22), F(XB, 36); d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    w = int(max(d.textlength(q, font=fq), d.textlength(label, font=fl))) + 130
    im = Image.new("RGBA", (w + 20, 140), (0, 0, 0, 0)); sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([10, 14, w + 10, 124], 26, fill=(0, 0, 0, 90)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    dd = ImageDraw.Draw(im); dd.rounded_rectangle([10, 10, w + 10, 120], 26, fill=(255, 255, 255, 250))
    dd.ellipse([30, 38, 82, 90], fill=(245, 130, 20)); dd.text((56, 64), "?", font=F(BLK, 34), fill=WHITE, anchor="mm")
    dd.text((100, 30), label, font=fl, fill=(120, 120, 120)); dd.text((100, 58), q, font=fq, fill=(20, 20, 20))
    return im

def product_card(brand, name, sub):
    tile = prod_tile(230); w = 760; h = tile.height + 30
    im = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0)); sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([15, 18, w + 15, h + 15], 30, fill=(0, 0, 0, 120)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(im); d.rounded_rectangle([15, 15, w + 15, h + 15], 30, fill=(22, 22, 22, 225))
    im.alpha_composite(tile, (30, 30)); x = 30 + tile.width + 34; cy = 15 + h // 2
    d.text((x, cy - 70), brand, font=F(XB, 26), fill=(150, 210, 90), anchor="lm")
    d.text((x, cy - 10), name, font=F(SERIF, 72), fill=CREAM, anchor="lm")
    d.text((x, cy + 58), sub, font=F(XB, 34), fill=WHITE, anchor="lm")
    return im

def end_card(e):
    has = PROD is not None; w, h = 720, 640 + (300 if has else 0)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 40, fill=(20, 20, 20, 215)); y = 40
    if has:
        t = prod_tile(250); im.alpha_composite(t, ((w - t.width) // 2, y)); y += t.height + 30; d = ImageDraw.Draw(im)
    d.text((w / 2, y + 40), e["line1"], font=F(BLK, 62), fill=WHITE, anchor="mm")
    for i, l in enumerate(e["serif"]): d.text((w / 2, y + 130 + i * 80), l, font=F(SERIF, 72), fill=CREAM, anchor="mm")
    y += 130 + 80 * len(e["serif"]) - 20
    if e.get("small"): d.text((w / 2, y), e["small"], font=F(BD, 32), fill=(200, 200, 200), anchor="mm"); y += 40
    y += 30; glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([160, y - 5, w - 160, y + 95], 50, fill=(230, 30, 40, 200)); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im); d.rounded_rectangle([170, y, w - 170, y + 90], 45, fill=(225, 30, 40))
    d.text((230, y + 45), "DM", font=F(BLK, 30), fill=(255, 220, 220), anchor="mm")
    d.text((w / 2 + 40, y + 45), "“%s”" % e["dm"], font=F(BLK, 54), fill=WHITE, anchor="mm")
    return im.crop((0, 0, w, min(h, y + 130)))

# ---------- captions: word timed, display text per word, accent words gold serif ----------
words = json.load(open(C["words"])); fix = {int(k): v for k, v in C.get("fix", {}).items()}
acc = set(C.get("accent", [])); fw, fa = F(XB, 58), F(SERIF, 66)
def disp(i): return fix.get(i, words[i]["w"].lstrip("-"))
def cap_img(idx):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1))); parts = [(disp(i), fa if i in acc else fw, CREAM if i in acc else WHITE) for i in idx if disp(i)]
    sp = 16; tw = sum(d.textlength(t, font=f) for t, f, _ in parts) + sp * (len(parts) - 1)
    im = Image.new("RGBA", (int(tw) + 60, 130), (0, 0, 0, 0)); sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ds, dd = ImageDraw.Draw(sh), ImageDraw.Draw(im); x = 30
    for t, f, c in parts:
        ds.text((x, 67), t, font=f, fill=(0, 0, 0, 255), anchor="ls", stroke_width=4, stroke_fill=(0, 0, 0, 255))
        dd.text((x, 65), t, font=f, fill=c, anchor="ls", stroke_width=2, stroke_fill=(0, 0, 0, 140)); x += d.textlength(t, font=f) + sp
    return Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)), im)
CAPS, G = [], C["groups"]
for gi, (a, b) in enumerate(G):
    nxt = words[G[gi + 1][0]]["s"] if gi + 1 < len(G) else DUR
    g_end = min(nxt, words[b - 1]["e"] + 0.8)
    for k in range(a, b):
        if not disp(k): continue
        nk = next((j for j in range(k + 1, b) if disp(j)), None)
        CAPS.append((words[k]["s"], words[nk]["s"] if nk else g_end, cap_img(range(a, k + 1))))

# ---------- build timed layers ----------
hk = C["hook"]; BIG = text_img(hk["big"], F(BLK, hk.get("size", 150)), YEL); KICK = text_img(hk["kicker"], F(XB, 50), WHITE, shadow=True)
WALLS = [(w["a"], w["b"], wall(w["word"], COL[w["color"]])) for w in C.get("walls", [])]
CARDS = []
for c in C.get("cards", []):
    if c["type"] == "list":
        for i, at in enumerate(c["times"]):
            CARDS.append((at, c["times"][i + 1] if i + 1 < len(c["times"]) else c["b"], c["a"], c["b"], dark_card(c["title"], c["items"], i + 1)))
    elif c["type"] == "bubble": CARDS.append((c["a"], c["b"], c["a"], c["b"], bubble(c["label"], c["q"])))
    elif c["type"] == "product": CARDS.append((c["a"], c["b"], c["a"], c["b"], product_card(c["brand"], c["name"], c["sub"])))
CARD_END = end_card(C["end"])

# ---------- person cutout ----------
sess = ort.InferenceSession(os.path.expanduser("~/easy-edit/models/modnet.onnx")); prev = None
STUDIO_VF = "curves=master='0/0 0.25/0.30 0.5/0.57 0.75/0.81 1/1',colorbalance=rs=-0.03:bs=0.02:rm=-0.03:bm=0.03,eq=contrast=1.05:saturation=1.04"
def matte(rgb):
    global prev
    x = np.asarray(Image.fromarray(rgb).resize((288, 512), Image.BILINEAR), np.float32) / 127.5 - 1
    m = sess.run(None, {"input": x.transpose(2, 0, 1)[None]})[0][0, 0]
    prev = m if prev is None else 0.6 * m + 0.4 * prev
    return Image.fromarray((np.clip(prev, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2))

# ---------- render ----------
dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", SRC, "-t", str(DUR), "-vf",
    f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}," + (STUDIO_VF if C.get("studio") else "eq=contrast=1.04:saturation=1.08:brightness=0.01"),
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-i", SRC, "-map", "0:v", "-map", "1:a", "-af", f"atrim=0:{DUR},apad", "-t", str(DUR + END),
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
n, last, bigy = 0, None, hk.get("y")
# ---------- studio light: brighter subject + soft key light on face, darker background, gentle vignette ----------
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.18 * np.clip(((XX - W / 2) / (W * 0.75)) ** 2 + ((YY - H * 0.45) / (H * 0.7)) ** 2, 0, 1))[..., None]
kc = None
def studio(rgb, m):
    global kc
    mk = np.asarray(m) > 128; rows = np.where(mk.sum(1) > 40)[0]
    if len(rows):
        top = rows.min(); cols = np.where(mk[top:top + 250].any(0))[0]
        c = np.array([cols.mean() if len(cols) else W / 2, top + 230.0])
        kc = c if kc is None else 0.85 * kc + 0.15 * c
    cx, cy = kc if kc is not None else (W / 2, 700)
    key = np.exp(-(((XX - cx) / 420) ** 2 + ((YY - cy) / 520) ** 2))[..., None]
    a = np.asarray(m.filter(ImageFilter.GaussianBlur(6)), np.float32)[..., None] / 255
    f = rgb.astype(np.float32)
    out = (f * (1.06 + 0.10 * key)) * a + f * 0.90 * (1 - a)
    return np.clip(out * VIG, 0, 255).astype(np.uint8)
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    t = n / FPS; rgb = np.frombuffer(raw, np.uint8).reshape(H, W, 3); m = matte(rgb)
    if C.get("studio"): rgb = studio(rgb, m)
    frame = Image.fromarray(rgb).convert("RGBA")
    if bigy is None:   # put the big word across the top of her head
        rows = np.where((np.asarray(m) > 128).sum(1) > 40)[0]; bigy = int(rows.min() + C["hook"].get("overlap", 60) - BIG.height / 2 + 75) if len(rows) else 470
    bg = frame.copy()
    for a, b, strips in WALLS:
        if a <= t < b: draw_wall(bg, strips, t - a, fade(t, a, b, 0.2, 0.15))
    if 0 <= t < hk["b"]:
        p = ease(t / 0.3); paste_c(bg, BIG, W / 2 + 30 - 20 * t, bigy, fade(t, 0, hk["b"]), 0.85 + 0.15 * p)
    person = frame.copy(); person.putalpha(m); bg.alpha_composite(person)
    if 0 <= t < hk["b"]: paste_c(bg, KICK, W / 2, bigy - 150 + 20 * (1 - ease((t - 0.15) / 0.3)), fade(t, 0.15, hk["b"]))
    for s, e, a, b, im in CARDS:
        if s <= t < e:
            p = ease((t - a) / 0.3); paste_c(bg, im, W / 2, 80 + im.height / 2 + 30 * (1 - p), fade(t, a, b), 0.92 + 0.08 * p)
    for a, b, im in CAPS:
        if a <= t < b: paste_c(bg, im, W / 2, C.get("cap_y", 1440), 1.0, 0.97 + 0.03 * ease((t - a) / 0.12)); break
    last = bg.convert("RGB"); enc.stdin.write(last.tobytes()); n += 1
blur = last.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.55)).convert("RGBA")
for k in range(int(END * FPS)):
    t = k / FPS; fr = blur.copy(); p = ease(t / 0.4)
    paste_c(fr, CARD_END, W / 2, 920 + 60 * (1 - p), p, 0.9 + 0.1 * p); enc.stdin.write(fr.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); print("frames", n, "->", OUT)
