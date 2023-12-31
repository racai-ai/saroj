import random
import re
import shutil
import tempfile

from entityMapping_config import args

NOT_FOUND = args.REPLACEMENT * 3
FIRST_TOKEN = 0
SECOND_TOKEN = 1


def get_random_X():
    return args.REPLACEMENT * random.randint(3, 10)


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
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        with open(mapping_file, 'r', encoding="utf-8") as file:
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
