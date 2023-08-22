import os
import zipfile

import ufal.udpipe as ud
from conllu import parse

from textExtractor_XMLParser import XMLParserWithPosition


def process_text_with_udpipe(udpipe_model, text):
    """
    Process the input 'text' using UDPipe.

    Args:
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

    Args:
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

    Args:
        value: The value to be converted.

    Returns:
        str: The converted value as a string or an underscore (_) if the value is None.
    """
    return "_" if value is None else str(value)


def udpipe_token_to_conllup(token_list, words):
    """
    Convert a list of tokens to CONLL-U formatted text.

    Args:
        token_list (list): A list of token dictionaries.
        words (list): A list of tuples containing the words and their offsets in the original text.

    Returns:
        str: The CONLL-U formatted text representing the list of tokens.

    Note:
        The `token_list` parameter should be a list of dictionaries, where each dictionary represents a token and its
        associated metadata. The function converts this list of tokens to CONLL-U format, where each line corresponds to
        a token, and the columns represent the token attributes (ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL,
        DEPS, MISC, START, END, NER).
    """

    conllup_text = ""
    words_id = 0
    for sentence in token_list:
        for token in sentence:
            acc_count = 1
            acc = ""
            while words_id < len(words):
                if token["form"] in words[words_id][0]:
                    start_offset = words[words_id][1]
                    end_offset = words[words_id][2]
                    break
                else:
                    acc += words[words_id][0]
                    if token["form"] in acc:
                        start_offset = words[words_id - acc_count + 1][1]
                        end_offset = words[words_id][2]
                        break
                    elif acc.startswith(" ") or len(acc) == 0:
                        acc_count -= 1
                        acc = acc.strip()
                    acc_count += 1
                words_id += 1
            words_id += 1
            if end_offset < start_offset:
                raise Exception("End position is smaller than start position for token " + token["form"])

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

    Args:
        text (spacy.tokens.Doc): The SpaCy `Doc` object representing the processed text.
        words (list): A list of tuples containing word forms and their corresponding start and end offsets.

    Returns:
        str: The CONLL-U formatted text representing the processed `text`.

    Raises:
        Exception: If the end position is smaller than the start position for any token.

    The function takes a SpaCy `Doc` object and a list of word forms with their start and end offsets as input.
    It converts the content of the `Doc` object into CONLL-U format, which is a common format for representing
    syntactic annotations of natural language sentences.

    For each token in the `Doc`, the function searches for the corresponding word in the `words` list using its text.
    It finds the start and end offsets for the token based on the `words` list.
    The function then generates the CONLL-U lines for each token by assigning token attributes such as token ID, form,
    start offset, and end offset, while other attributes are left as placeholders with "_".

    If any token's end position is smaller than its start position, an Exception is raised, indicating an error in the
    word offsets.

    The function returns the CONLL-U formatted text as a string.
    """

    conllup_text = ""
    token_id = 1
    words_id = 0
    for sentence in text.sents:
        for token in sentence:
            acc_count = 1
            acc = ""
            while words_id < len(words):
                if token.text in words[words_id][0]:
                    start_offset = words[words_id][1]
                    end_offset = words[words_id][2]
                    break
                else:
                    acc += words[words_id][0]
                    if token.text in acc:
                        start_offset = words[words_id - acc_count + 1][1]
                        end_offset = words[words_id][2]
                        break
                    elif acc.startswith(" ") or len(acc) == 0:
                        acc_count -= 1
                        acc = acc.strip()
                    acc_count += 1
                words_id += 1
            words_id += 1
            if end_offset < start_offset:
                raise Exception("End position is smaller than start position token " + token.text)
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
    """
    Extracts words with their positions from the 'document.xml' file inside a DOCX file.

    Args:
        docx_file (str): The path to the DOCX file from which to extract words.

    Returns:
        list: A list of tuples, each containing the tag name, attributes, and position of the word.
              The format of the tuples is: (tag_name, attributes, position).

    Raises:
        FileNotFoundError: If the specified DOCX file does not exist.
        zipfile.BadZipFile: If the specified file is not a valid ZIP archive.
        KeyError: If the 'document.xml' file is not found within the DOCX archive.
    """
    XMLparser = XMLParserWithPosition()
    with zipfile.ZipFile(docx_file, 'r') as zip_ref:
        with zip_ref.open("word/document.xml") as xml_file:
            for line in xml_file:
                XMLparser.parser.Parse(line)

    return XMLparser.words


def docx_to_conllup(model, docx_file, output_file, run_analysis=False, save_internal_files=False):
    """
    Convert a .docx file to CONLL-U formatted text.

    Args:
        model(str/spacy): The path to the UDPipe model to use for text analysis if `run_analysis` is True or
                     spacy model if `run_analysis` is False.
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
    filename, _ = os.path.splitext(output_file)
    if save_internal_files:
        with open(filename + ".te1", "w", encoding="utf-8") as f:
            word_lines = [f"Word: '{word[0]}' | Start Index: {word[1]} | End Index: {word[2]}\n" for word in words]
            f.writelines(word_lines)

    if run_analysis:
        # Process the text using UDPipe
        token_list, error = process_text_with_udpipe(model, text)
        if error:
            raise Exception("Error occurred while processing text with UDPipe.")
        conllup_text = udpipe_token_to_conllup(token_list, words)
    else:
        # Remove non-breaking spaces
        processed_text = text.replace("\u00A0", " ")
        conllup_text = spacy_token_to_conllup(model(processed_text), words)

    # Save the CONLL-U formatted text to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(conllup_text)
    return output_file


def allowed_file(filename):
    """
    Check if the given filename has a valid extension.

    Args:
        filename (str): The name of the file to be checked.

    Returns:
        bool: True if the file has a valid extension (in this case, .docx), False otherwise.
    """
    allowed_extensions = {'docx'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
