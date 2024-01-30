import re


def save_log(words, filename):
    with open(filename + ".te1", "w", encoding="utf-8") as f:
        word_lines = [f"Word: '{word[0]}' | Start Index: {word[1]} | End Index: {word[2]}\n" for word in words]
        f.writelines(word_lines)


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


def format_none_value(value):
    """
    Convert None values to underscores to conform to the CONLL-U format.

    Args:
        value: The value to be converted.

    Returns:
        str: The converted value as a string or an underscore (_) if the value is None.
    """
    return "_" if value is None else str(value)


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


def create_replacement_regex():
    """
    Create a regular expression pattern and replacement dictionary for replacing specific Unicode characters.

    Returns:
        tuple: A tuple containing the compiled regular expression pattern and the replacement dictionary.
    """
    repl = {
        "\u00A0": " ",
        "\u201C": "\"",
        "\u201D": "\"",
        "\u2018": "'",
        "\u2019": "'",
        "\u00AB": "\"",
        "\u00BB": "\"",
        "\u2039": "'",
        "\u203A": "'",
        "„": "\"",
        "\r": " ",
        "\t": " ",
        'ş': 'ș',
        'Ş': 'Ș',
        'Ţ': 'Ț',
        'ţ': 'ț',
        'Ã': 'Ă',
        'ã': 'ă',
        'ø': 'o'
    }
    # Add ranges of weird unicode characters
    for i in range(0x2000, 0x200F):
        repl[chr(i)] = " "
    for i in range(0x2020, 0x2025):
        repl[chr(i)] = "- "
    for i in range(0x2072, 0x2074):
        repl[chr(i)] = "- "
    repl[chr(0x208F)] = "- "
    for i in range(0x209D, 0x20A0):
        repl[chr(i)] = "- "
    for i in range(0x25A0, 0x26A0):
        repl[chr(i)] = "- "

    rgx = re.compile("|".join(map(re.escape, repl.keys())))

    return rgx, repl


def normalize_text(text, reg, replacements):
    """
    Normalize the given text by applying regular expression substitutions and additional rules.

    Args:
        text (str): The input text to be normalized.
        reg (re.Pattern): The compiled regular expression pattern used for substitutions.
        replacements (dict): A dictionary mapping matched patterns to their replacements.

    Returns:
        str: The normalized text.

    """
    text = reg.sub(lambda match: replacements[match.group(0)], text)

    text = re.sub(r'(([A-Z][.])+)([A-Z][a-z]+)', r'\1 \3', text)
    text = re.sub(r'([a-zA-Z.ăîâșțĂÎÂȘȚ]+)/([a-zA-Z.ăîâșțĂÎÂȘȚ]+)', r'\1 / \2', text)

    return text
