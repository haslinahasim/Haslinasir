"""Premenopause reel: elegant text sequence + symptom list + coach stats + CTA."""
import subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SRC, OUT = 1080, 1920, 30, "in.mov", "reel-premenopause.mp4"
PF = "/root/.fonts/Playfair_Display_wght_800_.woff2"
PFI = "/root/.fonts/Playfair_Display_ital_wght_1_700_.woff2"
GV = "/root/.fonts/Great_Vibes_.woff2"
XB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
BLK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
F = lambda p, s: ImageFont.truetype(p, s)
WHITE, PINK, ROSE, GOLD = (255, 255, 255), (255, 160, 190), (214, 92, 128), (255, 214, 120)
ease = lambda v: 1 - (1 - min(max(v, 0), 1)) ** 3
CX = (W - 60) / 2        # a little left of centre, clear of right-side icons

def txt(t, font, col, glow=False, stroke=0):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1))); l, tp, r, b = d.textbbox((0, 0), t, font=font, stroke_width=stroke)
    pad = 40; im = Image.new("RGBA", (r - l + pad * 2, b - tp + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((pad - l, pad - tp + 5), t, font=font, fill=(0, 0, 0, 230), stroke_width=stroke + 2, stroke_fill=(0, 0, 0, 230))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)))
    if glow:
        g = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).text((pad - l, pad - tp), t, font=font, fill=col + (190,))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(im).text((pad - l, pad - tp), t, font=font, fill=col, stroke_width=stroke, stroke_fill=(0, 0, 0))
    return im

def pill(t, w=760):
    im = Image.new("RGBA", (w + 30, 104), (0, 0, 0, 0)); sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([15, 18, w + 15, 96], 39, fill=(0, 0, 0, 140)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
    d = ImageDraw.Draw(im); d.rounded_rectangle([15, 12, w + 15, 90], 39, fill=(255, 255, 255, 235))
    d.ellipse([30, 22, 88, 80], fill=ROSE); d.line([(48, 40), (70, 62)], fill=WHITE, width=7); d.line([(48, 62), (70, 40)], fill=WHITE, width=7)
    f = F(XB, 40)
    while d.textlength(t, font=f) > w - 110: f = F(XB, f.size - 1)
    d.text((108, 51), t, font=f, fill=(40, 25, 35), anchor="lm"); return im

def stat_card():
    im = Image.new("RGBA", (W, 430), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([120, 10, W - 180, 420], 44, fill=(30, 14, 22, 205), outline=PINK + (200,), width=3)
    cx = (W - 60) / 2
    d.text((cx, 80), "Saya usia", font=F(PFI, 54), fill=WHITE, anchor="mm")
    d.text((cx, 175), "47 tahun", font=F(PF, 104), fill=PINK, anchor="mm")
    d.line([(cx - 160, 252), (cx + 160, 252)], fill=GOLD, width=3)
    d.text((cx - 150, 330), "54", font=F(PF, 96), fill=WHITE, anchor="mm"); d.text((cx - 150, 395), "kg", font=F(XB, 32), fill=GOLD, anchor="mm")
    d.text((cx, 330), "|", font=F(PF, 80), fill=(255, 255, 255, 120), anchor="mm")
    d.text((cx + 150, 330), "158", font=F(PF, 96), fill=WHITE, anchor="mm"); d.text((cx + 150, 395), "cm", font=F(XB, 32), fill=GOLD, anchor="mm")
    return im

def cta():
    im = Image.new("RGBA", (W, 330), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([110, 8, W - 170, 320], 42, fill=(30, 14, 22, 210), outline=GOLD + (170,), width=3)
    cx = (W - 60) / 2
    d.text((cx, 70), "Nak tak saya bantu?", font=F(PF, 62), fill=WHITE, anchor="mm")
    g = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).text((cx, 158), "kurus, cantik & sihat", font=F(GV, 84), fill=PINK + (190,), anchor="mm")
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(12))); d = ImageDraw.Draw(im)
    d.text((cx, 158), "kurus, cantik & sihat", font=F(GV, 84), fill=PINK, anchor="mm")
    d.rounded_rectangle([cx - 210, 228, cx + 210, 298], 35, fill=(225, 30, 40))
    d.text((cx, 264), "DM “CANTIK”", font=F(BLK, 44), fill=WHITE, anchor="mm")
    return im

SYMS = ["Perut jadi buncit", "Makan sikit pun tak turun", "Penat sentiasa", "Lutut dah “bagi signal”", "Tidur susah",
        "Berat? Naik mencanak!"]
PILLS = [pill(s) for s in SYMS]
# scenes: (start, end, items[(image, y, delay)])
SCENES = [
    (0.0, 2.5, [(txt("Dear", F(GV, 160), (255, 240, 245), True), 1180, 0.1), (txt("wanita 40-an ke atas", F(PF, 76), WHITE), 1330, 0.45)]),
    (2.5, 5.0, [(txt("PREMENOPAUSE", F(PF, 96), WHITE), 1000, 0.0), (txt("bukan mitos", F(GV, 150), PINK, True), 1150, 0.4)]),
    (5.0, 10.6, [(txt("Tanda-tandanya…", F(PFI, 62), WHITE), 860, 0.0)] + [(p, 970 + i * 96, 0.35 + i * 0.75) for i, p in enumerate(PILLS)]),
    (10.6, 12.7, [(stat_card(), 1060, 0.0)]),
    (12.7, 15.1, [(cta(), 1080, 0.0)]),
]

def paste(base, im, cx, cy, a=1.0, sc=1.0):
    if sc != 1: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    if a < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x, y = int(cx - im.width / 2), int(cy - im.height / 2); l, t = max(0, -x), max(0, -y); r, b = min(im.width, W - x), min(im.height, H - y)
    if r > l and b > t: base.alpha_composite(im.crop((l, t, r, b)), (x + l, y + t))

dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", SRC, "-vf",
    f"fps={FPS},scale={W}:{H}:flags=lanczos,hqdn3d=1.2:1.2:3:3,unsharp=5:5:0.6,eq=contrast=1.05:saturation=1.08:brightness=0.02",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-i", SRC, "-map", "0:v", "-map", "1:a?", "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
n = 0
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    t = n / FPS; img = Image.frombytes("RGB", (W, H), raw).convert("RGBA")
    for a, b, items in SCENES:
        if a <= t < b:
            out = ease((b - t) / 0.3) if b < 15 else 1
            for im, y, dl in items:
                p = ease((t - a - dl) / 0.45)
                if p > 0: paste(img, im, CX if im.width < W else W / 2, y + 25 * (1 - p), p * out, 0.92 + 0.08 * p)
    enc.stdin.write(img.convert("RGB").tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n, "->", OUT)
