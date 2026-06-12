"""Parametri normativi vigenti per il calcolo dei rimborsi spese.

Fonte: Circolare MEF n. 41/2024, in vigore per l'anno 2025.
"""

MASSIMALI_GIORNALIERI = {
    "trasferta_italia": 46.48,
    "trasferta_estero": 77.47,
    "pasto": 8.00,
}

MASSIMALE_KM = 0.42
MASSIMALE_NOTTE = 150.00
PLAFOND_MENSILE = 1200.00

CATEGORIE = {
    "trasferta_italia": "Trasferta in Italia",
    "trasferta_estero": "Trasferta all'estero",
    "pasto": "Rimborso pasto",
    "chilometrico": "Rimborso chilometrico",
    "alloggio": "Rimborso alloggio",
}

CATEGORIE_A_GIORNATE = ("trasferta_italia", "trasferta_estero", "pasto")

RIFERIMENTO_NORMATIVO = "Circolare MEF n. 41/2024"
