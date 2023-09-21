import argparse
import os
import sys

from flask import Flask, jsonify
from entityEncoding_process import read_mapping, process_conllup

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.saroj.input_data import get_input_data

from lib.saroj.gunicorn import StandaloneApplication

app = Flask(__name__)


@app.route('/process', methods=['POST', 'GET'])
def anonymize_docx():
    """
    Route to handle entity mapping inside CONLLU-P file.

    Expects a JSON object with "input", "output" and "mapping" keys containing file paths.

    Returns:
        JSON: A response containing status and message (e.g., {'status': 'OK', 'message': ''}).
    """

    status, data, error = get_input_data(["input", "output", "mapping"])
    if not status:
        return error

    input_path = data["input"]
    output_path = data["output"]
    mapping_path = data["mapping"]

    if input_path == '':
        return jsonify({"status": "ERROR", "message": "No file selected."})

    if input_path:
        try:
            entity_mapping = read_mapping(mapping_path)
            process_conllup(input_path, output_path, mapping_path, entity_mapping)
            return jsonify({"status": "OK", "message": ""})
        except Exception as e:
            return jsonify({"status": "ERROR", "message": str(e)})

    return jsonify({"status": "ERROR", "message": "Invalid file format or other error occurred."})


@app.route('/checkHealth', methods=['GET', 'POST'])
def check_health():
    """
    Endpoint to check the health/readiness of the module.

    Returns:
        JSON: A response indicating the status of the module (e.g., {'status': 'OK', 'message': ''}).
    """
    return jsonify({"status": "OK", "message": ""})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('PORT', type=int, help='Port to listen for requests')
    args = parser.parse_args()

    token_model = None

    options = {
        'bind': '%s:%s' % ('127.0.0.1', args.PORT),
        'workers': 1,
    }
    #app.run(debug=True, port=args.PORT)
    StandaloneApplication(app, options).run()
