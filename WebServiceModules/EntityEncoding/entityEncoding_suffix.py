
VOID_NER = ["O", "_"]


def suffix_replace(token):
    """
    Replace certain suffixes in a token with their corresponding replacements.

    Args:
        token (str): The token string to be processed.

    Returns:
        name (str): The token with the specified suffixes replaced.
        sfx (str): A suffix string indicating which suffix was replaced (e.g., "_ei", "_ăi", "_ilor", or "").

    Example:
        token = "studentei"
        name, sfx = suffix_replace(token)
        # 'name' will be "studenta" and 'sfx' will be "_ei" because the "ei" suffix was replaced.

    Notes:
        This function checks if the input token ends with specific suffixes and replaces them with corresponding
        replacements. If a suffix is replaced, a suffix string indicating which suffix was replaced is also returned.
        If no replacement is performed, an empty suffix string is returned.

    """
    suffixes = {
        "ei": "a",
        "ăi": "a",
        "ilor": "i",
        "ul": "",
        "zii": "da"
    }

    for suffix, replacement in suffixes.items():
        if token.endswith(suffix) and len(token) >= 4:
            name = token[:-len(suffix)] + replacement
            sfx = "_" + suffix
            return name, sfx

    return token, ""
