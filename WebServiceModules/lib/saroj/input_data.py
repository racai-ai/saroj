import re
import json
from flask import request, jsonify

_token_id_rx = re.compile(r'\d+')


def get_input_data(expected_values):
    if "input" not in request.values:
        return False, None, jsonify({"status": "ERROR", "message": "Missing input parameter"})

    try:
        data = json.loads(request.values["input"])
    except json.JSONDecodeError:
        return False, None, jsonify({"status": "ERROR", "message": "Invalid JSON provided in the input parameter"})

    if data is None:
        return False, None, jsonify(
            {"status": "ERROR", "message": "Invalid input JSON provided in the input parameter"})

    for v in expected_values:
        if v not in data:
            return False, None, jsonify({"status": "ERROR",
                                         "message": "Invalid input JSON provided in the input parameter. Missing field {value}".format(
                                             value=v)})

    return True, data, None


def is_file_conllu(input_file: str) -> bool:
    """Takes an input file path and verifies if it is a CoNLL-U file.
    File is CoNLL-U if:
    - there are multiple tokens beginning with an int;
    - IDs are consecutive in a sentence;
    - all lines which are not comments have the same number of fields."""

    number_of_fields = 0
    previous_id = 0

    try:
        with open(file=input_file, mode='r', encoding='utf-8', errors="ignore") as f:
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
    except FileNotFoundError:
        print(f'The file at {input_file} does not exist.')
    return True


def are_files_conllu(input_files):
    for file_path in input_files:
        if not is_file_conllu(file_path):
            return False
    return True
