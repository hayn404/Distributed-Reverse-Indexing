#!/usr/bin/env python3
import sys

current_word = None
current_doc = None
count = 0

for line in sys.stdin:
    parts = line.strip().split("\t")
    if len(parts) != 2:
        continue

    word, doc = parts

    if current_word == word and current_doc == doc:
        count += 1
    else:
        if current_word is not None:
            print(f"{current_word}\t{current_doc}\t{count}")
        current_word = word
        current_doc = doc
        count = 1

if current_word is not None:
    print(f"{current_word}\t{current_doc}\t{count}")
