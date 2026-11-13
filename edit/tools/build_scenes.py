"""Builds the B-roll scene files and index.html. Times are on the cut timeline (assets/cut.mp4)."""
import json
DUR = 87.70
CSS_COMMON = '''
    @font-face { font-family: "Inter"; src: url("assets/fonts/Inter-400.woff2") format("woff2"); font-weight: 400; }
    @font-face { font-family: "Inter"; src: url("assets/fonts/Inter-700.woff2") format("woff2"); font-weight: 700; }
    #root { position: absolute; inset: 0; }
    .bg { position: absolute; inset: 0; background: #f2eee8; }
    .wrap { position: absolute; inset: 0; opacity: 0; font-family: "Inter", sans-serif; color: #1c1c1e; }
    .card { position: absolute; left: 70px; right: 70px; top: 300px; background: #fff; border-radius: 40px;
            padding: 56px 60px 60px; box-shadow: 0 24px 70px rgba(40, 30, 20, 0.10); }
    .meta { font-size: 30px; color: #9a948c; margin-bottom: 18px; }
    .title { font-size: 64px; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 34px; }
    .row { display: flex; align-items: center; gap: 26px; font-size: 52px; padding: 22px 0;
           border-top: 2px solid #efebe5; opacity: 0; }
    .row:first-of-type { border-top: none; }
    .muted { color: #9a948c; }
    .tick { width: 54px; height: 54px; border-radius: 50%; border: 3px solid #d8d2ca; flex: none;
            display: flex; align-items: center; justify-content: center; }
    .tick svg { width: 30px; height: 30px; opacity: 0; }
    .tick.on { border-color: #1e63d6; background: #1e63d6; }
'''
def scene(sid, start, end, body, css, js):
    dur = round(end - start, 3)
    html = f'''<template>
  <style>{CSS_COMMON}{css}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="1080" data-height="1920">
    <div class="bg"></div>
    <div id="{sid}-wrap" class="wrap">
{body}
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    const D = {dur};
    tl.fromTo("#{sid}-wrap", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.16, ease: "power2.out" }}, 0);
    tl.fromTo("#{sid}-wrap .card", {{ y: 36, scale: 0.985 }}, {{ y: 0, scale: 1, duration: 0.45, ease: "power3.out" }}, 0);
{js}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
'''
    open(f'compositions/{sid}.html', 'w').write(html)
    return (sid, start, dur)

def row_in(sel, t): return f'    tl.fromTo("{sel}", {{ opacity: 0, x: -18 }}, {{ opacity: 1, x: 0, duration: 0.3, ease: "power2.out" }}, {t:.2f});'
CHECK = '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'

scenes = []
# 1 breakfast cravings
s, e = 22.95, 27.20
items = [("kuih", 24.20), ("kerepek", 24.59), ("nasi lemak", 25.39), ("roti canai", 26.57)]
body = '      <div class="card"><div class="meta">nota · pagi</div><div class="title">sarapan yang selalu teringin</div>\n' + \
  "\n".join(f'        <div id="sp-r{i}" class="row"><span class="dot"></span>{n}</div>' for i, (n, t) in enumerate(items)) + '\n      </div>'
css = '\n    .dot { width: 16px; height: 16px; border-radius: 50%; background: #d9576b; flex: none; }'
js = "\n".join(row_in(f"#sp-r{i}", t - s) for i, (n, t) in enumerate(items))
scenes.append(scene("sarapan", s, e, body, css, js))

# 2 routine with meal replacement
s, e = 32.75, 40.40
rows = [("pagi", "meal replacement", 33.17), ("tengah hari", "makan, enjoy sikit", 38.40)]
body = '      <div class="card"><div class="meta">rutin harian</div><div class="title">dah tahu nak makan apa</div>\n' + \
  "\n".join(f'        <div id="rt-r{i}" class="row"><span class="when">{w}</span><span class="what">{x}</span></div>' for i, (w, x, t) in enumerate(rows)) + '\n      </div>'
css = '\n    .when { width: 300px; flex: none; color: #9a948c; font-size: 44px; }\n    .what { font-size: 50px; }'
js = "\n".join(row_in(f"#rt-r{i}", min(t - s, e - s - 0.45)) for i, (w, x, t) in enumerate(rows))
scenes.append(scene("rutin", s, e, body, css, js))

# 3 calorie deficit bars
s, e = 44.30, 47.45
body = '''      <div class="card"><div class="meta">contoh sehari</div><div class="title">defisit kalori</div>
        <div class="bars">
          <div class="col"><div class="barbox"><div id="kl-in" class="bar in"></div></div><div class="lbl">makan<br><b>1,600</b> kcal</div></div>
          <div class="col"><div class="barbox"><div id="kl-out" class="bar out"></div><div id="kl-gap" class="gap">−400</div></div><div class="lbl">dibakar<br><b>2,000</b> kcal</div></div>
        </div>
      </div>'''
css = '''
    .bars { display: flex; gap: 80px; justify-content: center; padding-top: 10px; }
    .col { width: 260px; text-align: center; }
    .barbox { position: relative; height: 400px; display: flex; align-items: flex-end; justify-content: center; }
    .bar { width: 170px; border-radius: 22px 22px 8px 8px; transform-origin: 50% 100%; }
    .bar.in { height: 320px; background: #e4ddd3; }
    .bar.out { height: 400px; background: #1e63d6; }
    .gap { position: absolute; top: -6px; left: -40px; right: -40px; height: 100px; border: 3px dashed #d9576b;
           border-radius: 18px; color: #d9576b; font-size: 44px; font-weight: 700; display: flex;
           align-items: center; justify-content: center; opacity: 0; background: rgba(255,255,255,0.85); }
    .lbl { margin-top: 22px; font-size: 38px; color: #9a948c; line-height: 1.3; }
    .lbl b { color: #1c1c1e; font-size: 46px; }'''
js = f'''    tl.fromTo("#kl-in", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.5, ease: "power3.out" }}, 0.15);
    tl.fromTo("#kl-out", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.6, ease: "power3.out" }}, {44.90 - s:.2f});
    tl.fromTo("#kl-gap", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, {46.38 - s:.2f});'''
scenes.append(scene("kalori", s, e, body, css, js))

# 4 exercise then eat more
s, e = 51.65, 55.25
body = '''      <div class="card"><div class="meta">lepas gym</div><div class="title">bakar, lepas tu tambah</div>
        <div id="sn-r0" class="row"><span class="lab">bersenam</span><span class="num neg">−300 kcal</span></div>
        <div id="sn-r1" class="row"><span class="lab">tambah makan</span><span class="num">+450 kcal</span></div>
        <div id="sn-r2" class="row total"><span class="lab">hasilnya</span><span class="num pos">+150 kcal</span></div>
      </div>'''
css = '''
    .lab { flex: 1; }
    .num { font-weight: 700; }
    .num.neg { color: #1e63d6; }
    .num.pos { color: #d9576b; }
    .row.total { border-top: 3px solid #1c1c1e; margin-top: 8px; }'''
js = "\n".join([row_in("#sn-r0", 51.80 - s), row_in("#sn-r1", 54.10 - s), row_in("#sn-r2", 54.62 - s)])
scenes.append(scene("senam", s, e, body, css, js))

# 5 three days only
s, e = 67.95, 70.72
days = ["isn", "sel", "rab", "kha", "jum", "sab", "ahd"]
ticks = [69.51, 69.80, 70.10]
body = '      <div class="card"><div class="meta">diet sorang-sorang</div><div class="title">tiga hari je</div>\n        <div class="week">\n' + \
  "\n".join(f'          <div class="day"><div id="kd-{i}" class="tick">{CHECK}</div><div class="dn">{d}</div></div>' for i, d in enumerate(days)) + '\n        </div>\n      </div>'
css = '''
    .week { display: flex; justify-content: space-between; padding-top: 20px; }
    .day { text-align: center; }
    .day .tick { width: 96px; height: 96px; }
    .day .tick svg { width: 50px; height: 50px; }
    .dn { margin-top: 18px; font-size: 34px; color: #9a948c; }'''
js = "\n".join(
  f'    tl.set("#kd-{i}", {{ backgroundColor: "#1e63d6", borderColor: "#1e63d6" }}, {t - s:.2f});\n'
  f'    tl.fromTo("#kd-{i} svg", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)" }}, {t - s:.2f});'
  for i, t in enumerate(ticks))
scenes.append(scene("tigahari", s, e, body, css, js))

# 6 recap checklist
s, e = 77.40, 84.95
items = [("ada rutin", 78.65), ("bakar & defisit kalori", 81.27), ("komitmen", 83.92)]
body = '      <div class="card"><div class="meta">sebelum start diet</div><div class="title">3 perkara penting</div>\n' + \
  "\n".join(f'        <div class="row on"><div id="rc-t{i}" class="tick">{CHECK}</div><span id="rc-x{i}" class="muted">{n}</span></div>' for i, (n, t) in enumerate(items)) + '\n      </div>'
css = '\n    .row.on { opacity: 1; }'
js = "\n".join(
  f'    tl.set("#rc-t{i}", {{ backgroundColor: "#1e63d6", borderColor: "#1e63d6" }}, {t - s:.2f});\n'
  f'    tl.fromTo("#rc-t{i} svg", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)" }}, {t - s:.2f});\n'
  f'    tl.fromTo("#rc-x{i}", {{ color: "#9a948c" }}, {{ color: "#1c1c1e", duration: 0.2 }}, {t - s:.2f});'
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
