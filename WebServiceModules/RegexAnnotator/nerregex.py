import sys
import os
import re

ner_addr_sep = re.compile(r'''[\s,.;]''')
ner_address_fields = [
    # județul
    re.compile(r'''\b(?:[Jj]ud(?:\.\s*|\s+)|[Jj]ude[țtţ](?:ul)?\s+)'''),
    # orașul
    re.compile(r'''\b(?:[Oo]r[sșş]?(?:\.\s*|\s+)|[Oo]ra[sșş](?:ul)?\s+)'''),
    # municipiul
    re.compile(r'''\b(?:[Mm]un(?:ic)?(?:\.\s*|\s+)|[Mm]unicipiul?\s+)'''),
    # comuna
    re.compile(r'''\b(?:[Cc]om(?:\.\s*|\s+)|[Cc]omuna\s+)'''),
    # sat
    re.compile(r'''\b[Ss]at(?:ul)?\s+'''),
    # blocul
    re.compile(r'''\b(?:[Bb]l(?:\.\s*|\s+)|[Bb]loc(?:ul)?\s+)'''),
    # scara
    re.compile(r'''\b(?:[Ss]c(?:\.\s*|\s+)|[Ss]car[ăa]\s+)'''),
    # etaj
    re.compile(r'''\b(?:[Ee]t(?:\.\s*|\s+)|[Ee]taj(?:ul)?\s+)'''),
    # apartament
    re.compile(r'''\b(?:[Aa]pt?(?:\.\s*|\s+)|[Aa]partament(?:ul)?\s+)'''),
    # strada
    re.compile(r'''\b(?:[Ss]tr(?:\.\s*|\s+)|[Ss]trad[ăa]\s+)'''),
    # bulevardul
    re.compile(
        r'''\b(?:(?:[Bb][v-]?d|[Bb]lv)(?:\.\s*|\s+)|[Bb]ulevard(?:ul)?\s+|[Bb]-dul\s+)'''),
    # calea
    re.compile(r'''\b[Cc]alea\s+'''),
    # aleea
    re.compile(r'''\b[Aa]leea\s+'''),
    # numărul
    re.compile(r'''\b(?:[Nn][rR](?:\.\s*|\s+)|[Nn]um[ăa]r(?:ul)?\s+)'''),
    # corp
    re.compile(r'''\b[Cc]orp(?:ul)?\s+'''),
    # sector
    re.compile(r'''\b(?:[Ss]ect(?:\.\s*|\s+)|[Ss]ector(?:ul)?\s+)'''),
    # __DB_CITY__
    re.compile(r'''\b__DB_CITY__''')
]
# NOTE: All char sequences that have to be anonymized are captured in groups (...)
ner_regex = {
    # OK
    'CNP': re.compile(r'''
        \b
        (?:CNP|C\.N\.P\.)\s*:?\s*
        ([125678]\d{12}) # captura
        \b''', re.VERBOSE),
    # OK
    'FIRMA': re.compile(r'''
        \b
        (?:S\.C\.\s*|SC\s+|Societatea\s+)
        ([A-Z0-9ȘȚĂÎÂ].+?) # captura
        \s+(?:SA\b|S\.A\.|SRL\b|S\.R\.L\.)
        ''', re.VERBOSE),
    # OK
    'ADRESA': re.compile(r'''
        \b
        (?:cu\sdomiciliul\sîn\s+|domiciliat[ă]?\sîn\s+|cu\ssediul\sîn\s+|[îi]n\s+(?=__DB_CITY__))
        (
            (?:
                (?:
                    (?:
                        [Jj]ud|
                        [Oo]r[sșş]?|
                        [Mm]un(?:ic)?|
                        [Cc]om|
                        [Bb]l|
                        [Ee]t|
                        [Ss]c|
                        [Aa]pt?|
                        [Ss]tr|
                        [Bb][v-]?d|
                        [Bb]lv|
                        [Bb]-dul|
                        [Nn][Rr]|
                        [Ss]ect
                    )(?:\.\s*|\s+)
                    |
                    (?:
                        [Jj]ude[țtţ](?:ul)?|
                        [Mm]unicipiul?|
                        [Ss]at(?:ul)?|
                        [Oo]ra[sșş](?:ul)?|
                        [Cc]omun[ăa]|
                        [Bb]loc(?:ul)?|
                        [Aa]partament(?:ul)?|
                        [Ee]taj(?:ul)?|
                        [Ss]car[ăa]|
                        [Ss]trad[ăa]|
                        [Bb]ulevard(?:ul)?|
                        [Cc]alea|
                        [Nn]um[ăa]r(?:ul)?|
                        [Aa]leea|
                        [Cc]orp(?:ul)?|
                        [Ss]ector(?:ul)?
                    )\s+
                    |
                    __DB_CITY__
                )
                (?:
                    [A-ZȘȚĂÎÂŞŢ][A-ZȘȚĂÎÂŞŢa-zșțăîâşţ]*(?:\s*[&\s.-]\s*[A-ZȘȚĂÎÂŞŢ][A-ZȘȚĂÎÂŞŢa-zșțăîâşţ]*){0,2}|
                    [A-Z0-9]{1,3}(?:\s?bis)?
                ) # valoarea câmpului
                (?:[,.;]\s*|\s+) # separatorul
            )+
        ) # captura (toată adresa)
        ''', re.VERBOSE),
    # OK
    'TELEFON': re.compile(r'''
        \b
        (?:
            telefon(?:\s+|\s*:\s*)|
            tel(?:\.?\s+|\.?:\s*)|
            fax(?:\s+|\s*:\s*)
        )
        (0[\d\s/]{8,13}\d) # captura
        \b''', re.VERBOSE),
    # OK
    'DATA_NASTERII': re.compile(r'''
        \b
        n[ăa]scut[ăa]?\s+
        (\w+(?:\s+\w+){0,2})\s*,?\s+ # nume la naștere
        (?:la(?:\sdata\sde)?)?\s+
        (
            (?:0?[1-9]|[12]\d|3[01]) # zi
            [.\s/-] # separator
            (?:0?[1-9]|1[012]) # lună
            [.\s/-] # separator
            [12]\d{3} # an
        )
        \b''', re.VERBOSE),
    # OK
    'TEHNOREDACTOR': re.compile(r'''
        \b
        (?:
            Red(?:actor\s+|actat\s+|\.\s*)|
            Tehnored(?:actat\s+|actor\s+|\.\s*)|
            [ÎI]ntocmit\s+|
            Lucrat\s+|
            Gref(?:ier\s+|\.\s*)|
            Jud(?:ecător\s+|\.\s*)|
            Tehn\.\s*|
            Thred\.\s*|
            Dact(?:ilografiat\s+|ilograf[aă]?\s+|\.\s*)
        )(?:,\s*)?
        (
            [A-ZȘȚĂÎÂŞŢ](?:[a-zșțăîâşţ-]+\s+|\.)
            (?:[\s-]?[A-ZȘȚĂÎÂŞŢ](?:[a-zșțăîâşţ-]+\s+|\.))*
        ) # captura
        ''', re.VERBOSE),
    # OK
    'TEHNOREDACTOR2': re.compile(r'''
        \b
        (
            [A-ZȘȚĂÎÂŞŢ](?:[a-zșțăîâşţ-]+|\.)
            (?:[\s-][A-ZȘȚĂÎÂŞŢ](?:[a-zșțăîâşţ-]+|\.))*
        ) # captura
        \s+
        (?:
            Red(?:actor[\s,]|\.\s*)|
            Tehnored(?:actor[\s,]|\.\s*)|
            Tehn\.\s*|
            Thred\.\s*|
            Gref(?:ier[\s,]|\.\s*)
        )
        ''', re.VERBOSE),
    # OK
    'TEHNOREDACTOR3': re.compile(r'''
        \b
        (
            [A-ZȘȚĂÎÂŞŢ]\.?(?:-?[A-ZȘȚĂÎÂŞŢ]\.?)+
        ) # captura
        \s*/\s*
        (?:
            Red(?:actor[\s,]|\.\s*)|
            Tehnored(?:actor[\s,]|\.\s*)|
            Tehn\.\s*|
            Thred\.\s*|
            Gref(?:ier[\s,]|\.\s*)
        )
        ''', re.VERBOSE),
    # OK
    'HOTARARE': re.compile(r'''
        \b
        (?:
            [sS]\s{0,2}[eE]\s{0,2}[nN]\s{0,2}[tT]\s{0,2}[iI]\s{0,2}[nN]\s{0,2}[TtțȚţŢ]\s{0,2}(?:[AaĂă]|[eE]\s{0,2}[iI])|
            [iîIÎ]\s{0,2}[nN]\s{0,2}[cC]\s{0,2}[hH]\s{0,2}[eE]\s{0,2}[iI]\s{0,2}[eE]\s{0,2}[rR]\s{0,2}(?:[eE]|[eE]\s{0,2}[aA]|[iI]\s{0,2}[iI])|
            [dD]\s{0,2}[eE]\s{0,2}[cC]\s{0,2}[iI]\s{0,2}[zZ]\s{0,2}[iI]\s{0,2}(?:[eEaA]|[eE]\s{0,2}[iI])
        )\s+
        (
            (?:
                [cC]\s{0,2}[iI]\s{0,2}[vV]\s{0,2}[iI]|
                [pP]\s{0,2}[eE]\s{0,2}[nN]\s{0,2}[aA]|
                [cC]\s{0,2}[oO]\s{0,2}[mM]\s{0,2}[eE]\s{0,2}[rR]\s{0,2}[cC]\s{0,2}[iI]\s{0,2}[aA]
            )\s{0,2}[lL]\s{0,2}[ăĂeE]\s+
        )?
        (?:[Nn][rR](?:\s+|\.?\s*)|[Nn]um[aă]r(?:ul)?\s+)
        (\d+) # captura
        \b''', re.VERBOSE),
    # OK
    'COD_ECLI': re.compile(r'''
        \b
        :[12]\d{3}:\d{3}\.
        (\d{6}) # captura cod ECLI
        \b''', re.VERBOSE),
    # OK
    'NUMAR_DOSAR': re.compile(r'''
        \b
        [dD][oO][sS][Aa][Rr]\s(?:[Nn][rR](?:\s+|\.\s*)|[Nn]um[aă]r(?:ul)?\s+)
        (\d+) # captura nr. de dosar
        /\d+/[12]\d{3}
        \b''', re.VERBOSE),
    # OK
    'NUMAR_DOSAR_PENAL': re.compile(r'''
        \b
        [dD][oO][sS][Aa][Rr]\s(?:[Nn][rR](?:\s+|\.\s*)|[Nn]um[aă]r(?:ul)?\s+)
        (\d+) # captura nr. de dosar
        /P/[12]\d{3}
        \b''', re.VERBOSE),
    # OK
    'NUMAR_AUTO': re.compile(r'''
        \b
        (
            (?:AB|AG|AR|B|BC|BH|BN|BR|BT|BV|BZ|CJ|
            CL|CS|CT|CV|DB|DJ|GJ|GL|GR|HD|HR|IF|
            IL|IS|MH|MM|MS|NT|OT|PH|SB|SJ|SM|SV|
            TL|TM|TR|VL|VN) # județ
            [\s-]? # separator
            \d{2,3} # număr, și cu 3 cifre în București
            [\s-]? # separator
            [A-Z]{3} # 3 litere, fără diacritice
        ) # captura
        \b''', re.VERBOSE),
    # OK
    'SERIE_NUMAR': re.compile(r'''
        \b
        [Ss]eri[ea]\s+
        ([\w./-]{1,5}) # seria
        (?:,?\s*|\s+)
        (?:[Nn][rR](?:\s+|\.\s*)|[Nn]um[aă]r(?:ul)?\s+)
        (\d+) # numărul
        \b''', re.VERBOSE),
    # OK
    'EMAIL': re.compile(r'''
        \b
        (
            [a-z0-9._-]+  # cont
            \s?@\s?
            [a-z0-9-]+(?:\.[a-z0-9-]+)*\.[a-z]{2,4} # domeniu
        ) # captura
        \b''', re.VERBOSE),
    # OK
    'CUI': re.compile(r'''
        \b
        [cC].?\s?[uU].?\s?[iI].?\s+
        ((?:RO)?\d{6,8}) # captura
        \b''', re.VERBOSE),
    'IBAN': re.compile(r'''
        \b
        (?:cont(?:\sbancar)?|(?:cod\s)?IBAN)\s
        (RO[0-9A-Z]{22}) # captura, IBAN-ul are 24 de caractere în România
        \b
        ''', re.VERBOSE)
}
ner_label_map = {
    'CNP': 'CNP',
    'FIRMA': 'ORG',
    'ADRESA': 'LOC',
    'TELEFON': 'PHONE',
    'DATA_NASTERII': 'DATE',
    'HOTARARE': 'DECISION',
    'COD_ECLI': 'ECLI',
    'CUI': 'CUI',
    'NUMAR_AUTO': 'AUTO',
    'SERIE_NUMAR': 'ID',
    'EMAIL': 'EMAIL',
    'NUMAR_DOSAR': 'CASE',
    'NUMAR_DOSAR_PENAL': 'CASE',
    'TEHNOREDACTOR': 'INITIALS',
    'TEHNOREDACTOR2': 'INITIALS',
    'TEHNOREDACTOR3': 'INITIALS',
    'IBAN': 'IBAN'
}


def _load_localitati() -> set[str]:
    localitati_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'data', 'localitati.txt')
    localitati = set()

    print(f'Loading data file with cities [{localitati_file}]', file=sys.stderr, flush=True)

    with open(localitati_file, mode='r', encoding='utf-8') as f:
        for line in f:
            city_std = line.strip()
            city_old = city_std.replace('Ș', 'Ş')
            city_old = city_old.replace('Ț', 'Ţ')
            
            localitati.add(city_std)
            localitati.add(city_old)
        # end for
    # end with
    
    return localitati


ro_cities = _load_localitati()
_city_rx = re.compile(r'''
    \b
    (?:în|din)\s
    (
        [A-ZȘȚŞŢĂÎÂ][şţșțăîâa-z]+
        (?:
            [ -]
            (?:
                [A-ZȘȚŞŢĂÎÂ][şţșțăîâa-z]+
                |
                (?:de|cel|din|I\\.|sub|lui|la|1|cu|pe)
            )
        ){0,3}
    )\b''', re.VERBOSE
)


def _insert_city_marks(text: str) -> str:
    """Given an input text, mark possible Romanian cities with
    string `'__DB_CITY__'`, so that the ADDRESS regex is able
    to pick it up. Returns the modified text."""

    m = _city_rx.search(text)
    insert_indexes = []

    while m:
        city = m.group().upper()
        spc_idx = city.rfind(' ')
        city = city[spc_idx + 1:]

        if city in ro_cities:
            insert_indexes.append(m.start() + spc_idx + 1)
        # end if
            
        m = _city_rx.search(text, pos=m.end())
    # end while

    if not insert_indexes:
        # No cities found
        return text
    # end if

    text2_pieces = []
    from_i = 0
    
    for to_i in insert_indexes:
        text2_pieces.append(text[from_i:to_i])
        text2_pieces.append('__DB_CITY__')
        from_i = to_i
    # end if
    
    text2_pieces.append(text[from_i:])
    return ''.join(text2_pieces)


def do_regex_ner(text: str, previous_text: str) -> list[tuple[int, int, str]]:
    """Takes an input text and returns a list of tuples of type
    (start_offset, end_offset, etichetă), for all named entities
    that were recognized. If `previous_text` is not empty, it is preappended
    to `text` with a space after it. The offsets are given relative to `text`."""

    text = _insert_city_marks(text)
    offset_ballast = 0
    previous_text = previous_text.strip()

    if previous_text:
        previous_text = _insert_city_marks(previous_text)
        text = previous_text + ' ' + text
        # Plus 1 for the space
        offset_ballast = len(previous_text) + 1
    # end if
   
    entities = []

    # 1. Do NER with regular expressions
    for ner_label in ner_regex:
        regex = ner_regex[ner_label]
        m = regex.search(text)

        while m and m.lastindex:
            if ner_label == 'ADRESA':
                process_address_fields(
                    text, addr_start=m.start(), addr_end=m.end(), ner_list=entities)
            else:
                for gi in range(1, m.lastindex + 1):
                    entities.append((m.start(gi), m.end(gi), ner_label))
                # end for
            # end if

            m = regex.search(text, pos=m.end())
        # end while
    # end for

    entities2 = []

    # 2. Map regex labels to final labels
    for s, e, l in entities:
        if l in ner_label_map:
            entities2.append((s, e, ner_label_map[l]))
        else:
            entities2.append((s, e, l))
        # end if
    # end for
    
    entities3 = []

    # 3. Get rid of the offset balast.
    for s, e, l in entities2:
        # Only keep entities that appear in text, not
        # the ones that appear in the previous_text
        if e > offset_ballast:
            entities3.append((
                0 if s < offset_ballast else s - offset_ballast,
                e - offset_ballast, l))
        # end if
    # end for

    entities_dbci = []
    text = text[offset_ballast:]
    dbci = text.rfind('__DB_CITY__')
    dbc_len = len('__DB_CITY__')

    # 4. Remove __DB_CITY__ and adjust the offsets accordingly.
    if dbci >= 0:
        while dbci >= 0:
            for s, e, l in entities3:
                if s > dbci:
                    entities_dbci.append((s - dbc_len, e - dbc_len, l))
                else:
                    entities_dbci.append((s, e, l))
                # end if
            # end for
            
            dbci = text.rfind('__DB_CITY__', 0, dbci)
            entities3 = entities_dbci
            entities_dbci = []
        # end while
    # end if

    return entities3


def process_address_fields(
        text: str,
        addr_start: int, addr_end: int, ner_list: list) -> None:
    """Parses the values of the address fields and adds
    them to the list of recognized text spans."""

    end_match_indexes = []

    for regex in ner_address_fields:
        m = regex.search(text, pos=addr_start)

        if m and m.end() <= addr_end:
            end_match_indexes.append((m.start(), m.end()))
        # end if
    # end for

    end_match_indexes = sorted(end_match_indexes, key=lambda x: x[0])

    for i in range(0, len(end_match_indexes) - 1):
        v_start = end_match_indexes[i][1]
        v_end = end_match_indexes[i + 1][0]

        while ner_addr_sep.fullmatch(text[v_end - 1]):
            v_end -= 1
        # end while

        if v_start < v_end:
            ner_list.append((v_start, v_end, 'ADRESA'))
        # end if
    # end for

    # Handle the last value
    v_start = end_match_indexes[-1][1]
    v_end = addr_end

    while ner_addr_sep.fullmatch(text[v_end - 1]):
        v_end -= 1
    # end while

    if v_start < v_end:
        ner_list.append((v_start, v_end, 'ADRESA'))
    # end if
