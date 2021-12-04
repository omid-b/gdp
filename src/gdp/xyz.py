

def read_pollygon_dat(datfile, header, x=1, y=2):
    x += -1
    y += -1
    try:
        fopen = open(datfile, 'r')
        datlines = fopen.read().splitlines()[header:]
        fopen.close()
    except Exception as exc:
        print(exc)
        exit(0)
    try:
        lon = []
        lat = []
        for line in datlines:
            lon.append(line.split()[x])
            lat.append(line.split()[y])
