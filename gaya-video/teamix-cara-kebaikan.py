"""Recipe reel from silent b-roll clips: hook, numbered steps, benefits card, end card."""
import subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
CLIPS = ["c1.mov", "c2.mov", "c3.mov", "c4.mov"]
OUT, END, STILL = "reel-teamix-cara-kebaikan.mp4", 4.5, 7.0
FD = "/usr/share/fonts/opentype/inter/"
BLK, XB, BD = FD + "InterDisplay-Black.otf", FD + "InterDisplay-ExtraBold.otf", FD + "InterDisplay-Bold.otf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
YEL, CREAM, WHITE = (255, 214, 10), (243, 214, 150), (255, 255, 255)
F = lambda p, s: ImageFont.truetype(p, s)
ease = lambda x: 1 - (1 - min(max(x, 0), 1)) ** 3
def fade(t, a, b, fi=0.3, fo=0.25): return min(ease((t - a) / fi), ease((b - t) / fo))
def paste_c(base, im, cx, cy, alpha=1.0, scale=1.0):
    if scale != 1.0: im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if alpha < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    l, t = max(0, -x), max(0, -y); r, b = min(im.width, W - x), min(im.height, H - y)
    if r > l and b > t: base.alpha_composite(im.crop((l, t, r, b)), (x + l, y + t))

def text_img(txt, font, fill, stroke=0, shadow=True):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1))); l, t, r, b = d.textbbox((0, 0), txt, font=font, stroke_width=stroke)
    pad = 24; im = Image.new("RGBA", (r - l + pad * 2, b - t + pad * 2), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - l, pad - t + 4), txt, font=font, fill=(0, 0, 0, 200), stroke_width=stroke + 3, stroke_fill=(0, 0, 0, 200))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(7)))
    ImageDraw.Draw(im).text((pad - l, pad - t), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))
    return im

def shadow_box(w, h, r=30, fill=(22, 22, 22, 225)):
    im = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0)); sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([15, 18, w + 15, h + 15], r, fill=(0, 0, 0, 120)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    ImageDraw.Draw(im).rounded_rectangle([15, 15, w + 15, h + 15], r, fill=fill); return im

def step(n, txt, hi=False):
    f = F(XB, 54); tw = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(txt, font=f)
    im = shadow_box(int(tw) + 170, 110, 55); d = ImageDraw.Draw(im)
    d.ellipse([35, 30, 115, 110], fill=YEL); d.text((75, 70), n, font=F(BLK, 46), fill=(20, 20, 20), anchor="mm")
    d.text((140, 70), txt, font=f, fill=YEL if hi else WHITE, anchor="lm"); return im

def list_card(title, items, shown):
    w, rh = 860, 76; h = 90 + rh * shown; im = shadow_box(w, h); d = ImageDraw.Draw(im)
    d.text((52, 45), title, font=F(XB, 30), fill=(200, 200, 200))
    for i, (txt, hi) in enumerate(items[:shown]):
        y = 125 + i * rh
        d.ellipse([50, y - 21, 92, y + 21], fill=(50, 190, 100)); d.line([(61, y + 1), (69, y + 10), (82, y - 9)], fill=WHITE, width=6)
        d.text((112, y), txt, font=F(XB, 44), fill=YEL if hi else WHITE, anchor="lm")
    return im

def end_card(prod):
    w = 740; im = Image.new("RGBA", (w, 900), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    tile = Image.new("RGBA", (prod.width + 40, prod.height + 40), (0, 0, 0, 0))
    ImageDraw.Draw(tile).rounded_rectangle([0, 0, tile.width - 1, tile.height - 1], 26, fill=WHITE); tile.alpha_composite(prod, (20, 20))
    y = 40 + tile.height + 30
    d.rounded_rectangle([0, 0, w - 1, y + 400], 40, fill=(20, 20, 20, 215)); im.alpha_composite(tile, ((w - tile.width) // 2, 40)); d = ImageDraw.Draw(im)
    d.text((w / 2, y + 40), "Jom dapatkan", font=F(BLK, 62), fill=WHITE, anchor="mm")
    d.text((w / 2, y + 130), "Tea Mix", font=F(SERIF, 80), fill=CREAM, anchor="mm")
    d.text((w / 2, y + 200), "Herbalife", font=F(BD, 34), fill=(200, 200, 200), anchor="mm")
    by = y + 260; glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([150, by - 5, w - 150, by + 95], 50, fill=(230, 30, 40, 200)); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im); d.rounded_rectangle([160, by, w - 160, by + 90], 45, fill=(225, 30, 40))
    d.text((222, by + 45), "DM", font=F(BLK, 30), fill=(255, 220, 220), anchor="mm")
    d.text((w / 2 + 40, by + 45), "“TEAMIX”", font=F(BLK, 54), fill=WHITE, anchor="mm")
    return im.crop((0, 0, w, by + 130))

# ---------- join clips (cleaner, brighter "studio" look) ----------
STUDIO = "curves=master='0/0 0.25/0.30 0.5/0.57 0.75/0.81 1/1',colorbalance=rs=-0.03:bs=0.02:rm=-0.03:bm=0.03,eq=contrast=1.06:saturation=1.08"
durs = [float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", c], capture_output=True, text=True).stdout) for c in CLIPS]
starts = np.cumsum([0] + durs[:-1]); DUR = sum(durs)
inp = sum([["-i", c] for c in CLIPS], [])
fc = ";".join(f"[{i}:v]fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[v{i}]" for i in range(len(CLIPS)))
fc += ";" + "".join(f"[v{i}]" for i in range(len(CLIPS))) + f"concat=n={len(CLIPS)}:v=1:a=0,{STUDIO}"
dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", *inp, "-filter_complex", fc, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)

# product photo = the bottle in her photo
PH = Image.open("photo.jpg").convert("RGB")
w_, h_ = PH.size; PROD = PH.crop((int(w_ * 0.525), int(h_ * 0.55), int(w_ * 0.81), int(h_ * 0.865))).resize((220, 420), Image.LANCZOS).convert("RGBA")

s = starts
KICK = text_img("CARA BANCUH", F(BLK, 64), WHITE, stroke=3)
SUB2 = text_img("& kebaikannya", F(SERIF, 64), WHITE, stroke=3)
BIG = text_img("TEA MIX", F(BLK, 190), YEL, stroke=8)
SUB = text_img("Herbalife", F(SERIF, 80), CREAM, stroke=3)
STEPS = [(s[1] + 0.1, s[2], step("1", "Sediakan 200\u2013240ml air")), (s[2] + 0.1, s[3], step("2", "Masukkan \u00bd sudu teh Tea Mix")),
         (s[3] + 0.1, DUR, step("3", "Kacau \u2014 panas atau sejuk", False))]
BEN = [("Bantu kekal fokus & aktif", False), ("Manfaat antioksidan daripada teh", False), ("Rangsangan tenaga*", False), ("Hanya 6 kkal sehidangan", True), ("Mudah dibawa ke mana-mana", False)]
CARDS = []
ENDC = end_card(PROD)

enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a", "-shortest",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
n, last = 0, None
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    t = n / FPS; im = Image.frombytes("RGB", (W, H), raw).convert("RGBA")
    hb = s[1]
    if t < hb:
        paste_c(im, KICK, W / 2, 1230 + 20 * (1 - ease((t - 0.1) / 0.3)), fade(t, 0.1, hb))
        p = ease((t - 0.25) / 0.35); paste_c(im, BIG, W / 2, 1400, fade(t, 0.25, hb), 0.85 + 0.15 * p)
        paste_c(im, SUB, W / 2, 1570 + 20 * (1 - ease((t - 0.5) / 0.3)), fade(t, 0.5, hb))
    for a, b, st in STEPS:
        if a <= t < b:
            p = ease((t - a) / 0.35); paste_c(im, st, W / 2, 1560 + 40 * (1 - p), fade(t, a, b, 0.35, 0.2))
    for a, b, c in CARDS:
        if a <= t < b:
            p = ease((t - BA) / 0.35); paste_c(im, c, W / 2, 90 + c.height / 2 + 30 * (1 - p), fade(t, BA, DUR + 1))
    last = im.convert("RGB"); enc.stdin.write(last.tobytes()); n += 1
phs = PH.resize((W, int(PH.height * W / PH.width)), Image.LANCZOS)
phs = phs.crop((0, (phs.height - H) // 2, W, (phs.height - H) // 2 + H)) if phs.height >= H else phs.resize((W, H))
SIAP = step("4", "Siap! Jom minum", True)
for k in range(int(STILL * FPS)):
    t = k / FPS; z = 1 + 0.05 * t / STILL; cw, ch = int(W / z), int(H / z)
    f = phs.crop(((W - cw) // 2, int((H - ch) * 0.6), (W - cw) // 2 + cw, int((H - ch) * 0.6) + ch)).resize((W, H), Image.BILINEAR).convert("RGBA")
    p = ease(t / 0.35); paste_c(f, SIAP, W / 2, 1700 + 40 * (1 - p), p)
    n_ = min(len(BEN), 1 + int(max(t - 0.6, 0) / 0.9)) if t >= 0.6 else 0
    if n_:
        c = list_card("KEBAIKAN TEA MIX", BEN, n_); pc = ease((t - 0.6) / 0.35)
        paste_c(f, c, W / 2, 110 + c.height / 2 + 30 * (1 - pc), pc)
    enc.stdin.write(f.convert("RGB").tobytes()); last = f.convert("RGB")
blur = last.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.55)).convert("RGBA")
NOTE = Image.new("RGBA", (W, 140), (0, 0, 0, 0)); dn = ImageDraw.Draw(NOTE)
dn.text((W / 2, 40), "*Tenaga tambahan daripada kafein semula jadi.", font=F(BD, 28), fill=(210, 210, 215), anchor="mm")
dn.text((W / 2, 85), "Produk ini tidak bertujuan untuk mendiagnosis, merawat,", font=F(BD, 26), fill=(180, 180, 186), anchor="mm")
dn.text((W / 2, 120), "menyembuh atau mencegah sebarang penyakit.", font=F(BD, 26), fill=(180, 180, 186), anchor="mm")
for k in range(int(END * FPS)):
    t = k / FPS; f = blur.copy(); p = ease(t / 0.4); paste_c(f, ENDC, W / 2, 900 + 60 * (1 - p), p, 0.9 + 0.1 * p); paste_c(f, NOTE, W / 2, 1600, ease((t - 0.6) / 0.4))
    enc.stdin.write(f.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); print("dur", round(DUR + STILL + END, 1), "->", OUT)
