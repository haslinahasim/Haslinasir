"""Buah ikut kandungan gula: rows drop in top to bottom on a plain background, then CTA."""
import os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, OUT = 1080, 1920, 30, "reel-buah-ikut-gula.mp4"
BLK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
XB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
BD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
PF = "/root/.fonts/Playfair_Display_wght_800_.woff2"
GV = "/root/.fonts/Great_Vibes_.woff2"
F = lambda p, s: ImageFont.truetype(p, s)
WHITE, GOLD, PINK, INK = (255, 255, 255), (255, 214, 120), (255, 160, 190), (20, 20, 24)
ease = lambda v: 1 - (1 - min(max(v, 0), 1)) ** 3
def back(v):
    v = min(max(v, 0), 1); c1 = 1.6; return 1 + (c1 + 1) * (v - 1) ** 3 + c1 * (v - 1) ** 2

TIERS = [("SANGAT TINGGI", "50g+", (225, 35, 40), WHITE, ["Kurma", "Kismis", "Mangga Kering", "Kranberi Kering"]),
         ("TINGGI", "14–19g", (245, 125, 25), WHITE, ["Nangka", "Anggur", "Laici", "Mangga"]),
         ("SEDERHANA", "10–12g", (250, 210, 25), INK, ["Pisang", "Blueberi", "Epal", "Nanas"]),
         ("RENDAH", "6–9g", (125, 210, 60), INK, ["Oren", "Jambu Batu", "Betik", "Tembikai"]),
         ("PALING RENDAH", "bawah 5g", (35, 165, 75), WHITE, ["Strawberi", "Raspberi", "Belimbing", "Avokado"])]

# plain background: soft charcoal gradient with a gentle glow
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
base = np.zeros((H, W, 3), np.float32); base[...] = (24, 22, 28)
g = np.exp(-(((xx - W / 2) / 700) ** 2 + ((yy - 700) / 900) ** 2))[..., None] * np.array([40, 30, 40])
BG = Image.fromarray(np.clip(base + g, 0, 255).astype(np.uint8)).convert("RGBA")

def shadow_text(im, xy, t, f, fill, anchor="mm", stroke=0):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0], xy[1] + 5), t, font=f, fill=(0, 0, 0, 220), anchor=anchor, stroke_width=stroke + 3, stroke_fill=(0, 0, 0, 220))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7))); ImageDraw.Draw(im).text(xy, t, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))

def title():
    im = Image.new("RGBA", (W, 330), (0, 0, 0, 0)); cx = (W - 60) / 2
    shadow_text(im, (cx, 70), "BUAH IKUT", F(BLK, 86), WHITE)
    shadow_text(im, (cx, 175), "KANDUNGAN GULA", F(BLK, 96), (240, 50, 50))
    shadow_text(im, (cx, 262), "(anggaran gula setiap 100g)", F(XB, 38), (220, 220, 225))
    return im

def fruit_pic(name, col, size=150):
    path = f"gambar-buah/{name}.png"
    p = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS) if os.path.exists(path) else Image.new("RGBA", (size, size), (235, 235, 235, 255))
    m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).ellipse([0, 0, size - 1, size - 1], fill=255); p.putalpha(m)
    out = Image.new("RGBA", (size + 30, size + 30), (0, 0, 0, 0)); sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([8, 14, size + 22, size + 28], fill=(0, 0, 0, 160)); out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
    ImageDraw.Draw(out).ellipse([6, 6, size + 23, size + 23], fill=col); out.alpha_composite(p, (15, 15)); return out

def row(label, grams, col, tcol, fruits):
    rh = 240; im = Image.new("RGBA", (W, rh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([40, 30, 262, 200], 28, fill=col, outline=(0, 0, 0), width=4)
    f1 = F(BLK, 40)
    while d.textlength(label, font=f1) > 200: f1 = F(BLK, f1.size - 2)
    if " " in label and d.textlength(label, font=F(BLK, 40)) > 200:
        a, b = label.split(" ", 1); d.text((151, 82), a, font=F(BLK, 38), fill=tcol, anchor="mm"); d.text((151, 120), b, font=F(BLK, 38), fill=tcol, anchor="mm"); gy = 165
    else: d.text((151, 95), label, font=f1, fill=tcol, anchor="mm"); gy = 150
    d.text((151, gy), grams, font=F(BLK, 40), fill=tcol, anchor="mm")
    for k, fr in enumerate(fruits):
        cx = 272 + k * 182 + 91
        pic = fruit_pic(fr, col); im.alpha_composite(pic, (int(cx - pic.width / 2), 0))
        f = F(BLK, 28)
        if ImageDraw.Draw(im).textlength(fr, font=f) > 170 and " " in fr:
            a, b = fr.split(" ", 1); shadow_text(im, (cx, 193), a, F(BLK, 26), WHITE); shadow_text(im, (cx, 222), b, F(BLK, 26), WHITE)
        else: shadow_text(im, (cx, 200), fr, f, WHITE)
    return im

def cta():
    im = Image.new("RGBA", (W, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(im); cx = (W - 60) / 2
    d.rounded_rectangle([110, 10, W - 170, 550], 46, fill=(36, 20, 30, 235), outline=GOLD + (170,), width=3)
    d.text((cx, 95), "Makan buah pun", font=F(PF, 64), fill=WHITE, anchor="mm")
    d.text((cx, 175), "boleh turun berat!", font=F(PF, 64), fill=WHITE, anchor="mm")
    g = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).text((cx, 285), "Nak saya bantu?", font=F(GV, 100), fill=PINK + (190,), anchor="mm")
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(12))); d = ImageDraw.Draw(im)
    d.text((cx, 285), "Nak saya bantu?", font=F(GV, 100), fill=PINK, anchor="mm")
    d.rounded_rectangle([cx - 230, 400, cx + 230, 484], 42, fill=(225, 30, 40))
    d.text((cx, 443), "DM “CANTIK”", font=F(BLK, 50), fill=WHITE, anchor="mm")
    return im

TITLE = title(); ROWS = [row(*t) for t in TIERS]; CTA = cta()
NOTE = Image.new("RGBA", (W, 60), (0, 0, 0, 0)); shadow_text(NOTE, ((W - 60) / 2, 30), "Nilai anggaran gula semula jadi. Kawal porsi setiap hari.", F(BD, 26), (200, 200, 205))

def paste(base, im, x, y, a=1.0):
    if a < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x, y = int(x), int(y); l, t = max(0, -x), max(0, -y); r, b = min(im.width, W - x), min(im.height, H - y)
    if r > l and b > t: base.alpha_composite(im.crop((l, t, r, b)), (x + l, y + t))

T_ROW0, STEP, LIST_END, TOTAL = 1.0, 1.5, 11.5, 15.5
enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a", "-shortest",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for n in range(int(TOTAL * FPS)):
    t = n / FPS; img = BG.copy()
    out = ease((LIST_END - t) / 0.4)
    p = ease(t / 0.5); paste(img, TITLE, 0, 130 - 40 * (1 - p), p * (out if t < LIST_END else 0))
    if t < LIST_END:
        for i, r in enumerate(ROWS):
            at = T_ROW0 + i * STEP
            if t < at: break
            p = back((t - at) / 0.55)
            paste(img, r, 0, 455 + i * 234 - 160 * (1 - min(p, 1)), min(1, ease((t - at) / 0.3)) * out)   # drops in from above
        paste(img, NOTE, 0, 1625, ease((t - T_ROW0 - 4 * STEP - 0.5) / 0.5) * out)
    else:
        p = back((t - LIST_END) / 0.6); paste(img, CTA, 0, 680 - 60 * (1 - min(p, 1)), ease((t - LIST_END) / 0.4))
    enc.stdin.write(img.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); print("->", OUT)
