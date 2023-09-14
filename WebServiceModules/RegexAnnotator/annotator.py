import re
from csmregex import do_regex_ner


_int_rx = re.compile(r'^\d+\s')


def read_conllu_file(file: str, append_column: bool = True) -> list[str | list[str]]:
    """Reads a whole CoNLL-U file and stores lines as comments or
    empty lines (str) or tuples of fields if the line contains annotations."""

    file_lines = []

    with open(file, mode='r', encoding='utf-8') as f:
        for line in f:
            if _int_rx.match(line):
                fields = line.strip().split()

                if append_column:
                    # That's for NER info
                    fields.append('_')
                # end if

                file_lines.append(fields)
            else:
                file_lines.append(line)
            # end if
        # end for
    # end with

    return file_lines


def _no_space_after(words: list[str], index: int) -> None:
    """Modifies the list in place, making sure there is no space
    between `index` and `index + 1`. `words[index]` has a space appended."""

    if index + 1 < len(words):
        next_word = words[index + 1].strip()

        if next_word in ':;.,)}]':
            words[index] = words[index].strip()
        # end if

        curr_word = words[index].strip()

        if curr_word in '([{':
            words[index] = curr_word
        # end if
    # end if


def _get_text_from_conllu(file_lines: list[str | tuple]) -> tuple[str, list[str], list[int]]:
    """Takes the output of function `read_conllu_file()` and returns the text
    formed by joining all tokens with spaces, removing spaces around punctuation.
    Also returns a list of token to file line indexes and the list of normalized tokens."""

    file_words_indexes = []
    file_words = []

    for i, line in enumerate(file_lines):
        if isinstance(line, list):
            word = line[1]
            file_words_indexes.append(i)
            file_words.append(word + ' ')
        # end if
    # end for

    # Normalize text: no space between comma and previous word
    for i in range(len(file_words)):
        _no_space_after(words=file_words, index=i)
    # end for

    file_text = ''.join(file_words)
    return file_text, file_words, file_words_indexes


def _get_ner_line_indexes(
        tokens: list[str], token_lines: list[int],
        offset: tuple[int, int]) -> tuple[int, int] | None:
    """Takes the input `text` and its `tokens` and, given a
    start_offset, end_offset `offset` tuple, retrieves the range
    of the index(es) of the line(s) in the CoNLL-U file which
    should receive the NER annotation."""

    the_offset = 0
    left_i = -1
    right_i = -1

    for i, tok in enumerate(tokens):
        if left_i == -1:
            if the_offset + len(tok) > offset[0]:
                left_i = i
            elif the_offset + len(tok) == offset[0]:
                left_i = i + 1
            # end if
        # end if

        if right_i == -1:
            if the_offset + len(tok) > offset[1]:
                right_i = i
                break
            elif the_offset + len(tok) == offset[1]:
                right_i = i + 1
                break
            # end if
        # end if

        the_offset += len(tok)
    # end for

    if left_i >= 0 and left_i <= right_i:
        # Lines found
        return token_lines[left_i], token_lines[right_i]
    else:
        return None
    # end if


def regex_annotate(input_file: str, output_file: str) -> None:
    """Main function of this module. Takes an `input_file` (CoNLL-U format)
    from local storage and writes the produced CoNLL-U file to the `output_file`
    on the local storage."""

    input_lines = read_conllu_file(file=input_file)
    input_text, words, word_lines_indexes = _get_text_from_conllu(
        file_lines=input_lines)
    annotations = do_regex_ner(text=input_text)

    # Insert the annotations on the last column
    # '_' is the empty default
    for soff, eoff, label in annotations:
        if soff >= 0 and eoff >= 0:
            wli_info = \
                _get_ner_line_indexes(
                    tokens=words, token_lines=word_lines_indexes,
                    offset=(soff, eoff))
            
            if wli_info:
                from_wli, to_wli = wli_info

                # If a single line is affected
                if from_wli == to_wli:
                    to_wli += 1
                # end if

                for i in range(from_wli, to_wli):
                    input_lines[i][-1] = label
                # end for
            # end if
        # end if
    # end for
    
    with open(output_file, mode='w', encoding='utf-8') as f:
        for line in input_lines:
            if isinstance(line, list):
                print('\t'.join(line), file=f)
            else:
                print(line, file=f, end='')
            # end if
        # end for
    # end with
