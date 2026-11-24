"""Day 2 Osaka travel vlog: merged clips + photos, elegant titles, location labels, hashtag end card."""
import subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SRC, OUT = 1080, 1920, 30, "base.mp4", "reel-day2-osaka.mp4"
PF = "/root/.fonts/Playfair_Display_wght_800_.woff2"
PFI = "/root/.fonts/Playfair_Display_ital_wght_1_700_.woff2"
GV = "/root/.fonts/Great_Vibes_.woff2"
XB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
F = lambda p, s: ImageFont.truetype(p, s)
WHITE, GOLD, PINK = (255, 255, 255), (255, 214, 120), (255, 170, 200)
ease = lambda v: 1 - (1 - min(max(v, 0), 1)) ** 3
CX = (W - 60) / 2
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", SRC], capture_output=True, text=True).stdout)

def txt(t, font, col, glow=False):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1))); l, tp, r, b = d.textbbox((0, 0), t, font=font)
    pad = 40; im = Image.new("RGBA", (r - l + pad * 2, b - tp + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((pad - l, pad - tp + 5), t, font=font, fill=(0, 0, 0, 235))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)))
    if glow:
        g = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).text((pad - l, pad - tp), t, font=font, fill=col + (200,))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(im).text((pad - l, pad - tp), t, font=font, fill=col); return im

def label(t):
    f = F(PFI, 54); d = ImageDraw.Draw(Image.new("RGBA", (1, 1))); w = int(d.textlength(t, font=f)) + 110
    im = Image.new("RGBA", (w + 40, 140), (0, 0, 0, 0)); sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([20, 26, w + 20, 122], 48, fill=(0, 0, 0, 150)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(im); d.rounded_rectangle([20, 18, w + 20, 114], 48, fill=(25, 15, 22, 225), outline=GOLD + (200,), width=3)
    d.ellipse([46, 58, 62, 74], fill=GOLD); d.text((w / 2 + 30, 66), t, font=f, fill=WHITE, anchor="mm"); return im

def tag():
    im = Image.new("RGBA", (400, 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([10, 8, 390, 72], 32, fill=(25, 15, 22, 200), outline=GOLD + (170,), width=2)
    d.text((200, 40), "DAY 2  •  OSAKA", font=F(XB, 32), fill=GOLD, anchor="mm"); return im

TITLE = [(txt("Day 2", F(GV, 190), GOLD, True), 640, 0.2), (txt("OSAKA", F(PF, 150), WHITE), 820, 0.6),
         (txt("Herbalife Country Vacation 2025", F(PFI, 46), (255, 240, 230)), 950, 1.0)]
# (start, end, image, y)
LABELS = [(4.7, 12.2, label("Petang di bandar Osaka"), 1400), (12.7, 16.4, label("Check-in Hilton Osaka"), 1400),
          (16.9, 19.6, label("Bilik yang selesa"), 1400), (20.1, 23.2, label("Welcome gift dari Herbalife"), 430),
          (23.7, 35.2, label("Jalan-jalan malam"), 1400), (35.7, 41.0, label("Shopping time!"), 1400)]
END_AT = 41.4
END = [(txt("Kenangan indah", F(PFI, 64), WHITE), 560, 0.0), (txt("Osaka", F(GV, 170), PINK, True), 700, 0.35),
       (txt("#haslinasirtakesosaka2026", F(XB, 44), GOLD), 850, 0.8)]
TAG = tag()

yy = np.linspace(0, 1, H)[:, None]
GRAD = Image.fromarray(np.dstack([np.zeros((H, W, 3), np.uint8), (np.clip(1 - yy / 0.62, 0, 1) ** 1.4 * 170).astype(np.uint8).repeat(W, 1)[..., None]]), "RGBA")

def paste(base, im, cx, cy, a=1.0, sc=1.0):
    if sc != 1: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    if a < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x, y = int(cx - im.width / 2), int(cy - im.height / 2); l, t = max(0, -x), max(0, -y); r, b = min(im.width, W - x), min(im.height, H - y)
    if r > l and b > t: base.alpha_composite(im.crop((l, t, r, b)), (x + l, y + t))

dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a", "-shortest",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
n = 0
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    t = n / FPS; img = Image.frombytes("RGB", (W, H), raw).convert("RGBA")
    if t >= END_AT:
        e = ease((t - END_AT) / 0.7); bl = img.filter(ImageFilter.GaussianBlur(14))
        bl = Image.blend(bl, Image.new("RGBA", (W, H), (15, 8, 14, 255)), 0.45); img = Image.blend(img, bl, e)
    ga = max(ease((4.4 - t) / 0.5) if t < 4.4 else 0, ease((t - END_AT) / 0.6) if t >= END_AT else 0)
    if ga > 0:
        g = GRAD if ga >= 1 else GRAD.copy(); 
        if ga < 1: g.putalpha(GRAD.getchannel("A").point(lambda v: int(v * ga)))
        img.alpha_composite(g)
    if t < 4.4:
        out = ease((4.3 - t) / 0.4)
        for im, y, dl in TITLE:
            p = ease((t - dl) / 0.7)
            if p > 0: paste(img, im, CX, y + 30 * (1 - p), p * out, 0.94 + 0.06 * p)
    elif t < END_AT:
        paste(img, TAG, CX, 200, ease((t - 4.6) / 0.5) * ease((END_AT - t) / 0.4))
    for a, b, im, y in LABELS:
        if a <= t < b:
            p = ease((t - a) / 0.45); paste(img, im, CX + 40 * (1 - p), y, p * ease((b - t) / 0.3))
    if t >= END_AT:
        for im, y, dl in END:
            p = ease((t - END_AT - dl) / 0.7)
            if p > 0: paste(img, im, CX, y + 30 * (1 - p), p, 0.94 + 0.06 * p)
    enc.stdin.write(img.convert("RGB").tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n, "->", OUT)
