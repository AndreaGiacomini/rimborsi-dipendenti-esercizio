# Analisi Circolare MEF n. 18/2026 — Delta rispetto al codice attuale

**Documento di riferimento:** Circolare MEF n. 18/2026 – Rimborsi spese per lavoro dipendente  
**Sostituisce:** Circolare n. 41/2024 (massimali 2025)  
**Decorrenza:** 01/01/2026 (data di sostenimento della spesa)

---

## 1. Massimali aggiornati — `src/rules.py`

| Categoria        | Attuale (fino al 31/12/2025) | Nuovo (dal 01/01/2026)    |
| ---------------- | ---------------------------- | ------------------------- |
| trasferta_italia | 46,48 €/giorno               | **50,00 €/giorno**        |
| trasferta_estero | 77,47 €/giorno               | **85,00 €/giorno**        |
| pasto            | 8,00 €/giorno                | **10,00 €/giorno**        |
| chilometrico     | 0,42 €/km                    | **0,45 €/km**             |
| alloggio         | 150,00 €/notte               | **170,00 €/notte**        |
| lavoro_agile     | _non prevista_               | **3,50 €/giorno** (nuova) |
| PLAFOND_MENSILE  | 1.200,00 €/mese              | **1.400,00 €/mese**       |

---

## 2. Nuova categoria: `lavoro_agile` (home office)

**File coinvolti:** `src/rules.py`, `src/calculator.py`, `src/validator.py`

- Aggiungere `"lavoro_agile"` a `CATEGORIE` e `CATEGORIE_A_GIORNATE` in `rules.py`
- Aggiungere costante `MASSIMALE_GIORNATE_AGILE_MENSILE = 12`
- **Limite mensile specifico:** max 12 giornate esenti per mese per dipendente
- **Calcolo giornate ammesse:**
  ```
  giornate_ammesse = min(giorni_richiesti, max(0, 12 - giorni_agile_già_nel_mese))
  ```
- Il massimale teorico si basa solo sulle giornate ammesse, non su tutte quelle richieste
- **Non ammessa** per date anteriori al 01/01/2026 → respinta con `"categoria non riconosciuta"`
- La quota esente concorre al plafond mensile complessivo

---

## 3. Riduzione progressiva trasferta estera > 5 giorni

**File coinvolti:** `src/calculator.py`

Attualmente `massimale_teorico()` usa sempre 77,47 €/giorno per qualsiasi durata.
Dal 2026 per `trasferta_estero` con più di 5 giornate:

| Fascia      | Massimale              |
| ----------- | ---------------------- |
| Giorni 1–5  | 85,00 €/giorno (pieno) |
| Giorni 6–10 | 76,50 €/giorno (−10%)  |
| Giorni 11+  | 68,00 €/giorno (−20%)  |

**Formula:**

```
G1 = min(G, 5)              → quota piena  = G1 × 85,00
G2 = min(max(G−5, 0), 5)    → quota −10%   = G2 × 76,50
G3 = max(G−10, 0)            → quota −20%   = G3 × 68,00
massimale_teorico = quota piena + quota −10% + quota −20%
```

**Esempio (12 giornate):**  
`(5×85,00) + (5×76,50) + (2×68,00) = 425,00 + 382,50 + 136,00 = 943,50 €`

> La riduzione **non si applica** alle trasferte nazionali (massimale costante per qualsiasi durata).

---

## 4. Incompatibilità lavoro agile / trasferta

**File coinvolti:** `src/validator.py`, `src/storage.py`, `src/app.py`

- Lavoro agile e trasferta (nazionale o estera) non sono cumulabili nello stesso giorno per lo stesso dipendente
- La richiesta è respinta **integralmente** anche se l'overlap riguarda un solo giorno
- Motivazione: `"incompatibilità lavoro agile / trasferta"`
- Solo le richieste **valide** producono incompatibilità
- Il validator deve ricevere le richieste già registrate → impatta `app.py` che deve passarle a `validator.valida()`

---

## 5. Regime transitorio

Il discriminante è la **data di sostenimento** (non la data di presentazione):

| Data sostenimento | Plafond | Massimali        | Lavoro agile | Incompatibilità | Riduzione progressiva |
| ----------------- | ------- | ---------------- | ------------ | --------------- | --------------------- |
| ≤ 31/12/2025      | 1.200 € | vecchi (41/2024) | non ammessa  | non si applica  | non si applica        |
| ≥ 01/01/2026      | 1.400 € | nuovi (18/2026)  | ammessa      | si applica      | si applica            |

**Caso 6.7:** trasferta estera iniziata nel 2025 e conclusa nel 2026 → data sostenimento = data inizio → disciplina previgente per l'intera trasferta.

---

## 6. Riepilogo file da modificare

| File                                 | Modifiche necessarie                                                                                                                        |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/rules.py`                       | Nuovi massimali, nuova categoria `lavoro_agile`, nuovo plafond, costanti 2025 per regime transitorio, aggiornamento `RIFERIMENTO_NORMATIVO` |
| `src/calculator.py`                  | Riduzione progressiva trasferta estera, calcolo giornate agile ammesse, branching su data per regime transitorio                            |
| `src/validator.py`                   | Incompatibilità agile/trasferta, validazione `lavoro_agile`, regime transitorio                                                             |
| `src/storage.py`                     | Funzione conteggio giornate agile già rimborsate nel mese; utilità per verifica sovrapposizione giornate                                    |
| `src/app.py`                         | Passare le richieste esistenti al validator in `_registra()`                                                                                |
| `src/templates/nuova_richiesta.html` | Aggiungere `lavoro_agile` al menu categorie                                                                                                 |
| `src/static/app.js`                  | Mostrare campo "giorni" anche per `lavoro_agile`                                                                                            |
| `src/templates/normativa.html`       | Nuovi massimali, nuova categoria, plafond aggiornato                                                                                        |

---

## 7. Casi di test da coprire (Sezione 6 del PDF)

| Caso | Descrizione                                               | Risultato atteso                                        |
| ---- | --------------------------------------------------------- | ------------------------------------------------------- |
| 6.1  | Plafond quasi esaurito (1.350 € già usati su 1.400)       | Quota esente = capienza residua                         |
| 6.2  | Trasferta estera 6 giornate 2026, importo 500 €           | Massimale 501,50 → esente 500, imponibile 0             |
| 6.3  | Trasferta estera esattamente 5 giornate                   | Nessuna riduzione, massimale = 5×85 = 425               |
| 6.4  | Lavoro agile 15 giornate richieste, 0 già nel mese        | Giornate ammesse = 12, imponibile sulla parte eccedente |
| 6.5  | Lavoro agile con overlap su 1 giorno con trasferta valida | Respinta integralmente con motivazione incompatibilità  |
| 6.6  | Rimborso pasto data 18/12/2025 presentato nel 2026        | Massimali 2025 (8 €/g), plafond 1.200 €                 |
| 6.7  | Trasferta estera iniziata nel 2025 e conclusa nel 2026    | Disciplina previgente (77,47 €/g, no riduzione)         |
