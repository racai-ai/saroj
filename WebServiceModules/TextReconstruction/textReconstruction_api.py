import argparse
import os
import sys

from flask import Flask, jsonify
from textReconstruction_process import anonymize, read_conllup

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.saroj.input_data import get_input_data
from lib.saroj.gunicorn import StandaloneApplication

app = Flask(__name__)


@app.route('/process', methods=['POST', 'GET'])
def anonymize_docx():
    """
    Route to handle file upload and anonymization from .docx to CONLLUP.

    Expects a JSON object with "input", "output" and "original" keys containing file paths.

    Returns:
        JSON: A response containing status and message (e.g., {'status': 'OK', 'message': ''}).
    """

    status, data, error = get_input_data(["input", "output", "original"])
    if not status: return error

    input_file = data["input"]
    output_docx_path = data["output"]
    original_docx_path = data["original"]

    input_type="docx"
    valid_types={"txt":True,"docx":True}
    if "type" in data:
        input_type = data["type"].lower()
        if input_type not in valid_types: input_type="docx"

    if input_file == '':
        return jsonify({"status": "ERROR", "message": "No file selected."})

    if input_file:
        try:
            conllup_data = read_conllup(input_file)
            anonymize(conllup_data, original_docx_path, output_docx_path, args.SAVE_INTERNAL_FILES, input_type)
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
    parser.add_argument('--SAVE_INTERNAL_FILES', '-s', action='store_true',
                        help='if present, will save internal files, useful for debugging')
    args = parser.parse_args()

    token_model = None

    options = {
        'bind': '%s:%s' % ('127.0.0.1', args.PORT),
        'workers': 1,
    }
    #app.run(debug=True, port=args.PORT)
    StandaloneApplication(app, options).run()
