import os
import sys

from entityMapping_helpers import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from lib.saroj.suffix_process import suffix_replace, VOID_NER

old_rep = ""
extra_initials = False
counter_inst = 0
LAST_TOKEN = -1
NER = -2
NER_ID = 1
FORM = 1


def count_inst_entities(filename):
    """
    Count instances of NER entities in a file and return a list of instance counts.

    Args:
        filename (str): The path to a file containing NER entity annotations.

    Returns:
        list: A list of integer values representing the instance counts for each NER entity.

    The function reads the content of the specified `filename`, which is assumed to contain
    NER entity annotations. It counts the instances of NER entities and returns a list of
    integer values, each representing the instance count for a specific entity.

    Note:
    - The input file is expected to have NER annotations, typically in a tab-separated format.
    - The function accounts for both 'B-' (begin) and 'I-' (inside) entity labels.
    - The result list contains instance counts for each entity in the order they appear in the file.
    - Entities labeled as 'O' (outside) are not counted.
    - If the file is empty or does not contain relevant content, an empty list is returned.
    """
    result = []
    current_value = 0

    with open(filename, 'r', encoding="utf-8") as file:
        lines = file.readlines()

    for line in reversed(lines):
        if line.startswith("#") or not line.strip():
            continue
        columns = line.strip().split('\t')
        if columns[LAST_TOKEN] in VOID_NER:
            continue
        if columns[-2].startswith("I-"):
            current_value += 1
            result.append(current_value)
        elif columns[-2].startswith("B-"):
            result.append(current_value + 1)
            current_value = 0
        else:
            current_value = 0
            result.append(current_value)
    return result


def filter_neutral_valid_replacements(replacements):
    """
    Filter and select valid replacements from a list of replacements based on specific criteria.

    Args:
        replacements (list of str): A list of replacement candidates.

    Returns:
        str: A valid replacement selected based on the specified criteria or a randomly chosen replacement.

    The function filters the input `replacements` list by two criteria:
    1. Each replacement must have its first token not ending with 'a'.
    2. Each replacement must consist of exactly `counter_inst` tokens.

    If valid replacements are found, one of them is randomly chosen and returned.
    If no valid replacements are found, a random replacement from the original list is returned.
    If the original list of replacements is empty, a random value is generated using get_random_X().
    """
    filtered_replacements = [replacement for replacement in replacements
                             if not replacement.split()[FIRST_TOKEN].endswith('a')]

    valid_replacements = [replacement for replacement in filtered_replacements
                          if len(replacement.split()) == counter_inst]

    if valid_replacements:
        return random.choice(valid_replacements)

    return random.choice(replacements) if replacements else get_random_X()


def process_suffix_tokens(replacement, ner_id_and_potential_suffix):
    """
    Process a replacement by applying a suffix based on NER identifier and potential suffix.

    Args:
        replacement (str): The original replacement.
        ner_id_and_potential_suffix (str): The NER identifier and potential suffix.

    Returns:
        str: The processed replacement with the applied suffix.
    """

    def apply_suffix(token, sfx):
        return token + sfx if not token.endswith("a") else token[:LAST_TOKEN] + sfx

    def apply_first_token_suffix(sfx):
        return apply_suffix(replacement_tokens[FIRST_TOKEN], sfx)

    def handle_single_token_with_suffix():
        return apply_suffix(replacement, suffix)

    def handle_multi_token_with_suffix():
        return apply_first_token_suffix(suffix) + " " + " ".join(replacement_tokens[SECOND_TOKEN:])

    replacement_tokens = replacement.split()
    _, suffix = get_ner_and_suffix(ner_id_and_potential_suffix)

    if len(replacement_tokens) == 1 and counter_inst == 1:
        return handle_single_token_with_suffix()

    if len(replacement_tokens) > 1 and counter_inst == 1:
        return handle_multi_token_with_suffix()

    if counter_inst != 1 and NOT_FOUND not in replacement:
        return apply_first_token_suffix(suffix)


def already_mapped_I_inst(replacement):
    if len(replacement.split()) == 1:
        return "_"
    else:
        return replacement.split()[-counter_inst]


def process_already_mapped_replacement(replacement, ner_inst, type, ner_id_and_potential_suffix):
    """
    Process a replacement based on NER instance and potential suffix.

    Args:
        replacement (str): The original replacement.
        ner_inst (str): The NER instance.
        ner_id_and_potential_suffix (str): The NER identifier and potential suffix.

    Returns:
        str: The processed replacement.
    """

    if ner_inst.startswith("I-"):
        return already_mapped_I_inst(replacement)

    conditions = ["_" in ner_id_and_potential_suffix,
                  NOT_FOUND not in replacement,
                  type == "dictionary"]
    if all(conditions):
        return process_suffix_tokens(replacement, ner_id_and_potential_suffix)

    replacement_tokens = replacement.split()
    fallthrough_conditions = [len(replacement_tokens) > 1 and counter_inst == 1,
                              len(replacement.split()) == 1 and counter_inst > 1]

    if any(fallthrough_conditions):
        return replacement

    return replacement_tokens[-counter_inst] if len(replacement_tokens) >= counter_inst else "_"


def process_entity_inst_I(ner_id_and_potential_suffix, mapping_file):
    """
    Process entities with an instance marker 'I-'.

    Args:
        ner_id_and_potential_suffix (str): The NER identifier and potential suffix.
        mapping_file (str): The mapping file to update.

    Returns:
        str: The processed replacement.
    """

    split_old_rep = old_rep.split()
    split_old_rep.reverse()
    # Modify the replacement with the suffix if not found
    rep = split_old_rep[counter_inst - 1] if NOT_FOUND not in old_rep else old_rep
    # Update the mapping file and replacement dictionary
    update_mapping_file(mapping_file, ner_id_and_potential_suffix, rep if len(split_old_rep) > 1 else "")

    return rep if len(split_old_rep) > 1 else "_"


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

    # Get the NER and suffix from the identifier
    ner, suffix = get_ner_and_suffix(ner_id_and_potential_suffix)

    replacement_list = [fname for fname in replacement_dict[ner] if
                        fname.split()[FIRST_TOKEN].endswith('a') and fname != lemma]
    replacement = next((fname for fname in replacement_list if len(fname.split()) == counter_inst), None)

    if replacement is None:
        replacement = next((fname for fname in replacement_list), None)

    if replacement is None:
        replacement = random.choice(replacement_dict[ner]) if replacement_dict[ner] else get_random_X()

    old_rep = replacement
    # Modify the replacement with the suffix
    rep = insert_suffix_multiple_tokens(replacement, suffix)

    # Update the mapping file and replacement dictionary
    update_mapping_file(mapping_file, hashtag_ner(ner_id_and_potential_suffix), replacement)
    replacement_dict[ner] = [value for value in replacement_dict[ner] if not re.search(replacement, value)]

    return rep if len(rep.split()) > counter_inst else rep.split()[FIRST_TOKEN]


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
    ner, suffix = get_ner_and_suffix(ner_id_and_potential_suffix)

    replacements = replacement_dict[ner]
    replacement = filter_neutral_valid_replacements(replacements)

    # Set the new value for columns
    old_rep = rep = insert_suffix_multiple_tokens(replacement, suffix)

    # Update mapping and used values
    update_mapping_file(mapping_file, hashtag_ner(ner_id_and_potential_suffix), replacement)
    replacement_dict[ner] = [value for value in replacement_dict[ner] if not re.search(replacement, value)]

    return rep if len(rep.split()) > counter_inst else rep.split()[FIRST_TOKEN]


def handle_generic_entity(ner_id_and_potential_suffix, token_tpl, replacement_dict, mapping_file):
    ner, _ = get_ner_and_suffix(ner_id_and_potential_suffix)
    ner_inst, lemma = token_tpl
    if ner in replacement_dict:
        # all cases have embedded the update_mapping_file function call
        # because is not writing the same as returns, that's why could not be extracted, for the moment.
        if ner_inst.startswith("I-"):
            replacement = process_entity_inst_I(ner_id_and_potential_suffix, mapping_file)
        elif lemma.endswith('a'):
            replacement = process_female_entity(lemma, ner_id_and_potential_suffix, replacement_dict, mapping_file)
        else:
            replacement = process_neutral_entity(ner_id_and_potential_suffix, replacement_dict, mapping_file)
    else:
        replacement = get_random_X()
        update_mapping_file(mapping_file, hashtag_ner(ner_id_and_potential_suffix), replacement)
    return replacement


def process_entity(token_tpl, ner_id_and_potential_suffix, mapping_file, dicts):
    """
    Process a named entity based on token information and the type of named entity recognition (NER).

    Args:
        token_tpl (tuple): A tuple containing the NER instance and lemma.
        ner_id_and_potential_suffix (str): The NER identifier and potential suffix.
        mapping_file (str): The path to the file that contains mappings from entities to their replacements.
        dicts (dict): A dictionary containing additional configuration and replacement options.

    Returns:
        str: The processed replacement for the entity.

    This function processes a named entity based on the information in `token_tpl` and `ner_id_and_potential_suffix`.
    It uses the `mapping_file` to update the mappings as it processes each entity, and the `dicts` dictionary to 
    specify additional configuration and replacement options. The function returns the processed replacement for the entity.
    """
    global extra_initials
    ner, _ = get_ner_and_suffix(ner_id_and_potential_suffix)
    ner_inst, lemma = token_tpl
    replacement_dict = dicts["replacement"]
    config_dict = dicts["config"]

    # Create a dictionary mapping config keys to functions
    switch = {
        'character': handle_character,
        'counter': handle_counter,
        'initials': handle_initials,
        'dictionary': handle_generic_entity
    }

    # Get the function for the current ner_inst from the switch dictionary
    ner_config = config_dict.get(ner)
    case_func = switch.get(ner_config['type']) if ner_config else handle_generic_entity

    # If the config value for ner_inst is 'counter' or 'character', pass the extra_info as a second argument
    if ner_config and ner_config['type'] in ["counter", "character"]:
        replacement = case_func(ner, ner_config['extra_info'])
        update_mapping_file(mapping_file, hashtag_ner(ner_id_and_potential_suffix), replacement)

    elif ner_config and ner_config['type'] == "initials":
        replacement = case_func(ner, lemma)
        extra_initials = counter_inst != 1
        update_mapping_file(mapping_file, hashtag_ner(ner_id_and_potential_suffix), replacement)
    else:
        replacement = case_func(ner_id_and_potential_suffix, token_tpl, replacement_dict, mapping_file)

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
    ner_id_and_potential_suffix = columns[LAST_TOKEN]  # #PER1_ei

    if ner_id_and_potential_suffix in VOID_NER:
        return line, None

    ner_inst = columns[NER]  # B-PER
    form = columns[FORM]  # Mariei

    if "_" in ner_id_and_potential_suffix:
        form, _ = suffix_replace(form)

    return columns, (ner_id_and_potential_suffix, (ner_inst, form))


def anonymize_entities(input_file, output_file, mapping_file, dicts):
    """
    Anonymize Named Entity Recognition (NER) entities in an input file and write the result to an output file.

    Args:
        input_file (str): The path to the input file containing NER entities.
        output_file (str): The path to the output file where anonymized content will be written.
        mapping_file (str): The path to the file containing entity-to-replacement mappings.
        dicts (dict): A dictionary containing additional configuration and replacement options.

    This function reads the content of the specified `input_file`, processes NER entities,
    and replaces them with anonymized content based on the provided `mapping_file` and `dicts`.
    The resulting content is written to the `output_file`.

    The `dicts` parameter is expected to be a dictionary containing two keys: 'config' and 'replacement'.
    'config' is a dictionary that maps NER types to their configurations, and 'replacement' is a dictionary
    that maps NER entities to their replacements.

    Note:
    - The input file is expected to contain NER entities that need anonymization.
    - The `mapping_file` contains predefined entity-to-replacement mappings.
    - The `dicts['replacement']` is a dictionary of replacement options for entities not found already in the mapping file.
    """
    global counter_inst
    # Count the instances of each entity in the input file
    counter_inst_list = count_inst_entities(input_file)

    # Open the input and output files
    with open(input_file, 'r', encoding="utf-8") as input_f, open(output_file, 'w', encoding="utf-8") as output_f:
        # Process each line in the input file
        for line in input_f:
            # Preprocess the line to extract the columns and token information
            columns, token_info = preprocess_line(line)

            # If there is no token information, write the line to the output file as is
            if token_info is None:
                output_f.write(line)
                continue

            # Get the next counter instance from the list
            counter_inst = counter_inst_list.pop()

            # Extract the NER ID and potential suffix, and the NER instance from the token information
            ner_id_and_potential_suffix, token_tpl = token_info
            ner_inst = token_tpl[FIRST_TOKEN]
            ner = token_tpl[SECOND_TOKEN]

            # Search for a replacement for the NER ID in the mapping file
            replacement = search_mapping_file(mapping_file, hashtag_ner(ner_id_and_potential_suffix))

            # If a replacement was found, process it and write it to the output file
            if replacement and not extra_initials:
                replacement = process_already_mapped_replacement(replacement, ner_inst, dicts["config"].get(ner),
                                                                 ner_id_and_potential_suffix)
            else:
                replacement = process_entity(token_tpl, ner_id_and_potential_suffix, mapping_file, dicts)

            columns.append(replacement)
            write_output_columns(output_f, columns)
