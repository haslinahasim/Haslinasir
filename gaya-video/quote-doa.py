"""Quote reel: slow Ken Burns on photo + Malay quote revealed line by line (cream bold, reference style)."""
import subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H, FPS, TOTAL, OUT = 1080, 1920, 30, 13.0, "reel-doa-barakah.mp4"
SRC = "/root/.claude/uploads/3ae3b5b0-992e-568f-9118-f4bdb807456a/8d3d6d00-image.jpg"
XB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
CREAM = (255, 246, 196)
ease = lambda v: 1 - (1 - min(max(v, 0), 1)) ** 3
CX = (W - 60) / 2

ph = Image.open(SRC).convert("RGB")
ph = ImageEnhance.Color(ImageEnhance.Contrast(ph).enhance(1.05)).enhance(1.08)
BIG = ph.resize((int(W * 1.12), int(H * 1.12)), Image.LANCZOS)    # source is ~9:16

LINES = ["Biasakan berkata,", "“Ya Allah, aku sangat", "mahukan ini. Tapi aku", "mahukannya dengan",
         "redha-Mu. Dengan barakah.", "Dengan cara yang membawa", "aku lebih dekat kepada-Mu.”"]
f = ImageFont.truetype(XB, 66); LH = 84; Y0 = 390
def line_img(t):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1))); w = int(d.textlength(t, font=f)) + 80
    im = Image.new("RGBA", (w, LH + 50), (0, 0, 0, 0)); sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((40, 30), t, font=f, fill=(0, 0, 0, 230), stroke_width=4, stroke_fill=(0, 0, 0, 230))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(im).text((40, 25), t, font=f, fill=CREAM); return im
LIMGS = [line_img(t) for t in LINES]
T0, STEP = 0.8, 0.85

# soft darkening behind the text block
yy = np.linspace(0, 1, H)[:, None]
band = np.exp(-((yy * H - (Y0 + len(LINES) * LH / 2)) / 420) ** 2) * 150
SHADE = Image.fromarray(np.dstack([np.zeros((H, W, 3), np.uint8), band.astype(np.uint8).repeat(W, 1)[..., None]]), "RGBA")

enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a", "-shortest",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for n in range(int(TOTAL * FPS)):
    t = n / FPS; z = 1.12 - 0.10 * (t / TOTAL)                       # slow pull-out
    cw, ch = W * z / 1.12 * BIG.width / W / 1.0, 0
    w0, h0 = int(BIG.width / 1.12 * z / 1.0 * (1 / z) * z), 0
    cw, ch = int(W * z), int(H * z); x0 = (BIG.width - cw) // 2; y0 = int((BIG.height - ch) * 0.45)
    img = BIG.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR).convert("RGBA")
    img.alpha_composite(SHADE if t > 0.6 else Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 0)), SHADE, ease(t / 0.6)))
    for i, im in enumerate(LIMGS):
        p = ease((t - T0 - i * STEP) / 0.6)
        if p <= 0: continue
        a = im if p >= 1 else im.copy()
        if p < 1: a.putalpha(a.getchannel("A").point(lambda v: int(v * p)))
        img.alpha_composite(a, (int(CX - im.width / 2), int(Y0 + i * LH - 25 + 18 * (1 - p))))
    fade = ease((TOTAL - t) / 0.6)
    if fade < 1: img = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), img, fade)
    enc.stdin.write(img.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); print("->", OUT)
