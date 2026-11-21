"""7 sarapan yang sukarkan turun berat: list reel with food photos, TPFM pro style."""
import subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
OUT = "reel-7-sarapan.mp4"
FD = "/usr/share/fonts/opentype/inter/"
BLK, XB, BD = FD + "InterDisplay-Black.otf", FD + "InterDisplay-ExtraBold.otf", FD + "InterDisplay-Bold.otf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
RED, WHITE, GREY, GOLD, GRN = (226, 32, 48), (255, 255, 255), (195, 195, 202), (245, 200, 90), (60, 200, 110)
F = lambda p, s: ImageFont.truetype(p, s)
ease = lambda v: 1 - (1 - min(max(v, 0), 1)) ** 3
def back(v):
    v = min(max(v, 0), 1); c1 = 1.6; return 1 + (c1 + 1) * (v - 1) ** 3 + c1 * (v - 1) ** 2

ITEMS = [("Kuih-Muih", "Tinggi gula & minyak, cepat lapar semula"),
         ("Cereals", "Banyak gula tambahan, protein sangat sedikit"),
         ("Air Manis + Roti Kosong", "Gula + karbohidrat ringkas, gula darah melonjak"),
         ("Nasi Lemak Kosong / Bihun / Mee Goreng", "Kalori & minyak tinggi, hampir tiada protein"),
         ("Mee Kari", "Santan & minyak — kalori tinggi dalam satu mangkuk"),
         ("Sosej & Nugget", "Daging proses, tinggi garam & lemak"),
         ("Biskut", "Tepung putih & gula, kenyang sekejap saja")]

# ---------- background (same family as the TPFM promo) ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
base = np.zeros((H, W, 3), np.float32); base[..., 0] = 14 + 10 * yy / H; base[..., 1] = 12 + 2 * yy / H; base[..., 2] = 16 + 4 * yy / H
g = np.exp(-(((xx - W * .8) / 700) ** 2 + ((yy - 300) / 600) ** 2))[..., None] * np.array([110, 12, 25])
g2 = np.exp(-(((xx - W * .1) / 600) ** 2 + ((yy - 1700) / 600) ** 2))[..., None] * np.array([70, 8, 18])
BG = Image.fromarray(np.clip(base + g + g2, 0, 255).astype(np.uint8)).convert("RGBA")
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
for k in range(-6, 14): d.line([(k * 160, 0), (k * 160 + 900, H)], fill=(255, 255, 255, 7), width=2)
BG = Image.alpha_composite(BG, ov)

def paste(base, im, x, y, a=1.0, sc=1.0):
    if sc != 1.0:
        w0, h0 = im.width, im.height; im = im.resize((max(1, int(w0 * sc)), max(1, int(h0 * sc))), Image.LANCZOS); x += (w0 - im.width) / 2; y += (h0 - im.height) / 2
    if a < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x, y = int(x), int(y); l, t = max(0, -x), max(0, -y); r, b = min(im.width, W - x), min(im.height, H - y)
    if r > l and b > t: base.alpha_composite(im.crop((l, t, r, b)), (x + l, y + t))

def bar():
    im = Image.new("RGBA", (W, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(im); f = F(XB, 28); t = "TEAM POWERFIT MALAYSIA"; w = d.textlength(t, font=f)
    d.rounded_rectangle([60, 40, 60 + w + 70, 92], 26, fill=RED); d.ellipse([78, 58, 94, 74], fill=WHITE); d.text((108, 66), t, font=f, fill=WHITE, anchor="lm")
    d.text((W - 60, 66), "PROGRAM COACHING TPFM", font=F(BD, 26), fill=GREY, anchor="rm"); return im
BAR = bar()

def title():
    im = Image.new("RGBA", (W, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((70, 10), "7", font=F(BLK, 190), fill=RED)
    d.text((215, 30), "SARAPAN", font=F(BLK, 84), fill=WHITE)
    d.text((215, 120), "sukarkan proses", font=F(SERIF, 66), fill=GOLD)
    d.text((70, 215), "TURUN BERAT", font=F(BLK, 84), fill=WHITE)
    w = d.textlength("TURUN BERAT", font=F(BLK, 84)); d.line([(70, 296), (70 + w, 296)], fill=RED, width=6)
    return im
TITLE = title()

def photo(i, size):
    p = Image.open(f"food/{i + 1}.png").convert("RGBA").resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).ellipse([0, 0, size - 1, size - 1], fill=255); p.putalpha(m)
    out = Image.new("RGBA", (size + 40, size + 40), (0, 0, 0, 0)); sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([16, 26, size + 24, size + 34], fill=(0, 0, 0, 170)); out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(out).ellipse([14, 14, size + 26, size + 26], fill=RED); out.alpha_composite(p, (20, 20)); return out

def row(i, name, why):
    rh = 186; im = Image.new("RGBA", (W, rh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([50, 8, W - 50, rh - 8], 34, fill=(255, 255, 255, 16), outline=(255, 255, 255, 30), width=2)
    ph = photo(i, 150); im.alpha_composite(ph, (64, (rh - ph.height) // 2))
    d.ellipse([60, 14, 118, 72], fill=GOLD); d.text((89, 44), str(i + 1), font=F(BLK, 36), fill=(25, 20, 20), anchor="mm")
    x0 = 270; fn = F(BLK, 46)
    while d.textlength(name, font=fn) > W - 150 - x0: fn = F(BLK, fn.size - 2)
    d.text((x0, 52), name, font=fn, fill=WHITE, anchor="lm")
    fw = F(BD, 32)
    while d.textlength(why, font=fw) > W - 80 - x0: fw = F(BD, fw.size - 1)
    d.text((x0, 112), why, font=fw, fill=GREY, anchor="lm")
    cx, cy = W - 105, 52; d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=RED)
    d.line([(cx - 10, cy - 10), (cx + 10, cy + 10)], fill=WHITE, width=6); d.line([(cx - 10, cy + 10), (cx + 10, cy - 10)], fill=WHITE, width=6)
    return im
ROWS = [row(i, n, w) for i, (n, w) in enumerate(ITEMS)]

def tip():
    im = Image.new("RGBA", (W, 760), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((W / 2, 70), "Nak tahu sarapan", font=F(BLK, 80), fill=WHITE, anchor="mm")
    d.text((W / 2, 175), "yang bagus untuk diet?", font=F(SERIF, 84), fill=GOLD, anchor="mm")
    d.line([(W / 2 - 70, 260), (W / 2 + 70, 260)], fill=RED, width=6)
    d.text((W / 2, 360), "Komen", font=F(BD, 56), fill=GREY, anchor="mm")
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(glow).rounded_rectangle([230, 420, W - 230, 580], 80, fill=(230, 30, 40, 200))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(20))); d = ImageDraw.Draw(im)
    d.rounded_rectangle([240, 425, W - 240, 575], 75, fill=RED)
    d.text((W / 2, 500), "\u201cPART 2\u201d", font=F(BLK, 96), fill=WHITE, anchor="mm")
    # small comment bubble icon
    d.rounded_rectangle([W / 2 - 50, 640, W / 2 + 50, 710], 20, fill=(255, 255, 255, 40)); d.polygon([(W / 2 - 20, 708), (W / 2 - 34, 735), (W / 2 + 2, 708)], fill=(255, 255, 255, 40))
    for k in range(3): d.ellipse([W / 2 - 28 + k * 22, 669, W / 2 - 16 + k * 22, 681], fill=WHITE)
    return im
TIP = tip()

T0, STEP, HOLD, TIPD = 1.2, 2.4, 2.0, 5.0
TL = T0 + STEP * len(ITEMS) + HOLD; TOTAL = TL + TIPD
enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a", "-shortest",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for n in range(int(TOTAL * FPS)):
    t = n / FPS; img = BG.copy(); paste(img, BAR, 0, 0)
    if t < TL:
        out = ease((TL - t) / 0.3)
        p = back(t / 0.6); paste(img, TITLE, 0, 150 + 30 * (1 - min(p, 1)), min(1, ease(t / 0.4)) * out)
        for i, r in enumerate(ROWS):
            at = T0 + i * STEP
            if t < at: break
            p = back((t - at) / 0.5); act = (at <= t < at + STEP) and i < len(ROWS)
            sc = 0.92 + 0.08 * min(p, 1) + (0.03 * (1 - ease((t - at - 1.4) / 0.6)) if act else 0)
            paste(img, r, 140 * (1 - min(p, 1)), 480 + i * 196, min(1, ease((t - at) / 0.35)) * out, sc)
    else:
        lt = t - TL; p = back(lt / 0.6)
        paste(img, TIP, 0, 520 + 40 * (1 - min(p, 1)), min(1, ease(lt / 0.4)), 0.94 + 0.06 * min(p, 1))
    dd = ImageDraw.Draw(img); dd.rectangle([0, H - 10, W, H], fill=(255, 255, 255, 25)); dd.rectangle([0, H - 10, int(W * t / TOTAL), H], fill=RED)
    enc.stdin.write(img.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); print("->", OUT, round(TOTAL, 1), "s")
