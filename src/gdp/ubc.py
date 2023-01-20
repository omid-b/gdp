#!/usr/bin/env python3

import os
from . import io

def mod2xyz(args):
    # check inputs
    if not os.path.isfile(args.mesh):
        print(f"Error! Could not find mesh file: '{args.mesh}'")
        exit(1)
    for mod in args.models:
        if not os.path.isfile(mod):
            print(f"Error! Could not find model: '{mod}'")
            exit(1)
    
    # read mesh
    X,Y,Z = read_mesh3D_xyz(args.mesh)
    nx, ny, nz = [len(X), len(Y), len(Z)]

    # read models
    nom = len(args.models) # number of models
    models = nom * [[]]
    for im in range(nom):
        fopen = open(args.models[im], 'r')
        flines = fopen.read().splitlines()
        fopen.close()
        try:
            for line in flines:
                models[im].append(float(line))
        except Exception as e:
            print(f"Model format error: '{args.models[im]}'.{e}")
            exit(1)
        if len(models[im]) != (nx * ny * nz):
            print(f"Model format error: '{args.models[im]}'.\nNumber of cells does not mtch with the input mesh.")
            exit(1)

    # output models
    args.uniq = False
    args.sort = False
    args.append = False
    for im in range(nom):
        # outdir
        if args.outdir == None:
            outdir = os.path.split(os.path.abspath(args.models[im]))[0]
        else:
            outdir = os.path.abspath(args.outdir)
            if not os.path.isdir(outdir):
                os.mkdir(outdir)
        outlines = []
        index = -1
        for ix, x in enumerate(X):
            for iy, y in enumerate(Y):
                for iz, z in enumerate(Z):
                    index += 1
                    value = models[im][index]
                    line = f"%{args.fmt[0]}f %{args.fmt[0]}f %{args.fmt[0]}f %{args.fmt[1]}f" %(x, y, z, value)
                    if args.skipdummy and value == -100.0:
                        continue
                    else:
                        outlines.append(line)
        args.outfile = os.path.join(outdir, f"{os.path.splitext(os.path.split(args.models[im])[1])[0]}.xyz")
        outlines.insert(0, f" X Y Z {args.label}")
        io.output_lines(outlines, args)
        print(args.outfile)





def read_mesh3D_xyz(mesh_file):
    # Reads UBC mesh3D and outputs [[x],[y],[z]]
    fopen = open(mesh_file,'r')
    flines = fopen.read().splitlines()
    fopen.close()
    # read nx, ny, nz
    try:
        nx, ny, nz = flines[0].split()
        nx, ny, nz = [int(nx), int(ny), int(nz)]
    except:
        print(f"Error in reading mesh3D: '{mesh_file}'. Could not obtain (nx, ny, nz) from the first line.")
        exit(1)
    # read reference point XYZ coordinates
    try:
        x0 = float(flines[1].split()[0])
        y0 = float(flines[1].split()[1])
        z0 = float(flines[1].split()[2])
    except:
        print(f"Format error: '{mesh_file}'. Could not obtain reference point coordinates (line 2).")
        exit(1)
    # read mesh{X,Y,Z}
    try:
        meshX, meshY, meshZ = [[],[],[]]
        for ix in range(nx):
            meshX.append(float(flines[2].split()[ix]))
        for iy in range(ny):
            meshY.append(float(flines[3].split()[iy]))
        for iz in range(nz):
            meshZ.append(float(flines[4].split()[iz]))
    except Exception as e:
        print(f"Error reading mesh: '{mesh_file}'.\n{e}")
        exit(1)
    # calculate X, Y, Z
    X, Y, Z = [[],[],[]]
    for ix in range(nx):
        X.append(x0 + (meshX[ix] / 2) + sum(meshX[0:ix]))
    for iy in range(ny):
        Y.append(y0 + (meshY[iy] / 2) + sum(meshY[0:iy]))
    for iz in range(nz):
        Z.append(z0 - (meshZ[iz] / 2) - sum(meshZ[0:iz]))
    return [X, Y, Z]






