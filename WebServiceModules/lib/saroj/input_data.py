import json

from flask import request, jsonify


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
