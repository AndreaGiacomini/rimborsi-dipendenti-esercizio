"""Calcolo della quota esente e della quota imponibile di una richiesta."""

from src import rules

DATA_REGIME_2026 = "2026-01-01"


def _is_regime_2026(data_str):
    return data_str >= DATA_REGIME_2026


def massimale_teorico(richiesta):
    """Massimale di esenzione applicabile alla richiesta, in base alla categoria."""
    categoria = richiesta["categoria"]
    if _is_regime_2026(richiesta["data"]):
        massimali = rules.MASSIMALI_GIORNALIERI
        massimale_km = rules.MASSIMALE_KM
        massimale_notte = rules.MASSIMALE_NOTTE
    else:
        massimali = rules.MASSIMALI_GIORNALIERI_2025
        massimale_km = rules.MASSIMALE_KM_2025
        massimale_notte = rules.MASSIMALE_NOTTE_2025
    if categoria == "lavoro_agile":
        gia_nel_mese = richiesta.get("giorni_agile_gia_nel_mese", 0)
        ammesse = min(richiesta["giorni"], max(0, rules.MASSIMALE_GIORNATE_AGILE_MENSILE - gia_nel_mese))
        return round(rules.MASSIMALI_GIORNALIERI["lavoro_agile"] * ammesse, 2)
    if categoria == "trasferta_estero" and _is_regime_2026(richiesta["data"]):
        g = richiesta["giorni"]
        g1 = min(g, 5)
        g2 = min(max(g - 5, 0), 5)
        g3 = max(g - 10, 0)
        return round(85.00 * g1 + 76.50 * g2 + 68.00 * g3, 2)
    if categoria in rules.CATEGORIE_A_GIORNATE:
        return round(massimali[categoria] * richiesta["giorni"], 2)
    if categoria == "chilometrico":
        return round(massimale_km * richiesta["km"], 2)
    if categoria == "alloggio":
        return round(massimale_notte * richiesta["notti"], 2)
    raise ValueError(f"categoria non gestita: {categoria}")


def calcola(richiesta, esente_gia_riconosciuta):
    """Restituisce (quota_esente, quota_imponibile, dettaglio).

    `esente_gia_riconosciuta` è la quota esente già riconosciuta al dipendente
    nel mese della richiesta, ai fini del plafond mensile.
    """
    importo = richiesta["importo"]
    teorico = massimale_teorico(richiesta)
    esente_teorica = min(importo, teorico)
    plafond = rules.PLAFOND_MENSILE if _is_regime_2026(richiesta["data"]) else rules.PLAFOND_MENSILE_2025
    capienza = max(plafond - esente_gia_riconosciuta, 0.0)
    esente = round(min(esente_teorica, capienza), 2)
    imponibile = round(importo - esente, 2)
    dettaglio = {
        "massimale_teorico": teorico,
        "esente_teorica": round(esente_teorica, 2),
        "capienza_plafond": round(capienza, 2),
    }
    return esente, imponibile, dettaglio
