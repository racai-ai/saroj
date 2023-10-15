import argparse
import os
import sys

from flask import Flask, jsonify

from entityMapping_process import read_replacement_dictionary, anonymize_entities

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.saroj.input_data import get_input_data
from lib.saroj.gunicorn import StandaloneApplication

app = Flask(__name__)


@app.route('/process', methods=['POST', 'GET'])
def anonymize_docx():
    """
    Route to handle file upload and anonymization from .docx to CONLLUP.

    Expects a JSON object with "input", "output" and "mapping" keys containing file paths.

    Returns:
        JSON: A response containing status and message (e.g., {'status': 'OK', 'message': ''}).
    """

    status, data, error = get_input_data(["input", "output", "mapping"])
    if not status: return error

    input_file = data["input"]
    output_file = data["output"]
    mapping_file = data["mapping"]

    if input_file == '':
        return jsonify({"status": "ERROR", "message": "No file selected."})

    if input_file:
        try:
            # Read the replacement dictionary
            replacement_dict = read_replacement_dictionary(args.DICTIONARY)

            # Anonymize entities in the input file and write to the output file
            anonymize_entities(input_file, output_file, mapping_file, replacement_dict)

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
    parser.add_argument('--DICTIONARY', '-d', type=str, help='path for dictionary, mandatory ')
    args = parser.parse_args()

    if not os.path.exists(args.DICTIONARY):
        print(f"Replacement dictionary file '{args.DICTIONARY}' does not exist.")
        exit(1)

    options = {
        'bind': '%s:%s' % ('127.0.0.1', args.PORT),
        'workers': 1,
    }
    #app.run(debug=True, port=args.PORT)
    StandaloneApplication(app, options).run()
