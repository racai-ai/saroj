from collections import Counter, OrderedDict


def is_empty(data):
    return not data or all(not any(lin[0] for lin in line) for line in data)


def startswith_hashtag(data):
    return any(str(lin[0]).startswith("#") for line in data for lin in line)


def check_orthogonality(files):
    if not all(len(file) == len(files[0]) for file in files):
        raise ValueError("Input files do not have the same number of sentences.")


def replace_underscore_and_empty(input_collection):
    if isinstance(input_collection, list):
        return ['O' if element == '_' else element for element in input_collection]
    elif isinstance(input_collection, set):
        return {'O' if element == '_' else element for element in input_collection}
    else:
        raise ValueError("Input must be a list or a set")


def most_frequent_item(lst):
    if not lst:
        return None  # Return None for an empty list

    # Count the occurrences of each item in the list
    item_counts = Counter(lst)

    # Find the maximum frequency
    max_frequency = max(item_counts.values())

    threshold = round(len(lst)/2)
    # Find all items with the maximum frequency
    most_frequent_items = [item for item, count in item_counts.items() if count == max_frequency and count >= threshold]

    # If there's only one most frequent item, return it; otherwise, return None
    if len(most_frequent_items) > 1:
        return [item for item in most_frequent_items if item != "O"][0]
    elif len(most_frequent_items) == 1:
        return most_frequent_items[0]
    else:
        return None


# Function to read CoNLL-U Plus file
def read_conll_file(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8', errors="ignore") as file:
        lastEmpty=False
        for line in file:
            tokens = line.strip().split('\t')
            if len(tokens)>1:
                if lastEmpty:
                    data.append([])
                    lastEmpty=False
                data.append(tokens)
            else:
                lastEmpty=True
    return data


def diff_algorithm(files):
    result_data = []
    body = False
    for line in zip(*files):
        ner = replace_underscore_and_empty([sublist[-1] for sublist in line])

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
        ner = replace_underscore_and_empty(list(OrderedDict.fromkeys([sublist[-1].split('-')[-1] for sublist in line])))
        ner_w = next((value for value in ner if value != "O"), "O")

        if is_empty(line[0]) or startswith_hashtag(line[0]):
            result_data.append(line[0])
            body = False
            continue

        if ner_w != 'O' and (not body or previous_ner != ner_w):
            result_data.append(line[0][:-1] + ["B-" + str(ner_w)])
            previous_ner = str(ner_w)
            body = True
        elif ner_w != 'O' and body:
            result_data.append(line[0][:-1] + ["I-" + str(ner_w)])
            previous_ner = str(ner_w)
            body = True
        elif ner_w == 'O' and len(ner) == 1:
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
        ner_set = replace_underscore_and_empty(set([sublist[-1].split('-')[-1] for sublist in line]))

        if is_empty(line[0]) or startswith_hashtag(line[0]):
            result_data.append(line[0])
            body = False
            continue
        current_label = replace_underscore_and_empty(line[0][-1].split('-'))[-1]
        if len(ner_set) > 1 or current_label == "O":
            result_data.append(line[0][:-1] + ["O"])
            body = False
        elif len(ner_set) == 1 and body and current_label in old_label:
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
    old_mfi = ""
    for line in zip(*files):

        ner = replace_underscore_and_empty([sublist[-1].split('-')[-1] for sublist in line])
        mfi = most_frequent_item(ner)
        
        if is_empty(line[0]) or startswith_hashtag(line[0]):
            result_data.append(line[0])
            body = False
            continue

        if "O" == mfi or mfi is None:
            result_data.append(line[0][:-1] + ["O"])
            body = True if line[0][-1].startswith('B-') else False
        elif body and old_mfi == mfi:
            result_data.append(line[0][:-1] + ["I-" + str(mfi)])
        else:
            result_data.append(line[0][:-1] + ["B-" + str(mfi)])
            body = True
        old_mfi = mfi

    return result_data


# Function to write CoNLL-U Plus file
def write_conll_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8', errors="ignore") as file:
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
