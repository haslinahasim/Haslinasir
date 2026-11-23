"""Creative cut: hook first, pauses removed, punch transitions, word captions, RM190 pop, CTA + income disclaimer."""
import json, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SRC, OUT = 1080, 1920, 30, "in.mov", "reel-peluang-income.mp4"
BLK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
XB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
BD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
PF = "/root/.fonts/Playfair_Display_wght_800_.woff2"
PFI = "/root/.fonts/Playfair_Display_ital_wght_1_700_.woff2"
GV = "/root/.fonts/Great_Vibes_.woff2"
F = lambda p, s: ImageFont.truetype(p, s)
WHITE, GOLD, GREEN = (255, 255, 255), (255, 214, 120), (80, 220, 130)
ease = lambda v: 1 - (1 - min(max(v, 0), 1)) ** 3
def back(v):
    v = min(max(v, 0), 1); c1 = 1.7; return 1 + (c1 + 1) * (v - 1) ** 3 + c1 * (v - 1) ** 2
CX = (W - 60) / 2
END = 3.0   # extra end card

# source segments kept, in the new order
SEGS = [(8.26, 10.5), (0.0, 4.36), (5.0, 7.66), (11.6, 19.6), (19.6, 24.4), (25.15, 29.45)]
ZOOM = [1.12, 1.0, 1.10, 1.0, 1.10, 1.0]
starts = []; acc = 0.0
for a, b in SEGS: starts.append(acc); acc += b - a
DUR = acc
def to_new(ts):
    for (a, b), s0 in zip(SEGS, starts):
        if a <= ts < b: return s0 + ts - a
    return None

# ---------- cut the video (with audio) ----------
fc = "".join(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={b - a - 0.04}:d=0.04[a{i}];" for i, (a, b) in enumerate(SEGS))
fc += "".join(f"[v{i}][a{i}]" for i in range(len(SEGS))) + f"concat=n={len(SEGS)}:v=1:a=1[v][a]"
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", SRC, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-c:a", "aac", "-b:a", "192k", "cut.mp4"], check=True)

# ---------- captions (word by word, groups of up to 4 words) ----------
words = json.load(open("in_words.json"))
FIX = {39: "sahaja", 43: "RM190", 67: "jalan-jalan", 68: "", 72: "info!"}
ACC = {6, 13, 16, 28, 29, 42, 43, 44, 57, 58, 62, 63, 65, 71, 72}
GROUPS = [(22, 26), (26, 30), (0, 4), (4, 7), (7, 11), (11, 14), (14, 17), (17, 21), (33, 37), (37, 42), (42, 45), (45, 48),
          (48, 53), (53, 56), (56, 59), (59, 64), (64, 66), (66, 71), (71, 73)]
disp = lambda i: FIX.get(i, words[i]["w"])
def cap_img(idx):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1))); parts = [(disp(i), i in ACC) for i in idx if disp(i)]
    size = 62
    while True:
        fw, fa = F(BLK, size), F(PFI, int(size * 1.12)); sp = 15
        tw = sum(d.textlength(t, font=fa if a else fw) for t, a in parts) + sp * (len(parts) - 1)
        if tw < 820 or size < 36: break
        size -= 2
    im = Image.new("RGBA", (int(tw) + 60, int(size * 2.3)), (0, 0, 0, 0)); sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ds, dd = ImageDraw.Draw(sh), ImageDraw.Draw(im); x = 30; base = int(size * 1.35)
    for t, a in parts:
        f = fa if a else fw
        ds.text((x, base + 3), t, font=f, fill=(0, 0, 0, 255), anchor="ls", stroke_width=7, stroke_fill=(0, 0, 0, 255))
        dd.text((x, base), t, font=f, fill=GOLD if a else WHITE, anchor="ls", stroke_width=2, stroke_fill=(0, 0, 0, 160)); x += d.textlength(t, font=f) + sp
    return Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)), im)
CAPS = []
for a, b in GROUPS:
    shown = [k for k in range(a, b) if disp(k)]
    g_end_src = words[b - 1]["e"] + 0.5
    for j, k in enumerate(shown):
        s_new = to_new(words[k]["s"] + 0.01)
        if s_new is None: continue
        nxt = words[shown[j + 1]]["s"] if j + 1 < len(shown) else g_end_src
        e_new = to_new(min(nxt, g_end_src) - 0.01) or (s_new + 0.6)
        CAPS.append((s_new, max(e_new, s_new + 0.15), cap_img(range(a, k + 1))))
CAPS.sort(key=lambda c: c[0])

# ---------- graphics ----------
def txt(t, font, col, glow=False):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1))); l, tp, r, b = d.textbbox((0, 0), t, font=font)
    pad = 40; im = Image.new("RGBA", (r - l + pad * 2, b - tp + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((pad - l, pad - tp + 5), t, font=font, fill=(0, 0, 0, 230), stroke_width=4, stroke_fill=(0, 0, 0, 230))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)))
    if glow:
        g = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).text((pad - l, pad - tp), t, font=font, fill=col + (200,))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(16)))
    ImageDraw.Draw(im).text((pad - l, pad - tp), t, font=font, fill=col); return im
HOOK = [(txt("PELUANG", F(PF, 96), WHITE), 300, 0.0), (txt("income", F(GV, 190), GOLD, True), 440, 0.3), (txt("dengan Herbalife", F(PFI, 62), WHITE), 575, 0.6)]
RM = txt("RM190", F(PF, 200), GOLD, True); RMSUB = txt("cash, pagi tadi!", F(GV, 96), WHITE, True)
RM_AT = to_new(16.2)

def cta():
    im = Image.new("RGBA", (W, 330), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([110, 8, W - 170, 320], 40, fill=(20, 12, 18, 215), outline=GOLD + (170,), width=3)
    d.text((CX, 62), "Nak extra income?", font=F(PF, 60), fill=WHITE, anchor="mm")
    g = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).text((CX, 150), "travel & jalan-jalan", font=F(GV, 84), fill=GOLD + (190,), anchor="mm")
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(12))); d = ImageDraw.Draw(im)
    d.text((CX, 150), "travel & jalan-jalan", font=F(GV, 84), fill=GOLD, anchor="mm")
    d.rounded_rectangle([CX - 210, 225, CX + 210, 295], 35, fill=(225, 30, 40))
    d.text((CX, 261), "DM “INFO”", font=F(BLK, 44), fill=WHITE, anchor="mm")
    return im
CTA, CTA_AT = cta(), starts[5]
def disclaimer():
    im = Image.new("RGBA", (W, 112), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([80, 4, W - 140, 108], 18, fill=(0, 0, 0, 170))
    f = F(BD, 22); cx = (W - 60) / 2
    lines = ["Penafian: Pendapatan ialah pengalaman individu & bukan jaminan.",
             "Hasil bergantung pada usaha, masa & kemahiran masing-masing.",
             "Rujuk Penyata Purata Pendapatan Kasar Herbalife."]
    for k, l in enumerate(lines): d.text((cx, 26 + k * 29), l, font=f, fill=(235, 235, 240), anchor="mm")
    return im
DISC = disclaimer()

def paste(base, im, cx, cy, a=1.0, sc=1.0):
    if sc != 1: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    if a < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x, y = int(cx - im.width / 2), int(cy - im.height / 2); l, t = max(0, -x), max(0, -y); r, b = min(im.width, W - x), min(im.height, H - y)
    if r > l and b > t: base.alpha_composite(im.crop((l, t, r, b)), (x + l, y + t))

dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", "cut.mp4", "-vf",
    f"fps={FPS},scale={W}:{H}:flags=lanczos,hqdn3d=1.5:1.5:4:4,unsharp=5:5:0.8,eq=contrast=1.05:saturation=1.08:brightness=0.02",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-i", "cut.mp4", "-map", "0:v", "-map", "1:a", "-af", f"loudnorm=I=-15:TP=-1.5,apad", "-t", str(DUR + END),
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
n, last = 0, None
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    t = n / FPS; fr = Image.frombytes("RGB", (W, H), raw)
    k = max(i for i, s in enumerate(starts) if s <= t); lt = t - starts[k]
    tr = max(0, 1 - lt / 0.3) if k > 0 else 0
    z = ZOOM[k] * (1 + 0.10 * tr ** 2)
    if z > 1.001:
        cw, ch = int(W / z), int(H / z); x0 = (W - cw) // 2; y0 = int((H - ch) * 0.35)
        fr = fr.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)
    if tr > 0.05:
        fr = Image.blend(fr.filter(ImageFilter.BoxBlur(int(12 * tr))), Image.new("RGB", (W, H), (255, 255, 255)), 0.5 * tr ** 2)
    img = fr.convert("RGBA"); clean = fr
    if t < starts[1]:
        for im, y, dl in HOOK:
            p = ease((t - dl) / 0.4); paste(img, im, CX, y + 25 * (1 - p), p * ease((starts[1] - t) / 0.25))
    if RM_AT and RM_AT <= t < RM_AT + 3.4:
        p = back((t - RM_AT) / 0.5); o = ease((RM_AT + 3.4 - t) / 0.3)
        paste(img, RM, CX, 520, min(1, ease((t - RM_AT) / 0.2)) * o, 0.6 + 0.4 * min(p, 1.1))
        paste(img, RMSUB, CX, 680, ease((t - RM_AT - 0.4) / 0.4) * o)
    if t >= CTA_AT:
        p = ease((t - CTA_AT) / 0.6); paste(img, CTA, W / 2, 210 + 165 + 30 * (1 - p), p, 0.95 + 0.05 * p)
    if t >= RM_AT:
        paste(img, DISC, W / 2, 1575, ease((t - RM_AT - 0.3) / 0.5))
    for a, b, im in CAPS:
        if a <= t < b:
            paste(img, im, CX, 1415, 1.0, 0.96 + 0.04 * ease((t - a) / 0.12)); break
    last = clean; enc.stdin.write(img.convert("RGB").tobytes()); n += 1
blur = last.convert("RGB").filter(ImageFilter.GaussianBlur(24)).point(lambda v: int(v * 0.55)).convert("RGBA")
for k in range(int(END * FPS)):
    fr = blur.copy(); p = ease(k / FPS / 0.4)
    paste(fr, CTA, W / 2, 820, 1.0, 1.08); paste(fr, DISC, W / 2, 1100)
    enc.stdin.write(fr.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); print("dur", round(DUR + END, 1), "->", OUT)
