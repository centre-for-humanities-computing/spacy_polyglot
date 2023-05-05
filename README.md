# spaCy Polyglot
A spaCy wrapper for using polyglot within spaCy.


## Installation
```bash
pip install https://github.com/centre-for-humanities-computing/spacy_polyglot
```

You might need to install some dependencies first:
```bash
# install dev tools
apt-get install python3-venv
echo -e "[INFO:] Installing DEV tools ..." # user msg
apt-get update && apt-get install -y apt-transport-https -y
apt-get install libicu-dev -y
apt-get install python3-dev -y

#install things in this order
echo -e "[INFO:] Installing packages ..." # user msg
pip install pycld2
pip install polyglot
pip install --no-binary=:pyicu: pyicu
```

*Note*: This package is only intended to work on Linux.

## Usage
```python
import spacy
from spacy_polyglot import PolyglotComponent  # just to register the component


nlp = spacy.blank("da")
nlp.add_pipe("polyglot", last=True)
doc = nlp("Jeg hedder Anders og bor i Odense.")
print(doc.ents)
# (Anders, Odense)

nlp = spacy.blank("en")
nlp.add_pipe("polyglot", last=True)
doc = nlp("My name is Anders and I live in Odense.")
print(doc.ents)
# (Anders, Odense)
```
