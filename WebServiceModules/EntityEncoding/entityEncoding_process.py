import os
import re


def read_mapping(mapping_path):
    entity_mapping = {}
    # Check if mapping file exists; if not, create it
    if not os.path.exists(mapping_path):
        with open(mapping_path, "w") as mapping_file:
            mapping_file.write("")
    # Load existing mapping data into memory
    with open(mapping_path, "r", encoding="utf-8") as mapping_file:
        for line in mapping_file:
            token, ner_id = line.strip().split('\t')
            entity_mapping[token] = ner_id
    return entity_mapping


def suffix_replace(token):
    suffixes = {
        "ei": "a",
        "ăi": "a",
        "ilor": "i",
        "ul": "",
    }

    for suffix, replacement in suffixes.items():
        if token.endswith(suffix):
            name = token[:-len(suffix)] + replacement
            sfx = "_" + suffix
            return name, sfx

    return token, ""


def process_conllup(input_path, output_path, mapping_path, entity_mapping):
    # Process the CoNLL-U Plus file
    with open(input_path, "r", encoding="utf-8") as input_file, open(output_path, "w", encoding="utf-8") as output_file:
        for line in input_file:
            if line.startswith("#"):
                # Header lines, write them as-is
                output_file.write(line)
            else:
                fields = [token.strip() for token in re.split(r'(\t|  {2})', line) if token.strip()]
                token = fields[1]
                ner_tag = fields[-1]
                sfx = ''

                if ner_tag == "PER" or ner_tag == "LOC":
                    token, sfx = suffix_replace(token)

                # Check if the token is in the entity mapping
                if token in entity_mapping:
                    # Use the existing NER ID
                    new_ner_id = entity_mapping[token]
                else:
                    # Generate a new NER ID based on the current count
                    new_ner_id = f"#{ner_tag}{str(len(entity_mapping) + 1)}"
                    # Update the mapping
                    entity_mapping[token] = new_ner_id
                    if ner_tag != "_":
                        with open(mapping_path, "a", encoding="utf-8") as mapping_file:
                            mapping_file.write(f"{token}\t{new_ner_id}\n")

                if ner_tag != "_":
                    # Update the NER column with the new NER ID
                    fields.append(f"{new_ner_id}{sfx}")

                # Write the updated line to the output file
                output_file.write('\t'.join(fields) + '\n')
