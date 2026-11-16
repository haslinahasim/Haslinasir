"""Malay food tier list over the coach's own photo."""
import subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H, FPS, DUR = 1080, 1920, 30, 9.0
OUT = "reel-makanan-lemak-perut.mp4"
FD = "/usr/share/fonts/opentype/inter/"
BLK, XB = FD + "InterDisplay-Black.otf", FD + "InterDisplay-ExtraBold.otf"
F = lambda p, s: ImageFont.truetype(p, s)
ease = lambda x: 1 - (1 - min(max(x, 0), 1)) ** 3
TIERS = [("PALING\nTERUK", (225, 30, 35), WHITE := (255, 255, 255), ["Char Kuey Teow", "Nasi Kandar", "Roti Tisu", "Maggi Goreng"]),
         ("KALORI\nTERSEMBUNYI", (245, 120, 20), WHITE, ["Teh Tarik", "Milo Ais", "Roti Canai", "Nasi Lemak"]),
         ("JAGA\nPORSI", (250, 215, 20), (20, 20, 20), ["Nasi Ayam", "Satay", "Roti Telur", "Wantan Mee"]),
         ("PILIHAN\nBAIK", (120, 210, 60), (20, 20, 20), ["Thosai", "Capati", "Yong Tau Foo", "Sup Ayam"]),
         ("TERBAIK", (30, 170, 70), WHITE, ["Ayam Tandoori", "Ikan Bakar", "Telur Separuh Masak", "Teh O Kosong"])]

# background: her photo, 9:16, slightly darker so text reads
ph = Image.open("photo.jpg").convert("RGB"); s = max(W / ph.width, H / ph.height) * 1.08
ph = ph.resize((int(ph.width * s), int(ph.height * s)), Image.LANCZOS)
ph = ImageEnhance.Brightness(ph).enhance(0.62)
grad = np.linspace(0, 1, H)[:, None, None]
def bg(t):
    z = 1 + 0.05 * t / DUR
    ch = int(ph.height / z); cw = int(ch * W / H)
    if cw > ph.width: cw = ph.width; ch = int(cw * H / W)
    x0 = (ph.width - cw) // 2; y0 = (ph.height - ch) // 2
    return ph.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR).convert("RGBA")

def shadow_text(d_img, xy, txt, f, fill, stroke=6, anchor="mm", spacing=0):
    sh = Image.new("RGBA", d_img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).multiline_text((xy[0], xy[1] + 6), txt, font=f, fill=(0, 0, 0, 200), anchor=anchor, align="center", stroke_width=stroke + 2, stroke_fill=(0, 0, 0, 200), spacing=spacing)
    d_img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    ImageDraw.Draw(d_img).multiline_text(xy, txt, font=f, fill=fill, anchor=anchor, align="center", stroke_width=stroke, stroke_fill=(0, 0, 0), spacing=spacing)

def title_img():
    im = Image.new("RGBA", (W, 330), (0, 0, 0, 0))
    f = F(BLK, 92); d = ImageDraw.Draw(im)
    w1 = d.textlength("PALING TERUK ", font=f); w2 = d.textlength("UNTUK", font=f); x = (W - w1 - w2) / 2
    shadow_text(im, (W / 2, 70), "MAKANAN MALAYSIA", f, WHITE)
    shadow_text(im, (x, 185), "PALING TERUK", f, (255, 45, 45), anchor="lm")
    shadow_text(im, (x + w1, 185), "UNTUK", f, WHITE, anchor="lm")
    shadow_text(im, (W / 2, 280), "LEMAK PERUT", F(BLK, 92), (255, 214, 10))
    return im

def row_img(name, col, tcol, foods):
    rh = 200; im = Image.new("RGBA", (W, rh + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([40, 10, 300, 10 + rh], 26, fill=col, outline=(0, 0, 0), width=4)
    fs = 44 if "\n" in name and max(len(l) for l in name.split("\n")) > 8 else 52
    d.multiline_text((170, 10 + rh / 2), name, font=F(BLK, fs if len(name) < 14 else 32), fill=tcol, anchor="mm", align="center", spacing=4)
    for i, food in enumerate(foods):
        cx, cy = 320 + (i % 2) * 365, 10 + (i // 2) * 103
        d.rounded_rectangle([cx, cy, cx + 350, cy + 94], 20, fill=(15, 15, 20, 215), outline=col + (255,), width=3)
        f = F(XB, 40)
        while d.textlength(food, font=f) > 320: f = F(XB, f.size - 2)
        d.text((cx + 175, cy + 47), food, font=f, fill=WHITE, anchor="mm")
    return im

TITLE = title_img(); ROWS = [row_img(*t) for t in TIERS]
cta = Image.new("RGBA", (W, 140), (0, 0, 0, 0)); d = ImageDraw.Draw(cta)
d.rounded_rectangle([110, 15, W - 110, 125], 55, fill=(225, 30, 40))
d.text((W / 2, 70), "Nak makan tanpa rasa bersalah? DM “CANTIK”", font=F(BLK, 38), fill=WHITE, anchor="mm")

enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a", "-shortest",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
def put(base, im, x, y, a):
    if a <= 0: return
    if a < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x, y = int(x), int(y); im = im.crop((max(0, -x), 0, min(im.width, W - x), im.height)); base.alpha_composite(im, (max(0, x), y))
for n in range(int(DUR * FPS)):
    t = n / FPS; img = bg(t)
    p = ease(t / 0.5); put(img, TITLE, 0, 150 - 30 * (1 - p), p)
    for i, r in enumerate(ROWS):
        at = 0.6 + i * 0.45; p = ease((t - at) / 0.45)
        if t >= at: put(img, r, 160 * (1 - p), 520 + i * 222, p)
    p = ease((t - 3.2) / 0.4); put(img, cta, 0, 1650 + 30 * (1 - p), p)
    enc.stdin.write(img.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); print("->", OUT)
