import argparse
import os
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile

import spacy
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


def is_followed_by_punctuation(token, text):
    """ Check if a token is followed by punctuation or space in the text."""
    # Escape the token for use in the regex pattern
    escaped_token = re.escape(token)

    # List of punctuation characters to check for
    punctuation_characters = r" .,;:!?()[]{}'\""

    # Construct the regex pattern with positive lookahead for the punctuation characters
    pattern = r"{0}(?=[{1}])".format(escaped_token, re.escape(punctuation_characters))

    # Check if the pattern is found in the text
    return bool(re.search(pattern, text))


def format_none_value(value):
    """
    Convert None values to underscores to conform to the CONLL-U format.

    Parameters:
        value: The value to be converted.

    Returns:
        str: The converted value as a string or an underscore (_) if the value is None.
    """
    return "_" if value is None else str(value)


def udpipe_token_to_conllup(token_list, words):
    """
      Convert a list of tokens to CONLL-U formatted text.

      Parameters:
          token_list (list): A list of token dictionaries.
          words (list): A list of tuples containing the words and their offsets in the original text.

      Returns:
          str: The CONLL-U formatted text representing the list of tokens.

      Note:
          The `token_list` parameter should be a list of dictionaries, where each dictionary represents a token and its
          associated metadata. The function converts this list of tokens to CONLL-U format, where each line corresponds to
          a token, and the columns represent the token attributes (ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL,
          DEPS, MISC, START, END, NER)."""

    conllup_text = ""
    words_id = 0
    cursor_acc = 0
    acc = ""
    for sentence in token_list:
        for token in sentence:
            acc_count = 0
            cursor = 0
            word_reconstructed = ""
            while word_reconstructed != token["form"] and words_id < len(words):

                if token["form"] in words[words_id][0][cursor:]:
                    cursor += words[words_id][0].find(token["form"])
                    start_offset = words[words_id][1] + cursor
                    end_offset = start_offset + len(token["form"])
                    word_reconstructed = words[words_id][0][cursor:cursor + len(token["form"])]

                    if cursor + len(token["form"]) > len(words[words_id][0]):
                        cursor = 0
                    cursor_acc = 0
                    acc = ""
                    continue
                else:
                    acc += words[words_id][0]
                    if bool(re.search(r"\b" + re.escape(token["form"]), acc[cursor_acc:],
                                      flags=re.UNICODE)) or is_followed_by_punctuation(token["form"], acc[cursor_acc:]):
                        cursor_acc += acc[cursor_acc:].find(token["form"])
                        start_offset = words[words_id - acc_count][1] + words[words_id - acc_count][0].rfind(" ") + 1
                        end_offset = words[words_id][1] + words[words_id][0].find(" ")
                        word_reconstructed = acc[cursor_acc:cursor_acc + len(token["form"])]
                        cursor_acc += len(token["form"])

                        if cursor_acc + len(token["form"]) >= len(acc):
                            cursor_acc = 0
                            acc = ""
                        continue

                words_id += 1
                acc_count += 1

            if end_offset < start_offset:
                print("End position is smaller than start position " + token["form"])

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

        conllup_text += "\n"

    return conllup_text


def spacy_token_to_conllup(text, words):
    """
     Convert a spaCy document to CONLL-U formatted text.

     Parameters:
         text (spacy.tokens.doc.Doc): The spaCy document object to be converted.

     Returns:
         str: The CONLL-U formatted text representing the spaCy document.

     Note:
         The `text` parameter should be a spaCy document object. The function converts the spaCy document to CONLL-U
         format, where each line corresponds to a token, and the columns represent the token attributes (ID, FORM, LEMMA,
         UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC, START, END, NER)."""

    conllup_text = ""
    token_id = 1
    words_id = 0
    cursor_acc = 0
    acc = ""
    for sentence in text.sents:
        for token in sentence:
            acc_count = 0
            cursor = 0
            word_reconstructed = ""
            while word_reconstructed != token.text and words_id < len(words):

                if token.text in words[words_id][0][cursor:]:
                    cursor += words[words_id][0].find(token.text)
                    start_offset = words[words_id][1] + cursor
                    end_offset = start_offset + len(token.text)
                    word_reconstructed = words[words_id][0][cursor:cursor + len(token.text)]

                    if cursor + len(token.text) > len(words[words_id][0]):
                        cursor = 0
                    cursor_acc = 0
                    acc = ""
                    continue
                else:
                    acc += words[words_id][0]
                    if bool(re.search(r"\b" + re.escape(token.text), acc[cursor_acc:],
                                      flags=re.UNICODE)) or is_followed_by_punctuation(token.text, acc[cursor_acc:]):
                        cursor_acc += acc[cursor_acc:].find(token.text)
                        start_offset = words[words_id - acc_count][1] + words[words_id - acc_count][0].rfind(" ") + 1
                        end_offset = words[words_id][1] + words[words_id][0].find(" ")
                        word_reconstructed = acc[cursor_acc:cursor_acc + len(token.text)]
                        cursor_acc += len(token.text)

                        if cursor_acc + len(token.text) >= len(acc):
                            cursor_acc = 0
                            acc = ""
                        continue

                words_id += 1
                acc_count += 1

            if end_offset < start_offset:
                print("End position is smaller than start position " + token.text)
            # Get the token's attributes
            token_info = [
                str(token_id),
                token.text,
                "_",
                "_",
                "_",
                "_",
                "_",
                "_",
                "_",
                str(start_offset),
                str(end_offset),
                "_",
            ]
            token_id += 1
            conllup_text += "\t".join(token_info) + "\n"

        # Add a new line after each sentence
        conllup_text += "\n"
        # Reset token_id for each new sentence
        token_id = 1

    return conllup_text


def get_words_with_positions(docx_file):
    words = []

    # Unzip the DOCX file to a temporary folder
    temp_folder = "temp"
    os.makedirs(temp_folder, exist_ok=True)
    with zipfile.ZipFile(docx_file, 'r') as zip_ref:
        zip_ref.extractall(temp_folder)

    # Load the "document.xml" file
    xml_file = os.path.join(temp_folder, "word", "document.xml")
    with open(xml_file, 'r', encoding="utf-8") as xml:
        xml_content = xml.read()

    # Parse the XML content and find all text elements in paragraphs
    root = ET.fromstring(xml_content)
    current_position = 0
    for paragraph in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        for run in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r'):
            text = "".join(text_element.text if text_element.text else "" for text_element in
                           run.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
            if text:
                start_index = xml_content.find(text, current_position)
                words.append((text, start_index, len(text)))
                current_position = start_index + len(text)

    # Clean up the temporary folder and its contents
    shutil.rmtree(temp_folder)

    return words


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

    Raises:
        Exception: If an error occurs while processing text with UDPipe (when run_analysis is True).

    Note:
        The `run_analysis` parameter determines whether to perform text analysis using UDPipe or spaCy. If `run_analysis`
        is True, UDPipe is used for tokenization; otherwise, spaCy is used.
    """
    words = get_words_with_positions(docx_file)
    text = "".join(str(word[0]) for word in words)
    if save_internal_files:
        with open("words.te1", "w", encoding="utf-8") as f:
            word_lines = [f"Word: '{word[0]}' | Start Index: {word[1]} | Length: {word[2]}\n" for word in words]
            f.writelines(word_lines)

    if run_analysis:
        # Process the text using UDPipe
        token_list, error = process_text_with_udpipe(model, text)
        if error:
            raise Exception("Error occurred while processing text with UDPipe.")
        conllup_text = udpipe_token_to_conllup(token_list, words)
    else:
        nlp = spacy.load("ro_core_news_sm")
        conllup_text = spacy_token_to_conllup(nlp(text), words)

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
        return jsonify({"status": "ERROR", "message": "No file selected."})
    if not allowed_file(input_file):
        return jsonify({"status": "ERROR", "message": "Invalid file format."})

    if input_file:
        try:
            docx_to_conllup(input_file, output_file, args.RUN_ANALYSIS, args.SAVE_INTERNAL_FILES)
            return jsonify({"status": "OK", "message": output_file})
        except Exception as e:
            return jsonify({"status": "ERROR", "message": str(e)})

    return jsonify({"status": "ERROR", "message": "Invalid file format or other error occurred."})


@app.route('/checkHealth', methods=['GET'])
def check_health():
    """
    Endpoint to check the health/readiness of the module.

    Returns:
        JSON: A response indicating the status of the module (e.g., {'status': 'OK', 'message': ''}).
    """
    return jsonify({"status": "OK", "message": ""})


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
