"""Parametri normativi per il calcolo dei rimborsi spese.

Massimali vigenti: Circolare MEF n. 18/2026, in vigore dal 01/01/2026.
Massimali 2025 (archivio): Circolare MEF n. 41/2024.
"""

# --- Massimali vigenti 2026 (usati dal calcolatore) ---

MASSIMALI_GIORNALIERI = {
    "trasferta_italia": 50.00,
    "trasferta_estero": 85.00,
    "pasto": 10.00,
    "lavoro_agile": 3.50,
}

MASSIMALE_KM = 0.45
MASSIMALE_NOTTE = 170.00
PLAFOND_MENSILE = 1400.00

CATEGORIE = {
    "trasferta_italia": "Trasferta in Italia",
    "trasferta_estero": "Trasferta all'estero",
    "pasto": "Rimborso pasto",
    "chilometrico": "Rimborso chilometrico",
    "alloggio": "Rimborso alloggio",
    "lavoro_agile": "Lavoro agile (home office)",
}

CATEGORIE_A_GIORNATE = ("trasferta_italia", "trasferta_estero", "pasto", "lavoro_agile")

MASSIMALE_GIORNATE_AGILE_MENSILE = 12

RIFERIMENTO_NORMATIVO = "Circolare MEF n. 18/2026"

# --- Massimali 2025 (solo display in /normativa) ---

MASSIMALI_GIORNALIERI_2025 = {
    "trasferta_italia": 46.48,
    "trasferta_estero": 77.47,
    "pasto": 8.00,
}

MASSIMALE_KM_2025 = 0.42
MASSIMALE_NOTTE_2025 = 150.00
PLAFOND_MENSILE_2025 = 1200.00
RIFERIMENTO_NORMATIVO_2025 = "Circolare MEF n. 41/2024"
