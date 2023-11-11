from collections import Counter


def is_empty(data):
    return not data or all(not any(lin[0] for lin in line) for line in data)


def startswith_hashtag(data):
    return any(str(lin[0]).startswith("#") for line in data for lin in line)


def check_orthogonality(files):
    if not all(len(file) == len(files[0]) for file in files):
        raise ValueError("Input files do not have the same number of sentences.")


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
    result_data = []
    body = False
    for line in zip(*files):
        ner = [sublist[-1] for sublist in line]
        if is_empty(line[0]) or startswith_hashtag(line[0]):
            result_data.append(line[0])
            body = False
            continue
        if any(ner[0][2:] in item[2:] for item in ner[1:]):
            result_data.append(line[0][:-1] + ["O"])
            body = True if ner[0].startswith('B-') else False
        else:
            if body:
                result_data.append(line[0][:-1] + ["B-" + ner[0][2:]])
            else:
                result_data.append(line[0])
            body = False

    return result_data


# Function to perform ADD algorithm
def add_algorithm(files):
    result_data = []
    body = False
    previous_ner = ''

    for line in zip(*files):
        ner = set([sublist[-1].split('-')[-1] for sublist in line])
        
        if is_empty(line[0]) or startswith_hashtag(line[0]):
            result_data.append(line[0])
            body = False
            continue
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
    result_data = []
    body = False
    old_label = ''
    for line in zip(*files):
        ner_set = set([sublist[-1].split('-')[-1] for sublist in line[1:]])
        current_label = line[0][-1].split('-')[-1]
        
        if is_empty(line[0]) or startswith_hashtag(line[0]):
            result_data.append(line[0])
            body = False
            continue
        if current_label == "O":
            result_data.append(line[0][:-1] + ["O"])
            body = False
        elif 1 == len(ner_set) and "O" in ner_set:
            result_data.append(line[0][:-1] + ["O"])
            body = False
        elif body and current_label in old_label:
            result_data.append(line[0][:-1] + ["I-" + current_label])
        else:
            result_data.append(line[0][:-1] + ["B-" + current_label])
            body = True
        old_label = current_label

    return result_data


# Function to perform MAJORITY algorithm
def majority_algorithm(files):
    result_data = []
    body = False
    for line in zip(*files):

        ner = [sublist[-1].split('-')[-1] for sublist in line]
        mfi = most_frequent_item(ner)
        
        if is_empty(line[0]) or startswith_hashtag(line[0]):
            result_data.append(line[0])
            body = False
            continue
        if mfi is None:
            result_data.append(line[0])
            body = True if line[0][-1].startswith('B-') else False
        elif "O" == mfi:
            result_data.append(line[0][:-1] + ["O"])
            body = True if line[0][-1].startswith('B-') else False
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
    files = [read_conll_file(file) for file in input_files]
    check_orthogonality(files)
    if "DIFF" == algo:
        result = diff_algorithm(files)
    elif "ADD" == algo:
        result = add_algorithm(files)
    elif "INTERSECT" == algo:
        result = intersect_algorithm(files)
    elif "MAJORITY" == algo:
        result = majority_algorithm(files)
    else:
        return

    write_conll_file(output_file, result)
