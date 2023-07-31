import argparse

import docx2txt
import ufal.udpipe as ud
from conllu import parse
from flask import Flask, request, jsonify

app = Flask(__name__)


def process_text_with_udpipe(udpipe_model, text):
    """
    Process the input 'text' using UDPipe.

    Parameters:
        udpipe_model (str): The instance of UDPipe model.
        text (str): The text to be processed.

    Returns:
        tuple: A tuple containing the parsed token list and any potential error message (None if successful).
    """

    # Create an UDPipe pipeline
    pipeline = ud.Pipeline(udpipe_model, 'tokenizer', 'horizontal', 'conllu', ud.Pipeline.DEFAULT)

    # Process the text
    if not text:
        raise Exception("Empty .docx file")
    processed_text = pipeline.process(text)

    if not processed_text:
        raise Exception("Error occurred while processing text with UDPipe.")

    # Use the conllu library to parse the CONLL-U output into a TokenList object
    token_list = parse(processed_text)

    return token_list, None


def dict_to_string(d):
    """
    Convert a dictionary to a string representation.

    Parameters:
        d (dict): The dictionary to be converted.

    Returns:
        str: The string representation of the dictionary in the format "key1=value1|key2=value2|..."
             or an underscore (_) if the dictionary is empty.
    """
    if d:
        return "|".join([f"{key}={value}" for key, value in d.items()])
    else:
        return "_"


def format_none_value(value):
    """
    Convert None values to underscores to conform to the CONLL-U format.

    Parameters:
        value: The value to be converted.

    Returns:
        str: The converted value as a string or an underscore (_) if the value is None.
    """
    return "_" if value is None else str(value)


def docx_to_conllup(docx_file, output_file, run_analysis=False, save_internal_files=False):
    """
    Convert a .docx file to CONLL-U formatted text.

    Parameters:
        docx_file (str): The path to the input .docx file.
        output_file (str): The path where the CONLL-U formatted text will be saved.
        run_analysis (bool, optional): Whether to run text analysis using UDPipe. Default is False.
        save_internal_files (bool, optional): Whether to save internal files (useful for debugging). Default is False.

    Returns:
        str: The path of the output_file after processing (if run_analysis is False) or the CONLL-U formatted text.
    """
    text = docx2txt.process(docx_file)

    conllup_text = ""
    if run_analysis:
        # Process the text using UDPipe
        token_list, error = process_text_with_udpipe(model, text)
        if error:
            raise Exception("Error occurred while processing text with UDPipe.")

        # Convert the TokenList object to CONLL-U formatted string
        start_offset = 0
        for sentence in token_list:
            for token in sentence:
                end_offset = start_offset + text[start_offset:].find(token["form"]) + len(token["form"]) - 1
                start_offset += text[start_offset:].find(token["form"])

                token_info = [
                    str(token["id"]),
                    token["form"],
                    token["lemma"],
                    format_none_value(token["upos"]),
                    format_none_value(token["xpos"]),
                    dict_to_string(token["feats"]),
                    format_none_value(str(token["head"])),
                    format_none_value(token["deprel"]),
                    format_none_value(token["deps"]),
                    dict_to_string(token["misc"]),
                    str(start_offset),
                    str(end_offset),
                    "_",  # NER
                ]
                conllup_text += "\t".join(token_info) + "\n"

                # Move the start offset to the end of the token and any spaces after it
                start_offset = end_offset

            conllup_text += "\n"

    if save_internal_files and run_analysis:
        # Save the CONLL-U formatted text to the output file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(conllup_text)
    return output_file


def allowed_file(filename):
    """
    Check if the given filename has a valid extension.

    Parameters:
        filename (str): The name of the file to be checked.

    Returns:
        bool: True if the file has a valid extension (in this case, .docx), False otherwise.
    """
    allowed_extensions = {'docx'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/process', methods=['POST'])
def convert_docx_to_conllu():
    """
    Route to handle file upload and conversion from .docx to CONLL-U.

    Expects a JSON object with "input" and "output" keys containing file paths.

    Returns:
        JSON: A response containing status and message (e.g., {'status': 'OK', 'message': 'output_file.conllup'}).
    """
    data = request.get_json()
    if data is None or "input" not in data or "output" not in data:
        return jsonify({"status": "ERROR",
                        "message": "Invalid input format. Expected: {'input': '/path/to/file.docx', 'output': "
                                   "'/path/to/file.conllup'}"})

    input_file = data["input"]
    output_file = data["output"]

    if input_file == '':
        return jsonify({"status": "ERROR", "message": "No file selected."}), 400

    if input_file and allowed_file(input_file):
        try:
            docx_to_conllup(input_file, output_file, args.RUN_ANALYSIS, args.SAVE_INTERNAL_FILES)
            return jsonify({"status": "OK", "message": output_file}), 200
        except Exception as e:
            return jsonify({"status": "ERROR", "message": str(e)}), 500

    return jsonify({"status": "ERROR", "message": "Invalid file format or other error occurred."}), 400


@app.route('/checkHealth', methods=['GET'])
def check_health():
    """
    Endpoint to check the health/readiness of the module.

    Returns:
        JSON: A response indicating the status of the module (e.g., {'status': 'OK', 'message': 'Module is ready.'}).
    """
    return jsonify({"status": "OK", "message": "Module is ready."})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('PORT', type=int, help='port to listen for requests')
    parser.add_argument('--RUN_ANALYSIS', '-r', action='store_true', help='Y to run text analysis using UDPIPE')
    parser.add_argument('--SAVE_INTERNAL_FILES', '-s', action='store_true',
                        help='Y to save internal files, useful for debugging')
    parser.add_argument("udpipe_model_path", type=str, help="Path to the UDPipe model file.")

    args = parser.parse_args()

    model = ud.Model.load(args.udpipe_model_path)

    app.run(debug=True, port=args.PORT)
