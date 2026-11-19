"""Sayur untuk turun berat vs naik berat, over the coach's photo."""
import os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H, FPS = 1080, 1920, 30
OUT = "reel-4-set-turun-naik-berat.mp4"
FD = "/usr/share/fonts/opentype/inter/"
BLK, XB, BD = FD + "InterDisplay-Black.otf", FD + "InterDisplay-ExtraBold.otf", FD + "InterDisplay-Bold.otf"
F = lambda p, s: ImageFont.truetype(p, s)
ease = lambda v: 1 - (1 - min(max(v, 0), 1)) ** 3
def back(v):
    v = min(max(v, 0), 1); c1 = 1.7; return 1 + (c1 + 1) * (v - 1) ** 3 + c1 * (v - 1) ** 2
BLUE, RED, WHITE, INK = (30, 90, 230), (225, 30, 40), (255, 255, 255), (15, 15, 20)
SETS = [("BUAH", [("Epal", "\U0001F34E"), ("Jambu Batu", "\U0001F34F"), ("Tembikai", "\U0001F349"), ("Oren", "\U0001F34A"), ("Beri", "\U0001FAD0\U0001F353")],
                  [("Pisang", "\U0001F34C"), ("Mangga", "\U0001F96D"), ("Anggur", "\U0001F347"), ("Pic", "\U0001F351"), ("Kelapa Muda", "\U0001F965")]),
        ("SAYUR", [(n, None) for n in ["Sawi", "Timun", "Brokoli", "Lada Benggala", "Kacang Buncis"]],
                  [(n, None) for n in ["Kentang", "Avokado", "Keledek", "Jagung", "Ubi Kayu"]]),
        ("MINUMAN", [("Teh Hijau", "\U0001F375"), ("Kopi O Kosong", "\u2615"), ("Air Lemon", "\U0001F34B"), ("Air Kosong", "\U0001F4A7"), ("Teh Herba", "\U0001FAD6")],
                  [("Smoothie Pisang", "\U0001F34C\U0001F964"), ("Milkshake Coklat", "\U0001F36B\U0001F964"), ("Jus Buah", "\U0001F9C3"), ("Susu Full Cream", "\U0001F95B"), ("Teh Tarik", "\U0001F9CB")]),
        ("MAKANAN", [("Telur Rebus", "\U0001F95A"), ("Oat", "\U0001F963"), ("Capati", "\U0001FAD3"), ("Kacang Kuda", "\U0001FAD8"), ("Ikan Bakar", "\U0001F41F")],
                  [("Keju", "\U0001F9C0"), ("Nasi Putih", "\U0001F35A"), ("Roti Putih", "\U0001F35E"), ("Kacang Tanah", "\U0001F95C"), ("Kentang Goreng", "\U0001F35F")])]
SETDUR, INTRO, CTAD = 7.0, 0.8, 3.5
PHOTO_OK = {"Telur Rebus", "Oat", "Capati", "Kacang Kuda", "Ikan Bakar", "Keju", "Nasi Putih", "Roti Putih", "Kacang Tanah", "Kentang Goreng"}
DUR = INTRO + SETDUR * len(SETS) + CTAD
EF = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
def emoji_img(chars, size):
    out = Image.new("RGBA", (size, size), (255, 255, 255, 255)); n = len(chars)
    for k, ch in enumerate(chars):
        e = Image.new("RGBA", (150, 150), (0, 0, 0, 0)); ImageDraw.Draw(e).text((75, 75), ch, font=EF, embedded_color=True, anchor="mm")
        e = e.crop(e.getbbox()); s_ = int(size * (0.66 if n == 1 else 0.5)); e = e.resize((s_, s_), Image.LANCZOS)
        if n == 1: out.alpha_composite(e, ((size - s_) // 2, (size - s_) // 2))
        else: out.alpha_composite(e, (int(size * (0.12 if k == 0 else 0.4)), int(size * (0.14 if k == 0 else 0.36))))
    return out

ph = Image.open("photo.jpg").convert("RGB")
ph = ImageEnhance.Brightness(ph).enhance(0.78)
def bg(t):
    z = 1 + 0.04 * t / DUR; ch = int(ph.height / z); cw = int(ch * W / H)
    if cw > ph.width: cw = ph.width; ch = int(cw * H / W)
    x0 = (ph.width - cw) // 2; y0 = int((ph.height - ch) * 0.45)
    return ph.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR).convert("RGBA")

def pill(txt1, txt2, col):
    f = F(BLK, 58); d = ImageDraw.Draw(Image.new("RGBA", (1, 1))); w = d.textlength(txt1 + " " + txt2, font=f) + 70
    im = Image.new("RGBA", (int(w) + 30, 140), (0, 0, 0, 0)); sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([15, 22, w + 15, 122], 30, fill=(0, 0, 0, 140)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(im); d.rounded_rectangle([15, 15, w + 15, 115], 30, fill=WHITE, outline=col, width=8)
    x = 50; d.text((x, 66), txt1, font=f, fill=INK, anchor="lm"); x += d.textlength(txt1 + " ", font=f); d.text((x, 66), txt2, font=f, fill=col, anchor="lm")
    return im

def sub(t, col):
    f = F(XB, 32); d = ImageDraw.Draw(Image.new("RGBA", (1, 1))); w = d.textlength(t, font=f) + 40
    im = Image.new("RGBA", (int(w), 56), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.rounded_rectangle([0, 0, w - 1, 55], 28, fill=col + (230,))
    d.text((w / 2, 28), t, font=f, fill=WHITE, anchor="mm"); return im

def item(name, col, emo=None, size=196):
    path = f"veg/{name}.png"
    if emo and os.path.exists(path) and name in PHOTO_OK: emo = None
    out = Image.new("RGBA", (size + 60, size + 110), (0, 0, 0, 0)); cx = out.width // 2
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([cx - size / 2 - 6, 24, cx + size / 2 + 6, size + 36], fill=(0, 0, 0, 160))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(out); d.ellipse([cx - size / 2 - 7, 13, cx + size / 2 + 7, size + 27], fill=col)
    if emo: p = emoji_img(emo, size)
    elif os.path.exists(path):
        p = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
    else:
        p = Image.new("RGBA", (size, size), (235, 235, 235, 255))
    m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).ellipse([0, 0, size - 1, size - 1], fill=255); p.putalpha(m)
    out.alpha_composite(p, (cx - size // 2, 20))
    f = F(BLK, 40)
    while d.textlength(name, font=f) > out.width + 40: f = F(BLK, f.size - 2)
    lab = Image.new("RGBA", (out.width + 80, 70), (0, 0, 0, 0)); dl = ImageDraw.Draw(lab)
    dl.text((lab.width / 2, 35), name, font=f, fill=WHITE, anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))
    big = Image.new("RGBA", (lab.width, out.height), (0, 0, 0, 0)); big.alpha_composite(out, (40, 0)); big.alpha_composite(lab, (0, size + 34))
    return big

PL, PR = pill("Turun", "Berat", BLUE), pill("Naik", "Berat", RED)
SL, SR = sub("Rendah kalori, tinggi serat", BLUE), sub("Lebih tinggi kalori & kanji", RED)
ITEMS = [([item(n, BLUE, e) for n, e in L], [item(n, RED, e) for n, e in R]) for _, L, R in SETS]
def chip(t):
    f = F(BLK, 46); d = ImageDraw.Draw(Image.new("RGBA", (1, 1))); w = d.textlength(t, font=f) + 70
    im = Image.new("RGBA", (int(w), 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.rounded_rectangle([0, 0, w - 1, 79], 40, fill=(255, 214, 10))
    d.text((w / 2, 40), t, font=f, fill=INK, anchor="mm"); return im
CHIPS = [chip(n) for n, _, _ in SETS]
def cta_card():
    im = Image.new("RGBA", (W, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([110, 20, W - 110, 500], 50, fill=(15, 15, 20, 225))
    d.text((W / 2, 120), "Nak Join Program?", font=F(BLK, 72), fill=WHITE, anchor="mm")
    d.text((W / 2, 205), "Turun berat tanpa berlapar", font=F(BD, 40), fill=(205, 205, 210), anchor="mm")
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(glow).rounded_rectangle([240, 290, W - 240, 430], 70, fill=(230, 30, 40, 210))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18))); d = ImageDraw.Draw(im)
    d.rounded_rectangle([250, 295, W - 250, 425], 65, fill=RED)
    d.text((340, 360), "DM", font=F(BLK, 40), fill=(255, 215, 215), anchor="mm")
    d.text((W / 2 + 45, 362), "\u201cCANTIK\u201d", font=F(BLK, 76), fill=WHITE, anchor="mm")
    return im
CTA = cta_card()

def paste(base, im, x, y, a=1.0, sc=1.0):
    if sc != 1.0: w0, h0 = im.size; im = im.resize((max(1, int(w0 * sc)), max(1, int(h0 * sc))), Image.LANCZOS); x += (w0 - im.width) / 2; y += (h0 - im.height) / 2
    if a < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x, y = int(x), int(y); l, t = max(0, -x), max(0, -y); r, b = min(im.width, W - x), min(im.height, H - y)
    if r > l and b > t: base.alpha_composite(im.crop((l, t, r, b)), (x + l, y + t))

enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a", "-shortest",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
CX_L, CX_R, Y0, STEP = 210, 870, 500, 265
for n in range(int(DUR * FPS)):
    t = n / FPS; img = bg(t)
    for k, (pl, sb, cx) in enumerate([(PL, SL, CX_L + 30), (PR, SR, CX_R - 30)]):
        at = 0.2 + k * 0.2; p = back((t - at) / 0.5)
        if t >= at:
            paste(img, pl, cx - pl.width / 2, 230 - 30 * (1 - min(p, 1)), ease((t - at) / 0.3), 0.85 + 0.15 * min(p, 1.05))
            paste(img, sb, cx - sb.width / 2, 365, ease((t - at - 0.3) / 0.3))
    TEND = INTRO + SETDUR * len(SETS)
    si = min(int(max(t - INTRO, 0) // SETDUR), len(SETS) - 1); st = t - INTRO - si * SETDUR
    if t >= TEND:
        p = back((t - TEND) / 0.6); paste(img, CTA, 0, 760 + 60 * (1 - min(p, 1)), ease((t - TEND) / 0.35), 0.9 + 0.1 * min(p, 1.05))
    elif t >= INTRO:
        ch = CHIPS[si]; out = ease((SETDUR - st) / 0.3)
        paste(img, ch, (W - ch.width) / 2, 120, ease(st / 0.3) * out)
        IL, IR = ITEMS[si]
        for i in range(5):
            for side, lst, cx in [(0, IL, CX_L), (1, IR, CX_R)]:
                at = 0.2 + i * 0.35 + side * 0.17; p = back((st - at) / 0.4)
                if st >= at:
                    im = lst[i]; dx = (-120 if side == 0 else 120) * (1 - min(p, 1))
                    if st > SETDUR - 0.35: dx += (-1 if side == 0 else 1) * 400 * ease((st - SETDUR + 0.35) / 0.35)
                    paste(img, im, cx - im.width / 2 + dx, Y0 + i * STEP, ease((st - at) / 0.25) * out, 0.8 + 0.2 * min(p, 1.05))
    enc.stdin.write(img.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); print("->", OUT)
