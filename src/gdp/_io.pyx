

cpdef list read_file_lines(str ascii_file):
    cdef object fopen
    cpdef list lines
    try:
        fopen = open(ascii_file,'r')
        lines = fopen.read().splitlines()
        fopen.close()
    except Exception as exc:
        print(f"Error reading input file: {ascii_file}\n")
        exit(1)
    return lines


cpdef void output_lines(list lines, object args):
    cdef object fopen
    cdef str x
    lines = sorted(lines)
    if args.output:
        if args.append:
            fopen = open(args.output,'a')
        else:
            fopen = open(args.output,'w')
        for x in lines:
            fopen.write(f"{x}\n")
        fopen.close()
    else:
        for x in lines:
            print(f"{x}")



