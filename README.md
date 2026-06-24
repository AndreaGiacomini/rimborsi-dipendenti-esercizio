# Rimborsi Dipendenti

Strumento interno dell'ufficio HR per la gestione delle richieste di rimborso spese dei
dipendenti. Per ogni richiesta l'applicazione calcola la **quota esente** IRPEF e la
**quota imponibile** secondo i massimali della normativa vigente, applica le regole di
validazione e tiene traccia del plafond mensile di esenzione di ciascun dipendente.

## Funzionalità

- **Nuova richiesta**: inserimento di una richiesta di rimborso (trasferta Italia,
  trasferta estero, pasto, chilometrico, alloggio) con calcolo immediato di quota
  esente e imponibile e dettaglio del calcolo.
- **Richieste**: elenco di tutte le richieste, filtrabile per dipendente e mese, con
  stato (valida / respinta) e dettaglio espandibile.
- **Riepilogo mensile**: totali esente/imponibile per dipendente e mese, con barra di
  utilizzo del plafond mensile.
- **Normativa vigente**: massimali correnti applicati dal sistema.

## Requisiti

- Python 3.10 o superiore
- Nessun database e nessun servizio esterno: i dati sono salvati in `data/richieste.json`

## Avvio

```bash
python -m venv .venv
source .venv/bin/activate        # su Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app src.app run
```

L'applicazione è raggiungibile su <http://127.0.0.1:5000>.

## Test

```bash
pytest
```

## Struttura del progetto

```
src/
├── app.py          # routes Flask
├── rules.py        # parametri normativi vigenti (massimali, plafond)
├── calculator.py   # calcolo quota esente / quota imponibile
├── validator.py    # regole di validazione delle richieste
├── storage.py      # persistenza su file JSON
├── templates/      # pagine HTML (Jinja)
└── static/         # CSS e JavaScript
data/
└── richieste.json  # archivio delle richieste
tests/              # test pytest (calcolo, validazione, routes)
```
