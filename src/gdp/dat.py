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
    io.output_lines(union, args)



def intersect(args):
    nof = len(args.input_files)
    input_files = args.input_files
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    sets = []
    sets_concat = []
    for i in range(nof):
        sets.append(io.read_file_lines(input_files[i]))
        sets_concat += sets[-1]
    intersect = []
    intersect_inv = []
    for x in sets_concat:
        if all(x in l for l in sets):
            if x not in intersect:
                intersect.append(x)
        elif x not in intersect_inv:
            intersect_inv.append(x)
    if args.inverse:
        io.output_lines(intersect_inv, args)
    else:
        io.output_lines(intersect, args)




def difference(args):
    nof = len(args.input_files)
    input_files = args.input_files
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    sets = []
    sets_concat = []
    for i in range(nof):
        sets.append(io.read_file_lines(input_files[i]))
        sets_concat += sets[-1]
    difference = []
    difference_inv = []
    for x in sets_concat:
        if all(x not in l for l in sets[1:]):
            if x not in difference:
                difference.append(x)
        elif x not in difference_inv:
            difference_inv.append(x)
    if args.inverse:
        io.output_lines(difference_inv, args)
    else:
        io.output_lines(difference, args)



