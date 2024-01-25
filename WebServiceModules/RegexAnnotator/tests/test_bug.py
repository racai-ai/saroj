from nerregex import do_regex_ner

def test_tehnice():
    input_text = 'Prin realizarea obiectivului de investiții se creează condiții de siguranță în aprovizionarea cu ' + \
        'gaze naturale a pieței interne de gaze, facilitând echilibrarea balanței consum-producție internă – import ' + \
        'gaze naturale, prin acoperirea vârfurilor de consum cauzate în principal de variațiile de temperatură, precum ' +\
        'și menținerea caracteristicilor de funcționare optimă a sistemului național de transport gaze naturale, în scopul ' + \
        'obținerii de avantaje tehnice și economice.'
    results = do_regex_ner(text=input_text, previous_text='')
    
    assert not results


def test_cities():
    input_text = 'cu domiciliul ales la Cabinet de avocat Gabriela Bubiță-Ciorescu, ' + \
        'în București, str. Decebal nr. 113, bl. 13A, sc. A, ap. 23, sector 8, excelent.'
    results = do_regex_ner(text=input_text, previous_text='')
    
    assert len(results) == 6
    assert input_text[results[0][0]:results[0][1]] == 'București'
    assert input_text[results[1][0]:results[1][1]] == 'Decebal'
    assert input_text[results[2][0]:results[2][1]] == '113'
    assert input_text[results[3][0]:results[3][1]] == '13A'
    assert input_text[results[4][0]:results[4][1]] == 'A'
    assert input_text[results[5][0]:results[5][1]] == '23'


def test_cities2():
    input_text = 'Gogu, cu domiciliul în oraș ' + \
        'București, str. Decebal nr. 113, bl. 13A, sc. A, ap. 23, sector 8, excelent.'
    results = do_regex_ner(text=input_text, previous_text='')

    assert len(results) == 6
    assert input_text[results[0][0]:results[0][1]] == 'București'
    assert input_text[results[1][0]:results[1][1]] == 'Decebal'
    assert input_text[results[2][0]:results[2][1]] == '113'
    assert input_text[results[3][0]:results[3][1]] == '13A'
    assert input_text[results[4][0]:results[4][1]] == 'A'
    assert input_text[results[5][0]:results[5][1]] == '23'
