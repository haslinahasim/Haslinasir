"""Malay translated captions for an English trending sound + CTA."""
import subprocess, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SRC, OUT = 1080, 1920, 30, "in.mp4", "reel-kurus-nampak-cantik.mp4"
BLK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
XB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
PF = "/root/.fonts/Playfair_Display_wght_800_.woff2"
PFI = "/root/.fonts/Playfair_Display_ital_wght_1_700_.woff2"
GV = "/root/.fonts/Great_Vibes_.woff2"
F = lambda p, s: ImageFont.truetype(p, s)
WHITE, GOLD, PINK = (255, 255, 255), (255, 214, 120), (255, 160, 190)
ease = lambda v: 1 - (1 - min(max(v, 0), 1)) ** 3
CX = (W - 60) / 2

# (start, end, malay text with *accent*)
CAPS = [(0.0, 1.95, "Tak kisah. Saya suka jadi *kurus*."),
        (2.0, 3.9, "Suka sangat jadi *kurus*."),
        (3.94, 5.05, "Kenapa? Sebab nampak *cantik*."),
        (5.08, 6.1, "Nampak *paling cantik*."),
        (6.12, 10.4, "Boleh ikat rambut, tak risau *dagu berlapis* dari tepi."),
        (10.54, 14.2, "Tak risau leher besar & *lemak berlipat*."),
        (14.26, 18.25, "Boleh pakai *apa saja baju* tanpa risau."),
        (18.3, 20.0, "Kurus memang nampak *lebih cantik*."),
        (20.06, 22.3, "Bila orang tanya, kenapa obses sangat nak *kurus*?"),
        (22.34, 24.6, "Sebab nampak *cantik*!"),
        (24.68, 26.0, "Jom *ikut program*!")]

def cap_img(s):
    parts = [(w.strip("*"), w.startswith("*") or w.endswith("*") or "*" in w) for w in re.findall(r"\*[^*]+\*|\S+", s)]
    # split accent groups into words but keep their flag
    words = []
    for t, a in parts:
        for w in t.split():
            if words and all(ch in ".,!?&" for ch in w) and w != "&": words[-1] = (words[-1][0] + w, words[-1][1])
            else: words.append((w, a))
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1))); fw, fa = F(BLK, 58), F(PFI, 64); sp = 15; maxw = 800
    lines, cur, cw = [], [], 0
    for w, a in words:
        ww = d.textlength(w, font=fa if a else fw)
        if cur and cw + sp + ww > maxw: lines.append((cur, cw)); cur, cw = [], 0
        cur.append((w, a, ww)); cw += (sp if cw else 0) + ww
    lines.append((cur, cw))
    lh = 80; h = lh * len(lines) + 50; bw = max(c for _, c in lines) + 70
    im = Image.new("RGBA", (W, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([(W - bw) / 2, 10, (W + bw) / 2, h + 10], 30, fill=(15, 10, 14, 175))
    for i, (ln, w_) in enumerate(lines):
        x = (W - w_) / 2; y = 10 + 25 + i * lh + 58
        for w, a, ww in ln:
            d.text((x, y), w, font=fa if a else fw, fill=GOLD if a else WHITE, anchor="ls"); x += ww + sp
    return im
CIMG = [(a, b, cap_img(s)) for a, b, s in CAPS]

def cta():
    im = Image.new("RGBA", (W, 310), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([110, 8, W - 170, 300], 40, fill=(30, 14, 22, 215), outline=GOLD + (170,), width=3)
    d.text((CX, 62), "Nak saya bantu?", font=F(PF, 58), fill=WHITE, anchor="mm")
    g = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).text((CX, 145), "kurus, cantik & sihat", font=F(GV, 80), fill=PINK + (190,), anchor="mm")
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(12))); d = ImageDraw.Draw(im)
    d.text((CX, 145), "kurus, cantik & sihat", font=F(GV, 80), fill=PINK, anchor="mm")
    d.rounded_rectangle([CX - 210, 210, CX + 210, 278], 34, fill=(225, 30, 40))
    d.text((CX, 245), "DM “CANTIK”", font=F(BLK, 42), fill=WHITE, anchor="mm")
    return im
CTA, CTA_AT = cta(), 20.2

def paste(base, im, cx, cy, a=1.0, sc=1.0):
    if sc != 1: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    if a < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x, y = int(cx - im.width / 2), int(cy - im.height / 2); l, t = max(0, -x), max(0, -y); r, b = min(im.width, W - x), min(im.height, H - y)
    if r > l and b > t: base.alpha_composite(im.crop((l, t, r, b)), (x + l, y + t))

dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", SRC, "-vf",
    f"fps={FPS},scale={W}:{H}:flags=lanczos,hqdn3d=1.5:1.5:4:4,unsharp=5:5:0.8,eq=contrast=1.05:saturation=1.06:brightness=0.02",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-i", SRC, "-map", "0:v", "-map", "1:a?", "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
n = 0
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    t = n / FPS; img = Image.frombytes("RGB", (W, H), raw).convert("RGBA")
    for a, b, im in CIMG:
        if a <= t < b:
            p = ease((t - a) / 0.15); paste(img, im, CX + 30 - 30, 1440, p, 0.96 + 0.04 * p); break
    if t >= CTA_AT:
        p = ease((t - CTA_AT) / 0.6); paste(img, CTA, W / 2, 220 + 155 + 30 * (1 - p), p, 0.95 + 0.05 * p)
    enc.stdin.write(img.convert("RGB").tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n, "->", OUT)
