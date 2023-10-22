import os
import sys

from entityMapping_helpers import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from lib.saroj.suffix_process import suffix_replace, VOID_NER

old_rep = ""
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


def search_mapping_file(mapping_file, ner_id_and_potential_suffix):
    """
     Search for a replacement in a mapping file based on a given NER identifier and potential suffix.

     Args:
         mapping_file (str): The path to the mapping file.
         ner_id_and_potential_suffix (str): The NER identifier and potential suffix to look up.

     Returns:
         str: The replacement value found in the mapping file, or '' if not found.
     """
    replacement = ""  # Default replacement if not found
    with open(mapping_file, 'r', encoding="utf-8") as file:
        for line in file:
            columns = line.strip().split('\t')
            if len(columns) == 3 and columns[NER_ID] == ner_id_and_potential_suffix:
                replacement = columns[2]
                break  # Exit the loop once the entity is found
    return replacement


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

    def is_single_token_replacement():
        return len(replacement.split()) == 1

    if ner_inst.startswith("I-") and is_single_token_replacement():
        return "_"

    if "_" in ner_id_and_potential_suffix and NOT_FOUND not in replacement:
        return process_suffix_tokens(replacement, ner_id_and_potential_suffix)

    replacement_tokens = replacement.split()
    fallthrough_conditions = [len(replacement_tokens) > 1 and counter_inst == 1,
                              is_single_token_replacement() and counter_inst > 1]

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

    replacement_list = [fname for fname in replacement_dict[ner] if fname.split()[FIRST_TOKEN].endswith('a') and fname != lemma]
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
    old_rep, rep = insert_suffix_multiple_tokens(replacement, suffix)

    # Update mapping and used values
    update_mapping_file(mapping_file, hashtag_ner(ner_id_and_potential_suffix), replacement)
    replacement_dict[ner] = [value for value in replacement_dict[ner] if not re.search(replacement, value)]

    return rep if len(rep.split()) > counter_inst else rep.split()[FIRST_TOKEN]


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
    ner = get_ner_and_suffix(ner_id_and_potential_suffix)
    ner_inst, lemma = token_tpl

    if ner in replacement_dict:
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


def anonymize_entities(input_file, output_file, mapping_file, replacement_dict):
    """
    Anonymize NER entities in an input file and write the result to an output file.

    Args:
        input_file (str): The path to the input file containing NER entities.
        output_file (str): The path to the output file where anonymized content will be written.
        mapping_file (str): The path to the file containing entity-to-replacement mappings.
        replacement_dict (dict): A dictionary of replacement options for entities.

    The function reads the content of the specified `input_file`, processes NER entities,
    and replaces them with anonymized content based on the provided `mapping_file` and `replacement_dict`.
    The resulting content is written to the `output_file`.

    Note:
    - The input file is expected to contain NER entities that need anonymization.
    - The `mapping_file` contains predefined entity-to-replacement mappings.
    - The `replacement_dict` is a dictionary of replacement options for entities not found already in the mapping file.
    """
    global counter_inst
    counter_inst_list = count_inst_entities(input_file)
    with open(input_file, 'r', encoding="utf-8") as input_f, open(output_file, 'w', encoding="utf-8") as output_f:
        for line in input_f:
            columns, token_info = preprocess_line(line)
            if token_info is None:
                output_f.write(line)
                continue

            counter_inst = counter_inst_list.pop()
            ner_id_and_potential_suffix, token_tpl = token_info
            ner_inst = token_tpl[FIRST_TOKEN]

            replacement = search_mapping_file(mapping_file, hashtag_ner(ner_id_and_potential_suffix))

            if replacement:
                replacement = process_already_mapped_replacement(replacement, ner_inst, ner_id_and_potential_suffix)
                columns.append(replacement)
                write_output_columns(output_f, columns)
                continue

            columns.append(process_entity(token_tpl, ner_id_and_potential_suffix, mapping_file, replacement_dict))
            write_output_columns(output_f, columns)
