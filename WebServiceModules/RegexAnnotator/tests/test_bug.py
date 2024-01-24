from nerregex import do_regex_ner

def test_tehnice():
    input_text = 'Prin realizarea obiectivului de investiții se creează condiții de siguranță în aprovizionarea cu ' + \
        'gaze naturale a pieței interne de gaze, facilitând echilibrarea balanței consum-producție internă – import ' + \
        'gaze naturale, prin acoperirea vârfurilor de consum cauzate în principal de variațiile de temperatură, precum ' +\
        'și menținerea caracteristicilor de funcționare optimă a sistemului național de transport gaze naturale, în scopul ' + \
        'obținerii de avantaje tehnice și economice.'
    results = do_regex_ner(text=input_text, previous_text='')
    assert not results
