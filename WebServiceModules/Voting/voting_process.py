# Function to read CoNLL-U Plus file
def read_conll_file(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            tokens = line.strip().split('\t')
            data.append(tokens)
    return data


def diff_algorithm(files):
    if not all(len(file) == len(files[0]) for file in files):
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
    if not all(len(file) == len(files[0]) for file in files):
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
    pass


# Function to perform MAJORITY algorithm
def majority_algorithm(files):
    pass


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
