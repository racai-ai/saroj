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

    assert out_lines[0][2][-1] == 'B-ECLI'
    assert out_lines[1][0][-1] == 'B-CASE'
    assert out_lines[3][0][-1] == 'B-DECISION'
    assert out_lines[8][4][-1] == 'B-CNP'
    assert out_lines[8][10][-1] == 'B-LOC'
    assert out_lines[8][13][-1] == 'B-LOC'
    assert out_lines[8][14][-1] == 'I-LOC'
    assert out_lines[8][15][-1] == 'I-LOC'
    assert out_lines[8][18][-1] == 'B-LOC'
    assert out_lines[8][31][-1] == 'B-LOC'
    assert out_lines[8][34][-1] == 'B-LOC'
    assert out_lines[8][35][-1] == 'I-LOC'
    assert out_lines[8][36][-1] == 'I-LOC'
    assert out_lines[8][39][-1] == 'B-LOC'
    assert out_lines[8][42][-1] == 'B-LOC'
    assert out_lines[8][45][-1] == 'B-LOC'
    assert out_lines[8][48][-1] == 'B-LOC'
    assert out_lines[8][52][-1] == 'B-LOC'
    assert out_lines[8][55][-1] == 'B-LOC'
    assert out_lines[13][0][-1] == 'B-INITIALS'
    assert out_lines[14][0][-1] == 'B-INITIALS'
