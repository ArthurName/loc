LOC
---

Purpose: To count lines of code, docstrings, comments and empty lines in Python
files. Globbing and recursion is supported.

Usage: Run on command line using the python binary, or make it executable. Run
with -h for syntax help.

Usage examples:

python loc.py /usr/lib/python2.7/glob.py
python loc.py . -rvf
python loc.py . test/ -v
python loc.py -h
