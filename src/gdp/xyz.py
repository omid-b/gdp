
from . import io

def union(args):
    nof = len(args.input_files)
    input_files = args.input_files
    input_files_lines = []
    input_files_xy = [[] for i in range(nof)]
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        input_files_lines.append(io.xyz_lines(input_files[i], args))
        for line in input_files_lines[i]:
            input_files_xy[i].append(' '.join(line.split()[0:2]))
    union_xy = []
    union = []
    for i in range(nof):
        for j, xy in enumerate(input_files_xy[i]):
            if xy not in union_xy:
                union_xy.append(xy)
                union.append(input_files_lines[i][j])
    io.output_lines(union, args)


def intersect(args):
    nof = len(args.input_files)
    input_files = args.input_files
    input_files_lines = []
    input_files_xy = [[] for i in range(nof)]
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        input_files_lines.append(io.xyz_lines(input_files[i], args))
        for line in input_files_lines[i]:
            input_files_xy[i].append(' '.join(line.split()[0:2]))
    intersect = []
    intersect_xy = []
    for i in range(nof):
        nol = len(input_files_lines[i])
        for j in range(nol):
            if all(input_files_xy[i][j] in l for l in input_files_xy)\
            and input_files_xy[i][j] not in intersect_xy:
                intersect_xy.append(input_files_xy[i][j])
                intersect.append(input_files_lines[i][j])
    if args.inverse:
        intersect_inv = []
        for i in range(nof):
            nol = len(input_files_lines[i])
            for j in range(nol):
                line = input_files_lines[i][j]
                if line not in intersect:
                    intersect_inv.append(line)
        io.output_lines(intersect_inv, args)
    else:
        io.output_lines(intersect, args)



def difference(args):
    nof = len(args.input_files)
    input_files = args.input_files
    input_files_lines = []
    input_files_xy = [[] for i in range(nof)]
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        input_files_lines.append(io.xyz_lines(input_files[i], args))
        for line in input_files_lines[i]:
            input_files_xy[i].append(' '.join(line.split()[0:2]))
    difference = []
    difference_xy = []
    nol = len(input_files_lines[0])
    for j in range(nol):
        if all(input_files_xy[0][j] not in l for l in input_files_xy[1:])\
        and input_files_xy[0][j] not in difference_xy:
            difference_xy.append(input_files_xy[0][j])
            difference.append(input_files_lines[0][j])
    if args.inverse:
        difference_inv = []
        for i in range(nof):
            nol = len(input_files_lines[i])
            for j in range(nol):
                line = input_files_lines[i][j]
                if line not in difference:
                    difference_inv.append(line)
        io.output_lines(difference_inv, args)
    else:
        io.output_lines(difference, args)


def conv_1Dto3D(args):
    










