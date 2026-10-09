# Route digest — instructions for the scheduled Claude routine

You maintain `digest.json` in this repository. A personal iPhone travel app downloads it (raw GitHub URL)
and shows it to two Lithuanian travellers on a car trip. Your job each run: research what changed for the
route, translate it into Lithuanian, rate the risk, and publish an updated `digest.json`.

## 0. When to stop
Run `date -u +%Y-%m-%dT%H:%M:%SZ`. If the date is after **2026-11-09**, do nothing (no commit) and finish.

## 0b. Every run — no shortcuts
Do the **full research pass** every time (at least one local-language search per country on the upcoming days of the
route, plus the official sources in §3), even if `digest.json` looks fresh. Always set `updated` to the current time and
**commit and push every run**, even when nothing else changed — the app shows `updated` as "last checked".

## 1. The trip (dates are fixed)
| Day | Date (local) | Route |
|---|---|---|
| 1 | Fri 2026-10-30 | Lithuania → Via Baltica (A5/S61) → Warsaw bypass (S8) → A2 Poznań → Świecko → Berlin ring A10 → A2 → Peine (night) |
| 2 | Sat 10-31 | Peine → A2/A1 → Köln (2 h at the Dom) → Aachen (night) |
| 3 | Sun 11-01 (All Saints) | Aachen → Belgium (Liège, E40/E42, Tournai) → northern France (A2/A26/A29/A28) → Honfleur → Lisieux → Rouen (night) |
| 4 | Mon 11-02 | Rouen → Étretat → Rouen (night) |
| 5 | Tue 11-03 | Rouen → Chartres → around Paris (A104/N104/A86) → A4 → Reims (night) |
| 6 | Wed 11-04 | Reims, Épernay, Hautvillers, Montagne de Reims (night Reims) |
| 7 | Thu 11-05 | Reims → A4/A31 Verdun/Metz → Vosges passes → Colmar (night) |
| 8 | Fri 11-06 | Eguisheim → Rhine crossing → A5/A6/A3/A7 → Würzburg → Bamberg (night) |
| 9 | Sat 11-07 | Bamberg → A73/A9/A72/A4 → Bautzen → Görlitz/Zgorzelec → A4 Wrocław → A1 → Częstochowa (night, Jasna Góra) |
| 10 | Sun 11-08 | Częstochowa → Warsaw → Łomża → Suwałki → Lithuania |

Focus on **today and the coming days** of the trip (before the trip: announced events for the trip dates).
Days already in the past: keep their entries but do not research them further.

## 2. Canonical places and roads (keep these ids; you may add a place only if the route really includes it)
Places: `warszawa` Varšuva [1,10] · `czestochowa` Čenstakava [9,10] · `lomza` Lomža [10] · `braunschweig-peine` Peinė / Braunšveigas [1,2] ·
`koln` Kelnas [2] · `aachen` Achenas [2,3] · `belgium-transit` Belgija (Lježas, Briuselio žiedas, Turnė) [3] · `honfleur` Onflioras [3] ·
`lisieux` Lisieux [3] · `rouen` Ruanas [3,4,5] · `etretat` Etreta [4] · `chartres` Šartras [5] · `reims` Reimsas [5,6,7] ·
`epernay-hautvillers` Epernė ir Otvilė [6] · `verdun-metz` Verdenas ir Mecas [7] · `vosges` Vogėzų perėjos [7] · `colmar` Kolmaras [7,8] ·
`eguisheim` Egishaimas [8] · `wurzburg` Viurcburgas [8] · `bamberg` Bambergas [8,9] · `bautzen` Budyšinas [9] · `gorlitz-zgorzelec` Gerlicas / Zgoželecas [9]

Roads: `lt-a5-s61` Via Baltica (A5 / S61) [1,10] · `pl-s8` S8 Varšuvos apvažiavimas [1,10] · `pl-a2` A2 Varšuva–Svieckas [1] ·
`pl-a4` A4 Zgoželecas–Vroclavas–Gliwice [9] · `pl-a1` A1 į Čenstakavą [9,10] · `de-a10-a2` A10 Berlyno žiedas ir A2 [1] ·
`de-a1-a3-koln` A1/A3 aplink Kelną (Leverkuzenas) [2] · `de-a4-aachen` A4 Kelnas–Achenas [2,3] · `be-e40-e42` E40 / E42 Belgijoje [3] ·
`fr-a2-a26-a29-a28` Šiaurės Prancūzijos autostrados (A2, A26, A29, A28) [3] · `fr-a13` A13 / A28 aplink Ruaną [3,4,5] ·
`fr-paris-ring` Paryžiaus apvažiavimas (A104 / N104 / A86) [5] · `fr-a4-reims` A4 Paryžius–Reimsas–Mecas [5,7] ·
`fr-champagne-roads` Šampanės keliai (D951, A26) [6] · `fr-a4-a31` A4 / A31 Lotaringijoje [7] · `vosges-passes` Vogėzų perėjos [7] ·
`rhine-crossing` Reino perėja (A35 / Breisachas / A5) [8] · `de-a5-a6-a3-a7` A5 / A6 / A3 / A7 [8] · `de-a73-a70` A73 / A70 prie Bambergo [8,9] ·
`de-a9-a72-a4` A9 / A72 / A4 į Gerlicą [9]

## 3. What to research (use WebSearch / WebFetch; search in local languages)
- France (French): strikes / "journée de mobilisation" / "manifestation" / "blocage" / "pénurie de carburant" (prix-carburants.gouv.fr disponibilités),
  préfecture announcements for Rouen, Reims, Metz, Colmar; Bison Futé; autoroute closures; Météo-France vigilance.
- Germany (German): Streik, Demo/Demonstration, Vollsperrung (verkehr.autobahn.de), DWD Warnungen, Köln/Aachen/Bamberg/Würzburg/Bautzen city news.
- Belgium (French/Dutch): grève / staking / manifestation, E40/E42 works (SOFICO, Verkeerscentrum), KMI/IRM warnings.
- Poland (Polish): protest / blokada / utrudnienia on A2, S8, A1, A4, S61, GDDKiA, police actions (e.g. "Znicz"), border checks, IMGW warnings.
- Lithuania (Lithuanian): eismoinfo.lt, Via Baltica works.
Prefer official sources (police, prefectures, ministries, motorway operators, weather services) and reputable press. Never invent facts or URLs.

## 4. Risk levels (1–4) — calm, factual, sourced; no stereotypes, no fear-mongering
1 **Ramu** — normal conditions. 2 **Dėmesio** — minor known risks (pickpockets at tourist spots, roadworks, regular congestion).
3 **Atsargiai** — announced strike/demonstration on their day there, documented car break-in / rest-area theft hotspots on the route,
significant road restrictions, official orange weather warning. 4 **Pavojinga** — riots, blockades, closed roads, red warnings, official advice to avoid.
A level applies to the specific days they are there. Every reason needs a source in `sources`.

## 5. digest.json format (keep exactly; all user-facing text in Lithuanian with correct diacritics)
```json
{
  "updated": "2026-10-29T04:05:00Z",
  "summary": "2–4 sentences: overall picture for the whole trip and what matters most now",
  "top": ["item-id", "..."],
  "dayNotes": [{"day": 1, "note": "≤140 chars: what to watch that day"}],
  "places": [{"id": "reims", "name": "Reimsas", "country": "FR", "days": [5,6,7], "level": 3,
              "reasons": ["≤120 chars"], "tips": ["≤120 chars"], "sources": ["https://..."]}],
  "roads":  [{"id": "...", "name": "...", "country": "FR", "days": [5], "level": 2, "reasons": [], "tips": [], "sources": []}],
  "items":  [{"id": "unique-id", "title": "Lithuanian translation of the headline", "text": "≤220 chars: what it means for them",
              "days": [7], "places": ["reims"], "importance": 3, "level": 3, "date": "YYYY-MM-DD",
              "source": "Le Parisien", "url": "https://..."}]
}
```
- `importance`: 3 = must know, 2 = useful, 1 = background. `top`: up to 8 item ids, most important first.
- Keep ~15–40 items; drop items that are no longer relevant (event passed, resolved) — but keep anything still affecting upcoming days.
- `dayNotes` for every day 1–10 ("Ramu — žinomų sutrikimų nėra" when nothing).
- `updated` = current UTC time from `date -u`.

## 6. Privacy — never write personal data
No names, no home town (never name the travellers' home town; write "namai" instead), no address, phone numbers, car plate, policy or booking numbers. Only public information about places and roads.

## 7. Publish
0. Write the file with `json.dump(d, f, ensure_ascii=False, indent=1)` (readable Lithuanian, small diffs).
1. Validate: `python3 -c "import json;d=json.load(open('digest.json'));assert all(1<=x['level']<=4 for x in d['places']+d['roads'])"` and that every
   `top` id exists in `items`.
2. `git add digest.json && git commit -m "digest: <UTC time>"` and `git push origin HEAD:main`.
   If pushing to `main` is not allowed, push the same commit to branch `digest` (`git push -f origin HEAD:digest`) — the app reads both and uses the newer.
3. Finish with a 3-line summary of what changed.
