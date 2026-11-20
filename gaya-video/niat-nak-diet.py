"""Big centred text behind the speaker (person cut-out on top)."""
import os, subprocess, numpy as np, onnxruntime as ort
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SRC, OUT = 1080, 1920, 30, "in.mov", "reel-niat-nak-diet.mp4"
BLK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
YEL, WHITE = (255, 214, 10), (255, 255, 255)
ease = lambda v: 1 - (1 - min(max(v, 0), 1)) ** 3
def back(v):
    v = min(max(v, 0), 1); c1 = 1.7; return 1 + (c1 + 1) * (v - 1) ** 3 + c1 * (v - 1) ** 2
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", SRC], capture_output=True, text=True).stdout)

def line_img(parts, maxw=760):
    """parts: [(text, colour)] on one line, sized to fill the width."""
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1))); size = 170
    while True:
        f = ImageFont.truetype(BLK, size); sp = d.textlength(" ", font=f)
        tw = sum(d.textlength(t, font=f) for t, _ in parts) + sp * (len(parts) - 1)
        if tw <= maxw or size < 60: break
        size -= 4
    asc, desc = f.getmetrics(); h = asc + desc
    im = Image.new("RGBA", (W, h + 40), (0, 0, 0, 0)); sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    x = (W - tw) / 2; ds, di = ImageDraw.Draw(sh), ImageDraw.Draw(im)
    for t, c in parts:
        ds.text((x, 26), t, font=f, fill=(0, 0, 0, 170)); di.text((x, 16), t, font=f, fill=c, stroke_width=3, stroke_fill=(0, 0, 0))
        x += d.textlength(t, font=f) + sp
    full = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), im)
    ol = Image.new("RGBA", im.size, (0, 0, 0, 0)); do = ImageDraw.Draw(ol); x = (W - tw) / 2
    for t, c in parts:
        do.text((x, 16), t, font=f, fill=(0, 0, 0, 0), stroke_width=3, stroke_fill=c + (200,)); x += d.textlength(t, font=f) + sp
    return full, ol

PINK = (255, 120, 170)
XOFF = -55   # keep clear of the like/comment/share icons on the right
BLOCKS = [(0.0, 4.0, 0.35, [line_img([("NIAT", WHITE), ("NAK", WHITE)]), line_img([("DIET", YEL)]), line_img([("TAPI..", WHITE)])]),
          (4.0, 9.6, 1.15, [line_img([("CUTI", WHITE), ("SEKOLAH", YEL)]), line_img([("BALIK", WHITE), ("KAMPUNG", YEL)]), line_img([("KENDURI", WHITE), ("BANYAK", YEL)]), line_img([("NAK", WHITE), ("TRAVEL", YEL), ("OVERSEA", WHITE)])]),
          (9.6, DUR, 0.45, [line_img([("MUNGKIN", WHITE), ("TIADA", WHITE)]), line_img([("\u2018JODOH\u2019", PINK)]), line_img([("KURUS", YEL), ("KAN..", WHITE)])])]

def cta_img():
    im = Image.new("RGBA", (W, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(BLK, 64); sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((W / 2, 64), "Nak Join Program?", font=f1, fill=(0, 0, 0, 200), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0, 200))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8))); d = ImageDraw.Draw(im)
    d.text((W / 2, 58), "Nak Join Program?", font=f1, fill=WHITE, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(glow).rounded_rectangle([250, 125, W - 250, 255], 65, fill=(230, 30, 40, 210))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(16))); d = ImageDraw.Draw(im)
    d.rounded_rectangle([260, 130, W - 260, 250], 60, fill=(225, 30, 40))
    d.text((345, 190), "DM", font=ImageFont.truetype(BLK, 38), fill=(255, 215, 215), anchor="mm")
    d.text((W / 2 + 45, 192), "\u201cCANTIK\u201d", font=ImageFont.truetype(BLK, 70), fill=WHITE, anchor="mm")
    return im
CTA = cta_img(); CTA_AT = 10.8

def top_cta():
    im = Image.new("RGBA", (W, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([70, 10, W - 140, 280], 40, fill=(15, 15, 20, 215))
    f1 = ImageFont.truetype(BLK, 50)
    d.text(((W - 70) / 2, 72), "Nak saya bantu", font=f1, fill=WHITE, anchor="mm")
    d.text(((W - 70) / 2, 134), "kurus, cantik & sihat?", font=f1, fill=YEL, anchor="mm")
    d.rounded_rectangle([(W - 70) / 2 - 270, 180, (W - 70) / 2 + 270, 260], 40, fill=(225, 30, 40))
    d.text(((W - 70) / 2, 221), "DM / komen \u201cCANTIK\u201d", font=ImageFont.truetype(BLK, 44), fill=WHITE, anchor="mm")
    return im
TOPCTA = top_cta()

sess = ort.InferenceSession(os.path.expanduser("~/easy-edit/models/modnet.onnx")); prev = None
def matte(rgb):
    global prev
    x = np.asarray(Image.fromarray(rgb).resize((288, 512), Image.BILINEAR), np.float32) / 127.5 - 1
    m = sess.run(None, {"input": x.transpose(2, 0, 1)[None]})[0][0, 0]
    prev = m if prev is None else 0.6 * m + 0.4 * prev
    return Image.fromarray((np.clip(prev, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2))

def paste(base, im, x, y, a, sc):
    if sc != 1: w0, h0 = im.size; im = im.resize((int(w0 * sc), int(h0 * sc)), Image.LANCZOS); x += (w0 - im.width) / 2; y += (h0 - im.height) / 2
    if a < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x, y = int(x), int(y); l, t = max(0, -x), max(0, -y); r, b = min(im.width, W - x), min(im.height, H - y)
    if r > l and b > t: base.alpha_composite(im.crop((l, t, r, b)), (x + l, y + t))

dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", SRC, "-vf", f"fps={FPS},scale={W}:{H}:flags=lanczos,hqdn3d=1.5:1.5:4:4,unsharp=5:5:0.7:5:5:0.0,curves=master='0/0 0.25/0.29 0.5/0.56 0.75/0.8 1/1',colorbalance=rs=-0.02:bs=0.02:rm=-0.02:bm=0.02,eq=contrast=1.06:saturation=1.08,vignette=PI/6", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", SRC, "-map", "0:v", "-map", "1:a?",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
n = 0
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    t = n / FPS; rgb = np.frombuffer(raw, np.uint8).reshape(H, W, 3); frame = Image.fromarray(rgb).convert("RGBA"); m = matte(rgb)
    img = frame.copy(); FRONT = []
    for a, b, stg, lines in BLOCKS:
        if a <= t < b:
            total = sum(l[0].height for l in lines) - 22 * (len(lines) - 1); y = 820
            for k, l in enumerate(lines):
                at = a + 0.15 + k * stg; p = back((t - at) / 0.45); al = min(ease((t - at) / 0.3), ease((b - t) / 0.25))
                if t >= at: paste(img, l[0], XOFF, y + 40 * (1 - min(p, 1)), al, 0.8 + 0.2 * min(p, 1.05)); FRONT.append((l[0], y + 40 * (1 - min(p, 1)), al, 0.8 + 0.2 * min(p, 1.05)))
                y += l[0].height - 22
    person = frame.copy(); person.putalpha(m); img.alpha_composite(person)
    for ol, yy, al, sc in FRONT: paste(img, ol, XOFF, yy, al, sc)
    paste(img, TOPCTA, 0, 230 - 30 * (1 - ease((t - 0.3) / 0.5)), ease((t - 0.3) / 0.4), 1.0)
    enc.stdin.write(img.convert("RGB").tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n, "->", OUT)
