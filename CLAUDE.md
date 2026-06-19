# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Boundaries

- **Do not read, edit, or delete anything inside `data/`**. That directory contains live user data (`richieste.json`). It is not part of the codebase — treat it as an external runtime artifact.

## Setup

Requirements: Python 3.10+, no external services or databases.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The only runtime dependency is `data/richieste.json`, which is already present in the repo as an empty array `[]`. The app reads and writes it directly — no migration or initialization step needed.

## Commands

```bash
# Run all tests
pytest -v

# Run a single test file
pytest tests/test_calculator.py -v

# Run a single test by name
pytest tests/test_validator.py::test_richiesta_valida -v

# Start the Flask development server
flask --app src/app run

# Install dependencies
pip install -r requirements.txt
```

## Architecture

This is a Flask web application for managing Italian employee expense reimbursements under MEF circular regulations. There is no database — all requests are persisted in `data/richieste.json` as a flat JSON array, loaded and written in full on every request.

### Modules

**[src/rules.py](src/rules.py)** — Pure constants, no logic. Single source of truth for all regulatory parameters: daily allowance ceilings (`MASSIMALI_GIORNALIERI`), per-km rate (`MASSIMALE_KM`), per-night rate (`MASSIMALE_NOTTE`), and the monthly tax-exemption cap (`PLAFOND_MENSILE`). Also defines `CATEGORIE` (display labels) and `CATEGORIE_A_GIORNATE` (the three day-based categories). When updating regulations, change only this file.

**[src/calculator.py](src/calculator.py)** — Two public functions:
- `massimale_teorico(richiesta)` — computes the theoretical exemption ceiling for a request based on its category and quantity fields (`giorni`, `km`, or `notti`).
- `calcola(richiesta, esente_gia_riconosciuta)` — applies the two-step capping logic: first caps the exempt amount at the theoretical ceiling (`min(importo, massimale_teorico)`), then caps it again at the remaining monthly plafond capacity. Returns `(quota_esente, quota_imponibile, dettaglio)`. The `dettaglio` dict records the three intermediate values for auditability.

**[src/validator.py](src/validator.py)** — Single public function `valida(richiesta)` returning `(bool, str)`. Validates fields in order: `dipendente`, `categoria`, `importo`, `data`, then category-specific quantity fields. Uses early-return guard clauses; stops at the first failure.

**[src/storage.py](src/storage.py)** — JSON file I/O via `carica()` / `salva()`. The path `PERCORSO_DATI` is a module-level constant (monkeypatched in tests). Key helper: `esente_riconosciuta_nel_mese(richieste, dipendente, mese)` sums `quota_esente` across all `stato == "valida"` records for a given employee and month — this is what the calculator uses to determine remaining plafond capacity.

**[src/app.py](src/app.py)** — Flask application with 5 routes. All form coercion happens here via `_numero()` and `_intero()` helpers before the dict is handed off to the other layers. `_registra()` is the single write path: it loads storage, builds the request dict, validates, calculates, appends, and saves — all in one transaction-like sequence. Rejected requests are also saved (with `stato == "respinta"`, `quota_esente == 0.0`) so there is a complete audit trail.

### Routes

| Method | Path | Description |
|---|---|---|
| GET | `/` | Redirects to `/richieste` |
| GET/POST | `/nuova` | Submit a new reimbursement request |
| GET | `/richieste` | List all requests; filterable by `?dipendente=` and `?mese=` |
| GET | `/riepilogo` | Monthly summary per employee: totals and plafond usage % |
| GET | `/normativa` | Display current regulatory limits from `rules.py` |

### Data flow for a new request

```
POST /nuova
  → _registra(form)
      → storage.carica()                         # load full archive
      → validator.valida(richiesta)              # (bool, reason)
      → storage.esente_riconosciuta_nel_mese()   # plafond already used
      → calculator.calcola(richiesta, già_usata) # (esente, imponibile, dettaglio)
      → storage.salva(richieste)                 # write full archive back
```

### Request record schema

Each record in `data/richieste.json` has these fields:

```
id, dipendente, data, categoria, importo, giorni, km, notti,
stato,           # "valida" | "respinta"
motivazione,     # rejection reason or ""
quota_esente,    # exempt amount (0.0 if respinta)
quota_imponibile,
dettaglio        # {massimale_teorico, esente_teorica, capienza_plafond} or null
```

**Categories:** `trasferta_italia`, `trasferta_estero`, `pasto` (day-based) · `chilometrico` (km-based) · `alloggio` (night-based)

## Code style

**Naming language:** identifiers, dict keys, docstrings, and error messages are all in Italian (e.g. `dipendente`, `quota_esente`, `mese_riferimento`). This is intentional — keep it consistent.

**Naming conventions:**
- `snake_case` for functions and variables
- `UPPER_SNAKE_CASE` for module-level constants in `rules.py`
- No type hints anywhere in the codebase

**Docstrings:** every module has a one-line module docstring. Public functions get a single-line docstring only when the signature alone is not self-explanatory. No multi-line docstrings.

**Monetary values:** always stored and returned as `float`, always rounded with `round(..., 2)` at the point of computation — never at display time.

**Dict access:** use `richiesta["key"]` (direct) when the key is guaranteed to exist; use `richiesta.get("key")` at the validation boundary where values may be missing.

**Guard clauses:** `validator.py` uses early-return `(False, "reason")` for each invalid condition, with a final `return True, ""`. Follow this pattern for any new validation logic.

**No linter config** is present in the repo. Follow PEP 8 spacing and keep lines reasonably short.

## Regulatory context

The current rules implement **Circolare MEF n. 41/2024**. A planned update to Circolare MEF 18/2026 is documented in [doc/analisi-circolare-2026.md](doc/analisi-circolare-2026.md), which includes the exact code changes needed, updated limits, a new `lavoro_agile` category, transitional date logic, and 7 test cases to implement.

## Tests

Three test files, each with a distinct scope:

| File | Scope | Pattern |
|---|---|---|
| [tests/test_calculator.py](tests/test_calculator.py) | Unit — exempt/taxable calculation logic | `TestMassimaleTeorico` + `TestCalcola` classes |
| [tests/test_validator.py](tests/test_validator.py) | Unit — field validation per category | standalone functions |
| [tests/test_app.py](tests/test_app.py) | HTTP integration end-to-end | `client` fixture with Flask test client |

**`richiesta(**campi)` helper** — present in all three files; builds a valid request dict with defaults (`pasto`, `Maria Rossi`, `2025-10-06`) and overrides only the passed fields. Use it to build fixtures in new tests.

**`client` fixture in `test_app.py`** — uses `monkeypatch.setattr(storage, "PERCORSO_DATI", tmp_path / "richieste.json")` to isolate the JSON file in a temporary directory. Each test starts with empty storage. After POST requests, call `storage.carica()` directly to assert on persisted state.

**What the integration tests cover:**
- Redirect `/` → `/richieste`
- All main routes return 200
- Valid submission: `stato == "valida"`, correct `quota_esente` and `quota_imponibile`
- Rejected submission: `stato == "respinta"`, record saved with `quota_esente == 0.0`
- Amount above ceiling → exempt/taxable split
- Monthly plafond shared across multiple requests from the same employee in the same month
- Employee filter on `/richieste`
- Totals on `/riepilogo`
- Regulatory values on `/normativa`

**When adding a new category or changing limits in `rules.py`**, update:
1. `TestMassimaleTeorico` in `test_calculator.py` with the new expected ceiling
2. `test_validator.py` with the required fields for the category
3. `test_normativa_mostra_massimali_vigenti` in `test_app.py` with the new values
