"""Builds the B-roll overlay scenes and index.html. Times are on the cut timeline (assets/cut.mp4).
Overlays are translucent cards in the safe band y=176..396: below the app's top bar, above the face
(face top >= ~398 px across the video), never over the captions (y~1196)."""
import json
DUR = 87.70
CSS_COMMON = """
    @font-face { font-family: "Inter"; src: url("assets/fonts/Inter-400.woff2") format("woff2"); font-weight: 400; }
    @font-face { font-family: "Inter"; src: url("assets/fonts/Inter-700.woff2") format("woff2"); font-weight: 700; }
    #root { position: absolute; inset: 0; pointer-events: none; }
    .wrap { position: absolute; left: 48px; right: 48px; top: 176px; height: 220px; opacity: 0;
            font-family: "Inter", sans-serif; color: #1c1c1e; display: flex; gap: 16px; align-items: flex-start; }
    .card { flex: 1; background: rgba(255, 255, 255, 0.66); border: 1.5px solid rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
            border-radius: 28px; padding: 18px 28px 20px; box-shadow: 0 10px 34px rgba(0, 0, 0, 0.12); }
    .title { font-size: 36px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.2; margin-bottom: 10px;
             display: flex; justify-content: space-between; align-items: baseline; }
    .title small { font-size: 28px; font-weight: 400; color: #6f6a64; }
    .muted { color: #6f6a64; }
    .tick { width: 44px; height: 44px; border-radius: 50%; border: 3px solid rgba(28, 28, 30, 0.25); flex: none;
            display: flex; align-items: center; justify-content: center; }
    .tick svg { width: 24px; height: 24px; opacity: 0; }
"""

def scene(sid, start, end, body, css, js):
    dur = round(end - start, 3)
    html = f"""<template>
  <style>{CSS_COMMON}{css}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="1080" data-height="1920">
    <div id="{sid}-wrap" class="wrap">
{body}
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    const D = {dur};
    tl.fromTo("#{sid}-wrap", {{ opacity: 0, y: -16 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, 0);
    tl.to("#{sid}-wrap", {{ opacity: 0, duration: 0.2, ease: "power2.in" }}, D - 0.2);
{js}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
"""
    open(f"compositions/{sid}.html", "w").write(html)
    return (sid, start, dur)

def pop(sel, t):
    return f'    tl.fromTo("{sel}", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.28, ease: "power2.out" }}, {t:.2f});'

def tick(sel, t):
    return (f'    tl.set("{sel}", {{ backgroundColor: "#1e63d6", borderColor: "#1e63d6" }}, {t:.2f});\n'
            f'    tl.fromTo("{sel} svg", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)" }}, {t:.2f});')

CHECK = '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
scenes = []

# 1 breakfast cravings
s, e = 22.95, 27.20
items = [("kuih", 24.20), ("kerepek", 24.59), ("nasi lemak", 25.39), ("roti canai", 26.57)]
body = ('      <div class="card"><div class="title">sarapan yang selalu teringin</div><div class="chips">\n'
        + "\n".join(f'        <span id="sp-c{i}" class="chip">{n}</span>' for i, (n, t) in enumerate(items))
        + "\n      </div></div>")
css = """
    .chips { display: flex; gap: 14px; }
    .chip { font-size: 36px; padding: 8px 22px 10px; border-radius: 999px; background: rgba(217, 87, 107, 0.16); opacity: 0; }"""
js = "\n".join(pop(f"#sp-c{i}", t - s) for i, (n, t) in enumerate(items))
scenes.append(scene("sarapan", s, e, body, css, js))

# 2 routine, with her own meal replacement photo
s, e = 32.75, 40.40
body = """      <div class="card"><div class="title">rutin harian</div>
        <div id="rt-r0" class="row"><span class="when">pagi</span><span>meal replacement</span></div>
        <div id="rt-r1" class="row"><span class="when">tengah hari</span><span>makan, enjoy sikit</span></div>
      </div>
    </div>
    <div id="rt-photo" class="photo"><img src="assets/meal-replacement.jpg" alt="meal replacement" /></div>
    <div>"""
# photo sits left of the face (face never left of x~330 here), between the top band and the captions
css = """
    .photo { position: absolute; left: 54px; top: 440px; width: 256px; height: 332px; border-radius: 26px; overflow: hidden;
             opacity: 0; border: 3px solid rgba(255, 255, 255, 0.85); box-shadow: 0 12px 36px rgba(0, 0, 0, 0.22); }
    .photo img { width: 100%; height: 100%; object-fit: cover; display: block; }
    .row { display: flex; font-size: 36px; line-height: 50px; opacity: 0; }
    .when { width: 220px; flex: none; color: #6f6a64; }"""
js = "\n".join([
    '    tl.fromTo("#rt-photo", { opacity: 0, x: -20, scale: 0.97 }, { opacity: 1, x: 0, scale: 1, duration: 0.35, ease: "power3.out" }, %.2f);' % (33.17 - s),
    '    tl.to("#rt-photo", { opacity: 0, duration: 0.2, ease: "power2.in" }, D - 0.2);',
    pop("#rt-r0", 33.30 - s), pop("#rt-r1", 38.40 - s)])
scenes.append(scene("rutin", s, e, body, css, js))

# 3 calorie deficit, horizontal bars
s, e = 44.30, 47.45
body = """      <div class="card"><div class="title">defisit kalori <small>contoh sehari</small></div>
        <div class="hb"><span class="hl">makan</span><div class="track"><div id="kl-in" class="fill in"></div><div id="kl-gap" class="gap">&minus;400</div></div><span class="hv">1,600</span></div>
        <div class="hb"><span class="hl">dibakar</span><div class="track"><div id="kl-out" class="fill out"></div></div><span class="hv">2,000</span></div>
      </div>"""
css = """
    .hb { display: flex; align-items: center; height: 54px; font-size: 32px; }
    .hl { width: 150px; flex: none; color: #6f6a64; }
    .hv { width: 120px; flex: none; text-align: right; font-weight: 700; }
    .track { position: relative; flex: 1; height: 32px; }
    .fill { position: absolute; left: 0; top: 0; bottom: 0; border-radius: 10px; transform-origin: 0 50%; }
    .fill.in { width: 80%; background: #b9ab98; }
    .fill.out { width: 100%; background: #1e63d6; }
    .gap { position: absolute; left: 80%; width: 20%; top: -4px; bottom: -4px; border: 3px dashed #d9576b; border-radius: 10px;
           color: #d9576b; font-size: 28px; font-weight: 700; display: flex; align-items: center; justify-content: center; opacity: 0; }"""
js = (f'    tl.fromTo("#kl-in", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.5, ease: "power3.out" }}, 0.15);\n'
      f'    tl.fromTo("#kl-out", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: "power3.out" }}, {44.90 - s:.2f});\n'
      f'    tl.fromTo("#kl-gap", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25, ease: "power2.out" }}, {46.38 - s:.2f});')
scenes.append(scene("kalori", s, e, body, css, js))

# 4 exercise then eat more
s, e = 51.65, 55.25
body = """      <div class="card"><div class="title">bakar, lepas tu tambah</div><div class="eq">
        <div id="sn-0" class="term"><span class="muted">bersenam</span><b class="neg">&minus;300</b></div>
        <div id="sn-1" class="term"><span class="muted">tambah makan</span><b>+450</b></div>
        <div id="sn-2" class="term res"><span class="muted">hasilnya</span><b class="pos">+150 kcal</b></div>
      </div></div>"""
css = """
    .eq { display: flex; gap: 18px; }
    .term { flex: 1; display: flex; flex-direction: column; font-size: 28px; opacity: 0; }
    .term b { font-size: 44px; line-height: 1.2; }
    .term.res { border-left: 3px solid rgba(28, 28, 30, 0.6); padding-left: 18px; }
    .neg { color: #1e63d6; }
    .pos { color: #d9576b; }"""
js = "\n".join([pop("#sn-0", 51.80 - s), pop("#sn-1", 54.10 - s), pop("#sn-2", 54.62 - s)])
scenes.append(scene("senam", s, e, body, css, js))

# 5 three days only
s, e = 67.95, 70.72
days = ["isn", "sel", "rab", "kha", "jum", "sab", "ahd"]
ticks = [69.51, 69.80, 70.10]
body = ('      <div class="card"><div class="title">tiga hari je <small>diet sorang-sorang</small></div><div class="week">\n'
        + "\n".join(f'          <div class="day"><div id="kd-{i}" class="tick">{CHECK}</div><div class="dn">{d}</div></div>' for i, d in enumerate(days))
        + "\n      </div></div>")
css = """
    .week { display: flex; justify-content: space-between; padding: 0 10px; }
    .day { text-align: center; }
    .day .tick { width: 60px; height: 60px; }
    .day .tick svg { width: 32px; height: 32px; }
    .dn { margin-top: 6px; font-size: 28px; color: #6f6a64; }"""
js = "\n".join(tick(f"#kd-{i}", t - s) for i, t in enumerate(ticks))
scenes.append(scene("tigahari", s, e, body, css, js))

# 6 recap checklist
s, e = 77.40, 84.95
items = [("ada rutin", 78.65), ("bakar &amp; defisit kalori", 81.27), ("komitmen", 83.92)]
body = ('      <div class="card"><div class="title">3 perkara penting</div><div class="list">\n'
        + "\n".join(f'        <div class="it"><div id="rc-t{i}" class="tick">{CHECK}</div><span id="rc-x{i}">{n}</span></div>' for i, (n, t) in enumerate(items))
        + "\n      </div></div>")
css = """
    .list { display: flex; gap: 28px; }
    .it { display: flex; align-items: center; gap: 12px; font-size: 32px; white-space: nowrap; }"""
js = "\n".join(tick(f"#rc-t{i}", t - s) + "\n"
               + f'    tl.fromTo("#rc-x{i}", {{ color: "#6f6a64" }}, {{ color: "#1c1c1e", duration: 0.2 }}, {t - s:.2f});'
               for i, (n, t) in enumerate(items))
scenes.append(scene("recap", s, e, body, css, js))

# face-tracked slow zooms on emotional beats: (start, zoom-end, snap-back, origin x, origin y, scale)
ZOOMS = [
  (14.55, 17.05, 17.05, 545, 744, 1.14),   # "memang kena boring"
  (55.25, 57.90, 57.99, 544, 742, 1.14),   # "celah mana nak turun berat badan?"
  (61.65, 63.89, 63.89, 551, 750, 1.12),   # "sebab apa? bila bakar kalori, awak tambah makanan"
  (70.72, 75.00, 77.31, 530, 738, 1.16),   # "kawan dengan semua kaki makan, memang tak turun"
  (84.95, 87.70, None, 546, 742, 1.12),    # CTA
]
zjs = []
for a, b, snap, ox, oy, sc in ZOOMS:
    zjs.append(f'      tl.set("#cam", {{ transformOrigin: "{ox}px {oy}px", scale: 1 }}, {a});')
    zjs.append(f'      tl.to("#cam", {{ scale: {sc}, duration: {round(b - a, 2)}, ease: "sine.inOut" }}, {a});')
    if snap: zjs.append(f'      tl.set("#cam", {{ scale: 1 }}, {snap});')
hosts = "\n".join(
  f'''      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html"
        data-start="{st}" data-duration="{d}" data-track-index="2" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index: 5"></div>''' for sid, st, d in scenes)
index = f'''<!doctype html>
<html lang="ms">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      #cam {{ position: absolute; inset: 0; z-index: 1; }}
      #src {{ width: 1080px; height: 1920px; object-fit: cover; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
      <div id="cam">
        <video id="src" class="clip" src="assets/cut.mp4" data-start="0" data-duration="{DUR}"
          data-track-index="0" data-has-audio="true" playsinline></video>
      </div>
{hosts}
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html"
        data-start="0" data-duration="{DUR}" data-track-index="3" data-track-kind="captions"
        data-width="1080" data-height="1920" style="z-index: 10"></div>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(zjs)}
      tl.set({{}}, {{}}, {DUR});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
open('index.html', 'w').write(index)
print(scenes)
