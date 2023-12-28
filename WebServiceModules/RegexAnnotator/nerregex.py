import re

ner_addr_sep = re.compile(r'''[\s,]''')
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
    re.compile(r'''\b(?:[Nn][rR](?:\.\s*|\s+)|[Nn]um[ăa]r(?:ul)?\s+)''')
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
        (?:cu\sdomiciliul\sîn\s+|domiciliat[ă]?\sîn\s+|cu\ssediul\sîn\s+)
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
                        [Nn][Rr]
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
                        [Aa]leea
                    )\s+
                )
                [\s\w."'-]+  # valoarea câmpului
                (?:,\s*|\s+) # separatorul
            )+
        ) # captura (toată adresa)
        \b''', re.VERBOSE),
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
            [rR]ed(?:\s+|(?:actor\s+|actat\s+|\.\s*))|
            [tT]ehnored(?:\s+|(?:actat\s+|actor\s+|\.\s*))|
            [Îî]ntocmit\s+|[Ll]ucrat\s+|Gref(?:\s+|(?:ier\s+|\.\s*))|
            [Jj]ud(?:\s+|(?:ecător\s+|\.\s*))|[Tt]ehn(?:\s+|\.?\s*)|[Tt]hred(?:\s+|\.?\s*)
            [dD]act(?:\s+|(?:ilografiat|ilograf[aă]?|\.))
        )
        ([\w][\w.-]*[\w.]) # captura
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
        [dD]osar\s(?:[Nn][rR](?:\s+|\.\s*)|[Nn]um[aă]r(?:ul)?\s+)
        (\d+) # captura nr. de dosar
        /\d+/[12]\d{3}
        \b''', re.VERBOSE),
    # OK
    'NUMAR_DOSAR_PENAL': re.compile(r'''
        \b
        [dD]osar\s(?:[Nn][rR](?:\s+|\.\s*)|[Nn]um[aă]r(?:ul)?\s+)
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
    'IBAN': 'IBAN'
}


def do_regex_ner(text: str) -> list[tuple[int, int, str]]:
    """Takes an input test and returns a list of tuples of type
    (start_offset, end_offset, etichetă), for all named entities
    that were recognized."""

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

    return entities2


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
