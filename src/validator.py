"""Regole di validazione delle richieste di rimborso."""

from datetime import date

from src import rules, storage


def valida(richiesta, richieste=None):
    """Restituisce (True, "") se la richiesta è valida, altrimenti (False, motivazione)."""
    if not richiesta.get("dipendente"):
        return False, "dipendente mancante"

    categoria = richiesta.get("categoria")
    if categoria not in rules.CATEGORIE:
        return False, "categoria non riconosciuta"

    if categoria == "lavoro_agile" and (richiesta.get("data") or "") < "2026-01-01":
        return False, "categoria non riconosciuta"

    importo = richiesta.get("importo")
    if importo is None or importo <= 0:
        return False, "importo non positivo"

    try:
        date.fromisoformat(richiesta.get("data") or "")
    except ValueError:
        return False, "data mancante o non valida"

    if categoria in rules.CATEGORIE_A_GIORNATE:
        giorni = richiesta.get("giorni")
        if not giorni or giorni <= 0:
            return False, "numero di giornate non valido"

    if categoria == "chilometrico":
        km = richiesta.get("km")
        if not km or km <= 0:
            return False, "numero di chilometri non valido"

    if categoria == "alloggio":
        notti = richiesta.get("notti")
        if not notti or notti <= 0:
            return False, "numero di notti non valido"

    if richieste is not None and categoria in {"lavoro_agile", "trasferta_italia", "trasferta_estero"}:
        altra = (
            {"trasferta_italia", "trasferta_estero"}
            if categoria == "lavoro_agile"
            else {"lavoro_agile"}
        )
        giorni_nuova = storage.giornate_coperte(richiesta)
        for r in richieste:
            if (
                r["dipendente"] == richiesta["dipendente"]
                and r["stato"] == "valida"
                and r["categoria"] in altra
                and giorni_nuova & storage.giornate_coperte(r)
            ):
                return False, "incompatibilità lavoro agile / trasferta"

    return True, ""
