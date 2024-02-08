from nerregex import do_regex_ner

def test_cnp():
    input_text = "... numitul Georgică Blatistul, C.N.P. 1891208175432, domiciliat în ..."
    results = do_regex_ner(text=input_text, previous_text='')
    assert (39, 52, 'CNP') in results

    input_text = "... numita Petrica Șmenus, CNP:2901101123456"
    results = do_regex_ner(text=input_text, previous_text='')
    assert (31, 44, 'CNP') in results


def test_firma_cui():
    input_text = "Firma cu numele S.C. Mișto & Tare Co. S.A., cu CUI RO4134567, înregistrată la ..."
    results = do_regex_ner(text=input_text, previous_text='')
    assert (21, 37, 'ORG') in results
    assert (51, 60, 'CUI') in results


def test_telefon():
    input_text = "... numitul Baiby Alba Neagră, tel. 0745677612, s-a aflat ..."
    results = do_regex_ner(text=input_text, previous_text='')
    assert (36, 46, 'PHONE') in results


def test_data_nasterii():
    input_text = "Maria Giorcovan, născută Pristanda Chelaru, la data de 12/11/1994, s-a aflat ..."
    results = do_regex_ner(text=input_text, previous_text='')
    assert (25, 42, 'DATE') in results
    assert (55, 65, 'DATE') in results


def test_auto():
    input_text = "Mașina cu numărul de înmatriculare BH01ABC a acroșat ..."
    results = do_regex_ner(text=input_text, previous_text='')
    assert (35, 42, 'AUTO') in results


def test_dosar():
    input_text = "Dosar nr.2209/321/2019"
    results = do_regex_ner(text=input_text, previous_text='')
    assert (9, 13, 'CASE') in results


def test_dosar_penal():
    input_text = "Dosar nr. 2219/P/2021"
    results = do_regex_ner(text=input_text, previous_text='')
    assert (10, 14, 'CASE') in results


def test_email():
    input_text = "... numitul Babaruncă Nicșor, email: nicsiolaie@theshit.com, s-a aflat ..."
    results = do_regex_ner(text=input_text, previous_text='')
    assert (37, 59, 'EMAIL') in results


def test_serie_numar():
    input_text = "... numitul Babaruncă Nicșor, legitimat cu C.I. seria AB, nr. 123456, s-a aflat ..."
    results = do_regex_ner(text=input_text, previous_text='')
    assert (54, 56, 'ID') in results
    assert (62, 68, 'ID') in results


def test_serie_numar2():
    input_text = "Proces verbal seria XYZ numărul 123456789, din data de ..."
    results = do_regex_ner(text=input_text, previous_text='')
    assert (20, 23, 'ID') in results
    assert (32, 41, 'ID') in results


def test_cod_ecli():
    input_text = "ECLI:RO:TBNMT:2023:017.000012"
    results = do_regex_ner(text=input_text, previous_text='')
    assert (23, 29, 'ECLI') in results


def test_hotarare():
    input_text = "Sentința Civilă NR. 236786, din ..."
    results = do_regex_ner(text=input_text, previous_text='')
    assert (20, 26, 'DECISION') in results


def test_hotarare2():
    input_text = "ÎNCHEIEREA PENALĂ NR.123456, din ..."
    results = do_regex_ner(text=input_text, previous_text='')
    assert (21, 27, 'DECISION') in results


def test_readactat():
    input_text = "Red. Z.G.-C./Data - 30.06.2023\nTehnored. L.-C.I.\n"
    results = do_regex_ner(text=input_text, previous_text='')
    assert (5, 12, 'INITIALS') in results
    assert (41, 48, 'INITIALS') in results


def test_adresa():
    input_text = "Maria Ioanidi, domiciliată în com. Bucșa, jud. Bihor, sat Verești, str. Alunului nr. 45, s-a aflat ..."
    results = do_regex_ner(text=input_text, previous_text='')
    assert (35, 40, 'LOC') in results
    assert (47, 52, 'LOC') in results
    assert (58, 65, 'LOC') in results
    assert (72, 80, 'LOC') in results
    assert (85, 87, 'LOC') in results


def test_adresa2():
    input_text = "Maria Ioanidi, cu domiciliul în jud. Vaslui, oraș Vaslui str. Alunului Beat, nr. 45, bl. B1, sc. 2, apt. 25, s-a aflat ..."
    results = do_regex_ner(text=input_text, previous_text='')
    assert (37, 43, 'LOC') in results
    assert (50, 56, 'LOC') in results
    assert (62, 75, 'LOC') in results
    assert (81, 83, 'LOC') in results
    assert (89, 91, 'LOC') in results
    assert (97, 98, 'LOC') in results
    assert (105, 107, 'LOC') in results


def test_iban():
    input_text = "Societatea SC Bubu S.R.L, cont bancar RO49AAAA1B31007593840000, cu sediul în ..."
    results = do_regex_ner(text=input_text, previous_text='')
    assert (38, 62, 'IBAN') in results


def test_iban_spaces():
    input_text = "Societatea SC Bubu S.R.L, cont bancar RO 49 AAAA 1B31 0075 9384 0000, cu sediul în ..."
    results = do_regex_ner(text=input_text, previous_text='')
    assert (38, 68, 'IBAN') in results
