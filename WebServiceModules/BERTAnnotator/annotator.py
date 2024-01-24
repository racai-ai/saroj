import sys
import os
import re
import torch
from random import shuffle
from torch import nn, Tensor
from torch.utils.data import DataLoader, Dataset
from torch.optim import AdamW
from torch.optim.lr_scheduler import ExponentialLR
from tqdm import tqdm
from brat import read_txt_ann_folder, produce_ner_labels
# This is the Romanian WordPiece new PyPI package, at version 1.0.2
from rwpt import load_ro_pretrained_tokenizer
from transformers import AutoModel, BatchEncoding
from sklearn.metrics import classification_report
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.saroj.conllu_utils import CoNLLUFileAnnotator
from config import conf_window_length


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Running on device [{device}]', file=sys.stderr, flush=True)


class NERAddOn(nn.Module):
    """This is just a NN that has inputs from the BERT encoder
    and produces a NER classifier over NER labels, using softmax."""

    def __init__(self, labels_dim: int, bert_hidden_dim: int) -> None:
        """`labels_dim` -> how many labels we have,
        `bert_hidden_dim` -> size of the BERT encoding"""
        super().__init__()

        self._nn_linear = nn.Linear(
            in_features=bert_hidden_dim,
            out_features=labels_dim, dtype=torch.float32)
        self._logsoftmax = nn.LogSoftmax(dim=2)
        self.to(device)

    def forward(self, x):
        y = self._nn_linear(x)
        y = self._logsoftmax(y)

        return y


class NERDataset(Dataset):
    def __init__(self, examples: list[tuple]):
        super().__init__()
        self._examples = examples

    def reshuffle(self):
        shuffle(self._examples)

    def __len__(self):
        return len(self._examples)

    def __getitem__(self, idx):
        return self._examples[idx]


class BERTEntityTagger(object):
    # Initial learning rate
    _conf_lr = 1e-4
    # Multiplying factor between epochs of the LR
    _conf_gamma_lr = 0.8
    _conf_batch_size = 4
    _whitespace_rx = re.compile('\\s+')
    _sent_case_rx = re.compile('[A-ZȘȚĂÎÂ][a-zșțăîâ-]+')

    def __init__(self, seq_len: int) -> None:
        """Takes the BERT model input sequence length `seq_len`."""

        self._model_max_length = seq_len
        self._model_folder = \
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'model'
            )
        self._tokenizer = \
            load_ro_pretrained_tokenizer(max_sequence_len=self._model_max_length)

    def _tokenize_with_offsets(self, text: str) -> list[tuple[int, int, int]]:
        """Assume that tokenizer does not insert/delete characters!
        `RoBertPreTrainedTokenizer` will only change some characters."""

        tokens = self._tokenizer(text)
        int_tokens_offsets = []
        coff = 0

        # Map tokens to offsets in text
        for wid in tokens.data['input_ids']:
            token = self._tokenizer._convert_id_to_token(wid)

            if token.startswith('##'):
                int_tokens_offsets.append((wid, coff, coff + len(token) - 2))
                coff += len(token) - 2
            else:
                int_tokens_offsets.append((wid, coff, coff + len(token)))
                coff += len(token)
            # end if

            while coff < len(text) and \
                    BERTEntityTagger._whitespace_rx.fullmatch(text[coff]):
                coff += 1
            # end if
        # end for

        return int_tokens_offsets

    def prepare_train_dev_data(self,
                               examples: dict[str, list[tuple[str, int, int]]]) -> list[tuple]:
        tokenized_labeled_examples = []

        for text in tqdm(examples, desc='Tokenization'):
            int_tokens = self._tokenize_with_offsets(text=text)
            bio_labels = ['O'] * len(int_tokens)

            # Build the BIO labels for the int_tokens vector
            for label, soff, eoff in examples[text]:
                begin_label_set = False

                for i, (wid, tsoff, teoff) in enumerate(int_tokens):
                    if tsoff >= soff and not begin_label_set:
                        begin_label_set = True
                        bio_labels[i] = f'B-{label}'
                    elif teoff <= eoff and begin_label_set:
                        bio_labels[i] = f'I-{label}'
                    elif teoff > eoff:
                        break
                    # end if
                # end for all tokens
            # end for

            int_tokens = [wid for wid, _, _ in int_tokens]

            if len(int_tokens) <= self._model_max_length:
                tokenized_labeled_examples.append((int_tokens, bio_labels))
            else:
                for i in range(len(int_tokens) - self._model_max_length + 1):
                    tokenized_labeled_examples.append((
                        int_tokens[i:i + self._model_max_length],
                        bio_labels[i:i + self._model_max_length]
                    ))
                # end for
            # end if
        # all lines in training

        # Sequences are guaranteed to be <= self._model_max_length
        # Let's discard sequences with 'O' labels only...
        tokenized_labeled_examples2 = []

        for token_ids, bio_labels in tokenized_labeled_examples:
            o_count = sum([1 if x == 'O' else 0 for x in bio_labels])

            if o_count < len(bio_labels):
                tokenized_labeled_examples2.append((token_ids, bio_labels))
            # end if
        # end for

        return tokenized_labeled_examples2

    def _run_bert(self, token_ids: list[int]) -> Tensor:
        """Takes a pre-tokenized (with the same `self._tokenizer` tokenizer)
        and returns the BERT encoding for it, with gradients set for training."""

        token_ids = list(token_ids)
        token_cls = [0] * self._model_max_length
        token_msk = [1] * len(token_ids)

        while len(token_ids) < self._model_max_length:
            token_ids.append(self._tokenizer.pad_token_id)
            token_msk.append(0)
        # end while

        inputs = BatchEncoding(data={
            'input_ids': token_ids,
            'token_type_ids': token_cls,
            'attention_mask': token_msk
        }, tensor_type='pt', prepend_batch_axis=True).to(device)
        outputs = self._bertmodel(**inputs)
        # Shape of (1, 256, 256)
        return outputs.last_hidden_state

    def _ner_collate_fn(self, batch) -> tuple[Tensor, Tensor]:
        bert_encodings = []
        token_labels = []

        for tids, labs in batch:
            vec = self._run_bert(token_ids=tids)
            bert_encodings.append(vec)
            labs_ids = []

            for l in labs:
                labs_ids.append(self._ner_labels.index(l))
            # end for

            while len(labs_ids) < self._model_max_length:
                labs_ids.append(self._ner_labels.index('O'))
            # end while

            token_labels.append(torch.tensor(
                data=labs_ids, dtype=torch.long).view(1, -1).to(device))
        # end for

        return torch.cat(bert_encodings, dim=0), torch.cat(token_labels, dim=0)

    def train(self, train_folders: list[str], bert_checkpoint: str, epochs: int):
        """`train_folders` contain all folders which have .txt/.ann file pairs."""
        # 1. Get train/dev examples
        annotated_examples = {}

        for folder in train_folders:
            read_txt_ann_folder(ann_folder=folder,
                                annotations=annotated_examples)
        # end for

        self._ner_labels = produce_ner_labels(annotations=annotated_examples)
        tokenized_examples = self.prepare_train_dev_data(
            examples=annotated_examples)

        # 2. Set up models
        self._bertmodel = AutoModel.from_pretrained(bert_checkpoint)
        self._bertmodel.to(device)
        self._nermodel = NERAddOn(labels_dim=len(
            self._ner_labels), bert_hidden_dim=self._model_max_length)
        self._loss_fn = nn.NLLLoss()
        both_models_parameters = []

        both_models_parameters.extend(list(self._nermodel.parameters()))
        both_models_parameters.extend(list(self._bertmodel.parameters()))
        self._optimizer = AdamW(both_models_parameters,
                                lr=BERTEntityTagger._conf_lr)
        self._lr_scheduler = ExponentialLR(
            optimizer=self._optimizer, gamma=BERTEntityTagger._conf_gamma_lr, verbose=True)

        # 3. Create data sets
        shuffle(tokenized_examples)
        dev_size = int(len(tokenized_examples) * 0.1)
        dev_examples = tokenized_examples[0:dev_size]
        train_examples = tokenized_examples[dev_size:]

        train_dataset = NERDataset(examples=train_examples)
        train_dataloader = DataLoader(
            dataset=train_dataset,
            batch_size=BERTEntityTagger._conf_batch_size, shuffle=False, collate_fn=self._ner_collate_fn)
        dev_dataloader = DataLoader(
            dataset=NERDataset(examples=dev_examples),
            batch_size=BERTEntityTagger._conf_batch_size, shuffle=False, collate_fn=self._ner_collate_fn)

        best_acc = 0.

        for ep in range(epochs):
            self._nermodel.train(True)
            self._bertmodel.train(True)
            self._do_one_epoch(epoch=ep + 1, dataloader=train_dataloader)
            self._nermodel.eval()
            self._bertmodel.eval()
            ep_acc = self.eval(dataloader=dev_dataloader)

            if ep_acc > best_acc:
                print(file=sys.stderr)
                print(
                    f'Saving better BERTEntityTagger model with Acc = {ep_acc:.5f}',
                    file=sys.stderr)
                best_acc = ep_acc
                self._save()
                print(file=sys.stderr, flush=True)
            # end if

            self._lr_scheduler.step()
            train_dataset.reshuffle()
        # end for

    def _get_abbrev_file(self) -> str:
        abbr_file = os.path.join(self._model_folder,
            'abbrev.txt')
        print(
            f'Abbreviations file is [{abbr_file}]', file=sys.stderr, flush=True)
        return abbr_file

    def _get_neraddon_model_file(self) -> str:
        addon_path = os.path.join(self._model_folder,
            'ner_addon.pt')
        print(f'NER AddOn file is [{addon_path}]', file=sys.stderr, flush=True)
        return addon_path

    def _get_bert_nerfinetuned_folder(self) -> str:
        finetuned_path = os.path.join(self._model_folder,
            'finetuned')
        print(f'NER BERT folder is [{finetuned_path}]',
              file=sys.stderr, flush=True)
        return finetuned_path

    def _get_ner_labels_file(self) -> str:
        labels_path = os.path.join(self._model_folder,
            'ner_labels.txt')
        print(f'NER labels file is [{labels_path}]',
              file=sys.stderr, flush=True)
        return labels_path

    def _save(self):
        torch.save(
            self._nermodel.state_dict(), self._get_neraddon_model_file())
        self._bertmodel.save_pretrained(
            save_directory=self._get_bert_nerfinetuned_folder())

        with open(self._get_ner_labels_file(), mode='w', encoding='utf-8') as f:
            for label in self._ner_labels:
                print(label, file=f)
            # end for
        # end with

    def load(self, model_folder: str = ''):
        if model_folder:
            self._model_folder = model_folder
        # end if
        
        self._bertmodel = AutoModel.from_pretrained(
            self._get_bert_nerfinetuned_folder())
        self._bertmodel.to(device)
        self._bertmodel.eval()
        self._ner_labels = []

        with open(self._get_ner_labels_file(), mode='r', encoding='utf-8') as f:
            for line in f:
                self._ner_labels.append(line.strip())
            # end for
        # end with

        self._nermodel = NERAddOn(labels_dim=len(
            self._ner_labels), bert_hidden_dim=self._model_max_length)
        self._nermodel.load_state_dict(torch.load(
            self._get_neraddon_model_file(), map_location=device))
        # Put model into eval mode. It is used for inferencing.
        self._nermodel.eval()

    def tag_text(self, text: str) -> list[tuple[int, int, str]]:
        """Main method of this class: takes the input `text` and returns
        a list of (start_offset, end_offset, label) tuples.
        If `with_sentence_splitting is True`, do sentence splitting prior to NER."""
        
        tokens_offsets = self._tokenize_with_offsets(text)
        annotations = []

        if len(tokens_offsets) <= self._model_max_length:
            int_tokens = [wid for wid, _, _ in tokens_offsets]
            predicted_labels = self._tag_token_sequence(int_tokens)

            for i in range(len(tokens_offsets)):
                start_offset = tokens_offsets[i][1]
                end_offset = tokens_offsets[i][2]
                label = predicted_labels[i][0]

                annotations.append((start_offset, end_offset, label))
            # end for
        else:
            from_index = 0
            to_index = from_index + self._model_max_length
            no_more_tokens = False

            while True:
                w_tokens_offsets = tokens_offsets[from_index:to_index]
                w_int_tokens = [wid for wid, _, _ in w_tokens_offsets]
                w_predicted_labels = self._tag_token_sequence(w_int_tokens)

                for i in range(from_index, to_index):
                    start_offset = tokens_offsets[i][1]
                    end_offset = tokens_offsets[i][2]
                    label = w_predicted_labels[i - from_index][0]
                    label_prob = w_predicted_labels[i - from_index][1]

                    if i < len(annotations):
                        i_labels = annotations[i][2]

                        if label in i_labels:
                            i_labels[label].append(label_prob)
                        else:
                            i_labels[label] = [label_prob]
                        # end if
                    else:
                        annotations.append(
                            (start_offset, end_offset, {label: [label_prob]}))
                    # end if
                # end for
                
                if no_more_tokens:
                    break
                # end if
                        
                from_index += conf_window_length
                to_index = from_index + self._model_max_length

                if to_index > len(tokens_offsets):
                    to_index = len(tokens_offsets)
                    no_more_tokens = True
                # end if
            # end while

            annotations = [(so, eo, self._select_label(lbs))
                        for so, eo, lbs in annotations]
        # end if

        self._fix_inconsistent_annotations(annotations)
        return annotations

    def _fix_inconsistent_annotations(self, annotations: list[tuple[int, int, str]],
                                      consecutive_o: int = 1) -> None:
        """
        `consecutive_o`: how many consecutive 'O's to count before saying
        there's a new outside span.
        Fixes the following problems:
        - I-LBL O ... I-LBL -> I-LBL I-LBL ... I-LBL
        - B-LBL I-LBL I-LBL2 ... -> B-LBL I-LBL I-LBL ...
        - O I-LBL I-LBL ... -> B-LBL I-LBL ..."""

        annotation_indexes = []
        current_annotation = []

        for i in range(len(annotations)):
            soff, eoff, lbl = annotations[i]

            if lbl != 'O':
                current_annotation.append(i)
            elif current_annotation:
                o_last_index = len(current_annotation)

                for j in range(len(current_annotation) - 1, -1, -1):
                    if annotations[current_annotation[j]][2] == 'O':
                        o_last_index = j
                    else:
                        break
                    # end if
                # end for

                final_o_count = len(current_annotation) - o_last_index

                if final_o_count < consecutive_o:
                    current_annotation.append(i)
                else:
                    current_annotation = current_annotation[0:o_last_index]
                    annotation_indexes.append(current_annotation)
                    current_annotation = []
                # end if
            # end if
        # end for

        for ann_idx in annotation_indexes:
            labels = {}

            for i in ann_idx:
                lbl = annotations[i][2]
                lbl = lbl[2:]

                if lbl not in labels:
                    labels[lbl] = 1
                else:
                    labels[lbl] += 1
                # end if
            # end for

            s_labels = sorted(labels.keys(), key=lambda x,
                              d=labels: d[x], reverse=True)
            # What if s_labels[0] == s_labels[1] in frequency?
            the_label = s_labels[0]
            b_flag = True

            # Write the proper B-LBL I-LBL ... seqence
            for i in ann_idx:
                soff, eoff, lbl = annotations[i]

                if b_flag:
                    annotations[i] = (soff, eoff, f'B-{the_label}')
                    b_flag = False
                else:
                    annotations[i] = (soff, eoff, f'I-{the_label}')
                # end if
            # end for
        # end all found annotations

    def _select_label(self, labels: dict[str, list[float]]) -> str:
        """Applies a voting algorithm and returns the best label from the dictionary."""

        best_label = ''
        best_label_score = 0.0

        for lbl in labels:
            lbl_score = sum(labels[lbl]) / len(labels[lbl])

            if lbl_score > best_label_score:
                best_label_score = lbl_score
                best_label = lbl
            # end if
        # end for

        return best_label

    def _tag_token_sequence(self, int_tokens: list[int]) -> list[str]:
        with torch.no_grad():
            inputs_bert = self._run_bert(token_ids=int_tokens)
            outputs = self._nermodel(x=inputs_bert)
        # end with

        predicted_labels = torch.argmax(outputs, dim=2).flatten().tolist()
        predicted_probs = torch.exp(
            outputs[0, range(self._model_max_length), predicted_labels]).flatten().tolist()
        predicted_labels = [
            (self._ner_labels[x], predicted_probs[i])
            for i, x in enumerate(predicted_labels)]

        return predicted_labels

    def eval(self, dataloader: DataLoader) -> float:
        devset_target_labels = []
        devset_predicted_labels = []

        for inputs_bert, target_labels in tqdm(dataloader, desc='Validation: '):
            outputs = self._nermodel(x=inputs_bert)
            predicted_labels = torch.argmax(outputs, dim=2)
            devset_target_labels.extend(torch.flatten(target_labels).tolist())
            devset_predicted_labels.extend(
                torch.flatten(predicted_labels).tolist())
        # end for

        devset_target_labels = [self._ner_labels[x]
                                for x in devset_target_labels]
        devset_predicted_labels = [self._ner_labels[x]
                                   for x in devset_predicted_labels]
        devset_target_labels_noo = []
        devset_predicted_labels_noo = []

        # Discard the O label, we don't really care about it.
        for x, y in zip(devset_target_labels, devset_predicted_labels):
            if x != 'O' or y != 'O':
                devset_target_labels_noo.append(x)
                devset_predicted_labels_noo.append(y)
            # end if
        # end for

        perf_report = classification_report(
            devset_target_labels_noo, devset_predicted_labels_noo,
            labels=self._ner_labels, zero_division=0)
        print(perf_report)

        perf_dict = classification_report(
            devset_target_labels_noo, devset_predicted_labels_noo,
            output_dict=True, zero_division=0)
        return perf_dict['accuracy']

    def _do_one_epoch(self, epoch: int, dataloader: DataLoader):
        """Does one epoch of NN training."""
        running_loss = 0.
        epoch_loss = []
        counter = 0

        for inputs_bert, target_labels in tqdm(dataloader, desc=f'Epoch {epoch}'):
            counter += 1

            # Zero your gradients for every batch!
            self._optimizer.zero_grad()

            # Make predictions for this batch
            outputs = self._nermodel(x=inputs_bert)

            # Compute the loss and its gradients
            outputs = torch.swapaxes(input=outputs, axis0=1, axis1=2)
            loss = self._loss_fn(outputs, target_labels)
            loss.backward()

            # Adjust learning weights and learning rate schedule
            self._optimizer.step()

            # Gather data and report
            running_loss += loss.item()

            if counter % 100 == 0:
                # Average loss per batch
                average_running_loss = running_loss / 100
                print(f'\n  -> batch {counter}/{len(dataloader)} loss: {average_running_loss:.5f}',
                      file=sys.stderr, flush=True)
                epoch_loss.append(average_running_loss)
                running_loss = 0.
            # end if
        # end for i

        if epoch_loss:
            average_epoch_loss = sum(epoch_loss) / len(epoch_loss)
            print(
                f'  -> average epoch {epoch} loss: {average_epoch_loss:.5f}', file=sys.stderr, flush=True)
        # end if


class NeuralAnnotator(CoNLLUFileAnnotator):
    def __init__(self, input_file: str, tagger: BERTEntityTagger):
        super().__init__(input_file)
        self._bert_tagger = tagger

    def provide_annotations(self, text: str, text_before: str) -> list[tuple[int, int, str]]:
        return self._bert_tagger.tag_text(text=text)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python3 annotator.py <BERT checkpoint folder> <folder with .txt,.ann sub-folders>',
              file=sys.stderr, flush=True)
        exit(1)
    # end if

    nann = BERTEntityTagger(seq_len=256)
    bert_checkpoint_folder = sys.argv[1]

    if os.path.isdir(bert_checkpoint_folder):
        print(f'Fine-tuning checkpoint [{bert_checkpoint_folder}]', file=sys.stderr, flush=True)
    else:
        print(f'Error: BERT checkpoint [{bert_checkpoint_folder}] is not a folder', file=sys.stderr, flush=True)
        exit(1)
    # end if

    input_folders = []

    for txtann_folder in os.listdir(sys.argv[2]):
        txtann_folder = os.path.join(sys.argv[2], txtann_folder)

        if os.path.isdir(txtann_folder):
            print(
                f'Adding folder [{txtann_folder}] to the training set',
                file=sys.stderr, flush=True)
            input_folders.append(txtann_folder)
        # end if
    # end for

    if not input_folders:
        print('Error: no .txt,.ann input folders found. Need e.g. data/ with sub-folders doc1/, doc2/, ...', file=sys.stderr, flush=True)
        exit(1)
    # end if

    nann.train(
        train_folders=input_folders,
        bert_checkpoint=bert_checkpoint_folder, epochs=5)
