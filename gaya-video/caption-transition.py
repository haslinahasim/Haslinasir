"""Shake Summer Berries: word captions + punch-zoom transitions between sections."""
import json, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SRC, OUT = 1080, 1920, 30, "in.mov", "reel-shake-summer-berries.mp4"
FD = "/usr/share/fonts/opentype/inter/"
BLK, XB, BD = FD + "InterDisplay-Black.otf", FD + "InterDisplay-ExtraBold.otf", FD + "InterDisplay-Bold.otf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
WHITE, GOLD, PINK, PURP = (255, 255, 255), (255, 214, 120), (255, 120, 190), (190, 140, 255)
F = lambda p, s: ImageFont.truetype(p, s)
ease = lambda v: 1 - (1 - min(max(v, 0), 1)) ** 3
def back(v):
    v = min(max(v, 0), 1); c1 = 1.7; return 1 + (c1 + 1) * (v - 1) ** 3 + c1 * (v - 1) ** 2
DUR = 39.6   # end after "memang sedap sangat-sangat"

# ---------- sections: alternate framing, punch transition at each start ----------
CUTS = [0.0, 7.38, 17.70, 25.05, 31.70, 37.90]
ZOOM = [1.00, 1.16, 1.00, 1.16, 1.00, 1.18]
def section(t):
    k = max(i for i, c in enumerate(CUTS) if c <= t); return k, t - CUTS[k]

# ---------- captions ----------
words = json.load(open("in_words.json"))
FIX = {12: "kata-kata", 13: "", 15: "sangat-sangat!", 16: "", 26: "", 27: "", 28: "", 29: "", 49: "sangat-sangat!", 50: "", 34: "follow", 35: "dulu!", 41: "Berries!", 46: "cuba!"}
ACC = {4, 14, 25, 34, 39, 40, 41, 46, 48}
GROUPS = [(0, 3), (3, 5), (5, 8), (8, 11), (11, 14), (14, 17), (17, 20), (20, 21), (21, 23), (23, 26), (30, 34), (34, 36), (36, 38), (38, 42), (42, 45), (45, 47), (47, 51)]
disp = lambda i: FIX.get(i, words[i]["w"])
def cap_img(idx):
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1))); parts = [(disp(i), i in ACC) for i in idx if disp(i)]
    size = 64
    while True:
        fw, fa = F(BLK, size), F(SERIF, int(size * 1.12)); sp = 16
        tw = sum(d.textlength(t, font=fa if a else fw) for t, a in parts) + sp * (len(parts) - 1)
        if tw < 960 or size < 36: break
        size -= 2
    im = Image.new("RGBA", (int(tw) + 60, int(size * 2.2)), (0, 0, 0, 0)); sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ds, dd = ImageDraw.Draw(sh), ImageDraw.Draw(im); x = 30; base = int(size * 1.3)
    for t, a in parts:
        f = fa if a else fw
        ds.text((x, base + 3), t, font=f, fill=(0, 0, 0, 255), anchor="ls", stroke_width=6, stroke_fill=(0, 0, 0, 255))
        dd.text((x, base), t, font=f, fill=GOLD if a else WHITE, anchor="ls", stroke_width=2, stroke_fill=(0, 0, 0, 160)); x += d.textlength(t, font=f) + sp
    return Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)), im)
CAPS = []
for gi, (a, b) in enumerate(GROUPS):
    nxt = words[GROUPS[gi + 1][0]]["s"] if gi + 1 < len(GROUPS) else DUR
    g_end = min(nxt, words[b - 1]["e"] + 0.9)
    shown = [k for k in range(a, b) if disp(k)]
    for j, k in enumerate(shown):
        CAPS.append((words[k]["s"], words[shown[j + 1]]["s"] if j + 1 < len(shown) else g_end, cap_img(range(a, k + 1))))
CAPS.append((10.0, 17.5, cap_img_t := None))   # placeholder replaced below
CAPS[-1] = (10.0, 17.5, None)
TASTE = Image.new("RGBA", (W, 160), (0, 0, 0, 0)); d = ImageDraw.Draw(TASTE)
d.text((W / 2, 80), "cuba rasa…", font=F(SERIF, 80), fill=GOLD, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

# ---------- hook title ----------
def hook():
    im = Image.new("RGBA", (W, 420), (0, 0, 0, 0)); sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    lines = [("SHAKE", F(XB, 64), WHITE, 60), ("SUMMER", F(BLK, 150), PINK, 170), ("BERRIES", F(BLK, 150), PURP, 310), ("Herbalife", F(SERIF, 64), WHITE, 400)]
    for t, f, c, y in lines:
        ImageDraw.Draw(sh).text((W / 2, y + 6), t, font=f, fill=(0, 0, 0, 200), anchor="ms", stroke_width=8, stroke_fill=(0, 0, 0, 200))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10))); d = ImageDraw.Draw(im)
    for t, f, c, y in lines: d.text((W / 2, y), t, font=f, fill=c, anchor="ms", stroke_width=4, stroke_fill=(30, 10, 40))
    return im
HOOK = hook()

def paste(base, im, x, y, a=1.0, sc=1.0):
    if sc != 1.0: w0, h0 = im.size; im = im.resize((max(1, int(w0 * sc)), max(1, int(h0 * sc))), Image.LANCZOS); x += (w0 - im.width) / 2; y += (h0 - im.height) / 2
    if a < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x, y = int(x), int(y); l, t = max(0, -x), max(0, -y); r, b = min(im.width, W - x), min(im.height, H - y)
    if r > l and b > t: base.alpha_composite(im.crop((l, t, r, b)), (x + l, y + t))

dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", SRC, "-t", str(DUR), "-vf",
    f"fps={FPS},scale={W}:{H}:flags=lanczos,unsharp=5:5:0.6,eq=contrast=1.05:saturation=1.08:brightness=0.02",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-i", SRC, "-map", "0:v", "-map", "1:a", "-af", f"atrim=0:{DUR},loudnorm=I=-16:TP=-1.5,afade=t=out:st={DUR - 0.4}:d=0.4", "-t", str(DUR),
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
n = 0
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    t = n / FPS; fr = Image.frombytes("RGB", (W, H), raw)
    k, lt = section(t)
    z = ZOOM[k]
    tr = max(0, 1 - lt / 0.35) if k > 0 else 0          # transition strength just after a cut
    z *= 1 + 0.10 * tr ** 2                                 # punch-in that settles
    if z > 1.001:
        cw, ch = int(W / z), int(H / z); cx, cy = W / 2, H * 0.40
        x0 = int(min(max(cx - cw / 2, 0), W - cw)); y0 = int(min(max(cy - ch / 2, 0), H - ch))
        fr = fr.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)
    if tr > 0.05:
        fr = fr.filter(ImageFilter.BoxBlur(int(14 * tr)))
        fr = Image.blend(fr, Image.new("RGB", (W, H), (255, 255, 255)), 0.55 * tr ** 2)
    img = fr.convert("RGBA")
    if t < 4.2:
        p = back(t / 0.5); paste(img, HOOK, 0, 110 - 40 * (1 - min(p, 1)), min(1, ease(t / 0.3)) * ease((4.2 - t) / 0.4), 0.85 + 0.15 * min(p, 1.05))
    if 10.0 <= t < 17.5: paste(img, TASTE, 0, 1380, ease((t - 10) / 0.4) * ease((17.5 - t) / 0.3))
    for a, b, im in CAPS:
        if im is not None and a <= t < b:
            paste(img, im, (W - im.width) / 2, 1400, 1.0, 0.96 + 0.04 * ease((t - a) / 0.12)); break
    enc.stdin.write(img.convert("RGB").tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n, "->", OUT)
