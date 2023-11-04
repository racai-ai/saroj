import os
import sys
from flask import Flask, jsonify

from voting_config import *
from voting_process import vote

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.saroj.input_data import get_input_data, are_files_conllu
from lib.saroj.gunicorn import StandaloneApplication

app = Flask(__name__)


@app.route('/process', methods=['POST', 'GET'])
def anonymize_conllup():
    """
    Route to handle file upload, anonymization, and conversion to CONLLUP format.

    Expects a JSON object with "input," "output," and "mapping" keys containing file paths.

    Returns:
        JSON: A response containing status and message, indicating the success or failure of the operation.

    This route is designed to handle the following tasks:

    1. Accept a JSON object specifying the file paths for input, output, and mapping.
    2. Anonymize Named Entity Recognition (NER) entities in the input file using a provided mapping file.
    3. Respond with a JSON object indicating the status of the operation.

    Input JSON format:
    - "input": Path to the file to be processed.
    - "output": Path to save the output file with anonymized content in the CONLLUP format.
    - "mapping": Path to the mapping file containing entity-to-replacement mappings.

    Upon successful execution, the response includes a 'status' of 'OK' and an empty message.
    In case of errors or exceptions during processing, the response contains an error message indicating the problem.

    Note:
    - The function relies on the presence of "input," "output," and "mapping" keys in the JSON object.
    - The "args.DICTIONARY" attribute is expected to specify the dictionary file path.
    - Exceptions occurring during the process are caught and result in an "ERROR" status with an error message.
    """

    status, data, error = get_input_data(["input", "output"])
    if not status: return error

    input_files = data["input"]
    output_file = data["output"]

    if input_files == '':
        return jsonify({"status": "ERROR", "message": "No file selected."})
    if not are_files_conllu(input_files):
        return jsonify({"status": "ERROR", "message": "Input file is not conllup"})

    if input_files:
        try:
            vote(args.ALGORITHM, input_files, output_file)

            return jsonify({"status": "OK", "message": ""})
        except Exception as e:
            return jsonify({"status": "ERROR", "message": str(e)})

    return jsonify({"status": "ERROR", "message": "Invalid file format or other error occurred."})


@app.route('/checkHealth', methods=['GET', 'POST'])
def check_health():
    """
    Endpoint to check the health/readiness of the module.

    Returns:
        JSON: A response indicating the status of the module, along with an optional message.

    The function checks the health/readiness of the module by performing the following steps:

    1. It verifies the existence of the specified dictionary file.
    2. It reads the replacement dictionary from the file.
    3. It checks if the replacement dictionary is empty.

    If all checks pass successfully, the function returns a JSON response with a 'status' of 'OK' and a message that may
    include statistics about the replacement dictionary.
    If any of the checks fail, an appropriate error message is included in the response.
    """

    return jsonify({"status": "OK", "message": ""})


if __name__ == '__main__':

    options = {
        'bind': '%s:%s' % ('127.0.0.1', args.PORT),
        'workers': 1,
    }
    #app.run(debug=True, port=args.PORT)
    StandaloneApplication(app, options).run()
