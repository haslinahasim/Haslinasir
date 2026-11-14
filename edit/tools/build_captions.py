"""Builds compositions/captions.html from assets/transcript-cut.json + hand-corrected groups."""
import json, html
W = json.load(open('assets/transcript-cut.json'))
W = W if isinstance(W, list) else W['words']
DUR = 87.70
G = [
 (0,2,"sebelum anda faham"),(3,6,"3 perkara yang penting"),(7,11,"dalam proses turunkan berat badan"),
 (12,14,"kalau anda faham"),(15,18,"3 prinsip basic ni"),(19,23,"anda tak akan gagal diet"),
 (24,27,"bila anda mulakan diet"),(28,32,"pasti boleh turunkan berat badan"),
 (33,34,"yang pertama,"),(35,37,"yang paling penting"),(38,40,"yang ramai orang"),(41,43,"selalu tak faham"),
 (44,47,"sebenarnya turun berat ni"),(48,50,"memang kena boring"),(51,54,"dia kena ada rutin"),
 (55,58,"hidup yang ada rutin"),(59,61,"baru boleh fokus"),(62,64,"turunkan berat badan"),
 (65,67,"contohnya kalau pagi"),(68,71,"masih teringin kuih, kerepek"),(72,75,"nasi lemak, roti canai"),
 (76,79,"dia tak ada rutin"),(80,83,"anda masih lagi makan"),(84,87,"apa yang anda nak"),
 (88,92,"sebab tu kena create rutin"),(93,97,"sebab tu meal replacement ni"),(98,102,"dia bantu create rutin"),
 (103,106,"jadi anda ada rutin"),(107,110,"pagi dah tahu apa"),(111,115,"mungkin nak enjoy sikit makan"),
 (116,121,"waktu tengah hari atau petang"),(122,125,"kita dah ada rutin"),(126,128,"yang pertama tu"),
 (129,131,"ramai tak faham"),(132,133,"yang kedua,"),(134,137,"kita ada bakar kalori"),
 (138,141,"kita ada defisit kalori"),(142,146,"kalau kita faham dua ni"),(147,150,"kita akan buat dua-dua"),
 (151,153,"tanpa tambah makanan"),(154,156,"ramai orang bersenam"),(157,161,"dia rasa dah bersenam"),
 (162,164,"dia tambah makanan"),(165,167,"celah mana nak"),(168,170,"turun berat badan?"),
 (171,174,"mungkin awak dapat sihat"),(175,178,"dari segi awak bersenam"),(179,184,"tapi takkan turun berat badan"),
 (185,189,"sebab prinsip tu dah gagal"),(190,191,"sebab apa?"),(192,194,"bila bakar kalori"),
 (195,197,"awak tambah makanan"),(198,201,"last, diet seorang-seorang"),(202,204,"memang tak jadi"),
 (205,206,"kalau seorang-seorang"),(207,211,"disiplin ke, eat clean ke"),(212,216,"tiga hari tiga malam je"),
 (217,218,"tambah-tambah pula"),(219,225,"kawan dengan semua kaki makan"),(226,228,"memang tak turun"),
 (229,231,"sebab itulah pentingnya"),(232,234,"tiga elemen ni"),(235,237,"pertama sekali,"),
 (238,241,"fahamkan ada rutin"),(242,246,"kedua, mesti tahu bakar kalori"),(247,249,"dengan defisit kalori"),
 (250,253,"ketiga, kena ada komitmen"),(254,256,"baru start diet"),(257,259,"nak saya bantu?"),
 (260,262,"DM CANTIK"),
]
# sanity: contiguous coverage
assert G[0][0]==0 and G[-1][1]==len(W)-1, (G[-1], len(W))
for a,b in zip(G,G[1:]): assert b[0]==a[1]+1, (a,b)
groups=[]
for i,(a,b,t) in enumerate(G):
    s=max(0.15, W[a]['start']-0.06)
    nxt = W[G[i+1][0]]['start']-0.06 if i+1<len(G) else DUR
    e=min(nxt, max(W[b]['end']+0.35, s+0.6), DUR-0.02)
    groups.append((round(s,3),round(e,3),t))
# fix overlaps from min-length rule
for i in range(len(groups)-1):
    if groups[i][1]>groups[i+1][0]: groups[i]=(groups[i][0],groups[i+1][0],groups[i][2])
spans="\n".join(f'    <div id="cap-{i}" class="cap"><span>{html.escape(t)}</span></div>' for i,(s,e,t) in enumerate(groups))
js=",\n".join(f'      [{s},{e}]' for s,e,t in groups)
out=f'''<template>
  <style>
    @font-face {{ font-family: "Inter"; src: url("assets/fonts/Inter-400.woff2") format("woff2"); font-weight: 400; }}
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .cap {{
      position: absolute; left: 0; right: 0; top: 1196px;
      text-align: center; opacity: 0; overflow: visible;
    }}
    .cap span {{
      display: inline-block; padding: 12px 26px 14px; border-radius: 18px;
      background: rgba(12, 12, 14, 0.46);
      color: #fff; font-family: "Inter", sans-serif; font-weight: 400;
      font-size: 60px; line-height: 1.15; letter-spacing: -0.01em; white-space: nowrap;
      text-shadow: 0 1px 2px rgba(0,0,0,0.35);
    }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{spans}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    const T = [
{js}
    ];
    T.forEach(([s, e], i) => {{
      const g = "#cap-" + i;
      tl.fromTo(g, {{ opacity: 0, y: 8 }}, {{ opacity: 1, y: 0, duration: 0.12, ease: "power2.out" }}, s);
      tl.to(g, {{ opacity: 0, duration: 0.08, ease: "power2.in" }}, e - 0.08);
      tl.set(g, {{ opacity: 0, visibility: "hidden" }}, e);
    }});
    window.__timelines["captions"] = tl;
  </script>
</template>
'''
open('compositions/captions.html','w').write(out)
json.dump(groups,open('assets/caption-groups.json','w'),ensure_ascii=False,indent=0)
print(len(groups),'groups; max words',max(len(t.split()) for *_,t in groups))
