import os
from annotator import regex_annotate, read_conllu_file

def test_one():
    in_file = os.path.join('documents', 'test-1.out')
    out_file = os.path.join('documents', 'test-1.ner')

    if os.path.isfile(out_file):
        os.remove(out_file)
    # end if

    regex_annotate(input_file=in_file, output_file=out_file)
    out_lines = read_conllu_file(file=out_file, append_column=False)
    assert out_lines[9][-1] == 'ECLI'
    assert out_lines[38][-1] == 'DECISION'
    assert out_lines[114][-1] == 'CNP'
    assert out_lines[120][-1] == 'LOC'
    assert out_lines[123][-1] == 'LOC'
    assert out_lines[124][-1] == 'LOC'
    assert out_lines[128][-1] == 'LOC'
    assert out_lines[141][-1] == 'LOC'
    assert out_lines[144][-1] == 'LOC'
    assert out_lines[145][-1] == 'LOC'
    assert out_lines[146][-1] == 'LOC'
    assert out_lines[149][-1] == 'LOC'
    assert out_lines[152][-1] == 'LOC'
    assert out_lines[155][-1] == 'LOC'
    assert out_lines[155][-1] == 'LOC'
    assert out_lines[158][-1] == 'LOC'
    assert out_lines[162][-1] == 'LOC'
    assert out_lines[162][-1] == 'LOC'
    assert out_lines[165][-1] == 'LOC'
    assert out_lines[244][-1] == 'INITIALS'
    assert out_lines[252][-1] == 'INITIALS'
