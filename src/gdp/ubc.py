#!/usr/bin/env python3

import os
from . import io
from . import dat
from . import geographic

def mvi2xyz(args):
    # check inputs
    if not os.path.isfile(args.mesh):
        print(f"Error! Could not find mesh file: '{args.mesh}'")
        exit(1)
    models = []
    for mod in args.models:
        if not os.path.isfile(mod):
            print(f"Error! Could not find model: '{mod}'")
            exit(1)
        if os.path.splitext()[1].lower() not in ['.amp', '.fld', '.ind', '.rem', '.mod']:
            print(f"WARNING! Model file extension for '{os.path.basename(mod)}' is not in ['amp', 'fld', 'ind', 'rem', 'mod']; this file will be skipped!")
        else:
            fopen = open(mod, 'r')
            flines = fopen.read().splitlines()
            fopen.close()





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
    models = []
    for im in range(nom):
        model = []
        fopen = open(args.models[im], 'r')
        flines = fopen.read().splitlines()
        fopen.close()
        try:
            for line in flines:
                model.append(float(line))
        except Exception as e:
            print(f"Model format error: '{args.models[im]}'.{e}")
            exit(1)
        if len(model) != (nx * ny * nz):
            print(f"Model format error: '{args.models[im]}'.\nNumber of cells does not mtch with the input mesh.")
            exit(1)
        else:
            models.append(model)

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
                os.makedirs(outdir, exist_ok=True)
        outlines = [f" X Y Z {args.label}"]
        index = -1
        pos_cols = [[],[],[]]
        val_cols = [[]]
        for iy, y in enumerate(Y):
            for ix, x in enumerate(X):
                for iz, z in enumerate(Z):
                    index += 1
                    value = models[im][index]
                    if args.skipdummy and value == -100.0:
                        continue
                    else:
                        pos_cols[0].append(x)
                        pos_cols[1].append(y)
                        pos_cols[2].append(z)
                        val_cols[0].append(value)
                        outlines.append(f"%{args.fmt[0]}f %{args.fmt[0]}f %{args.fmt[0]}f %{args.fmt[1]}f" %(x, y, z, value))
        args.outfile = os.path.join(outdir, f"{os.path.splitext(os.path.split(args.models[im])[1])[0]}.xyz")
        args.uniq = False
        args.sort = False
        args.append = False
        # apply point-in-polygon ?
        if len(args.polygon):
            outlines = [f" X Y Z {args.label}"]
            polygons = io.return_polygon_objects(args.polygon)
            for ip in range(len(pos_cols[0])): # loop over points
                pip = True
                point = geographic.Point(pos_cols[0][ip], pos_cols[1][ip])
                for polygon in  polygons:
                    if not polygon.is_point_in(point):
                        pip = False
                if pip:
                   outlines.append(f"%{args.fmt[0]}f %{args.fmt[0]}f %{args.fmt[0]}f %{args.fmt[1]}f" \
                   %(pos_cols[0][ip], pos_cols[1][ip], pos_cols[2][ip], val_cols[0][ip]))
        io.output_lines(outlines, args)
        print(args.outfile)


def invcurves(args):
    import seaborn as sns
    import matplotlib.pyplot as plt
    invlogs = []
    for f in os.listdir(args.invdir):
        if os.path.splitext(f)[1] == '.out':
            invlogs.append(os.path.abspath(os.path.join(args.invdir, f)))
    if len(invlogs) == 0:
        print(f"Error! Could not find any '*.out' file in inversion directory: '{args.invdir}'")
        exit(0)
    invdata = []
    for logfile in invlogs:
        logdata = io.read_numerical_data(logfile, 12, 3,  ['.0','.4'], [1], range(2,12), skipnan=True)
        invdata.append({
            'iter':logdata[0][0],
            'beta':logdata[1][0],
            'data_misfit':logdata[1][1],
            'norm_s':logdata[1][2],
            'norm_e':logdata[1][3],
            'norm_n':logdata[1][4],
            'norm_z':logdata[1][5],
            'model_norm':logdata[1][6],
            'total_objective':logdata[1][7],
            'cg_iterations':logdata[1][8],
            'truncated_cells':logdata[1][9]
        })
    for i in range(len(invdata)):
        sns.set_context('notebook')
        sns.set_style('ticks')
        fig = plt.figure(figsize=(9,7))
        plt.suptitle(f'{invlogs[i]}')
        # ax1: model norm
        ax1 = fig.add_subplot(211)
        ax1.plot(invdata[i]['iter'], invdata[i]['data_misfit'], color='#4169E1')
        ax1.scatter(invdata[i]['iter'], invdata[i]['data_misfit'], s=20, c='#4169E1')
        ax1.set_xticks(range(1, int(max(invdata[i]['iter'])+1)))
        ax1.set_xlabel("Iteration")
        ax1.set_ylabel("Data misfit")
        ax1.yaxis.label.set_color('#4169E1')
        ax1.tick_params(axis='y', colors='#4169E1')
        ax1.spines['left'].set_color('#4169E1')
        # ax2: model norm
        ax2 = ax1.twinx()
        ax2.plot(invdata[i]['iter'], invdata[i]['model_norm'], color='#FF8C00')
        ax2.scatter(invdata[i]['iter'], invdata[i]['model_norm'], s=20, c='#FF8C00')
        ax2.set_xticks(range(1, int(max(invdata[i]['iter'])+1)))
        ax2.set_xlabel("Iteration")
        ax2.set_ylabel("Model Norm")
        ax2.yaxis.label.set_color('#FF8C00')
        ax2.tick_params(axis='y', colors='#FF8C00')
        ax2.spines['right'].set_color('#FF8C00')
        # ax3: L-curve
        ax3 = fig.add_subplot(212)
        ax3.plot(invdata[i]['model_norm'], invdata[i]['data_misfit'], color='#222')
        ax3.scatter(invdata[i]['model_norm'], invdata[i]['data_misfit'], s=20, c='#222')
        ax3.set_xlabel("Model Norm")
        ax3.set_ylabel("Data misfit")
        plt.tight_layout()
        # outdir
        if args.outdir == None:
            outdir = os.path.abspath(args.invdir)
            outfile = os.path.join(outdir, f'{os.path.basename(os.path.splitext(invlogs[i])[0])}.{args.ext}')
        else:
            outdir = os.path.abspath(args.outdir)
            if not os.path.isdir(outdir):
                os.makedirs(outdir, exist_ok=True)
            fname = os.path.split(os.path.split(os.path.abspath(invlogs[i]))[0])[1]\
            + '_' + os.path.basename(os.path.splitext(invlogs[i])[0])
            outfile = os.path.join(outdir, f'{fname}.{args.ext}')
        plt.savefig(outfile, dpi=args.dpi)
        plt.close()
        print(outfile)

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






