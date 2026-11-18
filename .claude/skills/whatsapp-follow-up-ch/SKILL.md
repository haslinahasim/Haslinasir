---
name: "whatsapp-follow-up-ch"
description: "Follow up existing WhatsApp Business customers as CH (reconnect, group support invite, ✅ check, challenge question) safely and personally. Use for \"run follow up customer lama\" or \"whatsapp follow up CH\"."
---

# WhatsApp Follow-Up — CH (WDT / TPFM)

Skill ni hantar follow-up kepada pelanggan lama melalui **WhatsApp Web (WhatsApp Business)** guna **Claude in Chrome**. Claude baca chat, pilih mesej ikut peringkat, tunjuk draf, dan hantar hanya selepas pengguna setuju.

Untuk pelanggan sedia ada yang bersetuju dihubungi sahaja. Tiada skrip yang boleh bypass sekatan WhatsApp, jadi kekal natural, personal, tak spam.

**Nama coach:** "CH" dalam skrip ialah nama coach. Jika pengguna bukan CH, tanya nama mereka sekali dan gantikan setiap "CH" dengan nama itu dalam draf.

## Peraturan keselamatan
- Mesej hanya pelanggan yang setuju dihubungi. Jangan blast.
- Satu mesej pada satu masa. Mesej seterusnya hanya selepas pelanggan reply.
- Belum reply: tunggu 2–3 hari, hantar SATU follow-up ringkas.
- Masih senyap: berhenti sehingga pelanggan hubungi semula.
- Jika pelanggan tak mahu terima mesej: berhenti terus, hormati.
- Jangan hantar kesemua skrip kepada orang yang sama. Pilih ikut situasi.
- Sebelum hantar, tunjuk setiap draf kepada pengguna dan tunggu kelulusan. Jangan hantar apa-apa tanpa kelulusan.

## Flow utama
Hari 1 → Mesej 1. Reply → Mesej 2. Tiada reply 2–3 hari → Mesej 3. Reply ✅ → Mesej 4, kemudian sambung secara personal.

### Mesej 1 — Reconnect
Salam, hai cik 🥰 Apa khabar?

CH ni. Macam mana journey weight loss cik sekarang? Okay ke setakat ni?

Kalau ada apa-apa cabaran, let me know tau. CH boleh bantu ❤️
reply je NAK CH

### Mesej 2 — Ajak group support (selepas reply)
I see 🥰

Cik nak tak join group support CH? Kita boleh sama-sama dapatkan semangat, sharing tips dan stay motivated dalam journey ni.

Group ni FREE je ❤️

### Mesej 3 — Follow-up ✅ (jika senyap 2–3 hari)
CH nak check sikit 🥰

Kalau cik masih nak CH bantu dalam journey weight loss, reply ✅ je tau.

Nanti CH follow up personally ❤️

### Mesej 4 — Bila reply ✅
Yeay, thank you cik! 🥰

CH nak tahu sikit, sekarang cabaran paling besar cik yang mana satu?

1️⃣ Susah nak control makan
2️⃣ Berat stuck
3️⃣ Craving selalu
4️⃣ Susah nak konsisten

Reply nombor je pun okay ❤️

## 10 skrip customer lama (tanpa "cik") — pilih SATU ikut situasi
1. Friendly Reconnect: Salam hai 🥰 Apa khabar? CH ni. Lama tak check in. Macam mana journey weight loss sekarang? Semua okay ke? ❤️
2. Check Cabaran: Hai ❤️ CH nak check sikit, sekarang ada apa-apa cabaran tak nak maintain berat atau jaga pemakanan? Share je tau, mana yang CH boleh bantu 🥰
3. Check Konsistensi: Hai 🥰 Macam mana rutin makan dan aktiviti sekarang? Masih on track ke atau dah lama berehat? No pressure tau, CH just nak check ❤️
4. Jemput Group Support: I see 🥰 CH ada group support untuk bantu kita stay motivated dan konsisten. Nak join tak? FREE je ❤️
5. Follow-Up ✅: Hai ❤️ Kalau masih nak CH bantu dalam journey weight loss, reply ✅ je tau. CH boleh follow up ikut apa yang diperlukan 🥰
6. Check Progress: Hai 🥰 CH curious nak tahu, sejak kali terakhir kita coaching, ada perubahan tak pada berat, ukuran badan atau energy? Share dengan CH tau ❤️
7. Pelanggan Lama Senyap: Salam ❤️ Lama kita tak catch up kan. Hope sihat dan semuanya okay. Kalau perlukan support untuk restart rutin sihat, CH masih ada tau 🥰
8. Jemput Restart: Hai 🥰 Kalau rasa nak restart balik healthy routine, CH ada group coaching yang boleh bantu susun semula rutin makan dan aktiviti. Nak CH share details? ❤️
9. Check Stok Produk: Hai ❤️ CH nak check, stok produk masih okay ke sekarang? Kalau perlukan bantuan untuk susun semula rutin penggunaan, boleh bagitahu CH tau 🥰
10. Follow-Up Terakhir: Hai 🥰 CH just nak check sekali lagi. Kalau perlukan support untuk journey sihat, boleh mesej CH bila-bila masa tau. Kalau belum ready pun tak apa. Take care ❤️

Skrip 10 ialah mesej terakhir. Selepas itu, berhenti.

## Cara run (Claude in Chrome + WhatsApp Web)

### Sebelum mula (sekali setiap sesi)
1. Muatkan tool Claude in Chrome sekali gus (ToolSearch: `select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__find,mcp__claude-in-chrome__get_page_text`). Panggil `tabs_context_mcp` dulu. Jika tool tiada, beritahu pengguna untuk pasang extension Claude in Chrome dan berhenti.
2. Tanya nama pengguna (untuk ganti "CH") jika belum tahu.
3. Tanya **nama label WhatsApp Business** yang mengandungi senarai pelanggan lama. Label berbeza untuk setiap ahli team. Ingat untuk sepanjang sesi, jangan tanya lagi.
4. Buka `https://web.whatsapp.com` dalam tab baru. Jika nampak QR code / belum login, berhenti dan minta pengguna login dulu.

### Untuk setiap chat dalam label
1. Buka label tersebut (Chats → filter/menu Labels → pilih label) dan senaraikan chat di dalamnya.
2. Buka satu chat. Baca sejarah terkini (mesej terakhir, siapa hantar, tarikh).
3. Tentukan peringkat:
   - Belum ada mesej follow-up dari kita → **Mesej 1** (atau satu skrip yang paling sesuai dari 10 skrip)
   - Pelanggan dah reply Mesej 1 → **Mesej 2**
   - Mesej terakhir kita 2–3 hari atau lebih, tiada reply, dan belum pernah hantar follow-up → **Mesej 3** (sekali sahaja)
   - Pelanggan reply ✅ → **Mesej 4**, selepas itu beritahu pengguna untuk sambung secara personal
   - Mesej terakhir kita kurang 2 hari dan belum reply → **skip, tunggu**
   - Dah dapat follow-up tapi masih senyap → **skip, berhenti**
   - Pelanggan minta berhenti / tak mahu terima mesej → **skip terus**
   - Perbualan sedang berjalan secara personal → **skip**, jangan ganggu
4. Tunjuk kepada pengguna: nama kontak, ringkasan chat, peringkat, dan draf penuh (dengan "CH" diganti nama pengguna). **Tunggu OK.** Jika pengguna edit, guna versi mereka.
5. Selepas OK: taip draf dalam kotak mesej (kekalkan baris baru guna Shift+Enter) dan hantar. Semak mesej keluar dengan betul.
6. Teruskan ke chat seterusnya.

### Kadar
- Kumpulan kecil: maksimum 5 kontak satu pusingan, kemudian tanya pengguna nak sambung atau tidak.
- Rentak natural, ada jeda antara chat. Jangan blast. Satu mesej satu masa setiap kontak.

### Penutup
Beri ringkasan: siapa dapat mesej apa, siapa di-skip dan sebab, dan siapa perlu disambung secara personal oleh pengguna.

