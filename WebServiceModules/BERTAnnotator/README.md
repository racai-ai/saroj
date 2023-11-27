## Installation
For this to work, there are two things that are required:
1. The `ro-wordpiece-tokenizer` from [GitHub](https://github.com/racai-ai/ro-wordpiece-tokenizer).
2. The `model.zip` archive, to unzip and overwrite the folder with the same name in this repository.

To install the Romanian wordpiece tokenizer, _until it makes its way to PyPI_, do this (assuming you are in the
folder containing this file):

```bash
cd ../lib/
git clone https://github.com/racai-ai/ro-wordpiece-tokenizer
cd ../BERTAnnotator
export PYTHONPATH=../lib/ro-wordpiece-tokenizer:$PYTHONPATH
```

Make sure not to commit the `../lib/ro-wordpiece-tokenizer` to the `saroj` repository!

Ask `radu@racai.ro` for the `model.zip` file.
