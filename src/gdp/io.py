

def read_file_lines(ascii_file):
    try:
        fopen = open(ascii_file,'r')
        lines = fopen.read().splitlines()
        fopen.close()
    except Exception as exc:
        print(f"Error reading input file: {ascii_file}\n")
        exit(1)
    return lines


def output_lines(lines, args):
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



