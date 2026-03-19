#!/usr/bin/env python3
import sys
from collections import defaultdict

current_word = None
doc_counts = defaultdict(int)

for line in sys.stdin:
    parts = line.strip().split("\t")
    if len(parts) != 3:
        continue

    word, doc, cnt = parts
    cnt = int(cnt)

    if current_word is not None and word != current_word:
        postings = ", ".join(f"{d}:{doc_counts[d]}" for d in sorted(doc_counts))
        print(f"{current_word} --> {postings}")
        doc_counts = defaultdict(int)

    current_word = word
    doc_counts[doc] += cnt

if current_word is not None:
    postings = ", ".join(f"{d}:{doc_counts[d]}" for d in sorted(doc_counts))
    print(f"{current_word} --> {postings}")
