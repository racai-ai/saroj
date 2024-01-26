from . import ann


def test_person():
    input_text = 'Totodată, petenta a arătat că intimata a emis procesul verbal fără să facă un control fizic, ' + \
        'nu a știut nimeni în momentul constatării de o posibilă sancțiune, iar în cuprinsul procesului verbal ' + \
        'se fac mențiuni false cu privire la faptul că s-ar fi ,,adus la cunoștință contravenientului dreptul ' + \
        'de a face obiecțiuni la conținutul prezentului proces verbal, șoferul Vasile Popescu nu este reprezentantul ' + \
        'legal al firmei pentru a emite opinii” (Florin Georgescu este reprezentantul legal al firmei).'
    result = ann.tag_text(text=input_text)

    assert result[63][2] == 'B-PER' and result[64][2] == 'I-PER'
    assert input_text[result[63][0]:result[64][1]] == 'Vasile Popescu'
    assert result[77][2] == 'B-PER' and result[78][2] == 'I-PER'
    assert input_text[result[77][0]:result[78][1]] == 'Florin Georgescu'


def test_organization():
    input_text = 'Pe rol judecarea cauzei civile privind pe petent EXIM SPEDITION SRL, pe ' + \
        'intimat COMPANIA INTERNAŢIONALĂ DE ADMINISTRARE A INFRASTRUCTURII AERIENE SA ABCD BUCUREŞTI, ' + \
        'având ca obiect plângere contravenţională.'
    result = ann.tag_text(text=input_text)

    assert result[8][2] == 'B-ORG' and result[9][2] == 'I-ORG' and \
        result[10][2] == 'I-ORG'
    assert input_text[result[8][0]:result[10][1]] == 'EXIM SPEDITION'


def test_location():
    input_text = 'Admite plângerea contravențională formulată de petenta PluriBand SRL, ' + \
        'cu sediul în sat Belciug, strada Brusturelui nr. 13, com. Ghiminați, jud. Bihor, având CUI 14789468, ' + \
        'în contradictoriu cu intimata.'
    result = ann.tag_text(text=input_text)

    assert result[14][2] == 'B-LOC' and result[31][2] == 'I-LOC'
    assert input_text[result[14][0]:result[31][1]] == \
        'sat Belciug, strada Brusturelui nr. 13, com. Ghiminați, jud. Bihor'
