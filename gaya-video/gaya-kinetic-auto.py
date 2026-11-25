"""Gaya kinetic: talking-head reel with word-by-word kinetic typography placed around the speaker
(mixed sizes, gold serif keywords, text tucked behind the head via MODNet matte), punch zooms,
vignette, rounded B-roll cards, CTA + income disclaimer end card."""
import json, os, subprocess, numpy as np, onnxruntime as ort
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SRC_RAW, SRC, OUT = 1080, 1920, 30, "in.mov", "cut.mp4", "reel-network-marketing-usj.mp4"
BLK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
BD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
SB = "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"
PF = "/root/.fonts/Playfair_Display_wght_800_.woff2"
PFI = "/root/.fonts/Playfair_Display_ital_wght_1_700_.woff2"
GV = "/root/.fonts/Great_Vibes_.woff2"
F = lambda p, s: ImageFont.truetype(p, s)
WHITE, GOLD, SOFT = (255, 255, 255), (247, 214, 120), (225, 225, 230)
ease = lambda v: 1 - (1 - min(max(v, 0), 1)) ** 3
CX = (W - 60) / 2
END = 3.2

# ---------- timeline: drop long pauses ----------
words = json.load(open("in_words.json"))
SRC_DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", SRC_RAW], capture_output=True, text=True).stdout)
SEGS = []; a0 = max(0, words[0]["s"] - 0.25)
for i in range(len(words) - 1):
    if words[i + 1]["s"] - words[i]["e"] > 0.55:
        SEGS.append((a0, words[i]["e"] + 0.2)); a0 = words[i + 1]["s"] - 0.15
SEGS.append((a0, min(SRC_DUR, words[-1]["e"] + 0.5)))
ZOOM = [1.0 if i % 2 == 0 else 1.08 for i in range(len(SEGS))]
starts = []; acc = 0.0
for a, b in SEGS: starts.append(acc); acc += b - a
DUR = acc
def to_new(ts):
    for (a, b), s0 in zip(SEGS, starts):
        if a <= ts < b: return s0 + ts - a
    return None
fc = "".join(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={b - a - 0.04}:d=0.04[a{i}];" for i, (a, b) in enumerate(SEGS))
fc += "".join(f"[v{i}][a{i}]" for i in range(len(SEGS))) + f"concat=n={len(SEGS)}:v=1:a=1[v][a]"
os.path.exists(SRC) or subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", SRC_RAW, "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-r", "30",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-c:a", "aac", "-b:a", "192k", SRC], check=True)

# ---------- words -> phrase blocks ----------
FIX = {0: "Tahu tak?", 1: "", 13: "sukses.", 25: "saya", 26: "", 97: "ini?", 53: "", 54: "the team."}
KEY = {0, 13, 29, 30, 32, 37, 41, 54, 61, 67, 81, 92, 101, 109, 113, 118, 124, 129, 136, 148}
ACC = {2, 10, 72, 86, 100, 110, 116, 128, 133, 151}
GROUPS = []; g0 = 0
for i in range(len(words)):
    t = FIX.get(i, words[i]["w"]); n = i + 1
    end = (i in KEY and not (n < len(words) and n in KEY)) or t.endswith((".", "?", ",")) or i - g0 >= 2 or \
          (n < len(words) and words[n]["s"] - words[i]["e"] > 0.5) or n == len(words)
    if end: GROUPS.append((g0, n)); g0 = n
disp = lambda i: FIX.get(i, words[i]["w"]).rstrip(",")

def word_img(t, kind, alt):
    if kind == "K":
        font, col = (F(PFI, 146), GOLD) if alt else (F(BLK, 138), WHITE)
    elif kind == "A": font, col = F(PFI, 80), GOLD
    else: font, col = F(BD, 54), WHITE
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1))); l, tp, r, b = d.textbbox((0, 0), t, font=font)
    pad = 30; im = Image.new("RGBA", (r - l + pad * 2, b - tp + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((pad - l, pad - tp + 4), t, font=font, fill=(0, 0, 0, 255), stroke_width=6, stroke_fill=(0, 0, 0, 255))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10))); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)).point(lambda v: v // 2))
    ImageDraw.Draw(im).text((pad - l, pad - tp), t, font=font, fill=col)
    return im, pad

class Block:
    """One phrase: words stacked in staggered lines; small words lead into one big keyword."""
    def __init__(self, idx, alt, gi):
        toks = [(k, disp(k)) for k in range(idx[0], idx[1]) if disp(k) and to_new(words[k]["s"] + 0.01) is not None]
        if not any(k in KEY for k, _ in toks) and not any(k in ACC for k, _ in toks):
            longest = max(toks, key=lambda x: len(x[1]))[0]; acc = {longest}
        else: acc = ACC
        lines, cur = [], []
        for k, t in toks:
            kind = "K" if k in KEY else "A" if k in acc else "S"
            if kind == "K":
                if cur: lines.append(cur); cur = []
                lines.append([(k, t, kind)])
            else:
                cur.append((k, t, kind))
                if sum(len(x[1]) for x in cur) > 14: lines.append(cur); cur = []
        if cur: lines.append(cur)
        # lay out
        self.items = []; y = 0; widths = []
        for li, ln in enumerate(lines):
            imgs = [word_img(t, kind, alt) for k, t, kind in ln]
            lw = sum(im.width - 2 * p for im, p in imgs) + 14 * (len(imgs) - 1); lh = max(im.height - 2 * p for im, p in imgs)
            shift = [0, 70, -50, 40][(li + gi) % 4] if ln[0][2] != "K" else 0
            x = -lw / 2 + shift
            for (k, t, kind), (im, p) in zip(ln, imgs):
                self.items.append([k, im, x - p, y - p + (lh - (im.height - 2 * p)), to_new(words[k]["s"] + 0.01)])
                x += im.width - 2 * p + 14
            widths.append((-lw / 2 + shift, lw / 2 + shift)); y += lh + (14 if ln[0][2] == "S" else 6)
        self.w = max(r for _, r in widths) - min(l for l, _ in widths) + 20; self.h = y
        self.l = min(l for l, _ in widths)
        self.t0 = min(it[4] for it in self.items)
        self.pos = None

GROUPS = [g for g in GROUPS if any(disp(k) and to_new(words[k]['s'] + 0.01) is not None for k in range(*g))]
BLOCKS = [Block(g, i % 2 == 1, i) for i, g in enumerate(GROUPS)]
BLOCKS.sort(key=lambda b: b.t0)
for i, b in enumerate(BLOCKS):
    b.t1 = BLOCKS[i + 1].t0 if i + 1 < len(BLOCKS) else DUR
    b.t1 = min(b.t1, max(it[4] for it in b.items) + 1.6)

# ---------- person matte ----------
sess = ort.InferenceSession(os.path.expanduser("~/easy-edit/models/modnet.onnx")); prev = None
def matte(rgb):
    global prev
    x = np.asarray(Image.fromarray(rgb).resize((288, 512), Image.BILINEAR), np.float32) / 127.5 - 1
    m = sess.run(None, {"input": x.transpose(2, 0, 1)[None]})[0][0, 0]
    prev = m if prev is None else 0.6 * m + 0.4 * prev
    return np.clip(prev, 0, 1)

def place(block, m, ylim=(190, 1540)):
    """Pick the emptiest spot (least person) in the safe zone; shrink the block when space is tight."""
    g = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((54, 96), Image.BILINEAR), np.float32) / 255
    g = np.maximum.reduce([np.roll(g, s, a) for s in (-1, 0, 1) for a in (0, 1)])   # dilate
    best = None
    for sc in (1.0, 0.85, 0.72, 0.6):
        bw, bh, bl = block.w * sc, block.h * sc, block.l * sc
        if bw > 840: continue
        for cy in range(ylim[0], int(ylim[1] - bh) + 1, 30):
            for cx in range(int(80 - bl), int(920 - bl - bw) + 1, 30):
                x0, y0 = int((cx + bl) / 20), int(cy / 20); x1, y1 = int((cx + bl + bw) / 20) + 1, int((cy + bh) / 20) + 1
                c = 3 * g[y0:y1, x0:x1].mean() + 0.10 * abs(cy + bh / 2 - 620) / H + 0.12 * abs(cx + bl + bw / 2 - CX) / W + 0.45 * (1 - sc)
                if best is None or c < best[0]: best = (c, cx, cy, sc)
    if best is None: return (CX, 260), 0.55
    return (best[1], best[2]), best[3]

# ---------- B-roll cards ----------
BROLL = [(to_new(words[124]["s"]), 3.2, "../v25/base.mp4", 12.0)]
def card_frames(src, ss, dur):
    p = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(ss), "-t", str(dur + 0.1), "-i", src, "-vf", "fps=30,scale=820:1458",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    n = len(p) // (820 * 1458 * 3); return [Image.frombytes("RGB", (820, 1458), p[i * 820 * 1458 * 3:(i + 1) * 820 * 1458 * 3]) for i in range(n)]
CARDS = [(t, d, card_frames(s, ss, d)) for t, d, s, ss in BROLL]
CMASK = Image.new("L", (820, 1458), 0); ImageDraw.Draw(CMASK).rounded_rectangle([0, 0, 819, 1457], 70, fill=255)
CMASK = CMASK.filter(ImageFilter.GaussianBlur(3))
CSH = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(CSH).rounded_rectangle([130, 410, 950, 1868], 70, fill=(0, 0, 0, 160))
CSH = CSH.filter(ImageFilter.GaussianBlur(24))

# ---------- vignette ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.45) / (H * 0.62)) ** 2)
VIG = Image.fromarray(np.dstack([np.zeros((H, W, 3), np.uint8), (np.clip((r - 0.55) / 0.6, 0, 1) ** 1.5 * 190).astype(np.uint8)]), "RGBA")

# ---------- CTA + disclaimer ----------
def cta():
    im = Image.new("RGBA", (W, 330), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([110, 8, W - 170, 320], 40, fill=(20, 12, 18, 225), outline=GOLD + (170,), width=3)
    d.text((CX, 62), "Nak bina bisnes macam ni?", font=F(PF, 54), fill=WHITE, anchor="mm")
    g = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(g).text((CX, 150), "dari mana-mana sahaja", font=F(GV, 84), fill=GOLD + (190,), anchor="mm")
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(12))); d = ImageDraw.Draw(im)
    d.text((CX, 150), "dari mana-mana sahaja", font=F(GV, 84), fill=GOLD, anchor="mm")
    d.rounded_rectangle([CX - 210, 225, CX + 210, 295], 35, fill=(225, 30, 40))
    d.text((CX, 261), "DM “INFO”", font=F(BLK, 44), fill=WHITE, anchor="mm"); return im
def disclaimer():
    im = Image.new("RGBA", (W, 112), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([80, 4, W - 140, 108], 18, fill=(0, 0, 0, 170))
    for k, l in enumerate(["Penafian: Pendapatan ialah pengalaman individu & bukan jaminan.",
                           "Hasil bergantung pada usaha, masa & kemahiran masing-masing.",
                           "Rujuk Penyata Purata Pendapatan Kasar Herbalife."]):
        d.text((CX, 26 + k * 29), l, font=F(BD, 22), fill=(235, 235, 240), anchor="mm")
    return im
CTA, DISC = cta(), disclaimer()
CTA_AT = DUR - 0.2

def paste(base, im, cx, cy, a=1.0, sc=1.0):
    if sc != 1: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    if a < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x, y = int(cx - im.width / 2), int(cy - im.height / 2); l, t = max(0, -x), max(0, -y); rr, b = min(im.width, W - x), min(im.height, H - y)
    if rr > l and b > t: base.alpha_composite(im.crop((l, t, rr, b)), (x + l, y + t))

dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", SRC, "-vf",
    f"fps={FPS},scale={W}:{H}:flags=lanczos,hqdn3d=1.5:1.5:4:4,unsharp=5:5:0.8,eq=contrast=1.06:saturation=1.05:brightness=0.0",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-i", SRC, "-map", "0:v", "-map", "1:a", "-af", "loudnorm=I=-15:TP=-1.5,apad", "-t", str(DUR + END),
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
n, last = 0, None
while True:
    t = n / FPS
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3:
        if t >= DUR + END or last is None: break
        fr = last
    else:
        fr = Image.frombytes("RGB", (W, H), raw)
        k = max(i for i, s in enumerate(starts) if s <= t); lt = t - starts[k]
        tr = max(0, 1 - lt / 0.3) if k > 0 else 0
        z = ZOOM[k] * (1 + 0.10 * tr ** 2) * (1 + 0.025 * min(lt / 4, 1))      # punch-in + slow push
        cw, ch = int(W / z), int(H / z); x0 = (W - cw) // 2; y0 = int((H - ch) * 0.35)
        fr = fr.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)
        if tr > 0.05: fr = fr.filter(ImageFilter.BoxBlur(int(10 * tr)))
        last = fr
    arr = np.asarray(fr); img = fr.convert("RGBA"); img.alpha_composite(VIG)
    m = matte(arr) if t < DUR else np.zeros((512, 288), np.float32)
    # B-roll card
    card_on = None
    for ct, cd, frames in CARDS:
        if ct <= t < ct + cd and frames:
            p = ease((t - ct) / 0.3) * ease((ct + cd - t) / 0.3); card_on = p
            bg = Image.blend(img.convert("RGB").filter(ImageFilter.GaussianBlur(18)), Image.new("RGB", (W, H), (8, 6, 10)), 0.45).convert("RGBA")
            img = Image.blend(img, bg, p)
            cf = frames[min(len(frames) - 1, int((t - ct) * FPS))].convert("RGBA"); cf.putalpha(CMASK)
            img.alpha_composite(CSH if p >= 1 else Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 0)), CSH, p))
            paste(img, cf, W / 2, 1110 + 60 * (1 - p), p, 0.92 + 0.08 * p)
    # kinetic words
    TL = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for b in BLOCKS:
        if b.t0 - 0.05 <= t < b.t1 and t < CTA_AT:
            if b.pos is None: b.pos, b.sc = ((CX - b.w / 2 - b.l, 230), min(1, 840 / b.w)) if card_on is not None else place(b, m)
            out = ease((b.t1 - t) / 0.18)
            for k, im, dx, dy, ts in b.items:
                if t < ts - 0.04: continue
                p = ease((t - ts + 0.04) / 0.22)
                paste(TL, im, b.pos[0] + (dx + im.width / 2) * b.sc, b.pos[1] + (dy + im.height / 2) * b.sc + 14 * (1 - p), p * out, b.sc * (1.12 - 0.12 * p))
    if card_on is None and t < DUR:      # tuck text behind the speaker
        mm = Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2))
        a = np.asarray(TL.getchannel("A"), np.float32) * (1 - np.asarray(mm, np.float32) / 255 * 0.0)
        TL.putalpha(Image.fromarray(a.astype(np.uint8)))
    img.alpha_composite(TL)
    # CTA end card
    if t >= CTA_AT:
        e = ease((t - CTA_AT) / 0.5)
        bl = Image.blend(img.filter(ImageFilter.GaussianBlur(16)), Image.new("RGBA", (W, H), (12, 8, 12, 255)), 0.4); img = Image.blend(img, bl, e)
        paste(img, CTA, W / 2, 760 + 30 * (1 - e), e, 0.95 + 0.05 * e)
        paste(img, DISC, W / 2, 1480, e)
    enc.stdin.write(img.convert("RGB").tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n, "->", OUT)
