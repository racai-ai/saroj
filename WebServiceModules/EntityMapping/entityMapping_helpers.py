from collections import defaultdict
import random
import re
import shutil
import string
import tempfile
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.saroj.dictionary_helper import read_replacement_dictionary
from entityMapping_config import args

NOT_FOUND = args.REPLACEMENT * 3
FIRST_TOKEN = 0
SECOND_TOKEN = 1
NER_ID = 1

# Global counters for each entity type
counters = {}

# Global mappings for initials
initials_mappings = {}

REPLACEMENTS = read_replacement_dictionary(args.DICTIONARY)

def get_random_X():
    return args.REPLACEMENT * random.randint(3, 10)


def get_random_ner(ner):
    return random.choice(REPLACEMENTS[ner])


def hashtag_ner(ner_id_and_potential_suffix):
    return ner_id_and_potential_suffix.split('_')[FIRST_TOKEN]


def insert_suffix_multiple_tokens(replacement, sfx):
    return replacement.split()[FIRST_TOKEN][:-1] + sfx + " " + " ".join(replacement.split()[SECOND_TOKEN:]) \
        if not (NOT_FOUND in replacement or not sfx) else replacement


def get_ner_and_suffix(ner_id_and_potential_suffix):
    return re.sub(r'[^a-zA-Z]', '', hashtag_ner(ner_id_and_potential_suffix)), \
        ner_id_and_potential_suffix.split("_")[SECOND_TOKEN] if "_" in ner_id_and_potential_suffix else ""


def write_output_columns(output_f, columns):
    output_line = '\t'.join(columns)
    output_f.write(output_line + '\n')


def update_mapping_file(mapping_file, entity, replacement):
    """
    Update a mapping file with a new replacement for a specified entity.

    Args:
        mapping_file (str): The path to the mapping file to be updated.
        entity (str): The identifier of the entity to be replaced.
        replacement (str): The replacement to be added for the specified entity.

    The function reads the content of the given `mapping_file` and locates the line containing
    the specified `entity` identifier. It then adds the `replacement` for that entity.

    The updated content is written to a temporary file. After processing is complete, the original
    mapping file is replaced with the temporary file, ensuring the mapping is updated.

    Note:
    - The mapping file is expected to be a tab-separated text file with at least three columns.
    - The 'entity' and 'replacement' parameters should match the appropriate columns in the file.

    Returns:
        None
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding="utf-8", errors="ignore") as temp:
        with open(mapping_file, 'r', encoding="utf-8", errors="ignore") as file:
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


def handle_character(ner_inst, replacement):
    # Generate a random number of replacement characters
    replacement = ''.join(random.choice(replacement or args.REPLACEMENT) for _ in range(random.randint(3, 10)))
    return replacement


def parse_mapping_file(mapping_file, config_dict):
    init_dict = defaultdict(list)
    name_dict = defaultdict(list)
    with open(mapping_file, 'r', encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split('\t')
            entity = ''.join(filter(str.isalpha, parts[1]))
            initials = parts[2] if len(parts) > 2 else None
            init_dict[entity].append(initials)
            if initials and config_dict.get(entity, {}).get('type') == 'initials':
                names = [s for part in parts[0].split() for s in part.split('-')]
                initials_list = initials.split()

                for name, initial in zip(names, initials_list):
                    name_dict[name] = initial
    return init_dict, name_dict


def handle_initials(ner_inst, name, mapping_file, config_dict):
    # Split name into words and map each word to a random initial, reusing existing mappings
    words = name.split("-")
    available_chars = set(string.ascii_uppercase)

    # Parse the mapping file
    mapping_dict, initials_mappings = parse_mapping_file(mapping_file,config_dict)

    # Remove used initials from available_chars
    used_initials = [initial for entity, initials_list in mapping_dict.items()
                     if entity in config_dict and config_dict[entity]['type'] == 'initials'
                     for initials in initials_list if initials is not None for initial in initials.split()]
    available_chars = list(filter(lambda initial: initial not in used_initials, available_chars))

    # Map each word to a random initial from the remaining available_chars
    initials = [initials_mappings.setdefault(word, random.choice(list(available_chars))
                if available_chars else random.choice(string.ascii_uppercase)) for word in words]

    initials = ' '.join(initials)
    return initials


def handle_counter(ner_inst, extra_info):
    # Increment the counter for ner_inst and return a string containing the starting word and the counter
    counters[ner_inst] = counters.get(ner_inst, 0) + 1
    return f'{extra_info} {counters[ner_inst]}'


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
    with open(mapping_file, 'r', encoding="utf-8", errors="ignore") as file:
        for line in file:
            columns = line.strip().split('\t')
            if len(columns) == 3 and columns[NER_ID] == ner_id_and_potential_suffix:
                replacement = columns[2]
                break  # Exit the loop once the entity is found

    return replacement


def read_config_file(file_path):
    """
    Reads a configuration file and returns a dictionary containing the configuration settings.

    Args:
        file_path (str): The path to the configuration file.

    Returns:
        dict: A dictionary containing the configuration settings. The keys are the configuration keys, and the values
              are dictionaries with the following structure:
              {
                  'type': str,  # The type of the configuration value
                  'extra_info': str  # Additional information about the configuration value (optional)
              }
    """
    config_dict = {}
    with open(file_path, 'r', encoding="utf-8", errors="ignore") as file:
        for line in file:
            line = line.strip()  # Remove leading/trailing whitespace
            if line:  # Skip empty lines
                parts = line.split("\t")  # Split on the first space
                if len(parts) < 2:  # Skip lines without a tab
                    continue
                key, type = parts[0], parts[1]
                extra_info = ''  # Default value for extra_info
                if ':' in type:  # If a colon is present in the value
                    type, extra_info = type.split(':', 1)  # Split on the first colon
                config_dict[key] = {'type': type.lower(), 'extra_info': extra_info}
    return config_dict
