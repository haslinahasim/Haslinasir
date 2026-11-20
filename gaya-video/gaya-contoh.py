import json, os, subprocess, numpy as np, onnxruntime as ort
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
SRC, OUT = "in.mov", "reel-gaya-contoh.mp4"
DUR = 9.9            # video length
END = 3.5            # end card length
BLACK_ = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
XB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
BD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
YEL, GRN, CREAM, WHITE = (255, 214, 10), (40, 200, 110), (243, 214, 150), (255, 255, 255)
F = lambda p, s: ImageFont.truetype(p, s)
ease = lambda x: 1 - (1 - min(max(x, 0), 1)) ** 3

# ---------- text helpers ----------
def text_img(txt, font, fill, stroke=0, sfill=(0, 0, 0), shadow=False):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = d.textbbox((0, 0), txt, font=font, stroke_width=stroke)
    pad = 20
    im = Image.new("RGBA", (r - l + pad * 2, b - t + pad * 2), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - l, pad - t + 3), txt, font=font, fill=(0, 0, 0, 170))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(5))); dd = ImageDraw.Draw(im)
    dd.text((pad - l, pad - t), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill)
    return im

def paste_c(base, im, cx, cy, alpha=1.0, scale=1.0):
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if alpha < 1:
        a = im.getchannel("A").point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    _paste_clip(base, im, int(cx - im.width / 2), int(cy - im.height / 2))

def _paste_clip(base, im, x, y):
    l, t = max(0, -x), max(0, -y)
    r, b = min(im.width, base.width - x), min(im.height, base.height - y)
    if r > l and b > t:
        base.alpha_composite(im.crop((l, t, r, b)), (x + l, y + t))

# ---------- 1. hook: big yellow text BEHIND her + small white kicker in front ----------
HOOK = (0.0, 3.2)
big = text_img("TANPA LAPAR!", F(BLACK_, 150), YEL)
kicker = text_img("NAK TURUN BERAT BADAN?", F(XB, 50), WHITE, shadow=True)

# ---------- 2. word walls behind her ----------
def wall(word, color, rows=9, size=150):
    f = F(BLACK_, size)
    fill = text_img(word + "  ", f, color)
    outl = text_img(word + "  ", f, (0, 0, 0, 0), stroke=3, sfill=WHITE)
    out = []
    for r in range(rows):
        tile = fill if r % 2 == 0 else outl
        strip = Image.new("RGBA", (tile.width * 4, tile.height), (0, 0, 0, 0))
        for k in range(4):
            strip.alpha_composite(fill if (k + r) % 2 == 0 else outl, (k * tile.width, 0))
        out.append(strip)
    return out
WALLS = [(3.22, 4.30, wall("BERAT BADAN", YEL)), (7.98, 9.90, wall("TANPA BERLAPAR", GRN))]

def draw_wall(base, strips, t, a):
    tint = Image.new("RGBA", (W, H), (15, 15, 15, int(185 * a)))
    base.alpha_composite(tint)
    rh = 205
    for r, s in enumerate(strips):
        step = s.width / 4
        off = (t * 220 * (1 if r % 2 else -1) + r * 137) % step
        x = int(-step + off)
        y = int(r * rh - 40)
        im = s
        if a < 1:
            im = s.copy(); im.putalpha(s.getchannel("A").point(lambda v: int(v * a)))
        _paste_clip(base, im, x, y)

# ---------- 3. comment bubble at top (her own question, like the viewer question in the sample) ----------
def bubble(label, q):
    fl, fq = F(BD, 22), F(XB, 36)
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    w = int(max(d.textlength(q, font=fq), d.textlength(label, font=fl))) + 130
    im = Image.new("RGBA", (w + 20, 140), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([10, 14, w + 10, 124], 26, fill=(0, 0, 0, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    dd.rounded_rectangle([10, 10, w + 10, 120], 26, fill=(255, 255, 255, 250))
    dd.ellipse([30, 38, 82, 90], fill=(245, 130, 20))
    dd.text((56, 64), "?", font=F(BLACK_, 34), fill=WHITE, anchor="mm")
    dd.text((100, 30), label, font=fl, fill=(120, 120, 120))
    dd.text((100, 58), q, font=fq, fill=(20, 20, 20))
    return im
BUB = (4.30, 7.95, bubble("Penonton bertanya", "Macam mana nak turun berat badan?"))

# ---------- 4. word-by-word captions, one accent word in gold serif italic ----------
words = json.load(open("in_words.json"))
GROUPS = [(0, 2), (2, 6), (6, 8), (8, 11), (11, 14), (14, 17), (17, 19), (19, 21), (21, 24), (24, 26), (26, 28)]
ACCENT = {"penat", "jalan", "berat", "badan", "tips", "berlapar"}
SHOW = {"ok": "Ok,", "badan": "badan", "berlapar": "berlapar?"}
fw, fa = F(XB, 58), F(SERIF, 66)
def cap_img(ws):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    parts = []
    for w in ws:
        t = w["w"]; t = "Ok," if t.lower() == "ok" else t
        if w is words[13] or w is words[27]: t += "?"
        if w is words[1] or w is words[7]: t += ","
        acc = w["w"].lower() in ACCENT
        parts.append((t, fa if acc else fw, CREAM if acc else WHITE))
    sp = 16; tw = sum(d.textlength(t, font=f) for t, f, _ in parts) + sp * (len(parts) - 1)
    im = Image.new("RGBA", (int(tw) + 60, 130), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh); dd = ImageDraw.Draw(im)
    x = 30
    for t, f, c in parts:
        ds.text((x, 67), t, font=f, fill=(0, 0, 0, 255), anchor="ls", stroke_width=4, stroke_fill=(0, 0, 0, 255))
        dd.text((x, 65), t, font=f, fill=c, anchor="ls", stroke_width=2, stroke_fill=(0, 0, 0, 140))
        x += d.textlength(t, font=f) + sp
    im = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)), im)
    return im
CAPS = []  # (start, end, image) each partial build
for gi, (a, b) in enumerate(GROUPS):
    g_end = words[GROUPS[gi + 1][0]]["s"] if gi + 1 < len(GROUPS) else DUR
    for k in range(a, b):
        CAPS.append((words[k]["s"], words[k + 1]["s"] if k + 1 < b else g_end, cap_img(words[a:k + 1])))

# ---------- 5. end card ----------
def end_card():
    im = Image.new("RGBA", (700, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 699, 559], 40, fill=(20, 20, 20, 215))
    d.text((350, 90), "Jom join", font=F(BLACK_, 62), fill=WHITE, anchor="mm")
    d.text((350, 180), "Program Turun", font=F(SERIF, 70), fill=CREAM, anchor="mm")
    d.text((350, 260), "Berat Badan", font=F(SERIF, 70), fill=CREAM, anchor="mm")
    d.text((350, 330), "tanpa berlapar", font=F(BD, 32), fill=(200, 200, 200), anchor="mm")
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([150, 395, 550, 495], 50, fill=(230, 30, 40, 200))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)))
    d.rounded_rectangle([160, 400, 540, 490], 45, fill=(225, 30, 40))
    d.text((215, 445), "DM", font=F(BLACK_, 30), fill=(255, 220, 220), anchor="mm")
    d.text((385, 445), "“CANTIK”", font=F(BLACK_, 54), fill=WHITE, anchor="mm")
    return im
CARD = end_card()

# ---------- person cutout ----------
sess = ort.InferenceSession(os.path.expanduser("~/easy-edit/models/modnet.onnx"))
prev = None
def matte(rgb):
    global prev
    x = np.asarray(Image.fromarray(rgb).resize((288, 512), Image.BILINEAR), np.float32) / 127.5 - 1
    m = sess.run(None, {"input": x.transpose(2, 0, 1)[None]})[0][0, 0]
    prev = m if prev is None else 0.6 * m + 0.4 * prev
    mi = Image.fromarray((np.clip(prev, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    return mi.filter(ImageFilter.GaussianBlur(2))

# ---------- render ----------
dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", SRC, "-t", str(DUR), "-vf",
    f"fps={FPS},scale={W}:{H},eq=contrast=1.04:saturation=1.08:brightness=0.01",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
    "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", SRC, "-map", "0:v", "-map", "1:a",
    "-af", f"atrim=0:{DUR},apad", "-t", str(DUR + END),
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)

n, last = 0, None
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    t = n / FPS; rgb = np.frombuffer(raw, np.uint8).reshape(H, W, 3)
    frame = Image.fromarray(rgb).convert("RGBA")
    m = matte(rgb)
    bg = frame.copy()
    # behind-her layers
    for a, b, strips in WALLS:
        if a <= t < b:
            al = min(ease((t - a) / 0.2), ease((b - t) / 0.15))
            draw_wall(bg, strips, t - a, al)
    if HOOK[0] <= t < HOOK[1]:
        p = ease((t - HOOK[0]) / 0.3); al = min(p, ease((HOOK[1] - t) / 0.2))
        paste_c(bg, big, W / 2 + 30 - 20 * (t - HOOK[0]), 470, al, 0.85 + 0.15 * p)
    person = frame.copy(); person.putalpha(m)
    bg.alpha_composite(person)
    # front layers
    if HOOK[0] <= t < HOOK[1]:
        al = min(ease((t - 0.15) / 0.3), ease((HOOK[1] - t) / 0.2))
        paste_c(bg, kicker, W / 2, 300 + 20 * (1 - ease((t - 0.15) / 0.3)), al)
    a, b, im = BUB
    if a <= t < b:
        p = ease((t - a) / 0.3); al = min(p, ease((b - t) / 0.2))
        paste_c(bg, im, W / 2, 190 + 30 * (1 - p), al, 0.92 + 0.08 * p)
    for a, b, im in CAPS:
        if a <= t < b:
            pop = ease((t - a) / 0.12)
            paste_c(bg, im, W / 2, 1440, 1.0, 0.97 + 0.03 * pop); break
    last = bg.convert("RGB")
    enc.stdin.write(last.tobytes()); n += 1

# end card: blurred, darker last frame + card popping in
blur = last.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.55)).convert("RGBA")
for k in range(int(END * FPS)):
    t = k / FPS; fr = blur.copy()
    p = ease(t / 0.4)
    paste_c(fr, CARD, W / 2, 900 + 60 * (1 - p), p, 0.9 + 0.1 * p)
    enc.stdin.write(fr.convert("RGB").tobytes())
enc.stdin.close(); enc.wait()
print("frames", n, "->", OUT)
