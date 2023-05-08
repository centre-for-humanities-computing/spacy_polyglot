"""the entire package"""
import ssl
from typing import Callable, Iterable, List

# download danish specific stuff
from polyglot.downloader import downloader

# import
from polyglot.tag import NEChunker, POSTagger
from polyglot.text import Text, WordList
from spacy.language import Language
from spacy.tokens import Doc, Span
from spacy.training import Example


def no_misc_getter(doc, attr):
    spans = getattr(doc, attr)
    for span in spans:
        if span.label_ == "MISC":
            continue
        yield span


def add_iob(doc: Doc, iob: List[str]) -> Doc:
    """Add iob tags to Doc.

    Args:
        doc (Doc): A SpaCy doc
        iob (List[str]): a list of tokens on the IOB format

    Returns:
        Doc: A doc with the spans to the new IOB
    """
    ent = []
    for i, label in enumerate(iob):
        # turn OOB labels into spans
        if label == "O":
            continue
        iob_, ent_type = label.split("-")
        if (i - 1 >= 0 and iob_ == "I" and iob[i - 1] == "O") or (
            i == 0 and iob_ == "I"
        ):
            iob_ = "B"
        if iob_ == "B":
            start = i
        if i + 1 >= len(iob) or iob[i + 1].split("-")[0] != "I":
            ent.append(Span(doc, start, i + 1, label=ent_type))
    doc.set_ents(ent)
    return doc


def apply_on_multiple_examples(func: Callable) -> Callable:
    def inner(examples: Iterable[Example], **kwargs) -> Iterable[Example]:
        return [func(e, **kwargs) for e in examples]

    return inner


@Language.factory("polyglot")
def my_component(nlp, name):
    """A custom component that loads a Flair model and adds named entities and POS tags"""
    return PolyglotComponent(nlp=nlp, name=name)


class PolyglotComponent:
    def __init__(self, nlp, name):
        self.name = name
        self.nlp = nlp
        # setup certificate to download polyglot extras

        ssl._create_default_https_context = ssl._create_unverified_context

        downloader.download(f"embeddings2.{nlp.lang}")
        downloader.download(f"pos2.{nlp.lang}")
        downloader.download(f"ner2.{nlp.lang}")

        # load model
        self.ne_chunker = NEChunker(lang=nlp.lang)
        self.pos_tagger = POSTagger(lang=nlp.lang)

        # setup certificate to download flair
        ssl._create_default_https_context = ssl._create_unverified_context

    def __call__(self, doc):
        # tokenization
        words = WordList(
            [t.text for t in doc],
            language=self.nlp.lang,
        )
        # ner
        iob = [iob for token, iob in self.ne_chunker.annotate(words)]
        # pos-tagging
        tags = [tag for t, tag in self.pos_tagger.annotate(words)]

        doc = Doc(self.nlp.vocab, words=[t.text for t in doc], tags=tags, pos=tags)
        doc = add_iob(doc, iob)
        return doc


if __name__ == "__main__":
    import spacy

    # for danish
    nlp = spacy.blank("da")
    nlp.add_pipe("polyglot", last=True)
    doc = nlp("Jeg hedder Anders og bor i Odense.")
    print(doc.ents)

    # for english
    nlp = spacy.blank("en")
    nlp.add_pipe("polyglot", last=True)
    doc = nlp("My name is Anders and I live in Odense.")
    print(doc.ents)
