import os
import sys
from nerregex import do_regex_ner
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.saroj.conllu_utils import CoNLLUFileAnnotator

class RegExAnnotator(CoNLLUFileAnnotator):
    def __init__(self, input_file: str):
        super().__init__(input_file)
        self._accumulated_text = ''

    # Assumes the CoNLL-U file is processed sentence by sentence (which it is)
    def provide_annotations(self, sentence: str) -> list[tuple[int, int, str]]:
        rx_annotations = do_regex_ner(text=sentence, previous_text=self._accumulated_text)
        
        if not self._accumulated_text:
            self._accumulated_text = sentence
        else:
            self._accumulated_text += ' ' + sentence
        # end if
            
        return rx_annotations
