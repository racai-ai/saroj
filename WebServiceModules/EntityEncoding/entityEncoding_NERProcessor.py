from entityEncoding_suffix import suffix_replace, VOID_NER


class NERProcessor:
    def __init__(self, output_file, new_ner_id, mapped_tokens):
        self.output_file = output_file
        self.new_ner_id = new_ner_id
        self.mapped_tokens = mapped_tokens
        self.search = []
        self.acc = []
        self.sfxs = []
        self.last_line = False

    def process_comment_or_empty_line(self, current_line):
        if current_line.startswith("#") or not current_line.strip():
            self.output_file.write(current_line)
            return None
        else:
            return current_line

    def process_valid_line(self, current_line, next_line):
        fields = current_line.strip().split("\t")
        fields_next = next_line.strip().split("\t") if next_line is not None else []

        token, ner_tag = fields[1], fields[-1]
        ner_tag_next = fields_next[-1] if fields_next else ""

        if ner_tag in VOID_NER:
            fields.append("_")
            self.output_file.write('\t'.join(fields) + '\n')
        else:
            self.process_non_void_ner(token, ner_tag, ner_tag_next, fields)

    def process_non_void_ner(self, token, ner_tag, ner_tag_next, fields):
        token, sfx = suffix_replace(token)
        self.search.append(token)

        if ner_tag_next.startswith("I-"):
            self.sfxs.append(sfx)
            self.acc.append('\t'.join(fields))
        else:
            match_tpl = next((t for t in self.mapped_tokens if t[0] == " ".join(self.search)), None)
            if match_tpl is not None:
                _, self.new_ner_id = match_tpl
                self.search.clear()
                self.acc_write()

            if ner_tag != "_":
                fields.append(f"{self.new_ner_id}{sfx}")
            self.output_file.write('\t'.join(fields) + '\n')

        if self.last_line:
            match_tpl = next((t for t in self.mapped_tokens if t[0] == " ".join(self.search)), None)
            if match_tpl is not None:
                _, self.new_ner_id = match_tpl
            self.acc_write()

    def acc_write(self):
        if self.acc:
            self.update_accumulated_entities()
            self.acc.clear()
            self.sfxs.clear()

    def update_accumulated_entities(self):
        for acc_item, sfx in zip(self.acc, self.sfxs):
            acc_item += f'\t{self.new_ner_id}{sfx}\n'
            self.output_file.write(acc_item)
