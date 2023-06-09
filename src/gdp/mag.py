
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
def calc_thd_meshgrid(dx_meshgrid, dy_meshgrid):
    dx_meshgrid = np.array(dx_meshgrid, dtype=float)
    dy_meshgrid = np.array(dy_meshgrid, dtype=float)
    thd_meshgrid = np.sqrt(dx_meshgrid**2 + dy_meshgrid**2)
    return thd_meshgrid.tolist()

#-------------------------#
def calc_as_meshgrid(dx_meshgrid, dy_meshgrid, dz_meshgrid):
    dx_meshgrid = np.array(dx_meshgrid, dtype=float)
    dy_meshgrid = np.array(dy_meshgrid, dtype=float)
    dz_meshgrid = np.array(dz_meshgrid, dtype=float)
    as_meshgrid = np.sqrt(dx_meshgrid**2 + dy_meshgrid**2 + dz_meshgrid**2)
    return as_meshgrid.tolist()

#-------------------------#
def calc_tdr_meshgrid(dz_meshgrid, thd_meshgrid):
    dz_meshgrid = np.array(dz_meshgrid, dtype=float)
    thd_meshgrid = np.array(thd_meshgrid, dtype=float)
    tdr_meshgrid = np.arctan2(dz_meshgrid, thd_meshgrid)
    return tdr_meshgrid.tolist()

#-------------------------#
def calc_tdx_meshgrid(dz_meshgrid, thd_meshgrid):
    dz_meshgrid = np.array(dz_meshgrid, dtype=float)
    thd_meshgrid = np.array(thd_meshgrid, dtype=float)
    tdr_meshgrid = np.arctan2(thd_meshgrid, dz_meshgrid)
    return tdr_meshgrid.tolist()


#-------------------------#
def calc_theta_meshgrid(thd_meshgrid, as_meshgrid):
    thd_meshgrid = np.array(thd_meshgrid, dtype=float)
    as_meshgrid = np.array(as_meshgrid, dtype=float)
    theta_meshgrid = thd_meshgrid / as_meshgrid
    return theta_meshgrid.tolist()

#-------------------------#
def calc_ethd_meshgrid(dz_meshgrid, thd_meshgrid, xSpacing, ySpacing):
    dz_meshgrid = np.array(dz_meshgrid, dtype=float)
    thd_meshgrid = np.array(thd_meshgrid, dtype=float)
    k = np.sqrt(xSpacing**2 + ySpacing**2)
    etdr = np.arctan2(k*dz_meshgrid, thd_meshgrid)
    ethd = np.sqrt(
        calc_dx_meshgrid(etdr, xSpacing)**2 +\
        calc_dy_meshgrid(etdr, ySpacing)**2
    )
    return ethd.tolist()


#-------------------------#
def calc_etdr_meshgrid(dz_meshgrid, thd_meshgrid, xSpacing, ySpacing):
    dz_meshgrid = np.array(dz_meshgrid, dtype=float)
    thd_meshgrid = np.array(thd_meshgrid, dtype=float)
    k = np.sqrt(xSpacing**2 + ySpacing**2)
    etdr = np.arctan2(k*dz_meshgrid, thd_meshgrid)
    return etdr.tolist()



#-------------------------#
def calc_dx_meshgrid(data_meshgrid, x_interval, method="fdiff"):
    if method=="fdiff":
        dx_meshgrid = np.gradient(data_meshgrid, x_interval, axis=1)
    elif method=="fft":
        from scipy.fft import fft2, ifft2
        # Perform 2D Fourier Transform
        fft_data = fft2(data_meshgrid)
        # Determine wave numbers in x and y directions
        ny, nx = data_meshgrid.shape
        wave_numbers_x = 2 * np.pi * np.fft.fftfreq(nx, d=x_interval)
        # Reshape wave numbers to match the shape of fft_data
        wave_numbers_x_reshaped = wave_numbers_x.reshape(1, nx)
        # multiply by iKx to get dX data
        fft_data *= 1j*wave_numbers_x_reshaped
        # Perform Inverse 2D Fourier Transform
        dx_meshgrid = np.real(ifft2(fft_data))
    return dx_meshgrid

#-------------------------#
def calc_dy_meshgrid(data_meshgrid, y_interval, method="fdiff"):
    if method=="fdiff":
        dy_meshgrid = np.gradient(data_meshgrid, y_interval, axis=0)
    elif method=="fft":
        from scipy.fft import fft2, ifft2
        # Perform 2D Fourier Transform
        fft_data = fft2(data_meshgrid)
        # Determine wave numbers in x and y directions
        ny, nx = data_meshgrid.shape
        wave_numbers_y = 2 * np.pi * np.fft.fftfreq(ny, d=y_interval)
        # Reshape wave numbers to match the shape of fft_data
        wave_numbers_y_reshaped = wave_numbers_y.reshape(ny, 1)
        # multiply by iKy to get dY data
        fft_data *= 1j*wave_numbers_y_reshaped
        # Perform Inverse 2D Fourier Transform
        dy_meshgrid = np.real(ifft2(fft_data))
    return dy_meshgrid


#-------------------------#
def calc_upward_meshgrid(data_meshgrid, grid_spacing_x, grid_spacing_y, delta_z):
    from scipy.fft import fft2, ifft2
    # Perform 2D Fourier Transform
    fft_data = fft2(data_meshgrid)
    # Determine wave numbers in x and y directions
    ny, nx = data_meshgrid.shape
    wave_numbers_x = 2 * np.pi * np.fft.fftfreq(nx, d=grid_spacing_x)
    wave_numbers_y = 2 * np.pi * np.fft.fftfreq(ny, d=grid_spacing_y)
    # Reshape wave numbers to match the shape of fft_data
    wave_numbers_x_reshaped = wave_numbers_x.reshape(1, nx)
    wave_numbers_y_reshaped = wave_numbers_y.reshape(ny, 1)
    wave_numbers_2D = np.sqrt(
                              np.power(wave_numbers_x_reshaped,2) +\
                              np.power(wave_numbers_y_reshaped,2)\
                      )
    # multiply by exp(-1 * delta_z * K) to get upwarded data
    fft_data *= np.exp(-1 * delta_z * wave_numbers_2D)
    # Perform Inverse 2D Fourier Transform
    upwarded_data = np.real(ifft2(fft_data))
    return upwarded_data

#-------------------------#
def calc_dz_meshgrid(data_meshgrid, grid_spacing_x, grid_spacing_y, method="fft", order=1):
    if method=="fft":
        from scipy.fft import fft2, ifft2
        # Perform 2D Fourier Transform
        fft_data = fft2(data_meshgrid)
        # Determine wave numbers in x and y directions
        ny, nx = data_meshgrid.shape
        wave_numbers_x = 2 * np.pi * np.fft.fftfreq(nx, d=grid_spacing_x)
        wave_numbers_y = 2 * np.pi * np.fft.fftfreq(ny, d=grid_spacing_y)
        # Reshape wave numbers to match the shape of fft_data
        wave_numbers_x_reshaped = wave_numbers_x.reshape(1, nx)
        wave_numbers_y_reshaped = wave_numbers_y.reshape(ny, 1)
        wave_numbers_2D = np.sqrt(
                                  np.power(wave_numbers_x_reshaped,2) +\
                                  np.power(wave_numbers_y_reshaped,2)\
                          )
        # Multiply Fourier coefficients by wave numbers in the x and y directions to get VD
        fft_data *= wave_numbers_2D ** order
        # Perform Inverse 2D Fourier Transform
        vertical_derivative = np.real(ifft2(fft_data))
    elif method=="fdiff":
        upward_amount = np.min([grid_spacing_x, grid_spacing_y]) / 10
        data_meshgrid_upward = calc_upward_meshgrid(data_meshgrid, grid_spacing_x, grid_spacing_y, upward_amount)
        vertical_derivative = (np.array(data_meshgrid, dtype=float) - np.array(data_meshgrid_upward, dtype=float)) / upward_amount
        vertical_derivative = vertical_derivative.tolist()
    return vertical_derivative

#-------------------------#
def calc_polygon_mask(polygon_x, polygon_y, nodes_meshgrid_x, nodes_meshgrid_y):
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        try:
            from . import _geographic as geographic
        except ImportError:
            print("WARNING! Could not use cythonized module: geographic")
            from . import geographic

    ny, nx = nodes_meshgrid_x.shape
    nodes_meshgrid_mask = np.multiply(np.nan, nodes_meshgrid_x)
    for ix in range(nx):
        for iy in range(ny):
            xn = nodes_meshgrid_x[iy][ix]
            yn = nodes_meshgrid_y[iy][ix]
            point = geographic.Point(xn, yn)
            polygon = geographic.Polygon(polygon_x, polygon_y)
            is_pip = polygon.is_point_in(point)
            if is_pip:
                nodes_meshgrid_mask[iy][ix] = 1.0
    return nodes_meshgrid_mask

#-------------------------#
def calc_maxgap_mask(tmi_data_x, tmi_data_y, nodes_meshgrid_x, nodes_meshgrid_y, maxgap):
    ny, nx = nodes_meshgrid_x.shape
    nodes_meshgrid_mask = np.multiply(np.nan, nodes_meshgrid_x)
    for ix in range(nx):
        for iy in range(ny):
            xn = nodes_meshgrid_x[iy][ix]
            yn = nodes_meshgrid_y[iy][ix]
            for idata, data_x in enumerate(tmi_data_x):
                data_y = tmi_data_y[idata]
                if dist([xn, yn], [data_x, data_y]) <= maxgap:
                    nodes_meshgrid_mask[iy][ix]=1.0
                    break
    return nodes_meshgrid_mask


#-------------------------#
def directional_derivatives(args):
    from alphashape import alphashape

    print("Reading input data ...")
    # read input data
    [[tmi_x, tmi_y],[tmi_v], _] = io.read_numerical_data(args.input_file, args.header,
                                                         args.footer, args.fmt,
                                                         args.x, args.v, skipnan=True)
    tmi_points = np.vstack((tmi_x, tmi_y)).T

    
    # max gap
    if args.maxgap == 9999:
        args.maxgap = 2 * args.interval
    elif args.maxgap <= 0:
        print("Error: Parameter 'maxgap' must be a positive value")
        exit(1)
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
    if args.fixedsmoothing == 0:
        print("Interpolation (2D Gridding) ... (adaptive smoothing)")
    else:
        print("Interpolation (2D Gridding) ... (1st pass: adaptive smoothing)")
    nodes_all_tmi_p1 = [] # pass 1
    for i, xn in enumerate(nodes_all_x):
        yn = nodes_all_y[i]
        # node value (adaptive smoothing)
        vn = get_grid_value(xn, yn, tmi_x, tmi_y, tmi_v, nodes_all_smth[i]) 
        nodes_all_tmi_p1.append(vn)

    if args.fixedsmoothing > 0:
        nodes_all_tmi_p2 = [] # pass 2
        print("Interpolation (2D Gridding) ... (2nd pass: fixed smoothing)") # for denoising purpose
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

    # calculate mask
    print("Calculating polygon and maxgap masks  ...")
    polygon = alphashape(tmi_points, 0.5) # prefer a relatively smooth bounding polygon
    if polygon.is_empty:
        polygon = alphashape(tmi_points, 0.0)
    polygon_x, polygon_y = polygon.exterior.xy
    polygon_x, polygon_y = polygon_x.tolist(), polygon_y.tolist()
    polygon_mask = calc_polygon_mask(polygon_x, polygon_y, nodes_all_x_meshgrid, nodes_all_y_meshgrid)
    maxgap_mask = calc_maxgap_mask(tmi_x, tmi_y, nodes_all_x_meshgrid, nodes_all_y_meshgrid, args.maxgap)
    mask_final = np.multiply(polygon_mask, maxgap_mask)


    print("Calculating 1st horizontal derivative along X-axis (dX) ...")
    nodes_all_dx_meshgrid = calc_dx_meshgrid(nodes_all_tmi_meshgrid, args.interval, method=args.hdmethod)

    print("Calculating 1st horizontal derivative along Y-axis (dY) ...")
    nodes_all_dy_meshgrid = calc_dy_meshgrid(nodes_all_tmi_meshgrid, args.interval, method=args.hdmethod)

    print("Calculating 1st vertical derivative (dZ) ...")
    nodes_all_dz_meshgrid_fft = calc_dz_meshgrid(nodes_all_tmi_meshgrid, args.interval, args.interval, method="fft")
    nodes_all_dz_meshgrid_fdiff = calc_dz_meshgrid(nodes_all_tmi_meshgrid, args.interval, args.interval, method="fdiff")

    nodes_all_dz_meshgrid = calc_dz_meshgrid(nodes_all_tmi_meshgrid, args.interval, args.interval, method=args.vdmethod)

    print("Calculating Total Horizontal Derivative (THD) ...")
    nodes_all_thd_meshgrid = calc_thd_meshgrid(nodes_all_dx_meshgrid, nodes_all_dy_meshgrid)
    
    print("Calculating Analytic Signal (AS) ...")
    nodes_all_as_meshgrid = calc_as_meshgrid(nodes_all_dx_meshgrid, nodes_all_dy_meshgrid, nodes_all_dz_meshgrid)
    
    print("Calculating Tilt Derivative (TDR) ...")
    nodes_all_tdr_meshgrid = calc_tdr_meshgrid(nodes_all_dz_meshgrid, nodes_all_thd_meshgrid)

    print("Calculating Horizontal Tilt Angle (TDX) ...")
    nodes_all_tdx_meshgrid = calc_tdx_meshgrid(nodes_all_dz_meshgrid, nodes_all_thd_meshgrid)

    print("Calculating Enhanced TDR (ETDR) ...")
    nodes_all_etdr_meshgrid = calc_etdr_meshgrid(nodes_all_dz_meshgrid, nodes_all_thd_meshgrid, args.interval, args.interval)

    print("Calculating Enhanced THD (ETHD) ...")
    nodes_all_ethd_meshgrid = calc_ethd_meshgrid(nodes_all_dz_meshgrid, nodes_all_thd_meshgrid, args.interval, args.interval)

    print("Calculating Theta Map (Theta) ...")
    nodes_all_theta_meshgrid = calc_theta_meshgrid(nodes_all_thd_meshgrid, nodes_all_as_meshgrid)

    print("Calculating THD of TDR (THDTDR) ...")
    nodes_all_thdtdr_meshgrid = calc_thd_meshgrid(
        calc_dx_meshgrid(nodes_all_tdr_meshgrid, args.interval, method="fdiff"),
        calc_dy_meshgrid(nodes_all_tdr_meshgrid, args.interval, method="fdiff"))


    # apply final mask to the main meshgrids
    nodes_all_tmi_meshgrid = np.multiply(mask_final, nodes_all_tmi_meshgrid)
    nodes_all_dx_meshgrid = np.multiply(mask_final, nodes_all_dx_meshgrid)
    nodes_all_dy_meshgrid = np.multiply(mask_final, nodes_all_dy_meshgrid)
    nodes_all_dz_meshgrid = np.multiply(mask_final, nodes_all_dz_meshgrid)
    nodes_all_dz_meshgrid_fft = np.multiply(mask_final, nodes_all_dz_meshgrid_fft)
    nodes_all_dz_meshgrid_fdiff = np.multiply(mask_final, nodes_all_dz_meshgrid_fdiff)
    nodes_all_thd_meshgrid = np.multiply(mask_final, nodes_all_thd_meshgrid)
    nodes_all_as_meshgrid = np.multiply(mask_final, nodes_all_as_meshgrid)
    nodes_all_tdr_meshgrid = np.multiply(mask_final, nodes_all_tdr_meshgrid)
    nodes_all_tdx_meshgrid = np.multiply(mask_final, nodes_all_tdx_meshgrid)
    nodes_all_etdr_meshgrid = np.multiply(mask_final, nodes_all_etdr_meshgrid)
    nodes_all_ethd_meshgrid = np.multiply(mask_final, nodes_all_ethd_meshgrid)
    nodes_all_theta_meshgrid = np.multiply(mask_final, nodes_all_theta_meshgrid)
    nodes_all_thdtdr_meshgrid = np.multiply(mask_final, nodes_all_thdtdr_meshgrid)

    # plot (temp XXX; shading options: auto, nearest, gouraud )
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(10,10))

    ax1 = fig.add_subplot(3, 4, 1)
    ax1.set_title("Input Data")
    pc1=ax1.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_tmi_meshgrid,
     cmap='jet', shading='nearest')
    fig.colorbar(pc1)
    
    ax2 = fig.add_subplot(3, 4, 2)
    ax2.set_title(f"dX ({args.hdmethod})")
    pc2=ax2.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dx_meshgrid,
     cmap='jet', shading='nearest')
    fig.colorbar(pc2)

    ax3 = fig.add_subplot(3, 4, 3)
    ax3.set_title(f"dY ({args.hdmethod})")
    pc3=ax3.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dy_meshgrid,
     cmap='jet', shading='nearest')
    fig.colorbar(pc3)
    
    ax4 = fig.add_subplot(3, 4, 4)
    ax4.set_title("THD")
    pc4=ax4.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_thd_meshgrid,
     cmap='jet', shading='nearest')
    fig.colorbar(pc4)

    ax5 = fig.add_subplot(3, 4, 5)
    ax5.set_title("dZ (fft)")
    pc5=ax5.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dz_meshgrid_fft,
     cmap='jet', shading='nearest')
    fig.colorbar(pc5)

    ax6 = fig.add_subplot(3, 4, 6)
    ax6.set_title("dZ (fdiff)")
    pc6=ax6.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dz_meshgrid_fdiff,
     cmap='jet', shading='nearest')
    fig.colorbar(pc6)

    ax8 = fig.add_subplot(3, 4, 8)
    ax8.set_title("AS")
    pc8=ax8.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_as_meshgrid,
     cmap='jet', shading='nearest')
    fig.colorbar(pc8)

    ax9 = fig.add_subplot(3, 4, 9)
    ax9.set_title("TDR")
    pc9=ax9.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_tdr_meshgrid,
     cmap='jet', shading='nearest')
    fig.colorbar(pc9)

    ax10 = fig.add_subplot(3, 4, 10)
    ax10.set_title("ETDR")
    pc10=ax10.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_etdr_meshgrid,
     cmap='jet', shading='nearest')
    fig.colorbar(pc10)

    ax11 = fig.add_subplot(3, 4, 11)
    ax11.set_title("ETHD")
    pc11=ax11.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_ethd_meshgrid,
     cmap='jet', shading='nearest')
    fig.colorbar(pc11)

    ax12 = fig.add_subplot(3, 4, 12)
    ax12.set_title("Theta")
    pc12=ax12.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_theta_meshgrid,
     cmap='jet', shading='nearest')
    fig.colorbar(pc12)

    
    plt.tight_layout()
    plt.show()




