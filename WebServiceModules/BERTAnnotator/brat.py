import sys
import re
import os
from pathlib import Path


_crlf_rx = re.compile('\r?\n$')


def read_txt_ann_pair(txt_file: str, ann_file: str) -> dict[str, list[tuple[str, int, int]]]:
    """Reads in a pair of a text file and its BRAT annotation counterpart
    and returns the list of paragraphs along with start/end offsets of annotations."""

    ann_offsets = []

    with open(ann_file, mode='r', encoding='utf-8') as f:
        line_count = 0
        
        for line in f:
            line_count += 1
            line_parts = line.strip().split('\t')
            example_added = False

            if len(line_parts) == 3:
                tid, offsets, entity = line_parts

                if tid and offsets and entity:
                    offs_parts = offsets.split()

                    if len(offs_parts) == 3:
                        label, start_off, end_off = offs_parts
                        start_off = int(start_off)
                        end_off = int(end_off)
                        ann_offsets.append((label, start_off, end_off, entity))
                        example_added = True
                    # end if
                # end if
            # end if

            if not example_added:
                print(f'Problem with example @ line [{line_count}] in .ann file [{ann_file}]',
                    file=sys.stderr, flush=True)
            # end if
        # end for
    # end with

    crt_offset = 0
    eol_offset = 0
    annotations = {}

    with open(txt_file, mode='r', encoding='utf-8', newline='') as f:
        # For each paragraph line
        for p_line in f:
            if p_line.endswith('\r\n'):
                _with_crlf = True
            else:
                _with_crlf = False
            # end if
            
            p_line = _crlf_rx.sub('', p_line)
            # If you want to split p_line into sentences,
            # add s_lines = list of sentences from p_line
            s_lines = [p_line]

            if not s_lines:
                if _with_crlf:
                    # Skip over \r and \n
                    eol_offset += 2
                else:
                    # Skip over \n
                    eol_offset += 1
                # end if

                crt_offset = eol_offset
            # end if

            # For each sentence line
            for i, line in enumerate(s_lines):
                eol_offset = crt_offset + len(line)

                if i == len(s_lines) - 1:
                    if _with_crlf:
                        # Skip over \r and \n
                        eol_offset += 2
                    else:
                        # Skip over \n
                        eol_offset += 1
                    # end if
                # end if

                for lbl, soff, eoff, ent in ann_offsets:
                    if soff >= crt_offset and eoff <= eol_offset:
                        line_soff = soff - crt_offset
                        line_eoff = eoff - crt_offset
                        
                        assert line[line_soff:line_eoff] == ent

                        if line not in annotations:
                            annotations[line] = []
                        # end if

                        annotations[line].append((lbl, line_soff, line_eoff))
                    # end if
                # end for

                crt_offset = eol_offset
            # end all sentence lines
        # end for
    # end with

    return annotations


def read_txt_ann_folder(ann_folder: str,
                        annotations: dict[str, list[tuple[str, int, int]]]) -> None:
    """Reads all BRAT annotations from folder and puts them in `annotations`."""

    for txt in os.listdir(ann_folder):
        if txt.endswith('.txt'):
            ann = os.path.join(ann_folder, Path(txt).stem + '.ann')

            if os.path.isfile(ann):
                txt = os.path.join(ann_folder, txt)
                results = read_txt_ann_pair(txt_file=txt, ann_file=ann)

                for line in results:
                    if line not in annotations:
                        annotations[line] = results[line]
                    else:
                        for lb1, so1, eo1 in results[line]:
                            conflict_found = False

                            for lb2, so2, eo2 in annotations[line]:
                                if ((so2 <= so1 and so1 <= eo2) or \
                                        (so2 <= eo1 and eo1 <= eo2)) and \
                                        lb1 != lb2:
                                    print(f'Conflicting annotation in file [{ann}]:', file=sys.stderr, flush=True)
                                    print(f'  -> {lb1} @ {so1} -- {eo1}', file=sys.stderr, flush=True)
                                    print(f'  -> {lb2} @ {so2} -- {eo2}', file=sys.stderr, flush=True)
                                    conflict_found = True
                                    break
                                # end if
                            # end search for conflic

                            if not conflict_found and \
                                    (lb1, so1, eo1) not in annotations[line]:
                                annotations[line].append((lb1, so1, eo1))
                            # end if
                        # end for
                    # end if
                # end for all lines in annotations
            # end if
        # end if
    # end for


def produce_ner_labels(annotations: dict[str, list[tuple[str, int, int]]]) -> list[str]:
    existing_labels = set()

    for line in annotations:
        existing_labels = existing_labels.union([lbl for lbl, _, _ in annotations[line]])
    # end for

    the_labels = ['O']

    for lbl in sorted(existing_labels):
        the_labels.append(f'B-{lbl}')
        the_labels.append(f'I-{lbl}')
    # end for

    return the_labels
