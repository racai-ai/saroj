import os
import sys
import itertools

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from lib.saroj.suffix_process import suffix_replace

NOT_FOUND = '\tO\n'


def load_dictionary_with_max_token_count(dictionary_path):
    """
    Load a dictionary from a specified file, where each line in the file is expected to have
    the format "entity_type<TAB>entity_name". The function returns the loaded dictionary
    and the maximum token count among all the entity names in the dictionary.

    Args:
        dictionary_path (str): A string representing the file path to the dictionary file.

    Returns:
        tuple: A tuple containing the loaded dictionary and the maximum token count.
               The dictionary is a mapping of entity names to their corresponding entity types.
               The maximum token count is an integer representing the highest number of tokens
               in any entity name.
    """
    dictionary = {}
    max_token_count = 0

    # Open the specified file for reading with UTF-8 encoding
    with open(dictionary_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                entity_type, entity_name = parts
                dictionary[entity_name] = entity_type
                # Calculate the maximum token count
                token_count = len(entity_name.split())
                # Check if the current entity name has more tokens than the current maximum
                if token_count > max_token_count:
                    max_token_count = token_count

    return dictionary, max_token_count


def process_word_entities(dictionary, current_entities, lines, outfile):
    """
    Process a list of lines containing words and their associated entities, given a dictionary
    mapping entity names to their types. This function identifies and tags entities within the
    input lines and writes the tagged lines to the output file.

    Args:
        dictionary (dict): A dictionary mapping entity names to their types.
        current_entities (list): A list of words representing the current entity to be processed.
        lines (list): A list of lines containing words and their associated entities.
        outfile (file): The output file where the tagged lines will be written.

    Returns:
        bool: A boolean value indicating whether any entities were found and processed in the input.
             True if entities were found, False otherwise.
    """
    found = False
    if current_entities:
        found = True
        entity_key = ' '.join(current_entities)

        current_entity_tags = [f"{'B' if i == 0 else 'I'}-{dictionary[entity_key]}" for i, _ in
                               enumerate(entity_key.split())]
        for _ in lines[:-len(current_entity_tags)]:
            outfile.write(lines.pop(0).strip() + NOT_FOUND)
        for line, tag in zip(lines, current_entity_tags):
            outfile.write(line.strip() + '\t' + tag + '\n')
    return found


def process_single_word_entity(entity_key, dictionary, lines, outfile):
    """
    Process a single-word entity and tag it using a given dictionary. This function appends
    the tagged entity to the output file while preserving the input lines.

    Args:
        entity_key (str): The single-word entity to be processed.
        dictionary (dict): A dictionary mapping entity names to their types.
        lines (list): A list of lines containing words and their associated entities.
        outfile (file): The output file where the tagged lines will be written.

    Returns:
        None
    """
    for line in lines[:-1]:
        outfile.write(line.strip() + NOT_FOUND)
    matching_value = [dictionary.get(entity, "") for entity in entity_key.split() if entity in dictionary]
    outfile.write(lines[-1].strip() + '\t' + "B-"+matching_value[0] + '\n')


def check_invalid_line(line):
    return True if line.startswith("#") or not line.strip() else False


def assign_ner(input_file, output_file, dictionary, max_count):
    """
    Process an input file, assigning Named Entity Recognition (NER) tags to entities based on a given dictionary.

    Args:
        input_file (str): The path to the input file containing lines to be processed.
            This file should have lines in the format "word<TAB>tag" where "word" is a token, and "tag" is the entity type.
        output_file (str): The path to the output file where tagged lines will be written.
        dictionary (dict): A dictionary mapping entity names to their types.
            This dictionary is used to determine the entity type for identified entities.
        max_count (int): The maximum number of tokens allowed in a single entity name.
            Entities with more tokens than this limit will be split or truncated.

    Returns:
        None

    This function processes the input file line by line, assigning NER tags to entities based on the provided dictionary.
    Entities can be single-word entities or multi-word entities, and the function handles them accordingly.
    Any lines in the input file that are deemed invalid are written to the output file as they are, without NER tagging.

    The function utilizes helper functions 'process_word_entities' and 'process_single_word_entity' to tag entities.

    Note:
        - The 'suffix_replace' function is used to transform tokens when needed.
        - The 'check_invalid_line' function checks if a line is valid for NER tagging.

    Example:
        Given a dict file with lines like:
        "PER	Gheorghe"
        "LOC	Bucuresti"

        If the input file contains the entries:
        "1 Gheorghe _ _ _ _ _ _.."
        "2 din _ _ _ _ _ _ _ _.."
        "3 Bucuresti _ _ _ _ _.."

        The function will produce tagged lines in the output file:
        "1 Gheorghe _ _ _ _ _ _.. B-PER"
        "2 din _ _ _ _ _ _ _ _.. O"
        "3 Bucuresti _ _ _ _ _.. B_LOC"


    """

    def reset_entities():
        current_entities.clear()
        lines.clear()

    low_dict = {key.lower(): value for key, value in dictionary.items()}

    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        current_entities = []
        lines = []
        for line in infile:
            lines.append(line)
            if check_invalid_line(line):
                outfile.writelines(line.strip() + NOT_FOUND if not check_invalid_line(line) else line for line in lines)
                reset_entities()
                continue
            token, _ = suffix_replace(line.strip().split('\t')[1])
            current_entities.append(token.lower())

            permutations = [' '.join(p) for length in range(len(current_entities), 1, -1)
                            for p in itertools.permutations(current_entities, length)]

            matching_permutations = [permuted_key for permuted_key in permutations if permuted_key in low_dict]

            if process_word_entities(low_dict, matching_permutations, lines, outfile):
                reset_entities()
                continue

            entity_key = ' '.join(current_entities)
            if any(entity_key.split()[i].lower() in low_dict for i in range(len(current_entities))):
                process_single_word_entity(entity_key, low_dict, lines, outfile)
                reset_entities()

            elif len(current_entities) == max_count:
                outfile.write(lines.pop(0).strip() + NOT_FOUND) if len(lines) > 1 else None
                current_entities.pop(0)
