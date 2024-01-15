import os
import sys
from nerregex import do_regex_ner
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.saroj.conllu_utils import CoNLLUFileAnnotator

class RegExAnnotator(CoNLLUFileAnnotator):
    def provide_annotations(self, text: str) -> list[tuple[int, int, str]]:
        return do_regex_ner(text=text)
