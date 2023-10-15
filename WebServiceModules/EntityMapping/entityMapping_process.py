import random
import re
import shutil
import tempfile
from collections import defaultdict

from lib.saroj.suffix_process import suffix_replace, VOID_NER

old_rep = None
used = defaultdict(list)
count_i = 0

NOT_FOUND = "XXX"


# Function to read the replacement dictionary from a file
def read_replacement_dictionary(dictionary_file):
    replacement_dict = {}
    with open(dictionary_file, 'r') as file:
        for line in file:
            columns = line.strip().split('\t')
            if len(columns) == 2:
                ner_id_and_potential_suffix, replacement = columns
                # Check if ner_id_and_potential_suffix exists in the dictionary
                if ner_id_and_potential_suffix not in replacement_dict:
                    replacement_dict[ner_id_and_potential_suffix] = []
                replacement_dict[ner_id_and_potential_suffix].append(replacement)
    return replacement_dict


def update_mapping_file(mapping_file, entity, replacement):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        with open(mapping_file, 'r') as file:
            for line in file:
                columns = line.strip().split('\t')
                if len(columns) >= 2:
                    original_entity, entity_id, *extra = columns
                    if entity_id == entity:
                        # Found the line with the entity, add the replacement
                        extra_part = ' '.join(extra) + ' ' if extra else ''
                        line = f"{original_entity}\t{entity_id}\t{extra_part}{replacement}\n"
                temp.write(line)
        temp_file = temp.name

    # Replace the original file with the temporary file
    shutil.move(temp_file, mapping_file)

def search_mapping_file(mapping_file, ner_id_and_potential_suffix):
    """
     Search for a replacement in a mapping file based on a given NER identifier and potential suffix.

     Args:
         mapping_file (str): The path to the mapping file.
         ner_id_and_potential_suffix (str): The NER identifier and potential suffix to look up.

     Returns:
         str: The replacement value found in the mapping file, or None if not found.
     """
    replacement = None  # Default replacement if not found
    with open(mapping_file, 'r') as file:
        for line in file:
            columns = line.strip().split('\t')
            if len(columns) == 3 and columns[1] == ner_id_and_potential_suffix:
                replacement = columns[2]
                break  # Exit the loop once the entity is found
    return replacement


def process_already_mapped_replacement(replacement, ner_inst, ner_id_and_potential_suffix):
    """
    Process a replacement based on NER instance and potential suffix.

    Args:
        replacement (str): The original replacement.
        ner_inst (str): The NER instance.
        ner_id_and_potential_suffix (str): The NER identifier and potential suffix.

    Returns:
        str: The processed replacement.
    """
    # Check if replacement is None or empty, return None in such cases
    if not replacement:
        return None

    # Check if ner_inst starts with "I-" and replacement has a single token
    if ner_inst.startswith("I-") and len(replacement.split()) == 1:
        return None

    suffix = ner_id_and_potential_suffix.split("_", 1)[1] \
        if ("_" in ner_id_and_potential_suffix) and (NOT_FOUND not in replacement) \
        else ''

    # Check if replacement contains more than one token
    if len(replacement.split(" ")) > 1:
        # Construct and return the appropriate token based on conditions
        return replacement.split(" ")[0] + suffix if not replacement.endswith("a") else replacement.split(" ")[0][
                                                                                        :-1] + suffix

    # Check if ner_id_and_potential_suffix contains underscores and "XXX" is not in replacement
    if "_" in ner_id_and_potential_suffix and NOT_FOUND not in replacement:
        # Construct and return the appropriate token based on conditions
        return replacement.split(" ")[0] + suffix if not replacement.endswith("a") else replacement.split(" ")[0][
                                                                                        :-1] + suffix

    # If none of the above conditions were met, return the second token or the full replacement
    return replacement.split(" ")[1] if len(replacement.split(" ")) > 1 else replacement


def process_entity_inst_I(ner_id_and_potential_suffix, mapping_file, replacement_dict):
    """
    Process entities with an instance marker 'I-'.

    Args:
        ner_id_and_potential_suffix (str): The NER identifier and potential suffix.
        mapping_file (str): The mapping file to update.
        replacement_dict (dict): A dictionary of replacements.

    Returns:
        str: The processed replacement.
    """
    global count_i
    count_i += 1

    # Get the NER type from the identifier
    ner = get_ner(ner_id_and_potential_suffix)

    # Extract the suffix from the identifier
    suffix = ner_id_and_potential_suffix.split("_", 1)[1] if "_" in ner_id_and_potential_suffix else ""

    # Filter replacements that match the count_i
    replacements = [replacement for replacement in used[ner] if len(replacement.split()) == count_i]

    # Choose the replacement based on old_rep and count_i
    replacement = next((lname for lname in [replacement.split(' ', 1)[count_i - 1] for replacement in replacements
                                            if old_rep in replacement]), 'X' * random.randint(3, 10))

    # Modify the replacement with the suffix if not found
    rep = replacement.split(' ', 1)[0] + suffix if NOT_FOUND not in replacement else replacement

    # Update the mapping file and replacement dictionary
    update_mapping_file(mapping_file, ner_id_and_potential_suffix, rep)
    replacement_dict[ner] = [value for value in replacement_dict[ner] if not re.search(replacement, value)]

    return rep


def process_female_entity(lemma, ner_id_and_potential_suffix, replacement_dict, mapping_file):
    """
    Process female entities.

    Args:
        lemma (str): The entity's lemma.
        ner_id_and_potential_suffix (str): The NER identifier and potential suffix.
        replacement_dict (dict): A dictionary of replacements.
        mapping_file (str): The mapping file to update.

    Returns:
        str: The processed replacement.
    """
    global old_rep
    global count_i
    count_i = 0

    # Get the NER type from the identifier
    ner = get_ner(ner_id_and_potential_suffix)

    # Extract the suffix from the identifier
    suffix = ner_id_and_potential_suffix.split("_", 1)[1] if "_" in ner_id_and_potential_suffix else ""

    # Choose the replacement based on old_rep, count_i, and matching 'a' suffix
    replacement = next((fname for fname in [replacement.split(' ', 1)[count_i] for replacement in replacement_dict[ner]]
                        if fname.endswith('a') and fname != lemma), 'X' * random.randint(3, 10))

    old_rep = replacement
    count_i += 1

    # Modify the replacement with the suffix if not found
    rep = replacement.split(' ', 1)[0][:-1] + suffix if not (NOT_FOUND in replacement or not suffix) else replacement

    # Update the mapping file, used list, and replacement dictionary
    update_mapping_file(mapping_file, hashtag_ner(ner_id_and_potential_suffix), rep)
    used[ner].extend([value for value in replacement_dict[ner] if re.search(replacement, value)])
    replacement_dict[ner] = [value for value in replacement_dict[ner] if not re.search(replacement, value)]

    return rep


def process_neutral_entity(ner_id_and_potential_suffix, replacement_dict, mapping_file):
    """
    Process neutral entities.

    Args:
        ner_id_and_potential_suffix (str): The NER identifier and potential suffix.
        replacement_dict (dict): A dictionary of replacements.
        mapping_file (str): The mapping file to update.

    Returns:
        str: The processed replacement.
    """
    global old_rep
    global count_i
    count_i = 1
    ner = get_ner(ner_id_and_potential_suffix)
    suffix = ner_id_and_potential_suffix.split("_", 1)[1] if "_" in ner_id_and_potential_suffix else None

    replacements = replacement_dict[ner]

    # Filter replacements to exclude those ending with 'a'
    valid_replacements = [replacement for replacement in replacements if not replacement.endswith('a')]

    # If there are valid replacements, select one at random, else use a random 'X' string
    replacement = random.choice(valid_replacements) if valid_replacements else 'X' * random.randint(3, 10)

    # Set the new value for columns[1]
    rep = replacement.split(" ")[0] + suffix if not (NOT_FOUND in replacement or not suffix) else replacement.split(" ")[0]

    # Update mapping and used values
    update_mapping_file(mapping_file, hashtag_ner(ner_id_and_potential_suffix), rep)
    old_rep = rep
    used[ner].extend([value for value in replacement_dict[ner] if re.search(replacement, value)])
    replacement_dict[ner] = [value for value in replacement_dict[ner] if not re.search(replacement, value)]

    return rep


def process_entity(token_tpl, ner_id_and_potential_suffix, mapping_file, replacement_dict):
    """
    Process an entity based on token information and NER type.

    Args:
        token_tpl (tuple): A tuple containing NER instance and lemma.
        ner_id_and_potential_suffix (str): The NER identifier and potential suffix.
        mapping_file (str): The mapping file to update.
        replacement_dict (dict): A dictionary of replacements.

    Returns:
        str: The processed replacement.
    """
    ner = get_ner(ner_id_and_potential_suffix)
    ner_inst, lemma = token_tpl

    if ner in replacement_dict:
        if ner_inst.startswith("I-"):
            replacement = process_entity_inst_I(ner_id_and_potential_suffix, mapping_file, replacement_dict)
        elif lemma.endswith('a'):
            replacement = process_female_entity(lemma, ner_id_and_potential_suffix, replacement_dict, mapping_file)
        else:
            replacement = process_neutral_entity(ner_id_and_potential_suffix, replacement_dict, mapping_file)
    else:
        replacement = 'X' * random.randint(3, 10)
        update_mapping_file(mapping_file, hashtag_ner(ner_id_and_potential_suffix), replacement)

    return replacement


def preprocess_line(line):
    """
    Preprocess a line from the input file, extracting relevant information and checking for VOID_NER.

    Args:
        line (str): The input line to be processed.

    Returns:
        tuple: A tuple containing processed columns and a tuple of (ner_id_and_potential_suffix, (ner_inst, form))
    """
    if line.startswith("#") or not line.strip():
        return line, None

    columns = line.strip().split('\t')
    ner_id_and_potential_suffix = columns[-1]  # #PER1_ei

    if ner_id_and_potential_suffix in VOID_NER:
        return line, None

    ner_inst = columns[-2]  # B-PER
    form = columns[1]  # Mariei

    if "_" in ner_id_and_potential_suffix:
        form, _ = suffix_replace(form)

    return columns, (ner_id_and_potential_suffix, (ner_inst, form))


def hashtag_ner(ner_id_and_potential_suffix):
    return ner_id_and_potential_suffix.split('_', 1)[0]


def get_ner(ner_id_and_potential_suffix):
    return re.sub(r'[^a-zA-Z]', '', hashtag_ner(ner_id_and_potential_suffix))


def write_output_columns(output_f, columns):
    output_line = '\t'.join(columns)
    output_f.write(output_line + '\n')


def anonymize_entities(input_file, output_file, mapping_file, replacement_dict):
    """
    Anonymize entities in the input file and write the result to the output file.

    Args:
        input_file (str): The input file path.
        output_file (str): The output file path.
        mapping_file (str): The mapping file path.
        replacement_dict (dict): A dictionary of replacements.

    Returns:
        None
    """
    with open(input_file, 'r') as input_f, open(output_file, 'w') as output_f:
        for line in input_f:
            columns, token_info = preprocess_line(line)
            if token_info is None:
                output_f.write(line)
                continue

            ner_id_and_potential_suffix, token_tpl = token_info
            ner_inst = token_tpl[0]

            replacement = search_mapping_file(mapping_file, hashtag_ner(ner_id_and_potential_suffix))

            rep = process_already_mapped_replacement(replacement, ner_inst, ner_id_and_potential_suffix)

            if rep:
                columns[1] = rep
                write_output_columns(output_f, columns)
                continue

            columns[1] = process_entity(token_tpl, ner_id_and_potential_suffix, mapping_file, replacement_dict)
            write_output_columns(output_f, columns)
