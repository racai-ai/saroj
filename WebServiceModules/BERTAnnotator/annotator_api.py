import os
import sys
import argparse
from flask import Flask, jsonify
from annotator import NeuralAnnotator, BERTEntityTagger
from bert import ReaderbenchSmall
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.saroj.gunicorn import StandaloneApplication
from lib.saroj.input_data import get_input_data
from lib.saroj.conllu_utils import is_file_conllu

app = Flask(__name__)
tagger = None

import sys, traceback

@app.route('/process', methods=['POST', 'GET'])
def annotate_conllu():
    """
    Route to handle file annotation with regular expressions.

    Expects an `.out` input file produced by the `../TextExtractor/textExtractor_api.py` module in this repo.

    Test with `{'input': 'documents/test-1.out', 'output': 'documents/test-1.ner'}` from the `documents` folder.

    Returns:
        JSON: A response containing status and message (e.g., `{'status': 'OK', 'message': '/path/to/output_file.ner'}`).
    """

    status, data, error = get_input_data(['input', 'output'])

    if not status:
        return error
    # end if

    input_file = data['input']
    output_file = data['output']

    if not input_file:
        return jsonify({'status': 'ERROR', 'message': 'No file selected.'})
    elif not os.path.isfile(input_file):
        return jsonify({'status': 'ERROR',
                        'message': 'Input file does not exist on the local storage.'})
    elif not is_file_conllu(input_file):
        return jsonify({'status': 'ERROR',
                        'message': 'Input file is not a (valid) CoNLL-U file.'})
    # end if

    # Model has to be loaded in worker, otherwise PyTorch freezes.
    # There is no way to load this in a more principled way, but
    # it's pretty fast and persisted after the load.
    global tagger

    if tagger is None:
        tagger = BERTEntityTagger(bert_model=ReaderbenchSmall())
        tagger.load(model_folder=args.MODEL)
    # end if

    try:
        ann = NeuralAnnotator(input_file, tagger)
        ann.annotate(output_file)
        return jsonify({'status': 'OK', 'message': output_file})
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify({'status': 'ERROR', 'message': str(e)})
    # end try


@app.route('/checkHealth', methods=['GET', 'POST'])
def check_health():
    """
    Endpoint to check the health/readiness of the module.

    Returns:
        JSON: A response indicating the status of the module (e.g., `{'status': 'OK', 'message': ''}`).
    """

    return jsonify({'status': 'OK', 'message': ''})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('PORT', type=int, help='port to listen for requests')
    parser.add_argument('MODEL', type=str, help='folder to read the model from')
    args = parser.parse_args()

    options = {
        'bind': f'127.0.0.1:{args.PORT}',
        'workers': 1
    }

    if not os.path.isdir(args.MODEL):
        print(f'Model folder [{args.MODEL}] is not a folder in the file system', file=sys.stderr, flush=True)
        exit(1)
    # end if

    StandaloneApplication(app, options).run()
    # This is for Windows debug testing only.
    #app.run(host='127.0.0.1', port=args.PORT)
