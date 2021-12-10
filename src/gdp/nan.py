from . import io


def union(args):
    nof = len(args.input_files)
    input_files = args.input_files
    datlines = [[] for i in range(nof)]
    union = []
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        datlines[i] = io.data_lines(input_files[i],args)
        nol = len(datlines[i])
        for j in range(nol):
            if datlines[i][j] not in union:
                union.append(datlines[i][j])
    if args.inverse:
        union_inv = []
        for i in range(nof):
            nol = len(args.input_files)
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
    intersect = []
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    ###
    for i in range(nof):
        datlines[i] = io.data_lines(input_files[i],args)
    nol = len(datlines[0])
    for j in range(nol):
        if all(datlines[0][j] in l for l in datlines[1:]):
            intersect.append(datlines[0][j])
    ###
    if args.inverse:
        intersect_inv = []
        for i in range(nof):
            nol = len(datlines[i])
            for j in range(nol):
                if datlines[i][j] not in intersect:
                    intersect_inv.append(datlines[i][j])
        io.output_lines(intersect_inv, args)
    else:
        io.output_lines(intersect, args)





def difference(args):
    nof = len(args.input_files)
    input_files = args.input_files
    datlines = [[] for i in range(nof)]
    difference = []
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    ###
    for i in range(nof):
        datlines[i] = io.data_lines(input_files[i],args)
    nol = len(datlines[0])
    for j in range(nol):
        if all(datlines[0][j] not in l for l in datlines[1:]):
            difference.append(datlines[0][j])
    ###
    if args.inverse:
        difference_inv = []
        for i in range(nof):
            nol = len(datlines[i])
            for j in range(nol):
                if datlines[i][j] not in difference:
                    difference_inv.append(datlines[i][j])
        io.output_lines(difference_inv, args)
    else:
        io.output_lines(difference, args)



