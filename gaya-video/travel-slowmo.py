"""Slow-motion travel reel with elegant text and CTA."""
import subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SRC, OUT = 1080, 1920, 30, "slow.mp4", "reel-travel-berat-ideal.mp4"
PF = "/root/.fonts/Playfair_Display_wght_800_.woff2"
PFI = "/root/.fonts/Playfair_Display_ital_wght_1_700_.woff2"
GV = "/root/.fonts/Great_Vibes_.woff2"
BD = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
F = lambda p, s: ImageFont.truetype(p, s)
WHITE, GOLD, PINK = (255, 255, 255), (255, 214, 120), (255, 150, 195)
ease = lambda v: 1 - (1 - min(max(v, 0), 1)) ** 3
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", SRC], capture_output=True, text=True).stdout)

def line(t, font, col, glow=False):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1))); l, tp, r, b = d.textbbox((0, 0), t, font=font)
    pad = 40; im = Image.new("RGBA", (r - l + pad * 2, b - tp + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((pad - l, pad - tp + 5), t, font=font, fill=(0, 0, 0, 220))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)))
    if glow:
        g = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).text((pad - l, pad - tp), t, font=font, fill=col + (200,))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(im).text((pad - l, pad - tp), t, font=font, fill=col)
    return im

# (start, end, [(line image, y centre, delay)])
SEG = [(0.3, 6.6, [(line("Tau tak apa", F(PF, 84), WHITE), 300, 0.0), (line("paling best bila", F(PF, 84), WHITE), 400, 0.4),
                   (line("travel?", F(GV, 170), GOLD, True), 530, 0.9)]),
       (6.9, 12.6, [(line("Ambil gambar semua", F(PF, 76), WHITE), 300, 0.0), (line("cantik", F(GV, 180), PINK, True), 425, 0.5),
                    (line("sebab berat badan ideal", F(PFI, 62), WHITE), 545, 1.1)])]

def cta():
    im = Image.new("RGBA", (W, 310), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([110, 8, W - 170, 300], 40, fill=(20, 12, 18, 205), outline=(255, 214, 120, 160), width=3)
    cx = (W - 60) / 2
    d.text((cx, 62), "Nak saya bantu?", font=F(PF, 58), fill=WHITE, anchor="mm")
    g = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).text((cx, 145), "kurus, cantik & sihat", font=F(GV, 80), fill=GOLD + (190,), anchor="mm")
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(12))); d = ImageDraw.Draw(im)
    d.text((cx, 145), "kurus, cantik & sihat", font=F(GV, 80), fill=GOLD, anchor="mm")
    d.rounded_rectangle([cx - 245, 210, cx + 245, 278], 34, fill=(225, 30, 40))
    d.text((cx, 245), "DM / komen \u201cCANTIK\u201d", font=F(BD, 40), fill=WHITE, anchor="mm")
    return im
CTA, CTA_AT = cta(), 12.9

# soft dark gradient at the top so text always reads on the lantern
yy = np.linspace(0, 1, H)[:, None]
GRAD = Image.fromarray(np.dstack([np.zeros((H, W, 3), np.uint8), (np.clip(1 - yy / 0.42, 0, 1) ** 1.6 * 150).astype(np.uint8).repeat(W, 1)[..., None]]), "RGBA")

def paste(base, im, cx, cy, a=1.0, sc=1.0):
    if sc != 1: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    if a < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x, y = int(cx - im.width / 2), int(cy - im.height / 2); l, t = max(0, -x), max(0, -y); r, b = min(im.width, W - x), min(im.height, H - y)
    if r > l and b > t: base.alpha_composite(im.crop((l, t, r, b)), (x + l, y + t))

dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a", "-shortest",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
n = 0; CX = (W - 60) / 2   # a little left of centre, clear of the right-side icons
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    t = n / FPS; img = Image.frombytes("RGB", (W, H), raw).convert("RGBA"); img.alpha_composite(GRAD)
    for a, b, lines in SEG:
        if a <= t < b:
            out = ease((b - t) / 0.4)
            for im, y, dl in lines:
                p = ease((t - a - dl) / 0.7)
                if p > 0: paste(img, im, CX, y + 30 * (1 - p), p * out, 0.94 + 0.06 * p)
    if t >= CTA_AT:
        p = ease((t - CTA_AT) / 0.7); paste(img, CTA, W / 2, 210 + 155 + 30 * (1 - p), p, 0.95 + 0.05 * p)
    enc.stdin.write(img.convert("RGB").tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n, "->", OUT)
