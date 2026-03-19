# The Digital Librarian — Distributed Reverse Indexing

**Big Data Analytics — Mini Project 1**  
Section 2 | Haneen Alaa `202201463` · Nehal Mohamed `202202020`

---

## What this does

Builds a reverse index over a corpus of text files using Hadoop MapReduce Streaming. For every unique word in the corpus, the output tells you which documents contain it and how many times it appears there.

```
whale --> pg2701.txt:1226, pg345.txt:3, pg1342.txt:1
```

---

## Project Structure

```
digital_librarian/
├── mapper.py        # tokenizes + filters each line, emits (word, doc)
├── combiner.py      # local aggregation before shuffle
├── reducer.py       # builds final index entries
├── stopwords.txt    # words to ignore (the, is, a, and, ...)
└── books/           # .txt files downloaded from Project Gutenberg
```

---

## Requirements

- Hadoop 3.x with Hadoop Streaming jar
- Python 3 available on all nodes
- HDFS running and accessible
- Books already placed in `~/digital_librarian/books/`

---

## Setup

### 1. Download the books

```bash
cd ~/digital_librarian/books

wget https://www.gutenberg.org/cache/epub/1342/pg1342.txt    # Pride and Prejudice
wget https://www.gutenberg.org/cache/epub/64317/pg64317.txt  # The Great Gatsby
wget https://www.gutenberg.org/cache/epub/11/pg11.txt        # Alice in Wonderland
wget https://www.gutenberg.org/cache/epub/1513/pg1513.txt    # Romeo and Juliet
wget https://www.gutenberg.org/cache/epub/37106/pg37106.txt  # The Story of My Life
wget https://www.gutenberg.org/cache/epub/45304/pg45304.txt  # The Importance of Being Earnest
wget https://www.gutenberg.org/cache/epub/2701/pg2701.txt    # Moby Dick
wget https://www.gutenberg.org/cache/epub/768/pg768.txt      # Wuthering Heights
wget https://www.gutenberg.org/cache/epub/1260/pg1260.txt    # Jane Eyre
wget https://www.gutenberg.org/cache/epub/2641/pg2641.txt    # A Room with a View
wget https://www.gutenberg.org/cache/epub/174/pg174.txt      # The Picture of Dorian Gray
wget https://www.gutenberg.org/cache/epub/100/pg100.txt      # Complete Works of Shakespeare
wget https://www.gutenberg.org/cache/epub/844/pg844.txt      # The Importance of Being Earnest (alt)
wget https://www.gutenberg.org/cache/epub/145/pg145.txt      # Middlemarch
wget https://www.gutenberg.org/cache/epub/345/pg345.txt      # Dracula
```

### 2. Upload to HDFS

```bash
hdfs dfs -mkdir -p /user/student/library
hdfs dfs -put -f ~/digital_librarian/books/*.txt /user/student/library/
```

Verify the upload:

```bash
hdfs dfs -ls /user/student/library/
```

---

## Running the Job

Make sure you're in the `digital_librarian/` directory (where the `.py` files and `stopwords.txt` live), then run:

```bash
hadoop jar /home/hadoop/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.1.jar \
  -input  /user/student/library \
  -output /user/student/output_index \
  -mapper  mapper.py \
  -combiner combiner.py \
  -reducer reducer.py \
  -file mapper.py \
  -file combiner.py \
  -file reducer.py \
  -file stopwords.txt
```

> **Note:** The `-file` flag is deprecated in newer Hadoop versions. You can use `-files` instead (generic option before `-input`). Both work.

If the output directory already exists from a previous run, delete it first:

```bash
hdfs dfs -rm -r -f /user/student/output_index
```

---

## Checking the Output

```bash
# list output files
hdfs dfs -ls /user/student/output_index/

# print first 20 lines of the index
hdfs dfs -cat /user/student/output_index/part-00000 | head -20

# search for a specific word
hdfs dfs -cat /user/student/output_index/part-00000 | grep "^whale "
```

---

## Scalability Testing

To reproduce the multi-node experiments, adjust the number of active Docker containers before each run:

```bash
# 1-node run — stop extra nodes first
sudo docker stop nodemanager2 datanode2 nodemanager3 datanode3 nodemanager4 datanode4

# 2-node run
sudo docker start datanode2 nodemanager2

# 4-node run
sudo docker start datanode2 nodemanager2 datanode3 nodemanager3 datanode4 nodemanager4
```

Wrap each job in `time` to record wall-clock duration:

```bash
time hadoop jar ... (full command above)
```

Speedup is calculated as **S = T1 / Tn** where T1 is the 1-node baseline time.

---

## How It Works

| Component | Role |
|-----------|------|
| **mapper.py** | Lowercases text, strips punctuation, filters stop words, emits `word\tdoc_name` |
| **combiner.py** | Counts consecutive identical `(word, doc)` pairs locally before the shuffle, emits `word\tdoc\tcount` — reduces network I/O by ~89.5% |
| **reducer.py** | Aggregates counts per document per word, writes final `word --> doc:freq, ...` entries |
| **stopwords.txt** | Loaded into a Python `set` at Mapper startup for O(1) per-token lookup |

---

## Notes

- The job expects Python 3 to be on `PATH` as `python3` on worker nodes. If your cluster uses `python`, update the shebang lines in the `.py` files accordingly.
- With replication factor 2 (set in `docker-compose.yml`), you need at least 2 DataNodes running or HDFS will warn about under-replicated blocks.
- All three `.py` files must be in the same directory from which you run the `hadoop jar` command, since they're distributed to workers via the `-file` flag.
