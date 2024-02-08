import ufal.udpipe as ud
from flask import Flask, jsonify
import spacy

from textExtractor_process import docx_to_conllup
from textExtractor_helpers import allowed_file, create_replacement_regex
from textExtractor_config import args

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.saroj.gunicorn import StandaloneApplication
from lib.saroj.input_data import get_input_data

app = Flask(__name__)


@app.route('/process', methods=['POST', 'GET'])
def convert_docx_to_conllu():
    """
    Route to handle file upload and conversion from .docx to CONLL-U.

    Expects a JSON object with "input" and "output" keys containing file paths.

    Returns:
        JSON: A response containing status and message (e.g., {'status': 'OK', 'message': 'output_file.conllup'}).
    """
    if args.RUN_ANALYSIS and token_model is None:
        return jsonify({"status": "ERROR", "message": "UDPipe model not loaded."})

    status, data, error = get_input_data(["input","output"])
    if not status: return error

    input_file = data["input"]
    output_file = data["output"]
    input_type="docx"
    valid_types={"txt":True,"docx":True}
    if "type" in data:
        input_type = data["type"].lower()
        if input_type not in valid_types: input_type="docx"

    if input_file == '':
        return jsonify({"status": "ERROR", "message": "No file selected."})
    if input_type == "docx" and not allowed_file(input_file):
        return jsonify({"status": "ERROR", "message": "Invalid file format."})

    if input_file:
        try:
            docx_to_conllup(token_model, input_file, output_file, regex, replacements, input_type)
            return jsonify({"status": "OK", "message": output_file})
        except Exception as e:
            return jsonify({"status": "ERROR", "message": str(e)})

    return jsonify({"status": "ERROR", "message": "Invalid file format or other error occurred."})


@app.route('/checkHealth', methods=['GET','POST'])
def check_health():
    """
    Endpoint to check the health/readiness of the module.

    Returns:
        JSON: A response indicating the status of the module (e.g., {'status': 'OK', 'message': ''}).
    """
    if args.RUN_ANALYSIS and token_model is None:
        return jsonify({"status": "ERROR", "message": "UDPipe model not loaded."})

    return jsonify({"status": "OK", "message": ""})


if __name__ == '__main__':

    token_model = None
    if args.udpipe_model:
        token_model = ud.Model.load(args.udpipe_model)

    if not args.RUN_ANALYSIS:
        token_model = spacy.load("ro_core_news_sm")

    regex, replacements = create_replacement_regex()
    
    options = {
        'bind': '%s:%s' % ('127.0.0.1', args.PORT),
        'workers': 1,
    }
    StandaloneApplication(app, options).run()
    #app.run(debug=True, port=args.PORT)
