import os

def read_file_lines(ascii_file):
    try:
        fopen = open(ascii_file,'r')
        lines = fopen.read().splitlines()
        fopen.close()
    except Exception as exc:
        print(f"Error reading input file: {ascii_file}\n")
        exit(1)
    return lines
