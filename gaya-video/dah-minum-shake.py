"""Slow-motion travel reel with elegant text and CTA."""
import subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SRC, OUT = 1080, 1920, 30, "base.mp4", "reel-dah-minum-shake.mp4"
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
SEG = [(0.3, 6.6, [(line("Dah minum", F(PF, 90), WHITE), 300, 0.0), (line("shake", F(GV, 200), GOLD, True), 445, 0.5),
                   (line("ke hari ni?", F(PF, 90), WHITE), 585, 1.0)]),
       (6.9, 10.2, [(line("Sarapan paling", F(PF, 80), WHITE), 300, 0.0), (line("senang", F(GV, 190), PINK, True), 440, 0.45),
                    (line("untuk disediakan", F(PFI, 70), WHITE), 575, 0.9)])]

def cta():
    im = Image.new("RGBA", (W, 430), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([110, 8, W - 170, 300], 40, fill=(20, 12, 18, 210), outline=(255, 214, 120, 170), width=3)
    cx = (W - 60) / 2
    d.text((cx, 62), "Nak dapatkan", font=F(PF, 58), fill=WHITE, anchor="mm")
    g = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).text((cx, 145), "produk Herbalife?", font=F(GV, 84), fill=GOLD + (190,), anchor="mm")
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(12))); d = ImageDraw.Draw(im)
    d.text((cx, 145), "produk Herbalife?", font=F(GV, 84), fill=GOLD, anchor="mm")
    d.rounded_rectangle([cx - 210, 210, cx + 210, 278], 34, fill=(225, 30, 40))
    d.text((cx, 245), "DM \u201cCANTIK\u201d", font=F(BD, 42), fill=WHITE, anchor="mm")
    return im
def disclaimer():
    im = Image.new("RGBA", (W, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([90, 5, W - 150, 125], 22, fill=(0, 0, 0, 150))
    f = F(BD, 25); cx = (W - 60) / 2
    d.text((cx, 34), "Produk ini tidak bertujuan untuk mendiagnosis, merawat,", font=f, fill=(235, 235, 240), anchor="mm")
    d.text((cx, 64), "menyembuh atau mencegah sebarang penyakit.", font=f, fill=(235, 235, 240), anchor="mm")
    d.text((cx, 96), "Gunakan bersama pemakanan seimbang & senaman.", font=f, fill=(255, 214, 120), anchor="mm")
    return im
DISC = disclaimer()
CTA, CTA_AT = cta(), 10.4

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
        paste(img, DISC, W / 2, 1460, ease((t - CTA_AT - 0.4) / 0.5))
    enc.stdin.write(img.convert("RGB").tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n, "->", OUT)
