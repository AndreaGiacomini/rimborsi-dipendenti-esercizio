"""Test cases from Section 6 of Circolare MEF 18/2026.

One test per case, exactly as specified in doc/analisi-circolare-2026.md §7.
"""

from src import calculator, storage, validator


def richiesta(**campi):
    base = {
        "dipendente": "Maria Rossi",
        "data": "2026-03-10",
        "categoria": "pasto",
        "importo": 10.0,
        "giorni": 1,
        "km": None,
        "notti": None,
    }
    base.update(campi)
    return base


def richiesta_valida_salvata(categoria, data, giorni, importo):
    """Builds a dict that looks like a stored valid request (for incompatibility checks)."""
    return {
        "dipendente": "Maria Rossi",
        "data": data,
        "categoria": categoria,
        "importo": importo,
        "giorni": giorni,
        "km": None,
        "notti": None,
        "stato": "valida",
        "quota_esente": importo,
    }


# --- Case 6.1 ---
# Plafond quasi esaurito (1.350 € già usati su 1.400).
# Expected: quota esente = capienza residua (50 €), eccedenza imponibile.

def test_6_1_plafond_quasi_esaurito():
    r = richiesta(categoria="alloggio", notti=1, importo=100.0)
    esente, imponibile, dettaglio = calculator.calcola(r, esente_gia_riconosciuta=1350.0)
    assert esente == 50.0
    assert imponibile == 50.0
    assert dettaglio["capienza_plafond"] == 50.0


# --- Case 6.2 ---
# Trasferta estera 6 giornate 2026, importo 500 €.
# Expected: massimale 501.50 (5×85 + 1×76.50) → esente 500, imponibile 0.

def test_6_2_trasferta_estera_6g_importo_500():
    r = richiesta(categoria="trasferta_estero", giorni=6, importo=500.0)
    assert calculator.massimale_teorico(r) == 501.50
    esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0)
    assert esente == 500.0
    assert imponibile == 0.0


# --- Case 6.3 ---
# Trasferta estera esattamente 5 giornate 2026.
# Expected: nessuna riduzione progressiva, massimale = 5 × 85 = 425.

def test_6_3_trasferta_estera_5g_nessuna_riduzione():
    r = richiesta(categoria="trasferta_estero", giorni=5, importo=500.0)
    assert calculator.massimale_teorico(r) == 425.0
    esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0)
    assert esente == 425.0
    assert imponibile == 75.0


# --- Case 6.4 ---
# Lavoro agile 15 giornate richieste, 0 già nel mese.
# Expected: giornate ammesse = 12, massimale = 42 €, parte eccedente imponibile.

def test_6_4_lavoro_agile_15g_cap_a_12():
    r = richiesta(
        categoria="lavoro_agile",
        giorni=15,
        giorni_agile_gia_nel_mese=0,
        importo=52.50,  # 15 × 3.50
    )
    assert calculator.massimale_teorico(r) == 42.0  # 12 × 3.50
    esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0)
    assert esente == 42.0
    assert imponibile == 10.50


# --- Case 6.5 ---
# Lavoro agile con overlap di 1 giorno con trasferta valida esistente.
# Expected: richiesta respinta con "incompatibilità lavoro agile / trasferta".

def test_6_5_agile_overlap_trasferta():
    trasferta = richiesta_valida_salvata("trasferta_italia", "2026-03-10", giorni=3, importo=150.0)
    agile = richiesta(data="2026-03-12", categoria="lavoro_agile", giorni=1)
    ok, motivazione = validator.valida(agile, [trasferta])
    assert not ok
    assert motivazione == "incompatibilità lavoro agile / trasferta"


# --- Case 6.6 ---
# Rimborso pasto con data di sostenimento 18/12/2025, presentato nel 2026.
# Expected: si applicano massimali 2025 (8 €/g) e plafond 1.200 €.

def test_6_6_pasto_data_2025_usa_regole_previgenti():
    r = richiesta(data="2025-12-18", categoria="pasto", giorni=1, importo=10.0)
    assert calculator.massimale_teorico(r) == 8.0  # vecchio massimale, non 10.0
    esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0)
    assert esente == 8.0
    assert imponibile == 2.0


def test_6_6_pasto_data_2025_plafond_1200():
    r = richiesta(data="2025-12-18", categoria="pasto", giorni=1, importo=8.0)
    esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1200.0)
    assert esente == 0.0     # vecchio plafond 1.200 già esaurito
    assert imponibile == 8.0


# --- Case 6.7 ---
# Trasferta estera iniziata nel 2025 e conclusa nel 2026.
# Discriminante = data di inizio (2025) → disciplina previgente per l'intera trasferta:
# massimale costante 77,47 €/g, nessuna riduzione progressiva.

def test_6_7_trasferta_estera_iniziata_2025():
    r = richiesta(data="2025-12-28", categoria="trasferta_estero", giorni=5, importo=400.0)
    assert calculator.massimale_teorico(r) == 387.35  # 5 × 77.47, no fascia
    esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0)
    assert esente == 387.35
    assert imponibile == 12.65


def test_6_7_trasferta_estera_2025_no_riduzione_progressiva():
    r = richiesta(data="2025-12-15", categoria="trasferta_estero", giorni=12, importo=1000.0)
    assert calculator.massimale_teorico(r) == 929.64  # 12 × 77.47, no fasce 2026
