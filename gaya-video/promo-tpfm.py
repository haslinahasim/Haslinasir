"""Rebuild the TPFM program promo with a clean, professional layout. Keeps the original voice-over."""
import subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SRC, OUT, DUR, END = 1080, 1920, 30, "in.mov", "promo-tpfm-pro.mp4", 37.0, 3.5
FD = "/usr/share/fonts/opentype/inter/"
BLK, XB, BD = FD + "InterDisplay-Black.otf", FD + "InterDisplay-ExtraBold.otf", FD + "InterDisplay-Bold.otf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
RED, WHITE, GREY, GOLD = (226, 32, 48), (255, 255, 255), (190, 190, 198), (245, 200, 90)
F = lambda p, s: ImageFont.truetype(p, s)
ease = lambda v: 1 - (1 - min(max(v, 0), 1)) ** 3
def back(v):
    v = min(max(v, 0), 1); c1 = 1.5; return 1 + (c1 + 1) * (v - 1) ** 3 + c1 * (v - 1) ** 2

def frame_at(t):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(t), "-i", SRC, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3)

def auto_box(t, ymin=0, ymax=H, pad=6):
    """Largest block of non-pink rows in the original slide (pink background ~ (250,200,210))."""
    a = frame_at(t).astype(int); bgc = np.median(a[5:40, 5:40].reshape(-1, 3), 0)
    m = (np.abs(a - bgc).sum(2) > 60); m[:ymin] = 0; m[ymax:] = 0
    rows = m.sum(1) > 25; runs, s = [], None
    for y, r in enumerate(list(rows) + [False]):
        if r and s is None: s = y
        if not r and s is not None:
            if y - s > 8: runs.append((s, y))
            s = None
    # merge runs separated by small gaps
    mr = []
    for r in runs:
        if mr and r[0] - mr[-1][1] < 14: mr[-1] = (mr[-1][0], r[1])
        else: mr.append(r)
    y0, y1 = max(mr, key=lambda r: r[1] - r[0])
    cols = np.where(m[y0:y1].sum(0) > 5)[0]
    return (max(0, cols.min() - pad), max(0, y0 - pad), min(W, cols.max() + pad), min(H, y1 + pad))

FULL = (0, 0, W, H)
# (start, end, step, title, accent word, sub, media) ; media = ("live", box) | ("still", t, box) | None
SC = [
    (0.00, 1.63, "", "Program Diet Online", "TPFM", "Transformasi kurus secara online", ("still", 0.8, auto_box(0.8, ymin=800))),
    (1.63, 4.90, "", "Kenali Head Coach", "Haslina", "Founder Team PowerFit Malaysia  •  turun 9 kg dalam 2.5 bulan", ("live", auto_box(3.0, ymax=950))),
    (4.90, 5.90, "", "Testimoni", "Peserta", "Hasil usaha mereka — boleh jadi hasil ANDA", ("live", auto_box(5.4, ymax=1400))),
    (5.90, 6.90, "", "Testimoni", "Peserta", "Hasil usaha mereka — boleh jadi hasil ANDA", ("live", auto_box(6.4, ymax=1400))),
    (6.90, 7.95, "", "Testimoni", "Peserta", "Hasil usaha mereka — boleh jadi hasil ANDA", ("live", auto_box(7.4, ymax=1400))),
    (7.95, 9.00, "", "Apa yang anda", "dapat?", "Jom tengok isi program ↓", None),
    (9.00, 11.07, "01", "Meal Plan", "Lengkap", "Makan 5 kali sehari — kenyang & kurus", ("live", auto_box(10.0, ymin=250))),
    (11.07, 12.57, "02", "Resipi Sedap &", "Mudah", "Untuk yang suka masak atau tak sempat makan di luar", ("live", (0, 0, W, 850))),
    (12.57, 14.07, "02", "Resipi Sedap &", "Mudah", "Untuk yang suka masak atau tak sempat makan di luar", ("live", (0, 1065, W, H))),
    (14.07, 18.67, "03", "Coach Pantau", "Setiap Meal", "Hantar gambar makanan — coach semak & beri rating", ("live", FULL)),
    (18.67, 20.10, "", "Contoh Menu", "Sehari", "Pagi  •  Lunch  •  Petang  •  Malam", ("live", auto_box(19.4))),
    (20.10, 21.00, "04", "Soalan Peribadi", "Dijawab", "Tanya terus kepada coach anda", ("live", auto_box(20.5))),
    (21.00, 23.90, "05", "Belajar Ilmu", "Pemakanan", "Faham cara jaga makan untuk jangka panjang", None),
    (23.90, 26.63, "05", "Topik-Topik", "Khas", "Ilmu lengkap supaya kurus kekal", ("live", auto_box(25.0, ymin=250))),
    (26.63, 29.00, "06", "Group", "Coaching", "Video & nota daripada coach, bersama rakan seperjuangan", ("live", FULL)),
    (29.00, 32.10, "07", "Pelan Turun Berat", "Peribadi", "Disesuaikan oleh coach, khas untuk anda", None),
    (32.10, DUR, "08", "Senaman Dalam", "App", "Rutin 21 hari + video Gym, Cardio, Six Pack & banyak lagi", ("app",)),
    (DUR, DUR + END, "", "Jom Mulakan Journey", "Kurus, Sihat & Cantik", "anda \u2014 sekarang!", "CTA"),
]
STILLS = {}
for s in SC:
    if isinstance(s[6], tuple) and s[6][0] == "still":
        x0, y0, x1, y1 = s[6][2]; STILLS[s[0]] = Image.fromarray(frame_at(s[6][1])[y0:y1, x0:x1])

# ---------- static layers ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
base = np.zeros((H, W, 3), np.float32)
base[..., 0] = 14 + 10 * yy / H; base[..., 1] = 12 + 2 * yy / H; base[..., 2] = 16 + 4 * yy / H
g = np.exp(-(((xx - W * .8) / 700) ** 2 + ((yy - 300) / 600) ** 2))[..., None] * np.array([110, 12, 25])
g2 = np.exp(-(((xx - W * .1) / 600) ** 2 + ((yy - 1700) / 600) ** 2))[..., None] * np.array([70, 8, 18])
BG = Image.fromarray(np.clip(base + g + g2, 0, 255).astype(np.uint8)).convert("RGBA")
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
for k in range(-6, 14):   # faint diagonal lines
    d.line([(k * 160, 0), (k * 160 + 900, H)], fill=(255, 255, 255, 7), width=2)
BG = Image.alpha_composite(BG, ov)

def brand_bar():
    im = Image.new("RGBA", (W, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = F(XB, 28); t = "TEAM POWERFIT MALAYSIA"; w = d.textlength(t, font=f)
    d.rounded_rectangle([60, 40, 60 + w + 70, 92], 26, fill=RED); d.ellipse([78, 58, 94, 74], fill=WHITE)
    d.text((108, 66), t, font=f, fill=WHITE, anchor="lm")
    d.text((W - 60, 66), "PROGRAM COACHING TPFM", font=F(BD, 26), fill=GREY, anchor="rm")
    return im
BAR = brand_bar()

def text_block(step, title, acc, sub, centered=False):
    im = Image.new("RGBA", (W, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = 10
    if step:
        d.text((70, y), step, font=F(BLK, 64), fill=RED); d.line([(160, y + 36), (260, y + 36)], fill=(255, 255, 255, 90), width=3); y += 90
    ft = F(BLK, 84 if not centered else 104); fa = F(SERIF, 96 if not centered else 120)
    while d.textlength(title, font=ft) > W - 120: ft = F(BLK, ft.size - 2)
    while d.textlength(acc, font=fa) > W - 120: fa = F(SERIF, fa.size - 2)
    tw = d.textlength(title + " ", font=ft); aw = d.textlength(acc, font=fa)
    if tw + aw <= W - 140:
        x0 = 70 if not centered else (W - tw - aw) / 2
        d.text((x0, y), title, font=ft, fill=WHITE); d.text((x0 + tw, y - 6), acc, font=fa, fill=GOLD); y += int(ft.size * 1.2)
    else:
        x0 = 70 if not centered else (W - d.textlength(title, font=ft)) / 2
        d.text((x0, y), title, font=ft, fill=WHITE); y += int(ft.size * 1.12)
        x0 = 70 if not centered else (W - aw) / 2
        d.text((x0, y - 6), acc, font=fa, fill=GOLD); y += int(fa.size * 1.15)
    fs = F(BD, 40 if not centered else 46); words, lines, ln = sub.split(), [], ""
    for wd in words:
        if d.textlength((ln + " " + wd).strip(), font=fs) > W - 160: lines.append(ln); ln = wd
        else: ln = (ln + " " + wd).strip()
    lines.append(ln)
    d.line([(70 if not centered else W / 2 - 60, y + 8), (190 if not centered else W / 2 + 60, y + 8)], fill=RED, width=6); y += 34
    for l in lines:
        d.text((70 if not centered else W / 2, y), l, font=fs, fill=GREY, anchor="la" if not centered else "ma"); y += int(fs.size * 1.3)
    return im.crop((0, 0, W, y + 10))

def card(img, maxw=880, maxh=1080, r=30):
    s = min(maxw / img.width, maxh / img.height); w, h = int(img.width * s), int(img.height * s)
    im = img.resize((w, h), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255); im.putalpha(m)
    out = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0)); sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([40, 52, 40 + w, 52 + h], r, fill=(0, 0, 0, 170)); out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))
    ImageDraw.Draw(out).rounded_rectangle([34, 34, 46 + w, 46 + h], r + 6, fill=(255, 255, 255, 40))
    out.alpha_composite(im, (40, 40)); return out

def cta():
    im = Image.new("RGBA", (W, 700), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([120, 40, W - 120, 300], 40, fill=(255, 255, 255, 18), outline=(255, 255, 255, 50), width=2)
    d.text((W / 2, 110), "bersama", font=F(BD, 40), fill=GREY, anchor="mm")
    d.text((W / 2, 190), "TEAM POWERFIT MALAYSIA", font=F(BLK, 62), fill=WHITE, anchor="mm")
    d.text((W / 2, 255), "Program Coaching TPFM", font=F(SERIF, 46), fill=GOLD, anchor="mm")
    return im
CTA = cta()
APW, APH = 540, 1170
_raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", "app.mp4", "-filter_complex",
    "[0:v]trim=0:7.6,setpts=PTS-STARTPTS[a];[0:v]trim=10:14.5,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0,setpts=PTS/2.55,fps=30,scale=%d:%d" % (APW, APH),
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
APP = [np.frombuffer(_raw[k:k + APW * APH * 3], np.uint8).reshape(APH, APW, 3) for k in range(0, len(_raw) - APW * APH * 3 + 1, APW * APH * 3)]
print("app frames", len(APP))
def phone(scr):
    b = 18; w, h = APW + 2 * b, APH + 2 * b
    out = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0)); sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([40, 56, 40 + w, 56 + h], 70, fill=(0, 0, 0, 190)); out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(24)))
    d = ImageDraw.Draw(out); d.rounded_rectangle([40, 40, 40 + w, 40 + h], 70, fill=(10, 10, 12), outline=(90, 90, 98), width=4)
    im = Image.fromarray(scr).convert("RGBA"); m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, APW - 1, APH - 1], 54, fill=255); im.putalpha(m)
    out.alpha_composite(im, (40 + b, 40 + b)); return out
TXT = {i: text_block(s[2], s[3], s[4], s[5], centered=(s[6] is None or s[6] == "CTA")) for i, s in enumerate(SC)}

def paste(base, im, x, y, a=1.0, sc=1.0):
    if sc != 1.0: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS); x += (im.width / sc - im.width) / 2; y += (im.height / sc - im.height) / 2
    if a < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x, y = int(x), int(y); l, t = max(0, -x), max(0, -y); r, b = min(im.width, W - x), min(im.height, H - y)
    if r > l and b > t: base.alpha_composite(im.crop((l, t, r, b)), (x + l, y + t))

# ---------- render ----------
dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", SRC, "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", SRC,
    "-map", "0:v", "-map", "1:a", "-af", "atrim=0:%.2f,afade=t=out:st=%.2f:d=0.5,apad" % (DUR, DUR - 0.5), "-t", str(DUR + END),
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
last, cache = None, {}
for n in range(int((DUR + END) * FPS)):
    t = n / FPS
    raw = dec.stdout.read(W * H * 3)
    if len(raw) == W * H * 3: last = np.frombuffer(raw, np.uint8).reshape(H, W, 3)
    i = max(k for k, s in enumerate(SC) if s[0] <= t); s0, s1, step, title, acc, sub, media = SC[i]; lt = t - s0
    img = BG.copy(); paste(img, BAR, 0, 0)
    same_text = i > 0 and SC[i - 1][3] == title and SC[i - 1][6] not in (None,) and media not in (None, "CTA")
    ta = 1 if same_text else ease(lt / 0.35)
    tb = TXT[i]
    if media is None or media == "CTA":
        ty = 620 if media is None else 380
        paste(img, tb, 0, ty + (0 if same_text else 40 * (1 - ta)), ta)
        if media == "CTA": p = back((lt - 0.4) / 0.6); paste(img, CTA, 0, 1000 + 60 * (1 - min(p, 1)), min(1, ease((lt - 0.4) / 0.4)), 0.9 + 0.1 * p)
        if media is None:   # small animated dots under text-only scenes
            dd = ImageDraw.Draw(img)
            for k in range(3):
                a = 0.4 + 0.6 * max(0, np.sin(t * 5 - k))
                dd.ellipse([W / 2 - 60 + k * 50, 1250, W / 2 - 40 + k * 50, 1270], fill=(226, 32, 48, int(255 * a)))
    else:
        paste(img, tb, 0, 170 + (0 if same_text else 30 * (1 - ta)), ta)
        top = 170 + tb.height + 30
        if media[0] == "app":
            k = min(int(lt * FPS), len(APP) - 1); ph = phone(APP[k]); p = back(lt / 0.5)
            sc_ = min(1.0, (H - 120 - top) / ph.height)
            paste(img, ph, (W - ph.width) / 2, top - 20 + 50 * (1 - min(p, 1)), min(1, ease(lt / 0.3)), sc_ * (0.94 + 0.06 * p))
            src = None
        elif media[0] == "still": src = STILLS[s0]
        else:
            fr_ = last
            if 14.0 <= t < 18.67 and abs(int(last[976, 140, 0]) - 250) < 25 and int(last[976, 140, 1]) > 180:   # hide old pink caption bubble
                pi = Image.fromarray(last).convert("RGBA"); dq = ImageDraw.Draw(pi)
                dq.rounded_rectangle([110, 830, 962, 1122], 60, fill=(18, 16, 20, 245))
                dq.text((536, 976), "\u2713  Coach semak setiap meal", font=F(BLK, 58), fill=GOLD, anchor="mm")
                fr_ = np.asarray(pi.convert("RGB"))
            x0, y0, x1, y1 = media[1]; src = Image.fromarray(fr_[y0:y1, x0:x1])
        maxh = H - 150 - top
        if src is None:
            dd = ImageDraw.Draw(img); dd.rectangle([0, H - 10, W, H], fill=(255, 255, 255, 25)); dd.rectangle([0, H - 10, int(W * t / (DUR + END)), H], fill=RED)
            enc.stdin.write(img.convert("RGB").tobytes()); continue
        cd = card(src, 900, maxh)
        p = back(lt / 0.5); kb = 1 + 0.03 * min(lt / (s1 - s0), 1)
        paste(img, cd, (W - cd.width) / 2, top + (maxh + 80 - cd.height) / 2 + 50 * (1 - min(p, 1)), min(1, ease(lt / 0.3)), (0.94 + 0.06 * p) * kb)
    # progress bar
    dd = ImageDraw.Draw(img); dd.rectangle([0, H - 10, W, H], fill=(255, 255, 255, 25)); dd.rectangle([0, H - 10, int(W * t / (DUR + END)), H], fill=RED)
    enc.stdin.write(img.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); print("->", OUT)
