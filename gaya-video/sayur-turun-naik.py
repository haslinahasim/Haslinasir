"""Sayur untuk turun berat vs naik berat, over the coach's photo."""
import os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H, FPS, DUR = 1080, 1920, 30, 11.0
OUT = "reel-sayur-turun-naik-berat.mp4"
FD = "/usr/share/fonts/opentype/inter/"
BLK, XB, BD = FD + "InterDisplay-Black.otf", FD + "InterDisplay-ExtraBold.otf", FD + "InterDisplay-Bold.otf"
F = lambda p, s: ImageFont.truetype(p, s)
ease = lambda v: 1 - (1 - min(max(v, 0), 1)) ** 3
def back(v):
    v = min(max(v, 0), 1); c1 = 1.7; return 1 + (c1 + 1) * (v - 1) ** 3 + c1 * (v - 1) ** 2
BLUE, RED, WHITE, INK = (30, 90, 230), (225, 30, 40), (255, 255, 255), (15, 15, 20)
LEFT = ["Sawi", "Timun", "Brokoli", "Lada Benggala", "Kacang Buncis"]
RIGHT = ["Kentang", "Avokado", "Keledek", "Jagung", "Ubi Kayu"]

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

def item(name, col, size=196):
    path = f"veg/{name}.png"
    out = Image.new("RGBA", (size + 60, size + 110), (0, 0, 0, 0)); cx = out.width // 2
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([cx - size / 2 - 6, 24, cx + size / 2 + 6, size + 36], fill=(0, 0, 0, 160))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(out); d.ellipse([cx - size / 2 - 7, 13, cx + size / 2 + 7, size + 27], fill=col)
    if os.path.exists(path):
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
IL = [item(n, BLUE) for n in LEFT]; IR = [item(n, RED) for n in RIGHT]

def paste(base, im, x, y, a=1.0, sc=1.0):
    if sc != 1.0: w0, h0 = im.size; im = im.resize((max(1, int(w0 * sc)), max(1, int(h0 * sc))), Image.LANCZOS); x += (w0 - im.width) / 2; y += (h0 - im.height) / 2
    if a < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x, y = int(x), int(y); l, t = max(0, -x), max(0, -y); r, b = min(im.width, W - x), min(im.height, H - y)
    if r > l and b > t: base.alpha_composite(im.crop((l, t, r, b)), (x + l, y + t))

enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a", "-shortest",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
CX_L, CX_R, Y0, STEP = 210, 870, 470, 270
for n in range(int(DUR * FPS)):
    t = n / FPS; img = bg(t)
    for k, (pl, sb, cx) in enumerate([(PL, SL, CX_L + 30), (PR, SR, CX_R - 30)]):
        at = 0.8 + k * 0.3; p = back((t - at) / 0.5)
        if t >= at:
            paste(img, pl, cx - pl.width / 2, 230 - 30 * (1 - min(p, 1)), ease((t - at) / 0.3), 0.85 + 0.15 * min(p, 1.05))
            paste(img, sb, cx - sb.width / 2, 365, ease((t - at - 0.3) / 0.3))
    for i in range(5):
        for side, lst, cx in [(0, IL, CX_L), (1, IR, CX_R)]:
            at = 1.8 + i * 0.9 + side * 0.45; p = back((t - at) / 0.45)
            if t >= at:
                im = lst[i]; dx = (-120 if side == 0 else 120) * (1 - min(p, 1))
                paste(img, im, cx - im.width / 2 + dx, Y0 + i * STEP, ease((t - at) / 0.3), 0.8 + 0.2 * min(p, 1.05))
    enc.stdin.write(img.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); print("->", OUT)
