from nerregex import do_regex_ner
from lib.saroj.conllu_utils import CoNLLUFileAnnotator

class RegExAnnotator(CoNLLUFileAnnotator):
    def provide_annotations(self, text: str) -> list[tuple[int, int, str]]:
        return do_regex_ner(text=text, label_map=True)
