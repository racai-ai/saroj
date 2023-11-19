import os
import sys
from itertools import islice
import io

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from collections import deque

from Trie import *

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


def check_invalid_line(line):
    return True if line.startswith("#") or not line.strip() else False


def custom_sort(item):
    # Define a function to determine the sorting key for each item
    if item.isalpha():
        return 0, item  # Alpha characters come first
    else:
        return 1, item  # Non-alpha characters come next


def test_subsequences(tokens, trie_root):
    results = ()

    cleaned_tokens = [token for token in tokens if token != "-" ]
    for position in range(len(cleaned_tokens), 0, -1):
        subsequence = list(islice(cleaned_tokens, position))
        sorted_subsequence = sorted(subsequence, key=custom_sort)
        found, ner = find_in_trie(trie_root, sorted_subsequence)

        if found:
            results = (' '.join(subsequence), ner)

    return results


def parse_text_document(input_file):
    output = []

    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            # Assuming the lines are separated by tabs
            line_data = line.strip().split('\t')
            value_to_store = (line_data[1], line) if not check_invalid_line(line) else ("", line)
            output.append(value_to_store)

    return output


def process_and_write_entities(output_buffer, current_line, r,current_entities):
    subsequence_words = r[0].split()
    ner = [r[1]] * len(subsequence_words)  # Ensure ner is repeated for each word
    current_entity_tags = [f"{'B' if i == 0 else 'I'}-{label}" for i, (word, label) in
                           enumerate(zip(subsequence_words, ner))]

    for tag in current_entity_tags:
        output_buffer.write(current_line.popleft().strip() + '\t' + tag + '\n')
        current_entities.popleft()


def process_and_write(output_buffer, current_line, current_entities, trie_root):
    r = test_subsequences(current_entities, trie_root)
    if r:
        process_and_write_entities(output_buffer, current_line, r, current_entities)
    else:
        handle_not_found(output_buffer, current_line, current_entities)


def handle_not_found(output_buffer, current_line, current_entities):
    if current_entities[0] != "":
        output_buffer.write(current_line.popleft().strip() + NOT_FOUND)
    else:
        output_buffer.write(current_line.popleft())


def assign_ner(input_file, output_file, trie_root, max_count):
    """
    Process an input file, assigning Named Entity Recognition (NER) tags to entities based on a given dictionary.

    Args:
        input_file (str): The path to the input file containing lines to be processed.
            This file should have lines in the format "word<TAB>tag" where "word" is a token, and "tag" is the entity type.
        output_file (str): The path to the output file where tagged lines will be written.
        trie_root (TrieNode): The root of the trie data structure for efficient substring matching.
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
    output_buffer = io.StringIO()
    lines = parse_text_document(input_file)
    current_entities = deque(maxlen=max_count)
    current_line = deque(maxlen=max_count)

    for line in lines:
        token, _ = suffix_replace(line[0].lower())
        current_entities.append(token)
        current_line.append(line[1])

        if len(current_entities) >= max_count:
            process_and_write(output_buffer, current_line, current_entities, trie_root)
    
    current_entities.popleft()
    while current_entities:
        process_and_write(output_buffer, current_line, current_entities, trie_root)
        current_entities.popleft()

    # Write the final output
    output_buffer.seek(0)
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(output_buffer.read())
