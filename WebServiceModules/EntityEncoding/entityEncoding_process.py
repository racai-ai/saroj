import os
from itertools import zip_longest

from entityEncoding_NERProcessor import NERProcessor
from entityEncoding_suffix import suffix_replace, VOID_NER


def read_mapping(mapping_path):
    """
    Read an entity mapping from a mapping file and return it as a dictionary.

    Args:
        mapping_path (str): The path to the mapping file containing token-to-NER-ID mappings.

    Returns:
        entity_mapping (dict): A dictionary that maps tokens to NER IDs.

    Example:
        mapping_path = "entity_map.txt"
        entity_mapping = read_mapping(mapping_path)
        # 'entity_mapping' will contain token-to-NER-ID mappings read from 'mapping_path'.

    Notes:
        This function reads an entity mapping from the specified 'mapping_path', where each line of the file is expected
        to contain a token and its corresponding NER ID separated by a tab character ('\t'). It loads this data into
        a dictionary and returns it as 'entity_mapping'. If the mapping file does not exist, an empty dictionary is
        returned.

    """
    entity_mapping = {}
    # Check if mapping file exists; if not, create it
    if not os.path.exists(mapping_path):
        with open(mapping_path, "w") as mapping_file:
            mapping_file.write("")
    # Load existing mapping data into memory
    with open(mapping_path, "r", encoding="utf-8") as mapping_file:
        for line in mapping_file:
            token, ner_id = line.strip().split('\t')
            entity_mapping[token] = ner_id
    return entity_mapping


def read_tokens_from_file(input_path):
    """
    Read tokens and their Named Entity Recognition (NER) tags from a CoNLL-U Plus file.

    Args:
        input_path (str): The path to the input CoNLL-U Plus file containing token and NER tag information.

    Returns:
        tokens (list): A list of tokens, each represented as a tuple (token, ner_tag), where 'token' is the token
            string, and 'ner_tag' is the NER tag associated with the token.

    Example:
        input_path = "input.conllu"
        tokens = read_tokens_from_file(input_path)
        # 'tokens' will contain the token and NER tag information read from 'input_path'.

    Notes:
        This function reads a CoNLL-U Plus file from the specified 'input_path' and extracts the token and NER tag
        information. It returns this information as a list of tuples where each tuple contains a token and its
        corresponding NER tag. Lines starting with "#" and empty lines in the input file are skipped.

    """
    tokens = []

    with open(input_path, "r", encoding="utf-8") as input_file:
        for line in input_file:
            line = line.strip()
            if not line or line.startswith("#"):
                # Skip empty lines and lines starting with "#"
                continue

            # Split the line by tab to get columns
            columns = line.strip().split("\t")
            token = columns[1]
            ner_tag = columns[-1]
            tokens.append((token, ner_tag))

    return tokens


def check_invalid_token_and_extract_sfx(token, ner_tag):
    """
    Checks if the token is valid and extracts suffix information.

    This function checks if the token is not in VOID_NER and removes any suffix
    information using the `suffix_replace` function. It returns the processed
    token if valid, or None if the token is considered invalid.

    Args:
        token (str): The token to be checked and processed.
        ner_tag (str): The NER tag associated with the token.

    Returns:
        str or None: The processed token if valid, or None if the token is invalid.

    """
    token, _ = suffix_replace(token)
    return token if ner_tag not in VOID_NER else None


def add_entity_mapping(current_entity_tokens, entity_mapping, map_file, previous_ner):
    """
    Add an entity to the mapping and map file.

    If it's a new entity (not found in `entity_mapping`), this function adds
    it to the mapping dictionary with a unique identifier and appends the
    mapping information to the specified map file.

    Args:
        current_entity_tokens (list): List of tokens belonging to the current entity.
        entity_mapping (dict): A dictionary storing entity mappings.
        map_file (str): The path to the map file for storing mappings.
        previous_ner (str): The NER tag of the previous entity.
    Returns:
        None

    """
    # If it's a new entity, add the previous entity (if any) to the map
    if current_entity_tokens:
        combined_string = " ".join(current_entity_tokens)

        # Check if the entity is already mapped in the entity_mapping
        if combined_string not in entity_mapping:
            # If not found in the mapping, add it to the mapping and the map file
            previous_ner = previous_ner[2:] if "-" in previous_ner else previous_ner
            entity_mapping[combined_string] = f"#{previous_ner}{str(len(entity_mapping) + 1)}"
            # entity_mapping[combined_string] = previous_ner
            with open(map_file, "a", encoding="utf-8") as mapping_file:
                mapping_file.write(f"{combined_string}\t{entity_mapping[combined_string]}\n")


def add_token_to_current_entity(token, ner_tag, previous_ner, current_entity_tokens):
    """
    Add a token to the current entity if it satisfies specified conditions.

    This function appends a token to the list of tokens belonging to the current
    entity if it meets one of the following conditions:
    1. It is a continuation of the current entity (ner_tag starts with 'I-') and there
       is a previous NER tag.
    2. It belongs to the same entity as the previous token (previous_ner == ner_tag).

    Args:
        token (str): The token to be added to the current entity.
        ner_tag (str): The NER tag associated with the token.
        previous_ner (str): The NER tag of the previous entity.
        current_entity_tokens (list): List of tokens belonging to the current entity.

    Returns:
        list: The updated list of tokens belonging to the current entity.

    """
    if ner_tag.startswith("I-") and previous_ner:
        # Condition 1: Check if it's a continuation of the current entity
        current_entity_tokens.append(token)
    elif previous_ner == ner_tag:
        # Condition 2: Check if it's the same entity
        current_entity_tokens.append(token)
    return current_entity_tokens


def update_mapping(tokens, entity_mapping, map_file):
    """
    Update an entity mapping based on tokens with Named Entity Recognition (NER) tags and write the mapping to a map file.

    Args:
        tokens (list): A list of tokens, each represented as a tuple (token, ner_tag). The 'token' is the token string,
            and 'ner_tag' is the NER tag associated with the token.
        entity_mapping (dict): A dictionary that maps tokens to new NER IDs. The keys are token strings, and the values
            are NER IDs (e.g., "#PER1") assigned based on the mapping.
        map_file (str): The path to the map file where the updated entity mapping will be written.

    Returns:
        entity_mapping (dict): The updated entity mapping containing new entries based on the tokens provided.

    Example:
        tokens = [("John", "B-PER"), ("Smith", "I-PER"), ("lives", "O"), ("in", "O"), ("New", "B-LOC"), ("York", "I-LOC")]
        entity_mapping = {
            "John Smith": "#PER1",
            "New York": "#LOC1",
        }
        map_file = "entity_map.txt"
        updated_mapping = update_mapping(tokens, entity_mapping, map_file)
        # The 'entity_mapping' dictionary is updated with new entries based on the 'tokens' and written to 'map_file'.
        # 'updated_mapping' contains the same dictionary as 'entity_mapping'.

    Notes:
        This function updates an entity mapping based on the provided tokens and their NER tags. It identifies entities
        (e.g., persons, locations) within the tokens and assigns or updates NER IDs in the entity mapping. New entities
        are added to the mapping, and the mapping is written to 'map_file'. Tokens without NER tags or with tags of "O"
        (indicating no tag) are ignored.

    """
    previous_ner = None
    current_entity_tokens = []

    # Iterate through the tokens
    for token, ner_tag in tokens:
        token = check_invalid_token_and_extract_sfx(token, ner_tag)

        if token is None:
            add_entity_mapping(current_entity_tokens, entity_mapping, map_file, previous_ner)
            previous_ner = None
            continue

        # Check if the current entity is None or the NER tag starts with "B-"
        if previous_ner is None or ner_tag.startswith("B-") or previous_ner[2:] != ner_tag[2:]:
            add_entity_mapping(current_entity_tokens, entity_mapping, map_file, previous_ner)
            previous_ner = ner_tag
            current_entity_tokens = [token]

        else:
            current_entity_tokens = add_token_to_current_entity(token, ner_tag, previous_ner, current_entity_tokens)
    # Process the last entity  
    add_entity_mapping(current_entity_tokens, entity_mapping, map_file, previous_ner)

    # Return the updated entity_mapping
    return entity_mapping


def map_tokens(entity_mapping, tokens):
    """
    Map tokens to their corresponding Named Entity Recognition (NER) tags based on a given entity mapping.

    Args:
        entity_mapping (dict): A dictionary that maps tokens to new NER IDs. The keys are token strings, and the values
            are tuples (entity_type, entity_id, new_ner_id), where entity_type is the entity type (e.g., 'PER' for person),
            entity_id is the unique identifier for the entity, and new_ner_id is the new NER ID to be assigned to the token.
        tokens (list): A list of tokens, each represented as a tuple (token, ner). The 'token' is the token string, and 'ner'
            is the original NER tag associated with the token.

    Returns:
        entity_merge_map (list): A list of tuples, each containing the token, and the new NER ID assigned based on the
        entity mapping.

    Notes:
        This function maps tokens to their new NER IDs based on the provided entity mapping. It merges consecutive tokens
        that have matching keys in the entity mapping and assigns the corresponding new NER ID to the merged entity.
        Tokens without matching keys in the entity mapping are assigned an NER tag of "_".
    """

    entity_merge_map = []
    current_key = ""
    current_names = []

    for (token, ner), (_, next_ner) in zip_longest(tokens, tokens[1:], fillvalue=("None", "None")):
        token, _ = suffix_replace(token)
        if ner in VOID_NER:
            entity_merge_map.extend([(token, ner, "_")])
            continue

        current_key += " " + token
        current_names.append(token)
        if next_ner.startswith("I-"):
            continue

        if current_key.strip() in entity_mapping:
            value = entity_mapping[current_key.strip()]
            entity_merge_map.append([" ".join(current_names), value])
            current_key = ""
            current_names = []
    return entity_merge_map


def process_line(current_line, next_line, ner_processor):
    current_line = ner_processor.process_comment_or_empty_line(current_line)
    if current_line is not None:
        ner_processor.process_valid_line(current_line, next_line)


def process_and_update_ner_tags(input_path, output_path, entity_mapping, tokens):
    """
    Process a CoNLL-U Plus file, updating Named Entity Recognition (NER) tags based on a given entity mapping.

    Args:
        input_path (str): The path to the input CoNLL-U Plus file to be processed.
        output_path (str): The path to the output file where the processed data will be saved.
        entity_mapping (dict): A dictionary that maps tokens to new NER IDs. The keys are token strings, and the values
            are tuples (entity_type, new_ner_id), where entity_type is the entity type (e.g., 'PER' for person), and
            new_ner_id is the new NER ID to be assigned to the token.
        tokens (list): A list of tokens used for mapping, typically generated from CoNLL-U Plus file.

    Returns:
        None

    Notes:
        This function reads a CoNLL-U Plus file from the input_path, processes each line, and add the entity tags for
        tokens based on the provided entity mapping. It then writes the processed data to the output_path. Header lines,
        which start with "#" or are empty, are written as-is.

    Example:
        input_path = "input.conllu"
        output_path = "output.conllu"
        entity_mapping = {
            "John Doe": "#PER_1",
            "New York": "#LOC_2"),
        }
        tokens = [("John", "B-PER"), ("Doe", "I-PER")]
        process_and_update_ner_tags(input_path, output_path, entity_mapping, tokens)
    """
    new_ner_id = ""
    mapped_tokens = map_tokens(entity_mapping, tokens)

    with open(input_path, "r", encoding="utf-8") as input_file, open(output_path, "w", encoding="utf-8") as output_file:
        ner_processor = NERProcessor(output_file, new_ner_id, mapped_tokens)
        current_line = None

        for next_line in input_file:
            if current_line is not None:
                process_line(current_line, next_line, ner_processor)
            current_line = next_line

        # Process the last line (if any) after the loop
        if current_line is not None:
            process_line(current_line, next_line, ner_processor)
