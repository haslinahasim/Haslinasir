"""Original Malay explainer: what menopause does to the body (facts from published studies)."""
import subprocess, math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
OUT = "reel-menopaus.mp4"
FD = "/usr/share/fonts/opentype/inter/"
BLK, XB, BD = FD + "InterDisplay-Black.otf", FD + "InterDisplay-ExtraBold.otf", FD + "InterDisplay-Bold.otf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
YEL, PINK, CREAM, WHITE, GREY, BLUE, GRN = (255, 214, 10), (255, 95, 140), (243, 214, 150), (255, 255, 255), (165, 165, 175), (110, 170, 255), (60, 205, 120)
F = {}
def font(p, s):
    if (p, s) not in F: F[(p, s)] = ImageFont.truetype(p, s)
    return F[(p, s)]
ease = lambda x: 1 - (1 - min(max(x, 0), 1)) ** 3
X0 = 90; TW = W - 2 * X0

# ---------- background: deep plum gradient with a slow moving glow ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
BASE = np.zeros((H, W, 3), np.float32); BASE[..., 0] = 22 + 10 * yy / H; BASE[..., 1] = 14 + 4 * yy / H; BASE[..., 2] = 30 + 8 * yy / H
def background(t):
    cx, cy = W * (0.5 + 0.25 * math.sin(t / 5)), H * (0.42 + 0.08 * math.cos(t / 7))
    g = np.exp(-(((xx - cx) / 650) ** 2 + ((yy - cy) / 800) ** 2))[..., None]
    img = BASE + g * np.array([70, 22, 48], np.float32)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")

# ---------- drawing helpers (all take alpha a and slide p) ----------
def wrap(d, txt, f, width):
    out, line = [], ""
    for w in txt.split():
        if d.textlength((line + " " + w).strip(), font=f) <= width: line = (line + " " + w).strip()
        else: out.append(line); line = w
    return out + [line]

def layer_text(img, xy, txt, f, fill, a, anchor="la", width=TW, lh=1.18, rich=None):
    """Draw (wrapped) text with soft shadow. rich: list of (word, color) to colour single words."""
    if a <= 0: return xy[1]
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    lines = wrap(d, txt, f, width); x, y = xy; step = int(f.size * lh)
    for i, ln in enumerate(lines):
        yy_ = y + i * step
        if anchor == "ma": lx = x - d.textlength(ln, font=f) / 2
        else: lx = x
        for w in ln.split(" "):
            col = fill
            for rw, rc in (rich or []):
                if w.strip(".,!?:").lower() == rw.lower(): col = rc
            d.text((lx, yy_), w, font=f, fill=col)
            lx += d.textlength(w + " ", font=f)
    bb = lay.getbbox()
    if bb:
        bx = (max(0, bb[0] - 20), max(0, bb[1] - 20), min(W, bb[2] + 20), min(H, bb[3] + 20)); lay = lay.crop(bx)
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.7)))
        combo = Image.alpha_composite(sh, lay)
        if a < 1: combo.putalpha(combo.getchannel("A").point(lambda v: int(v * a)))
        img.alpha_composite(combo, (bx[0], bx[1]))
    return y + len(lines) * step

def rbox(img, box, a, fill=(255, 255, 255, 18), outline=None, r=28):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle(box, r, fill=fill[:3] + (int(fill[3] * a),), outline=None if not outline else outline[:3] + (int(255 * a),), width=3)
    img.alpha_composite(lay)

def fade_in(t, at, d=0.45): return ease((t - at) / d)
def slide(t, at, dist=40, d=0.45): return int(dist * (1 - ease((t - at) / d)))

def label(img, t, at, txt, y, color=YEL):
    a = fade_in(t, at); layer_text(img, (X0, y + slide(t, at)), txt.upper(), font(XB, 40), color, a)

def source(img, t, at, txt):
    layer_text(img, (X0, 1560), "Sumber: " + txt, font(BD, 30), GREY, fade_in(t, at) * 0.95, width=TW)

def counter(t, at, val, d=1.2, dec=0):
    v = val * ease((t - at) / d)
    return f"{v:,.{dec}f}" if dec else f"{int(round(v)):,}"

# ---------- scenes: each is (duration, draw(img, t)) ----------
def s_hook(img, t):
    label(img, t, 0.1, "Kajian 1 juta wanita", 420)
    a = fade_in(t, 0.3)
    layer_text(img, (X0, 500 + slide(t, 0.3)), "Menopaus ubah", font(BLK, 104), WHITE, a)
    layer_text(img, (X0, 640), counter(t, 0.6, 52, 1.0), font(BLK, 300), YEL, fade_in(t, 0.6))
    layer_text(img, (X0 + 380, 760), "/ 90", font(BLK, 150), WHITE, fade_in(t, 0.8))
    layer_text(img, (X0, 1000 + slide(t, 1.2)), "ujian kesihatan", font(BLK, 92), WHITE, fade_in(t, 1.2))
    layer_text(img, (X0, 1110 + slide(t, 1.6)), "serentak.", font(SERIF, 120), PINK, fade_in(t, 1.6))
    layer_text(img, (X0, 1340 + slide(t, 2.3)), "Ini apa yang berlaku pada badan wanita ↓", font(XB, 50), CREAM, fade_in(t, 2.3))

def s_data(img, t):
    label(img, t, 0.1, "Kajian terbesar setakat ini", 360)
    layer_text(img, (X0, 440), counter(t, 0.3, 300, 1.0) + " JUTA", font(BLK, 170), YEL, fade_in(t, 0.3))
    layer_text(img, (X0, 650 + slide(t, 0.7)), "keputusan ujian makmal daripada lebih 1 juta wanita.", font(XB, 64), WHITE, fade_in(t, 0.7))
    rbox(img, (X0 - 10, 900, W - X0 + 10, 1240), fade_in(t, 1.6), (255, 95, 140, 40))
    layer_text(img, (X0 + 30, 930 + slide(t, 1.6)), "Disusun ikut tarikh haid terakhir,", font(XB, 58), WHITE, fade_in(t, 1.6), width=TW - 60)
    layer_text(img, (X0 + 30, 1090 + slide(t, 2.0)), "bukan ikut umur.", font(SERIF, 86), PINK, fade_in(t, 2.0), width=TW - 60)
    source(img, t, 0.5, "Pridham 2026, Nature Medicine")

def s_dots(img, t):
    label(img, t, 0.1, "Sebaik haid berhenti", 330)
    layer_text(img, (X0, 400 + slide(t, 0.2)), "52 daripada 90 ujian melonjak.", font(BLK, 68), WHITE, fade_in(t, 0.2), rich=[("52", YEL)])
    lay = ImageDraw.Draw(img); n = int(52 * ease((t - 0.8) / 2.2)) if t > 0.8 else 0
    for row, (name, col, lit) in enumerate([("WANITA", PINK, n), ("LELAKI", BLUE, 0)]):
        y0 = 720 + row * 400; a = fade_in(t, 0.5 + row * 0.3)
        layer_text(img, (X0, y0 - 70), name, font(XB, 44), col, a)
        num = f"{lit} / 90" if row == 0 else "0 / 90"
        layer_text(img, (W - X0 - 260, y0 - 80), num, font(BLK, 56), col if (row == 0 and lit) else GREY, a)
        for k in range(90):
            cx, cy = X0 + 20 + (k % 15) * 64, y0 + 20 + (k // 15) * 52
            on = k < lit; c = col if on else (90, 80, 100)
            lay.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=c + (int(255 * a),))
    layer_text(img, (X0, 1460 - 20 + slide(t, 3.2)), "Lelaki sebaya? Tiada lonjakan.", font(XB, 58), CREAM, fade_in(t, 3.2))
    source(img, t, 0.5, "Pridham 2026, Nature Medicine")

def item_rows(img, t, at, rows, y, gap=1.0, size=60, rh=110):
    for i, (icon, txt, col) in enumerate(rows):
        a = fade_in(t, at + i * gap); yy_ = y + i * rh + slide(t, at + i * gap)
        if a <= 0: continue
        d = ImageDraw.Draw(img)
        d.ellipse([X0, yy_ + 4, X0 + 72, yy_ + 76], fill=col + (int(255 * a),))
        d.text((X0 + 36, yy_ + 40), icon, font=font(BLK, 46), fill=(25, 15, 30, int(255 * a)), anchor="mm")
        layer_text(img, (X0 + 100, yy_ + 2), txt, font(XB, size), WHITE, a, width=TW - 100)

def s_year1(img, t):
    label(img, t, 0.1, "1 tahun selepas haid terakhir", 330)
    layer_text(img, (X0, 400 + slide(t, 0.2)), "Apa yang berubah?", font(BLK, 90), WHITE, fade_in(t, 0.2))
    item_rows(img, t, 0.8, [("↓", "Tulang makin nipis (semua bahagian)", PINK),
                            ("↑", "Kolesterol LDL naik", PINK), ("↑", "Enzim hati naik", PINK),
                            ("↑", "Natrium darah naik", PINK), ("=", "Gula darah tak melonjak", GRN)], 590, gap=0.8, size=56, rh=165)
    source(img, t, 0.5, "Pridham 2026, Nature Medicine")

def s_systems(img, t):
    label(img, t, 0.1, "Daripada 14 sistem badan", 330)
    layer_text(img, (X0, 400 + slide(t, 0.2)), "5 menua lebih cepat pada wanita:", font(BLK, 80), WHITE, fade_in(t, 0.2), rich=[("5", YEL)])
    words = ["Lemak darah", "Tulang", "Buah pinggang", "Hati", "Tidur"]
    for i, w in enumerate(words):
        at = 1.0 + i * 0.5; a = fade_in(t, at); f = font(XB, 60); d = ImageDraw.Draw(img)
        tw = d.textlength(w, font=f)
        if i == 0: s_systems.pos = [X0, 690]
        x, y0 = s_systems.pos
        if x + tw + 60 > W - X0: x, y0 = X0, y0 + 140
        s_systems.pos = [x + tw + 80, y0]; y = y0 + slide(t, at)
        rbox(img, (x, y, x + tw + 60, y + 110), a, PINK + (230,), r=55)
        layer_text(img, (x + 30, y + 22), w, f, WHITE, a)
    rbox(img, (X0 - 10, 1180, W - X0 + 10, 1380), fade_in(t, 3.8), (110, 170, 255, 45))
    layer_text(img, (X0 + 30, 1210 + slide(t, 3.8)), "Lelaki? Hanya 1: kerapuhan badan.", font(XB, 56), WHITE, fade_in(t, 3.8), width=TW - 60, rich=[("1:", BLUE)])
    source(img, t, 0.5, "Reicher 2024, Nature Aging")

def bar(img, x, y, w, h, frac, col, a):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x, y, x + w, y + h], h // 2, fill=(255, 255, 255, int(30 * a)))
    if frac > 0.02: d.rounded_rectangle([x, y, x + int(w * frac), y + h], h // 2, fill=col + (int(255 * a),))

def s_insulin(img, t):
    label(img, t, 0.1, "Rintangan insulin", 330)
    layer_text(img, (X0, 400 + slide(t, 0.2)), "Tak melonjak. Tapi naik perlahan-lahan.", font(BLK, 78), WHITE, fade_in(t, 0.2))
    rows = [("Sebelum", 1.0, "~1%", GREY), ("4 tahun sekitar haid terakhir", 4.3, "4.3%", PINK), ("Selepas", 1.0, "~1%", GREY)]
    for i, (nm, v, s, col) in enumerate(rows):
        at = 1.0 + i * 0.7; a = fade_in(t, at); y = 720 + i * 220
        layer_text(img, (X0, y), nm, font(XB, 50), CREAM if i == 1 else WHITE, a)
        bar(img, X0, y + 80, 640, 60, v / 4.6 * ease((t - at) / 1.0), col, a)
        layer_text(img, (X0 + 680, y + 62), s, font(BLK, 76), col if i == 1 else WHITE, a)
    layer_text(img, (X0, 1400 + slide(t, 3.6)), "setahun", font(SERIF, 70), PINK, fade_in(t, 3.6))
    source(img, t, 0.5, "Karlamangla 2026, JCI Insight (SWAN, 1,315 wanita)")

def s_visceral(img, t):
    label(img, t, 0.1, "Lemak yang tak nampak", 330)
    layer_text(img, (X0, 400 + slide(t, 0.2)), "Lemak di sekeliling organ naik", font(BLK, 82), WHITE, fade_in(t, 0.2))
    layer_text(img, (X0, 640), "+" + counter(t, 0.8, 6, 0.9) + "%", font(BLK, 300), YEL, fade_in(t, 0.8))
    layer_text(img, (X0 + 20, 960), "setahun", font(SERIF, 90), CREAM, fade_in(t, 1.2))
    rbox(img, (X0 - 10, 1150, W - X0 + 10, 1380), fade_in(t, 2.4), (255, 95, 140, 40))
    layer_text(img, (X0 + 30, 1180 + slide(t, 2.4)), "Tapi berat badan tak naik lebih laju. Timbangan tak nampak perubahan ini.", font(XB, 54), WHITE, fade_in(t, 2.4), width=TW - 60)
    source(img, t, 0.5, "Greendale 2021, JCEM; Greendale 2019 (SWAN)")

def s_hrt(img, t):
    label(img, t, 0.1, "17 kajian klinikal", 330)
    layer_text(img, (X0, 400 + slide(t, 0.2)), "Terapi hormon kurangkan rintangan insulin.", font(BLK, 80), WHITE, fade_in(t, 0.2))
    for i, (nm, v, col) in enumerate([("Plasebo", 0.85, GREY), ("Terapi hormon", 0.55, PINK)]):
        at = 1.2 + i * 0.5; a = fade_in(t, at); y = 760 + i * 190
        layer_text(img, (X0, y), nm, font(XB, 50), WHITE, a)
        bar(img, X0, y + 75, TW, 60, v * ease((t - at) / 1.0), col, a)
    rbox(img, (X0 - 10, 1180, W - X0 + 10, 1400), fade_in(t, 3.0), (255, 214, 10, 40))
    layer_text(img, (X0 + 30, 1210 + slide(t, 3.0)), "Tapi 10 tahun selepas berhenti, bezanya hilang.", font(XB, 58), WHITE, fade_in(t, 3.0), width=TW - 60, rich=[("hilang.", YEL)])
    source(img, t, 0.5, "Li 2025, Climacteric; KEEPS (Kantarci 2024)")

def s_train(img, t):
    label(img, t, 0.1, "Apa yang membantu?", 330)
    layer_text(img, (X0, 400 + slide(t, 0.2)), "Latihan berat, 3 kali seminggu.", font(BLK, 86), WHITE, fade_in(t, 0.2), rich=[("berat,", YEL)])
    for i, (nm, v, sub, col) in enumerate([("Lemak perut", "−1.5 kg", "senaman ringan: +0.1 kg", PINK), ("Otot", "+0.4 kg", "senaman ringan: −0.4 kg", GRN)]):
        at = 1.0 + i * 0.6; a = fade_in(t, at); x = X0 + i * 470
        rbox(img, (x, 720, x + 430, 1120), a, (255, 255, 255, 22))
        layer_text(img, (x + 30, 750 + slide(t, at)), nm, font(XB, 48), CREAM, a, width=380)
        layer_text(img, (x + 30, 850), v, font(BLK, 92), col, a, width=400)
        layer_text(img, (x + 30, 1010), sub, font(BD, 34), GREY, a, width=380)
    layer_text(img, (X0, 1220 + slide(t, 2.6)), "Dalam 13 bulan, untuk wanita yang dah menopaus.", font(XB, 52), WHITE, fade_in(t, 2.6))
    source(img, t, 0.5, "Hettchen 2021, kajian ACTLIFE (54 wanita)")

def s_lift(img, t):
    label(img, t, 0.1, "Angkat berat untuk tulang", 330)
    item_rows(img, t, 0.4, [("5", "5 set × 5 ulangan", YEL), ("%", "85% beban maksimum", YEL),
                            ("2", "2 kali seminggu", YEL), ("✓", "Dengan pengawasan jurulatih", YEL)], 420, gap=0.5, size=56, rh=125)
    layer_text(img, (X0, 920), "+" + counter(t, 2.4, 2.9, 1.0, 1) + "%", font(BLK, 250), GRN, fade_in(t, 2.4))
    layer_text(img, (X0, 1200), "ketumpatan tulang belakang dalam 8 bulan", font(XB, 54), WHITE, fade_in(t, 2.8))
    layer_text(img, (X0, 1360), "Senaman ringan: −1.2%", font(XB, 50), GREY, fade_in(t, 3.4))
    source(img, t, 0.5, "Watson 2018, JBMR (LIFTMOR, 101 wanita); Kemmler 2021")

def s_end(img, t):
    layer_text(img, (W / 2, 470 + slide(t, 0.1)), "Menopaus bukan penamat.", font(BLK, 74), WHITE, fade_in(t, 0.1), anchor="ma", width=W - 40)
    layer_text(img, (W / 2, 600 + slide(t, 0.5)), "Mula jaga badan dari sekarang.", font(SERIF, 70), CREAM, fade_in(t, 0.5), anchor="ma", width=W - 40)
    a = fade_in(t, 1.1)
    rbox(img, (130, 860, W - 130, 1300), a, (20, 12, 24, 230), r=40)
    layer_text(img, (W / 2, 900), "Nak bimbingan pemakanan & senaman?", font(XB, 52), WHITE, a, anchor="ma", width=W - 340)
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0)); ImageDraw.Draw(glow).rounded_rectangle([270, 1110, W - 270, 1230], 60, fill=(230, 30, 40, int(200 * a)))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(img); d.rounded_rectangle([280, 1115, W - 280, 1225], 55, fill=(225, 30, 40, int(255 * a)))
    d.text((360, 1170), "DM", font=font(BLK, 36), fill=(255, 220, 220, int(255 * a)), anchor="mm")
    d.text((W / 2 + 45, 1170), "“CANTIK”", font=font(BLK, 66), fill=(255, 255, 255, int(255 * a)), anchor="mm")
    layer_text(img, (W / 2, 1420), "Maklumat umum, bukan nasihat perubatan. Rujuk doktor anda.", font(BD, 30), GREY, fade_in(t, 1.6), anchor="ma")

SCENES = [(4.5, s_hook), (5.0, s_data), (5.5, s_dots), (6.0, s_year1), (5.8, s_systems), (5.5, s_insulin),
          (5.0, s_visceral), (5.0, s_hrt), (5.5, s_train), (5.5, s_lift), (4.5, s_end)]

enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a", "-shortest",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
import sys
PREVIEW = [float(x) for x in sys.argv[1:]]
T = 0.0; total = sum(d for d, _ in SCENES); n = 0
for si, (dur, fn) in enumerate(SCENES):
    for k in range(int(dur * FPS)):
        t = k / FPS; img = background(n / FPS)
        sc = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fn(sc, t)
        a = min(ease(t / 0.25) if si else 1, ease((dur - t) / 0.25) if si < len(SCENES) - 1 else 1)   # crossfade between scenes
        if a < 1: sc.putalpha(sc.getchannel("A").point(lambda v: int(v * a)))
        img.alpha_composite(sc)
        prog = (n + 1) / (total * FPS); d = ImageDraw.Draw(img)   # thin progress bar at top
        d.rectangle([0, 0, int(W * prog), 8], fill=PINK + (255,))
        enc.stdin.write(img.convert("RGB").tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n, "dur", round(n / FPS, 1), "->", OUT)
