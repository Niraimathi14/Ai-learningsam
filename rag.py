import os
import re
import math
from collections import Counter


def _tokenize(text):
    return re.findall(r"[a-zA-Z']+", text.lower())


def _split_sentences(text):
    # Simple sentence splitter on '.', '!', '?'
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


class Chunk:
    def __init__(self, text, source, topic):
        self.text = text
        self.source = source
        self.topic = topic
        self.tokens = _tokenize(text)


class RAGIndex:
    def __init__(self, corpus_dir="data/course_materials"):
        self.corpus_dir = corpus_dir
        self.chunks = []
        self.idf = {}
        self._build()

    def _build(self):
        if not os.path.isdir(self.corpus_dir):
            return
