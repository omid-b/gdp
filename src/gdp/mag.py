
from . import io
import numpy as np
from math import dist
from math import exp
from math import pow

def igrf(args):
    print("Hello from igrf!")
    exit(0)

    
def gem2dat(args):
    print("Hello from gem2dat!")
    exit(0)

    
def sphere(args):
    print("Hello from sphere!")
    exit(0)

def window_xy(data_x, data_y, min_x, max_x, min_y, max_y):
    data_x_win = []
    data_y_win = []
    for i, x in enumerate(data_x):
        y = data_y[i]
        if x >= min_x and x <= max_x and y >= min_y and y <= max_y:
            data_x_win.append(x)
            data_y_win.append(y)
    return [data_x_win, data_y_win]

#-------------------------#
def window_xyz(data_x, data_y, data_z, min_x, max_x, min_y, max_y):
    data_x_win = []
    data_y_win = []
    data_z_win = []
    for i, x in enumerate(data_x):
        y = data_y[i]
        z = data_z[i]
        if x >= min_x and x <= max_x and y >= min_y and y <= max_y:
            data_x_win.append(x)
            data_y_win.append(y)
            data_z_win.append(z)
    return [data_x_win, data_y_win, data_z_win]

#-------------------------#
def calc_nodes_smoothing(data_x, data_y, nodes_x, nodes_y, smoothfactor):
    # calculate nodes smoothing (adaptive smoothing)
    nodes_smoothing = []
    for i, xn in enumerate(nodes_x):
        yn = nodes_y[i]
        # loop through data points and find distance from this node to data points
        dists = []
        for j, xd in enumerate(data_x):
            yd = data_y[j]
            dists.append(dist([xn, yn], [xd, yd]))
        dists = sorted(dists)
        # use second closest data point distance for smoothing
        nodes_smoothing.append(dists[1] * smoothfactor) 
    return nodes_smoothing



#-------------------------#
def gridder_node_weights(x, y, data_x, data_y, smoothing):
    wgt = []
    for i, xd in enumerate(data_x):
        yd = data_y[i]
        temp = exp(-1 * (1 / pow(smoothing, 2)) * (pow(xd - x, 2) + pow(yd - y, 2)))
        if temp < smoothing:
            wgt.append(temp)
        else:
            wgt.append(0)
    return wgt

#-------------------------#
def gridder_node_value(node_weights, data_val):
    s=0
    for i, wgt in enumerate(node_weights):
        s += wgt * data_val[i]
    ret = s / np.sum(node_weights)
    return ret

#-------------------------#
def get_grid_value(x, y, data_x, data_y, data_val, smoothing):
    data_x_win, data_y_win, data_val_win = window_xyz(data_x, data_y, data_val,
                                                    x - 3*smoothing,
                                                    x + 3*smoothing,
                                                    y - 3*smoothing,
                                                    y + 3*smoothing)
    node_weights = gridder_node_weights(x, y, data_x_win, data_y_win, smoothing)
    node_val = gridder_node_value(node_weights, data_val_win)
    return node_val

#-------------------------#
def calc_dx_meshgrid_finite_difference(tmi_meshgrid, x_interval):
    nx = len(tmi_meshgrid[0])
    ny = len(tmi_meshgrid)
    dx_meshgrid = []
    for iy in range(ny):
        dx_meshgrid.append([])
        for ix in range(2, nx):
            dx_meshgrid[iy].append((tmi_meshgrid[iy][ix] - tmi_meshgrid[iy][ix-2]) / (2 * x_interval))
        dx_meshgrid[iy].append(dx_meshgrid[iy][-1])
        dx_meshgrid[iy].insert(0, dx_meshgrid[iy][0])
    return dx_meshgrid

#-------------------------#
def calc_dy_meshgrid_finite_difference(tmi_meshgrid, y_interval):
    tmi_meshgrid = np.array(tmi_meshgrid, dtype=float).transpose()
    nx = len(tmi_meshgrid[0])
    ny = len(tmi_meshgrid)
    dy_meshgrid = []
    for iy in range(ny):
        dy_meshgrid.append([])
        for ix in range(2, nx):
            dy_meshgrid[iy].append((tmi_meshgrid[iy][ix] - tmi_meshgrid[iy][ix-2]) / (2 * y_interval))
        dy_meshgrid[iy].append(dy_meshgrid[iy][-1])
        dy_meshgrid[iy].insert(0, dy_meshgrid[iy][0])
    return np.array(dy_meshgrid, dtype=float).transpose().tolist()
    
#-------------------------#
def calc_thdr_meshgrid(dx_meshgrid, dy_meshgrid):
    dx_meshgrid = np.array(dx_meshgrid, dtype=float)
    dy_meshgrid = np.array(dy_meshgrid, dtype=float)
    thdr_meshgrid = np.sqrt(dx_meshgrid**2 + dy_meshgrid**2)
    return thdr_meshgrid.tolist()


#-------------------------#
def directional_derivatives(args):
    # read input data
    [[tmi_x, tmi_y],[tmi_v], _] = io.read_numerical_data(args.input_file, args.header,
                                                         args.footer, args.fmt,
                                                         args.x, args.v, skipnan=True)
    # max gap
    if args.maxgap == 9999:
        args.maxgap = 4 * args.interval
    # find grid nodes
    min_x = np.floor(np.nanmin(tmi_x) - args.maxgap - args.interval)
    max_x = np.ceil( np.nanmax(tmi_x) + args.maxgap + args.interval)
    min_y = np.floor(np.nanmin(tmi_y) - args.maxgap - args.interval)
    max_y = np.ceil( np.nanmax(tmi_y) + args.maxgap + args.interval)
    nodes_all_x_meshgrid, nodes_all_y_meshgrid = np.meshgrid(np.arange(min_x, max_x, args.interval),
                                                 np.arange(min_y, max_y, args.interval))
    nodes_all_x = nodes_all_x_meshgrid.flatten()
    nodes_all_y = nodes_all_y_meshgrid.flatten()
    nodes_all_nx = len(nodes_all_x_meshgrid[0]) # number of uniq x nodes
    nodes_all_ny = len(nodes_all_x_meshgrid) # number of uniq y nodes
    
    # calculate adaptive smoothing values at grid nodes
    print("Calculating adaptive smoothing values ...")
    nodes_all_smth = calc_nodes_smoothing(tmi_x, tmi_y, nodes_all_x, nodes_all_y, args.smoothfactor)

    # Gridding
    print("2D interpolation (gridding) ... 1st pass (adaptive smoothing)")
    nodes_all_tmi_p1 = [] # pass 1
    for i, xn in enumerate(nodes_all_x):
        yn = nodes_all_y[i]
        # node value (adaptive smoothing)
        vn = get_grid_value(xn, yn, tmi_x, tmi_y, tmi_v, nodes_all_smth[i]) 
        nodes_all_tmi_p1.append(vn)

    if args.fixedsmoothing > 0:
        nodes_all_tmi_p2 = [] # pass 2
        print("2D interpolation (gridding) ... 2nd pass (fixed smoothing)") # for denoising purpose
        if args.fixedsmoothing == 9999:
            smoothing = args.interval
        else:
            smoothing = args.fixedsmoothing
        for i, xn in enumerate(nodes_all_x):
            yn = nodes_all_y[i]
            # node value (fixed smoothing):
            vn = get_grid_value(xn, yn, nodes_all_x, nodes_all_y, nodes_all_tmi_p1, smoothing)
            nodes_all_tmi_p2.append(vn)
        nodes_all_tmi = nodes_all_tmi_p2
    else:
        nodes_all_tmi = nodes_all_tmi_p1


    nodes_all_tmi_meshgrid = np.array(nodes_all_tmi, dtype=float).reshape(nodes_all_ny, nodes_all_nx)


    import matplotlib.pyplot as plt

    # calculate dx and dy (finite difference method)
    print("Calculating dX ...")
    nodes_all_dx_meshgrid = calc_dx_meshgrid_finite_difference(nodes_all_tmi_meshgrid, args.interval)
    print("Calculating dY ...")
    nodes_all_dy_meshgrid = calc_dy_meshgrid_finite_difference(nodes_all_tmi_meshgrid, args.interval)
    # calculate total horizontal drivatives
    print("Calculating THDR ...")
    nodes_all_thdr_meshgrid = calc_thdr_meshgrid(nodes_all_dx_meshgrid, nodes_all_dy_meshgrid)
    
    # plot (temp XXX)
    plt.figure(figsize=(12,4))
    ax1 = plt.subplot(141)
    ax1.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_tmi_meshgrid, cmap='jet')
    ax2 = plt.subplot(142)
    ax2.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dx_meshgrid, cmap='jet')
    ax3 = plt.subplot(143)
    ax3.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dy_meshgrid, cmap='jet')
    ax4 = plt.subplot(144)
    ax4.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_thdr_meshgrid, cmap='jet')
    plt.show()




