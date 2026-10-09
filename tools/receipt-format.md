# Receipt JSON format (receipt runs, ROUTINE.md §0d)

One JSON object per receipt. Numbers are JSON numbers (decimal point). Lithuanian text uses correct diacritics.

```json
{
  "isReceipt": true,
  "merchant": "Le Bistrot d'Arthur",
  "merchantType": "restoranas",
  "address": "12 rue Damiette",
  "city": "Ruanas",
  "country": "FR",
  "date": "2026-11-02T20:41",
  "currency": "EUR",
  "items": [
    {"name": "Café crème", "nameLt": "Kava su pienu", "product": "kava.pienu", "category": "gerimai.kava",
     "qty": 2, "size": null, "unitPrice": 3.2, "total": 6.4},
    {"name": "Pression 50cl", "nameLt": "Alus iš statinės 0,5 l", "product": "alus", "category": "gerimai.alus",
     "qty": 1, "size": 0.5, "unitPrice": 7.5, "total": 7.5}
  ],
  "subtotal": null, "tax": 2.32, "tip": null, "total": 13.9,
  "payment": "kortele",
  "language": "fr",
  "lines": [{"original": "CAFE CREME   2 x 3,20   6,40", "lt": "Kava su pienu   2 × 3,20   6,40"}],
  "notes": ["Aptarnavimo mokestis įskaičiuotas į kainas"]
}
```

Rules
- Extract exactly what is printed; OCR text may contain errors — correct obvious ones (0/O, 1/l, missing decimal comma)
  using the line totals and the receipt total. One item per purchased line; quantity multiplied out; a discount is a
  negative line; service charge or tip → category `aptarnavimas` (and `tip` when it is a tip).
- `nameLt`: short, natural Lithuanian. Well-known dish names keep the original in parentheses:
  "Kruasanas (croissant)", "Choucroute garnie (raugintų kopūstų patiekalas)".
- `size`: litres when printed (25cl → 0.25, 0,5 l → 0.5) or implied by a standard pour: demi 0.25, pinte 0.5,
  galopin 0.125, verre de vin 0.125–0.15, pichet/carafe as printed (25/50 cl), Halbe 0.5, Maß 1, Seidel/Pils 0.3,
  kufel 0.5, mały 0.3; else null. `unitPrice`: price of one unit, else null.
- `city`: the Lithuanian name when it is a place of the trip (the run text lists the plan's names), else the local name.
  `country`: ISO 3166-1 alpha-2. `date`: local "YYYY-MM-DDTHH:MM" from the receipt (or "YYYY-MM-DD"), else null.
- `payment`: "kortele", "grynieji" or null. **Never** output card numbers, terminal or authorisation codes, loyalty or
  customer numbers, cashier or customer names — write "•••" instead (also inside `lines`).
- `lines`: every printed line, original ↔ Lithuanian translation.
- If the text is not a receipt: `{"isReceipt": false, "notes": ["…why…"]}`.

`merchantType`: restoranas, kavine, baras, kepykla, parduotuve, degaline, parkingas, kelio_mokestis, muziejus, vaistine,
suvenyrai, sendaikciai, nakvyne, kita.

`category` (detailed): gerimai.kava, gerimai.karsti (tea, hot chocolate), gerimai.gaivieji (water, juice, soft drinks),
gerimai.alus (beer, cider), gerimai.vynas (wine, champagne by the glass/bottle consumed), gerimai.stiprus, kepiniai,
desertai, pusryciai, uzkandziai (starters, soups, snacks), patiekalai (main dishes), suriai, greitas (sandwiches,
burgers, crêpes, kebab, pizza slices), produktai (groceries), aptarnavimas, kuras.degalai, kuras.kita, keliai.mokestis,
keliai.parkingas, bilietai.lankytinos, bilietai.degustacijos, bilietai.termos, pirkiniai.lauktuves,
pirkiniai.sendaikciai, pirkiniai.vynas (bottles bought to take home), pirkiniai.higiena, pirkiniai.kita,
nakvyne.mokestis (tourist tax), nakvyne.kita, kita.

`product` (for price comparison between cities; the closest key or "kita"): kava.espresso, kava.pienu (café crème,
cappuccino, latte, Milchkaffee), kava.juoda (filter / americano), arbata, sokoladas, vanduo, gaivieji, sultys, alus,
sidras, vynas.taure, vynas.butelis, sampanas.taure, sampanas.butelis, kruasanas, sokoladine (pain au chocolat),
duona (baguette, bread), pyragaitis (pastry, tart), ledai, krepas (crêpe, galette), sumustinis, mesainis, pica, salotos,
sriuba, pagrindinis, desertas, meniu (formule / menu du jour), pusryciai, degalai (per litre: size = litres, unitPrice =
price per litre), parkingas, muziejus, kita.
