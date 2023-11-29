import json
from flask import request, jsonify
from .conllu_utils import is_file_conllu


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


def are_files_conllu(input_files):
    for file_path in input_files:
        if not is_file_conllu(file_path):
            return False
    return True
