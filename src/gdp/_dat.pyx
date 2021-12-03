from . import _io


def union(object args):
    cdef int nof = len(args.input_files)
    cdef list input_files = args.input_files
    cdef list union = []
    cdef list sets_concat = []
    cdef int i
    cdef str x
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        sets_concat += _io.read_file_lines(input_files[i])
    for x in sets_concat:
        if x not in union:
            union.append(x)
    _io.output_lines(union, args)



def intersect(object args):
    cdef int nof = len(args.input_files)
    cdef list input_files = args.input_files
    cdef list sets = []
    cdef list sets_concat = []
    cdef int i
    cdef list intersect = []
    cdef list intersect_inv = []
    cdef str x
    cdef list l
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        sets.append(_io.read_file_lines(input_files[i]))
        sets_concat += sets[-1]
    for x in sets_concat:
        if all(x in l for l in sets):
            if x not in intersect:
                intersect.append(x)
        elif x not in intersect_inv:
            intersect_inv.append(x)
    if args.inverse:
        _io.output_lines(intersect_inv, args)
    else:
        _io.output_lines(intersect, args)




def difference(object args):
    cdef int nof = len(args.input_files)
    cdef list input_files = args.input_files
    cdef list sets = []
    cdef list sets_concat = []
    cdef list difference = []
    cdef list difference_inv = []
    cdef str x
    cdef int i
    if nof < 2:
        print("Error! Number of input_files should be larger than 2 for this operation.")
        exit(1)
    for i in range(nof):
        sets.append(_io.read_file_lines(input_files[i]))
        sets_concat += sets[-1]
    for x in sets_concat:
        if all(x not in l for l in sets[1:]):
            if x not in difference:
                difference.append(x)
        elif x not in difference_inv:
            difference_inv.append(x)
    if args.inverse:
        _io.output_lines(difference_inv, args)
    else:
        _io.output_lines(difference, args)



