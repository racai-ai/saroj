import os
import zipfile
from jellyfish import jaro_winkler_similarity

import ufal.udpipe as ud
from conllu import parse

from textExtractor_XMLParser import XMLParserWithPosition
from textExtractor_config import args
from textExtractor_helpers import *
from xml.sax.saxutils import escape

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
        DEPS, MISC, START, END).
    """

    conllup_text = ""
    words_id = 0
    for sentence in token_list:
        for token in sentence:
            acc_count = 1
            acc = ""
            while words_id < len(words):
                score = jaro_winkler_similarity(token["form"], words[words_id][0])
                if score > 0.7:  # Threshold chosen arbitrarily
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
            if len(str(token).strip()) == 0:
                continue
            acc_count = 1
            acc = ""
            while words_id < len(words):
                score = jaro_winkler_similarity(token.text, words[words_id][0])
                if score > 0.7:  # Threshold chosen arbitrarily
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
                str(token_id),      # ID
                token.text,         # FORM
                "_",                # LEMMA
                "_",                # UPOS
                "_",                # XPOS
                "_",                # FEATS
                "_",                # HEAD
                "_",                # DEPREL
                "_",                # DEPS
                "_",                # MISC
                str(start_offset),  # START
                str(end_offset),    # END
            ]
            token_id += 1
            conllup_text += "\t".join(token_info) + "\n"

        # Add a new line after each sentence
        conllup_text += "\n"
        # Reset token_id for each new sentence
        token_id = 1

    return conllup_text


def get_words_with_positions(docx_file, input_type):
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

    if input_type == "txt":
        XMLparser.parser.Parse("<d>")
        with open(docx_file, 'r', encoding='utf-8', errors='ignore') as fin: 
            for line in fin:
                txt="<w:p><w:t>"
                txt+=escape(line)
                txt+="</w:t></w:p>"
                XMLparser.parser.Parse(txt)
        XMLparser.parser.Parse("</d>")
    else:
        with zipfile.ZipFile(docx_file, 'r') as zip_ref:
            with zip_ref.open("word/document.xml") as xml_file:
                for line in xml_file:
                    XMLparser.parser.Parse(line)

    return XMLparser.words


def docx_to_conllup(model, docx_file, output_file, regex, replacements, input_type):
    """
    Convert a .docx file to CONLL-U formatted text.

    Args:
        model (str/spacy): The path to the UDPipe model to use for text analysis if `run_analysis` is True or
                           spacy model if `run_analysis` is False.
        docx_file (str): The path to the input .docx file.
        output_file (str): The path where the CONLL-U formatted text will be saved.
        regex (str): The regular expression pattern for text normalization.
        replacements (dict): A dictionary of replacement patterns for text normalization.

    Returns:
        str: The path of the output_file after processing (if run_analysis is False) or the CONLL-U formatted text.

    Raises:
        Exception: If an error occurs while processing text with UDPipe (when run_analysis is True).

    """
    words = get_words_with_positions(docx_file, input_type)
    # normalize words
    normalized_words = [(normalize_text(word[0], regex, replacements), word[1], word[2]) for word in words]
    normalized_text = "".join(str(word[0]) for word in normalized_words)
    filename, _ = os.path.splitext(output_file)
    # in .te1 file the words are not normalized - are the original ones
    if args.SAVE_INTERNAL_FILES:
        save_log(words, filename)
    if args.RUN_ANALYSIS:
        # Process the text using UDPipe
        token_list, error = process_text_with_udpipe(model, normalized_text)
        if error:
            raise Exception("Error occurred while processing text with UDPipe.")
        conllup_text = udpipe_token_to_conllup(token_list, normalized_words)
    else:
         # Process the text using Spacy
        spacy_model_output = model(normalized_text)
        conllup_text = spacy_token_to_conllup(spacy_model_output, normalized_words)

    # Save the CONLL-U formatted text to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(conllup_text)
    return output_file
