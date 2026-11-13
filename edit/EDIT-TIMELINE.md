# Edit timeline: "3 perkara sebelum diet"

Source: IMG_6606 (1080×1920, 99.0 s) → final cut **87.7 s**.
Rebuild: `python3 tools/build_captions.py && python3 tools/build_scenes.py && npx hyperframes render`.
(`assets/source.mp4` / `assets/cut.mp4` are not committed; the cut list is in `assets/keep.json`.)

## 1. Cuts (filler, pauses, false starts)
- 28 dead-air pauses/hesitations (0.35 – 0.83 s each) were cut down to about 0.14 s, giving 29 jump-cut segments (`assets/keep.json`).
- False start removed: "…tiga elemen ni, ~~faham tentang~~, pertama kali itu, fahamkan…" (source 86.9–88.7 s).
- Kept: slang and code-switching ("boring", "enjoy sikit", "eat clean", "last", "kaki makan").

## 2. Captions
70 groups, 3–5 words, lowercase, Inter Regular, soft dark pill, sitting at chest height (y≈1196), never over the face.
Spelling standardised from the transcript: kalori, defisit, nasi lemak, roti canai, meal replacement, create rutin, komitmen.

## 3. B-roll (translucent overlay cards, no cutaways)
All visuals sit in the safe band **y 176–396 px**: below the app's top bar, above the face (the top of the face never goes above y≈398), and never over the captions (y≈1196). The cards are frosted, see-through white (66% opacity with a background blur), so the video always shows through.
| Cut time | Said | Visual |
|---|---|---|
| 22.95–27.20 | kuih, kerepek, nasi lemak, roti canai | "sarapan yang selalu teringin" chips pop in as named |
| 32.75–40.40 | meal replacement… create rutin | her own shake + Formula 1 photo (`assets/meal-replacement.jpg`) next to a routine card |
| 44.30–47.45 | bakar kalori, defisit kalori | horizontal bars: makan 1,600 vs dibakar 2,000, −400 gap (example numbers) |
| 51.65–55.25 | bersenam, lepas tu tambah makan | −300 / +450 / hasilnya +150 kcal (example numbers) |
| 67.95–70.72 | tiga hari tiga malam je | week strip, 3 days ticked |
| 77.40–84.95 | recap 3 elemen | 3 ticks: ada rutin · bakar & defisit kalori · komitmen |

## 4. Face-tracked slow zoom (emotional beats)
Face found by detection (centre ≈ x545, y745). Zoom is anchored on the face, eases in, and resets on the next cut.
| Cut time | Beat | Scale |
|---|---|---|
| 14.55–17.05 | "memang kena boring" | 1.14 |
| 55.25–57.99 | "celah mana nak turun berat badan?" | 1.14 |
| 61.65–63.89 | "sebab apa? bila bakar kalori, awak tambah makanan" | 1.12 |
| 70.72–77.31 | "kawan dengan semua kaki makan, memang tak turun" | 1.16 |
| 84.95–87.70 | CTA "nak saya bantu, DM CANTIK" | 1.12 |
