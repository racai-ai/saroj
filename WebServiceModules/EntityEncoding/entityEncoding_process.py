import os
import re

from itertools import zip_longest

VOID_NER = ["O", "_"]


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
            columns = line.split("\t")
            token = columns[1]
            ner_tag = columns[-1]
            tokens.append((token, ner_tag))

    return tokens


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
        token, _ = suffix_replace(token)
        # Check if the NER tag is not "_" or "O" (indicating no tag)
        if ner_tag not in VOID_NER:
            # Check if the current entity is None or the NER tag starts with "B-"
            if previous_ner is None or ner_tag.startswith("B-") or previous_ner[2:] != ner_tag[2:]:
                # If it's a new entity, add the previous entity (if any) to the map
                if current_entity_tokens:
                    combined_string = " ".join(current_entity_tokens)

                    # Check if the entity is already mapped in the entity_mapping
                    if combined_string not in entity_mapping:
                        #     ner_tag = entity_mapping[combined_string]
                        # else:
                        # If not found in the mapping, add it to the mapping and the map file
                        previous_ner = previous_ner[2:] if "-" in previous_ner else previous_ner
                        entity_mapping[combined_string] = f"#{previous_ner}{str(len(entity_mapping) + 1)}"
                        # entity_mapping[combined_string] = previous_ner
                        with open(map_file, "a", encoding="utf-8") as mapping_file:
                            mapping_file.write(f"{combined_string}\t{entity_mapping[combined_string]}\n")

                # Start a new entity
                previous_ner = ner_tag
                current_entity_tokens = [token]
            elif ner_tag.startswith("I-") and previous_ner:
                # Add the token to the current entity
                current_entity_tokens.append(token)
            elif previous_ner == ner_tag:
                current_entity_tokens.append(token)

        else:
            continue

    # Process the last entity (if any)
    if current_entity_tokens:
        combined_string = " ".join(current_entity_tokens)

        # Check if the entity is already mapped in the entity_mapping
        if combined_string not in entity_mapping:
            # If not found in the mapping, add it to the mapping and the map file
            previous_ner = previous_ner[2:] if "-" in previous_ner else previous_ner
            entity_mapping[combined_string] = f"#{previous_ner}{str(len(entity_mapping) + 1)}"
            with open(map_file, "a", encoding="utf-8") as mapping_file:
                mapping_file.write(f"{combined_string}\t{entity_mapping[combined_string]}\n")

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
        entity_merge_map (list): A list of tuples, each containing the token, original NER tag, and the new NER ID assigned
            based on the entity mapping.

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


def process_and_update_ner_tags(input_path, output_path, entity_mapping, tokens):
    """
    Process a CoNLL-U Plus file, updating Named Entity Recognition (NER) tags based on a given entity mapping.

    Args:
        input_path (str): The path to the input CoNLL-U Plus file to be processed.
        output_path (str): The path to the output file where the processed data will be saved.
        entity_mapping (dict): A dictionary that maps tokens to new NER IDs. The keys are token strings, and the values
            are tuples (entity_type, entity_id, new_ner_id), where entity_type is the entity type (e.g., 'PER' for person),
            entity_id is the unique identifier for the entity, and new_ner_id is the new NER ID to be assigned to the token.
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
    search = []
    acc = []
    sfxs = []

    mapped_tokens = map_tokens(entity_mapping, tokens)

    with open(input_path, "r", encoding="utf-8") as input_file, open(output_path, "w", encoding="utf-8") as output_file:
        current_line = None

        for next_line in input_file:
            if current_line is not None:
                if current_line.startswith("#") or not current_line.strip():
                    # Header lines, write them as-is
                    output_file.write(current_line)
                else:
                    fields = [token.strip() for token in re.split(r'(\t|  {2})', current_line) if token.strip()]
                    fields_next = [token.strip() for token in re.split(r'(\t|  {2})', next_line) if token.strip()]

                    token = fields[1]
                    ner_tag = fields[-1]
                    ner_tag_next = fields_next[-1] if fields_next else ""

                    if ner_tag in VOID_NER:
                        fields.append("_")
                    else:
                        token, sfx = suffix_replace(token)
                        search.append(token)

                        if ner_tag_next.startswith("I-"):
                            sfxs.append(sfx)
                            acc.append('\t'.join(fields))
                            current_line = next_line
                            continue

                        match_tpl = next((t for t in mapped_tokens if t[0] == " ".join(search)), None)

                        if match_tpl is not None:
                            _, new_ner_id = match_tpl
                            search.clear()

                            if acc:
                                acc[-1] += f'\t{new_ner_id}{sfxs.pop()}\n'
                                output_file.write(acc.pop())

                        if ner_tag != "_":
                            # Update the NER column with the new NER ID
                            fields.append(f"{new_ner_id}{sfx}")

                    # Write the updated line to the output file
                    output_file.write('\t'.join(fields) + '\n')

            current_line = next_line
