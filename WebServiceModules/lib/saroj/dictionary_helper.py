def count_instances_in_dict(input_dict):
    """
    Count the number of instances for each key in a dictionary.

    Args:
        input_dict (dict): A dictionary where keys are identifiers and values are lists of instances.

    Returns:
        str: A string containing a count for each key in the input dictionary.

    The function takes an input dictionary where keys are identifiers and values are lists of instances.
    It counts the number of instances for each key and returns a string with the key-value pairs.

    Note:
    - The input dictionary should have keys as identifiers and values as lists of instances.
    - The function ensures that keys are treated as strings.
    - The returned string contains key-value pairs in the format "key:count," separated by a comma and space.
    """
    instance_count = {}

    for key, values in input_dict.items():
        key = str(key)  # Ensure the key is a string
        if key in instance_count:
            instance_count[key] += len(values)
        else:
            instance_count[key] = len(values)

    result = ""
    for key, count in instance_count.items():
        result += f"{key}:{count}, "

    if result:
        result = result[:-2]  # Remove the trailing comma and space

    return result


def read_replacement_dictionary(dictionary_file):
    """
    Read and parse a replacement dictionary from a text file.

    Args:
        dictionary_file (str): The path to the dictionary file.

    Returns:
        dict: A replacement dictionary where keys are NER identifiers and values are lists of replacements.

    The function reads the content of the specified `dictionary_file`, assuming it is a tab-separated text file
    with two columns: NER identifiers (keys) and their corresponding replacements (values).

    It constructs and returns a replacement dict where NER identifiers are mapped to lists of possible replacements.

    Note:
    - The function expects the dictionary file to have exactly two columns per line.
    - If an NER identifier already exists in the dictionary, the replacement is appended to its list.
    """
    replacement_dict = {}
    with open(dictionary_file, 'r', encoding="utf-8") as file:
        for line in file:
            columns = line.strip().split('\t')
            if len(columns) == 2:
                ner, replacement = columns
                # Check if ner_id_and_potential_suffix exists in the dictionary
                if ner not in replacement_dict:
                    replacement_dict[ner] = []
                replacement_dict[ner].append(replacement)
    return replacement_dict
