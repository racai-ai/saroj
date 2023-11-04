from collections import Counter


def is_orthogonal(files):
    return all(len(file) == len(files[0]) for file in files)


def most_frequent_item(lst):
    if not lst:
        return None  # Return None for an empty list

    # Count the occurrences of each item in the list
    item_counts = Counter(lst)

    # Find the maximum frequency
    max_frequency = max(item_counts.values())

    # Find all items with the maximum frequency
    most_frequent_items = [item for item, count in item_counts.items() if count == max_frequency]

    # If there's only one most frequent item, return it; otherwise, return None
    if len(most_frequent_items) == 1:
        return most_frequent_items[0]
    else:
        return None


# Function to read CoNLL-U Plus file
def read_conll_file(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            tokens = line.strip().split('\t')
            data.append(tokens)
    return data


def diff_algorithm(files):
    if not is_orthogonal(files):
        raise ValueError("Input files do not have the same number of sentences.")
    result_data = []
    body = False
    for line in zip(*files):
        ner = [sublist[-1] for sublist in line]
        if ner[0] in ner[1:]:
            result_data.append(line[0][:-1] + ["O"])
            if ner[0].startswith('B-'):
                body = True
        else:
            if body:
                result_data.append(line[0][:-1] + ["B-" + ner[0][2:]])
            else:
                result_data.append(line[0])
            body = False

    return result_data


# Function to perform ADD algorithm
def add_algorithm(files):
    if not is_orthogonal(files):
        raise ValueError("Input files do not have the same number of sentences.")
    result_data = []
    body = False
    previous_ner = ''
    for line in zip(*files):
        ner = set([sublist[-1].split('-')[-1] for sublist in line])
        for i in ner:
            if i != 'O' and (not body or previous_ner != i):
                result_data.append(line[0][:-1] + ["B-" + str(i)])
                previous_ner = str(i)
                body = True
            elif i != 'O' and body:
                result_data.append(line[0][:-1] + ["I-" + str(i)])
                previous_ner = str(i)
                body = True
            elif i == 'O' and len(ner) == 1:
                result_data.append(line[0])
                previous_ner = ""
                body = False

    return result_data


# Function to perform INTERSECT algorithm
def intersect_algorithm(files):
    if not is_orthogonal(files):
        raise ValueError("Input files do not have the same number of sentences.")
    result_data = []
    body = False
    for line in zip(*files):
        ner = set([sublist[-1].split('-')[-1] for sublist in line[1:]])
        for i in ner:
            if "O" == line[0][-1].split('-')[-1]:
                result_data.append(line[0][:-1] + ["O"])
                body = False
                break
            elif i == line[0][-1].split('-')[-1] and body:
                result_data.append(line[0][:-1] + ["I-" + str(i)])
                body = True
                break
            elif i == line[0][-1].split('-')[-1] and not body:
                result_data.append(line[0][:-1] + ["B-" + str(i)])
                body = True
                break
            elif len(ner) == 1:
                result_data.append(line[0][:-1] + ["O"])
                body = False
                break

    return result_data


# Function to perform MAJORITY algorithm
def majority_algorithm(files):
    if not is_orthogonal(files):
        raise ValueError("Input files do not have the same number of sentences.")
    result_data = []
    body = False
    for line in zip(*files):

        ner = [sublist[-1].split('-')[-1] for sublist in line]
        mfi = most_frequent_item(ner)

        if mfi is None:
            result_data.append(line[0])
            body = False
        elif mfi == "O":
            result_data.append(line[0][:-1] + ["O"])
            body = False
        elif body:
            result_data.append(line[0][:-1] + ["I-" + str(mfi)])
        else:
            result_data.append(line[0][:-1] + ["B-" + str(mfi)])
            body = True

    return result_data


# Function to write CoNLL-U Plus file
def write_conll_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        for line in data:
            file.write('\t'.join(line) + '\n')


def vote(algo, input_files, output_file):
    if algo == "DIFF":
        result = diff_algorithm([read_conll_file(file) for file in input_files])
    elif algo == "ADD":
        result = add_algorithm([read_conll_file(file) for file in input_files])
    elif algo == "INTERSECT":
        result = intersect_algorithm([read_conll_file(file) for file in input_files])
    elif algo == "MAJORITY":
        result = majority_algorithm([read_conll_file(file) for file in input_files])
    else:
        return

    write_conll_file(output_file, result)
