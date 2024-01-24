import os
from annotator import RegExAnnotator
from lib.saroj.conllu_utils import read_conllu_file

def test_one():
    in_file = os.path.join('documents', 'test-1.out')
    out_file = os.path.join('documents', 'test-1.ner')

    if os.path.isfile(out_file):
        os.remove(out_file)
    # end if

    ann = RegExAnnotator(input_file=in_file)
    ann.annotate(output_file=out_file)
    out_lines = read_conllu_file(file=out_file, append_column=False)

    assert out_lines[0][9][-1] == 'B-ECLI'
    assert out_lines[1][2][-1] == 'B-CASE'
    assert out_lines[3][2][-1] == 'B-DECISION'
    assert out_lines[8][6][-1] == 'B-CNP'
    assert out_lines[8][36][-1] == 'B-LOC'
    assert out_lines[8][41][-1] == 'B-LOC'
    assert out_lines[8][44][-1] == 'B-LOC'
    assert out_lines[8][47][-1] == 'B-LOC'
    assert out_lines[8][50][-1] == 'B-LOC'
    assert out_lines[8][54][-1] == 'B-LOC'
    assert out_lines[8][57][-1] == 'B-LOC'
    assert out_lines[13][2][-1] == 'B-INITIALS'
    assert out_lines[14][2][-1] == 'B-INITIALS'
