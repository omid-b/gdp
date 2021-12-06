
from . import io

def union(args):
    nof = len(args.input_files)
    input_files = args.input_files
    datlines = [[] for i in range(nof)]
    datlines_pos = [[] for i in range(nof)]
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        datlines[i] = io.dat_lines(input_files[i], args)
        for line in datlines[i]:
            datlines_pos[i].append(' '.join(line.split()[0:len(args.x)]))
    union = []
    union_pos = []
    for i in range(nof):
        nol = len(datlines_pos[i])
        for j in range(nol):
            if datlines_pos[i][j] not in union_pos:
                union.append(datlines[i][j])
                union_pos.append(datlines_pos[i][j])
    if args.inverse:
        union_inv = []
        for i in range(nof):
            nol = len(datlines[i])
            for j in range(nol):
                if datlines[i][j] not in union:
                    union_inv.append(datlines[i][j])
        io.output_lines(union_inv, args)
    else:
        io.output_lines(union, args)


def intersect(args):
    nof = len(args.input_files)
    input_files = args.input_files
    datlines = [[] for i in range(nof)]
    datlines_pos = [[] for i in range(nof)]
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        datlines[i] = io.dat_lines(input_files[i], args)
        for line in datlines[i]:
            datlines_pos[i].append(' '.join(line.split()[0:len(args.x)]))
    intersect = []
    intersect_pos = []
    nol = len(datlines[0])
    for j in range(nol):
        if all(datlines_pos[0][j] in l for l in datlines_pos[1:])\
        and datlines_pos[i][j] not in intersect_pos:
            intersect.append(datlines[0][j])
            intersect_pos.append(datlines_pos[0][j])
    if args.inverse:
        intersect_inv = []
        for i in range(nof):
            nol = len(datlines[i])
            for j in range(nol):
                line = datlines[i][j]
                if line not in intersect:
                    intersect_inv.append(line)
        io.output_lines(intersect_inv, args)
    else:
        io.output_lines(intersect, args)


def difference(args):
    nof = len(args.input_files)
    input_files = args.input_files
    datlines = [[] for i in range(nof)]
    datlines_pos = [[] for i in range(nof)]
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        datlines[i] = io.dat_lines(input_files[i], args)
        for line in datlines[i]:
            datlines_pos[i].append(' '.join(line.split()[0:len(args.x)]))
    difference = []
    difference_pos = []
    nol = len(datlines[0])
    for j in range(nol):
        if all(datlines_pos[0][j] not in l for l in datlines_pos[1:])\
        and datlines_pos[0][j] not in difference_pos:
            difference.append(datlines[0][j])
            difference_pos.append(datlines_pos[0][j])
    if args.inverse:
        difference_inv = []
        for i in range(nof):
            nol = len(datlines[i])
            for j in range(nol):
                line = datlines[i][j]
                if line not in difference:
                    difference_inv.append(line)
        io.output_lines(difference_inv, args)
    else:
        io.output_lines(difference, args)


# def difference(args):
#     nof = len(args.input_files)
#     input_files = args.input_files
#     input_files_lines = []
#     input_files_xy = [[] for i in range(nof)]
#     if nof < 2:
#         print("Error! Number of input_files should be larger than 2 for this operation.")
#         exit(1)
#     for i in range(nof):
#         input_files_lines.append(io.xyz_lines(input_files[i], args))
#         for line in input_files_lines[i]:
#             input_files_xy[i].append(' '.join(line.split()[0:2]))
#     difference = []
#     difference_xy = []
#     nol = len(input_files_lines[0])
#     for j in range(nol):
#         if all(input_files_xy[0][j] not in l for l in input_files_xy[1:])\
#         and input_files_xy[0][j] not in difference_xy:
#             difference_xy.append(input_files_xy[0][j])
#             difference.append(input_files_lines[0][j])
#     if args.inverse:
#         difference_inv = []
#         for i in range(nof):
#             nol = len(input_files_lines[i])
#             for j in range(nol):
#                 line = input_files_lines[i][j]
#                 if line not in difference:
#                     difference_inv.append(line)
#         io.output_lines(difference_inv, args)
#     else:
#         io.output_lines(difference, args)


def conv_1Dto2D(args):
    print("HELLLLOOO!!")
    pass


def conv_1Dto3D(args):
    pass


def conv_2Dto1D(args):
    pass    


def conv_2Dto3D(args):
    pass 


def conv_3Dto1D(args):
    pass 


def conv_3Dto1D(args):
    pass 


