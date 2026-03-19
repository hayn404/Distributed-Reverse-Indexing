#!/usr/bin/env python3
import sys
import re
import os

STOPWORDS = set()
with open("stopwords.txt", "r", encoding="utf-8") as f:
    for line in f:
        w = line.strip().lower()
        if w:
            STOPWORDS.add(w)

current_file = os.environ.get("mapreduce_map_input_file", "")
doc_name = os.path.basename(current_file) if current_file else "unknown_document"

for line in sys.stdin:
    line = line.lower()
    line = re.sub(r"[^a-z0-9\s]", " ", line)
    words = line.split()

    for word in words:
        if word and word not in STOPWORDS:
            print(f"{word}\t{doc_name}")
