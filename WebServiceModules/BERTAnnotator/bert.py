from transformers import AutoModel, AutoTokenizer, \
    PreTrainedTokenizer, PreTrainedTokenizerFast, \
    BertModel
from rwpt import load_ro_pretrained_tokenizer


class NERBertModel(object):
    def __init__(self, name_or_folder: str = '') -> None:
        self._hidden_dim = 0
        self._max_seq_len = 0
        self._tokenizer = None
        self._model = None

    def get_tokenizer(self) -> PreTrainedTokenizer | PreTrainedTokenizerFast:
        raise NotImplementedError(
            'No tokenizer is set, please use a sub-class')

    def get_model(self) -> BertModel:
        raise NotImplementedError(
            'No model is set, please use a sub-class')

    @property
    def bert_hidden_size(self) -> int:
        return self._hidden_dim

    @property
    def max_sequence_len(self) -> int:
        return self._max_seq_len


class CorolaBert(NERBertModel):
    def __init__(self, name_or_folder: str = '') -> None:
        super().__init__(name_or_folder)
        self._max_seq_len = 256
        self._hidden_dim = 256
        self._tokenizer = \
            load_ro_pretrained_tokenizer(max_sequence_len=self._max_seq_len)
        self._model = AutoModel.from_pretrained(name_or_folder)

    def get_tokenizer(self) -> PreTrainedTokenizer | PreTrainedTokenizerFast:
        return self._tokenizer

    def get_model(self) -> BertModel:
        return self._model


class DumitrescuBert(NERBertModel):
    def __init__(self, name_or_folder: str = '') -> None:
        super().__init__(name_or_folder)
        self._tokenizer = AutoTokenizer.from_pretrained(
            'dumitrescustefan/bert-base-romanian-cased-v1')
        self._model: BertModel = AutoModel.from_pretrained(
            'dumitrescustefan/bert-base-romanian-cased-v1')
        self._hidden_dim = self._model.config.hidden_size
        self._max_seq_len = self._model.config.max_position_embeddings

    def get_tokenizer(self) -> PreTrainedTokenizer | PreTrainedTokenizerFast:
        return self._tokenizer

    def get_model(self) -> BertModel:
        return self._model


class ReaderbenchSmall(NERBertModel):
    def __init__(self, name_or_folder: str = '') -> None:
        super().__init__(name_or_folder)
        self._tokenizer = AutoTokenizer.from_pretrained(
            'readerbench/RoBERT-small')
        self._model: BertModel = AutoModel.from_pretrained('readerbench/RoBERT-small')
        self._hidden_dim = self._model.config.hidden_size
        self._max_seq_len = self._model.config.max_position_embeddings

    def get_tokenizer(self) -> PreTrainedTokenizer | PreTrainedTokenizerFast:
        return self._tokenizer

    def get_model(self) -> BertModel:
        return self._model


class ReaderbenchBase(NERBertModel):
    def __init__(self, name_or_folder: str = '') -> None:
        super().__init__(name_or_folder)
        self._tokenizer = AutoTokenizer.from_pretrained(
            'readerbench/RoBERT-base')
        self._model: BertModel = AutoModel.from_pretrained(
            'readerbench/RoBERT-base')
        self._hidden_dim = self._model.config.hidden_size
        self._max_seq_len = self._model.config.max_position_embeddings

    def get_tokenizer(self) -> PreTrainedTokenizer | PreTrainedTokenizerFast:
        return self._tokenizer

    def get_model(self) -> BertModel:
        return self._model
