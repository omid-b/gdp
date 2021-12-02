from . import io


def union(args):
    nof = len(args.input_files)
    input_files = args.input_files
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    sets_concat = []
    for i in range(nof):
        sets_concat += io.read_file_lines(input_files[i])
    union = []
    for x in sets_concat:
        if x not in union:
            union.append(x)
    union = sorted(union)
    if args.output:
        if args.append:
            fopen = open(args.output,'a')
        else:
            fopen = open(args.output,'w')
        for x in union:
            fopen.write(f"{x}\n")
        fopen.close()
    else:
        for x in union:
            print(f"{x}")
    exit(0)


def intersect(args):
    nof = len(args.input_files)
    input_files = args.input_files
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)


def difference(args):
    nof = len(args.input_files)
    input_files = args.input_files
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
