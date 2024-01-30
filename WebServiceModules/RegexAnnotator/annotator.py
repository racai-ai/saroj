import os
import sys
from nerregex import do_regex_ner
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.saroj.conllu_utils import CoNLLUFileAnnotator

class RegExAnnotator(CoNLLUFileAnnotator):
    def __init__(self, input_file: str):
        super().__init__(input_file)
        self._previous_sentences = []

    # Assumes the CoNLL-U file is processed sentence by sentence (which it is)
    def provide_annotations(self, sentence: str) -> list[tuple[int, int, str]]:
        accumulated_text = ' '.join(self._previous_sentences)
        rx_annotations = do_regex_ner(text=sentence, previous_text=accumulated_text)
        
        # Keep only last 3 sentences as previous context
        if not self._previous_sentences or \
                len(self._previous_sentences) < 3:
            self._previous_sentences.append(sentence)
        else:
            self._previous_sentences.pop(0)
            self._previous_sentences.append(sentence)
        # end if
            
        return rx_annotations
