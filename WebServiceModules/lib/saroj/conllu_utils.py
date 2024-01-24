import re

def read_conllu_file(file: str, append_column: bool = True) -> list[list[str | list[str]]]:
    """Reads a whole CoNLL-U file and stores lines as comments or
    or tuples of fields if the line contains annotations. When an empty
    line is found, a sentence boundary is inserted. Returns the list of
    such sentences from the file."""

    file_sentences = []
    crt_sentence = []

    with open(file, mode='r', encoding='utf-8') as f:
        for line in f:
            if CoNLLUFileAnnotator._int_rx.match(line):
                fields = line.strip().split()

                if append_column:
                    # That's for NER info
                    # All tokens are 'O'utside any annotation,
                    # to begin with
                    fields.append('O')
                # end if

                crt_sentence.append(fields)
            elif not line.strip():
                if crt_sentence:
                    file_sentences.append(crt_sentence)
                    crt_sentence = []
                # end if
            else:
                crt_sentence.append(line)
            # end if
        # end for
    # end with
                
    if crt_sentence:
        file_sentences.append(crt_sentence)
    # end if

    return file_sentences


_token_id_rx = re.compile(r'\d+')


def is_file_conllu(input_file: str) -> bool:
    """Takes an input file path and verifies if it is a CoNLL-U file.
    File is CoNLL-U if:
    - there are multiple tokens beginning with an int;
    - IDs are consecutive in a sentence;
    - all lines which are not comments have the same number of fields.
    It will IGNORE all UTF-8 related encodings errors!"""

    number_of_fields = 0
    previous_id = 0

    with open(file=input_file, mode='r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()

            if line and not line.startswith('#'):
                parts = line.split()

                if number_of_fields == 0:
                    number_of_fields = len(parts)
                elif number_of_fields != len(parts):
                    # A line with a different number of fields.
                    # CoNLL-U isn't valid.
                    return False
                # end if

                if _token_id_rx.fullmatch(parts[0]):
                    tid = int(parts[0])

                    if previous_id == 0:
                        if tid != 1:
                            # First ID in the sentence is not 1
                            # CoNLL-U isn't valid.
                            return False
                        else:
                            previous_id = 1
                        # end if
                    elif previous_id + 1 != tid:
                        # IDs are not consecutive.
                        # CoNLL-U isn't valid.
                        return False
                    else:
                        previous_id = tid
                    # end if
                else:
                    # There is no ID as the first token of the line
                    # CoNLL-U isn't valid.
                    return False
                # end if
            else:
                previous_id = 0
            # end if
        # end for
    # end with

    return True


class CoNLLUFileAnnotator(object):
    """This class represents a CoNLL-U file for an NER annotator,
    which takes the CoNLL-U file, extracts the text, runs the annotator
    and then inserts the annotations back into the CoNLL-U file, on the last column.
    Sub-classes have to implement the `annotate()` method."""

    _int_rx = re.compile(r'^\d+\s')

    def __init__(self, input_file: str):
        """Takes a CoNLL-U `input_file` and parses it."""
        if not is_file_conllu(input_file):
            raise RuntimeError(f'File [{input_file}] is not a valid CoNLL-U file.')
        # end if

        self._conllu_sentences = read_conllu_file(file=input_file)
    
    def _no_space_after(self, words: list[str], index: int):
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

    def _get_text_from_conllu_sentence(self,
                                       conllu_sentence: list[str | list[str]]) -> tuple[str, list[str], list[int]]:
        """Takes one sentence as returned by function `read_conllu_file()` and returns the text
        formed by joining all tokens with spaces, removing spaces around punctuation.
        Also returns a list of token to file line indexes and the list of normalized tokens."""

        words_indexes = []
        words = []

        for i, line in enumerate(conllu_sentence):
            if isinstance(line, list):
                word = line[1]
                words_indexes.append(i)
                words.append(word + ' ')
            # end if
        # end for

        # Normalize text: no space between comma and previous word
        for i in range(len(words)):
            self._no_space_after(words=words, index=i)
        # end for

        sentence_text = ''.join(words)
        return sentence_text, words, words_indexes

    def _add_iob_to_label(self, label: str) -> bool:
        return not label.startswith('B-') and \
            not label.startswith('I-') and \
            label != 'O'

    def annotate(self, output_file: str):
        """Does the annotation, using the abstract method `provide_annotations()`
        and writes the resulting file to `output_file`."""

        previous_sentnce = ''

        with open(output_file, mode='w', encoding='utf-8') as f:
            # Go sentence by sentence
            for conllu_sentence in self._conllu_sentences:
                sentence, snt_words, snt_words_indexes = \
                    self._get_text_from_conllu_sentence(conllu_sentence)
                annotations = \
                    self.provide_annotations(
                        text=sentence, text_before=previous_sentnce)

                # Insert the annotations on the last column
                # 'O' is the 'outside' default
                for soff, eoff, label in annotations:
                    if soff >= 0 and eoff >= 0 and label != 'O':
                        wli_info = \
                            self._get_ner_line_indexes_in_sentence(
                                offset=(soff, eoff),
                                s_words=snt_words,
                                s_words_indexes=snt_words_indexes)

                        if wli_info:
                            from_wli, to_wli = wli_info

                            # If a single line is affected
                            if from_wli == to_wli:
                                to_wli += 1
                            # end if

                            # Also do the BIO annotation here,
                            # as here we have consecutive tokens.
                            for i in range(from_wli, to_wli):
                                if isinstance(conllu_sentence[i], list):
                                    if i == from_wli: 
                                        if self._add_iob_to_label(label):
                                            conllu_sentence[i][-1] = f'B-{label}'
                                        else:
                                            conllu_sentence[i][-1] = label
                                        # end if
                                    else:
                                        if self._add_iob_to_label(label):
                                            conllu_sentence[i][-1] = f'I-{label}'
                                        else:
                                            conllu_sentence[i][-1] = label
                                        # end if
                                    # end if
                                # end if
                            # end for
                        # end if
                    # end if
                # end for annotations in sentence
                
                for line in conllu_sentence:
                    if isinstance(line, list):
                        print('\t'.join(line), file=f)
                    else:
                        # EOL is already included
                        print(line, file=f, end='')
                    # end if
                # end for
                
                # Print EOS mark
                print(file=f)
                previous_sentnce = sentence
            # end for sentence
        # end with

    def provide_annotations(self, text: str, text_before: str) -> list[tuple[int, int, str]]:
        """This is the specific annotator method. To be implemented in sub-classes.
        Takes the `text` to annotate and returns a list of (start_offset, end_offset, label) annotations
        relative to `text`. Some annotators may need the previous text `text_before` to work, such as
        the previous sentence if `text` is the current sentence."""

        raise NotImplementedError('Do not know how to supply the annotations. Please implement me!')

    def _get_ner_line_indexes_in_sentence(self,
                                          offset: tuple[int, int],
                                          s_words: list[str],
                                          s_words_indexes: list[int]) -> tuple[int, int] | None:
        """Given a start_offset, end_offset `offset` tuple, retrieves the range
        of the index(es) of the line(s) in the CoNLL-U sentence which
        should receive the NER annotation."""

        the_offset = 0
        left_i = -1
        right_i = -1

        for i, tok in enumerate(s_words):
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
            return (s_words_indexes[left_i], s_words_indexes[right_i])
        else:
            return None
        # end if
