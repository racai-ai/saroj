from flask import Flask, jsonify


from dictionary_process import *
from dictionary_config import args

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.saroj.input_data import get_input_data, is_file_conllu
from lib.saroj.dictionary_helper import read_replacement_dictionary, count_instances_in_dict
from lib.saroj.gunicorn import StandaloneApplication

app = Flask(__name__)


@app.route('/process', methods=['POST', 'GET'])
def anonymize_conllup():
    """
    Route to handle file upload, anonymization, and conversion to CONLLUP format.

    Expects a JSON object with "input", and "output" keys containing file paths.

    Returns:
        JSON: A response containing status and message, indicating the success or failure of the operation.

    This route is designed to handle the following tasks:

    1. Accept a JSON object specifying the file paths for input, output, and mapping.
    2. Anonymize Named Entity Recognition (NER) entities in the input file using a provided mapping file.
    3. Respond with a JSON object indicating the status of the operation.

    Input JSON format:
    - "input": Path to the file to be processed.
    - "output": Path to save the output file with anonymized content in the CONLLUP format.

    Upon successful execution, the response includes a 'status' of 'OK' and an empty message.
    In case of errors or exceptions during processing, the response contains an error message indicating the problem.

    Note:
    - The function relies on the presence of "input" and "output" keys in the JSON object.
    - The "args.DICTIONARY" attribute is expected to specify the dictionary file path.
    - Exceptions occurring during the process are caught and result in an "ERROR" status with an error message.
    """

    status, data, error = get_input_data(["input", "output"])
    if not status: return error

    input_file = data["input"]
    output_file = data["output"]

    if input_file == '':
        return jsonify({"status": "ERROR", "message": "No file selected."})
    if not is_file_conllu(input_file):
        return jsonify({"status": "ERROR", "message": "Input file is not conllup"})

    if input_file:
        try:
            # Read the replacement dictionary
            assign_ner(input_file, output_file, trie_root, max_count)

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
    if not args.DICTIONARY:
        return jsonify({"status": "OK", "message": f"The dictionary file parameter is missing."})

    if not os.path.exists(args.DICTIONARY):
        return jsonify({"status": "OK", "message": f"Dictionary file '{args.DICTIONARY}' does not exist."})

    replacement_dict = read_replacement_dictionary(args.DICTIONARY)

    if not replacement_dict:
        return jsonify({"status": "OK", "message": f"Dictionary file '{args.DICTIONARY}' is empty."})
    else:
        return jsonify({"status": "OK", "message": f"max_count = {max_count} containing "
                                                   f"{count_instances_in_dict(replacement_dict)}"})


if __name__ == '__main__':

    options = {
        'bind': '%s:%s' % ('127.0.0.1', args.PORT),
        'workers': 1,
    }
    dictionary, max_count = load_dictionary_with_max_token_count(args.DICTIONARY)
    trie_root = TrieNode()
    for key, value in dictionary.items():
        words = sorted(key.lower().split(), key=custom_sort)
        add_to_trie(trie_root, words, value)
    del dictionary

    #app.run(debug=True, port=args.PORT)
    StandaloneApplication(app, options).run()
