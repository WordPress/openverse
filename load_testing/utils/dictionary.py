from pathlib import Path
from typing import Iterable
from random import Random

with open(Path('/') / 'usr' / 'share' / 'dict' / 'american-english') as dictionary:
    words: list[str] = dictionary.readlines()

random = Random()

def random_words(count=float('inf')) -> Iterable[str]:
    yielded = 0
    i = 0
    while yielded < count and i < len(words):
        word = words[i]
        if word[0] == word[0].lower() and random.choice((True, False)):
            yield word.strip()
        i += 1
