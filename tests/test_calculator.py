from src import calculator


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


class TestMassimaleTeorico:
    def test_trasferta_italia(self):
        r = richiesta(categoria="trasferta_italia", giorni=4)
        assert calculator.massimale_teorico(r) == 200.00

    def test_trasferta_estero(self):
        r = richiesta(categoria="trasferta_estero", giorni=3)
        assert calculator.massimale_teorico(r) == 255.00

    def test_pasto(self):
        r = richiesta(categoria="pasto", giorni=5)
        assert calculator.massimale_teorico(r) == 50.0

    def test_chilometrico(self):
        r = richiesta(categoria="chilometrico", km=250)
        assert calculator.massimale_teorico(r) == 112.50

    def test_alloggio(self):
        r = richiesta(categoria="alloggio", notti=2)
        assert calculator.massimale_teorico(r) == 340.0

    def test_nuovo_massimale_km(self):
        r = richiesta(categoria="chilometrico", km=100)
        assert calculator.massimale_teorico(r) == 45.0


class TestCalcola:
    def test_importo_sotto_massimale_tutto_esente(self):
        r = richiesta(categoria="pasto", giorni=5, importo=35.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0)
        assert esente == 35.0
        assert imponibile == 0.0

    def test_importo_sopra_massimale_eccedenza_imponibile(self):
        r = richiesta(categoria="trasferta_italia", giorni=2, importo=120.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0)
        assert esente == 100.0
        assert imponibile == 20.0

    def test_plafond_incapiente_limita_la_quota_esente(self):
        r = richiesta(categoria="alloggio", notti=2, importo=300.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1300.0)
        assert esente == 100.0
        assert imponibile == 200.0

    def test_plafond_esaurito_tutto_imponibile(self):
        r = richiesta(categoria="pasto", giorni=1, importo=10.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1400.0)
        assert esente == 0.0
        assert imponibile == 10.0

    def test_plafond_1400_accoglie_importi_che_prima_sforavano(self):
        # Con il vecchio plafond 1200 questo importo sarebbe stato interamente imponibile;
        # con il nuovo plafond 1400 la capienza residua è 150 e copre l'intero importo.
        r = richiesta(categoria="pasto", giorni=1, importo=10.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1250.0)
        assert esente == 10.0
        assert imponibile == 0.0

    def test_dettaglio_del_calcolo(self):
        r = richiesta(categoria="trasferta_estero", giorni=2, importo=200.0)
        _, _, dettaglio = calculator.calcola(r, esente_gia_riconosciuta=1300.0)
        assert dettaglio == {
            "massimale_teorico": 170.0,
            "esente_teorica": 170.0,
            "capienza_plafond": 100.0,
        }


class TestLavoroAgile:
    def test_massimale_base(self):
        r = richiesta(categoria="lavoro_agile", giorni=5, giorni_agile_gia_nel_mese=0)
        assert calculator.massimale_teorico(r) == 17.50

    def test_capienza_parziale(self):
        r = richiesta(categoria="lavoro_agile", giorni=6, giorni_agile_gia_nel_mese=8)
        assert calculator.massimale_teorico(r) == 14.00

    def test_capienza_esaurita(self):
        r = richiesta(categoria="lavoro_agile", giorni=3, giorni_agile_gia_nel_mese=12)
        assert calculator.massimale_teorico(r) == 0.00

    def test_15_giorni_richiesti_cap_a_12(self):
        r = richiesta(categoria="lavoro_agile", giorni=15, giorni_agile_gia_nel_mese=0, importo=60.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0)
        assert esente == 42.0
        assert imponibile == 18.0


class TestRiduzionProgressiva:
    def test_trasferta_estero_5_giorni_nessuna_riduzione(self):
        r = richiesta(categoria="trasferta_estero", giorni=5)
        assert calculator.massimale_teorico(r) == 425.00  # 5 × 85.00

    def test_trasferta_estero_fascia_2(self):
        r = richiesta(categoria="trasferta_estero", giorni=6)
        assert calculator.massimale_teorico(r) == 501.50  # 5×85 + 1×76.50

    def test_trasferta_estero_fascia_3(self):
        r = richiesta(categoria="trasferta_estero", giorni=12)
        assert calculator.massimale_teorico(r) == 943.50  # 5×85 + 5×76.50 + 2×68

    def test_trasferta_estero_6g_importo_500_tutto_esente(self):
        r = richiesta(categoria="trasferta_estero", giorni=6, importo=500.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0)
        assert esente == 500.0  # massimale 501.50 > importo 500
        assert imponibile == 0.0

    def test_trasferta_estero_2025_nessuna_riduzione(self):
        r = richiesta(data="2025-10-06", categoria="trasferta_estero", giorni=6)
        assert calculator.massimale_teorico(r) == 464.82  # 6 × 77.47, nessuna riduzione


class TestRegimeTransitorio:
    def test_pasto_2025_usa_massimali_vecchi(self):
        r = richiesta(data="2025-10-06", categoria="pasto", giorni=5)
        assert calculator.massimale_teorico(r) == 40.0  # 5 × 8.00, not 5 × 10.00

    def test_pasto_2025_plafond_1200(self):
        r = richiesta(data="2025-10-06", categoria="pasto", giorni=1, importo=8.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1200.0)
        assert esente == 0.0
        assert imponibile == 8.0
