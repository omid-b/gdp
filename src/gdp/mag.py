
import os
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
def calc_thd_meshgrid(dx_meshgrid, dy_meshgrid):
    dx_meshgrid = np.array(dx_meshgrid, dtype=float)
    dy_meshgrid = np.array(dy_meshgrid, dtype=float)
    thd_meshgrid = np.sqrt(dx_meshgrid**2 + dy_meshgrid**2)
    return thd_meshgrid

#-------------------------#
def calc_as_meshgrid(dx_meshgrid, dy_meshgrid, dz_meshgrid):
    dx_meshgrid = np.array(dx_meshgrid, dtype=float)
    dy_meshgrid = np.array(dy_meshgrid, dtype=float)
    dz_meshgrid = np.array(dz_meshgrid, dtype=float)
    as_meshgrid = np.sqrt(dx_meshgrid**2 + dy_meshgrid**2 + dz_meshgrid**2)
    return as_meshgrid

#-------------------------#
def calc_tdr_meshgrid(dz_meshgrid, thd_meshgrid):
    dz_meshgrid = np.array(dz_meshgrid, dtype=float)
    thd_meshgrid = np.array(thd_meshgrid, dtype=float)
    tdr_meshgrid = np.arctan2(dz_meshgrid, thd_meshgrid)
    return tdr_meshgrid

#-------------------------#
def calc_tdx_meshgrid(dz_meshgrid, thd_meshgrid):
    dz_meshgrid = np.array(dz_meshgrid, dtype=float)
    thd_meshgrid = np.array(thd_meshgrid, dtype=float)
    tdr_meshgrid = np.arctan2(thd_meshgrid, dz_meshgrid)
    return tdr_meshgrid


#-------------------------#
def calc_theta_meshgrid(thd_meshgrid, as_meshgrid):
    thd_meshgrid = np.array(thd_meshgrid, dtype=float)
    as_meshgrid = np.array(as_meshgrid, dtype=float)
    theta_meshgrid = thd_meshgrid / as_meshgrid
    return theta_meshgrid

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
    return ethd


#-------------------------#
def calc_etdr_meshgrid(dz_meshgrid, thd_meshgrid, xSpacing, ySpacing):
    dz_meshgrid = np.array(dz_meshgrid, dtype=float)
    thd_meshgrid = np.array(thd_meshgrid, dtype=float)
    k = np.sqrt(xSpacing**2 + ySpacing**2)
    etdr = np.arctan2(k*dz_meshgrid, thd_meshgrid)
    return etdr



#-------------------------#
def calc_dx_meshgrid(data_meshgrid, mesh_interval, order=1, method="fdiff", rfactor=1):
    # input data must be already gridded and in 2D meshgrid format
    if method=="fdiff":
        dx_meshgrid = np.gradient(data_meshgrid, mesh_interval, axis=1)
        if order > 1:
            i = 2
            while i<=order:
                dx_meshgrid = np.gradient(dx_meshgrid, mesh_interval, axis=1)
                i += 1
    elif method=="fft":
        from scipy.fft import fft2, ifft2
        # Perform 2D Fourier Transform
        fft_data = fft2(data_meshgrid)
        # Determine wave numbers in x and y directions
        ny, nx = data_meshgrid.shape
        wave_numbers_x = 2 * np.pi * np.fft.fftfreq(nx, d=mesh_interval)
        # Reshape wave numbers to match the shape of fft_data
        wave_numbers_x_reshaped = wave_numbers_x.reshape(1, nx)
        # multiply by iKx to get dX data
        fft_data *= (1j*wave_numbers_x_reshaped)**order
        # Perform Inverse 2D Fourier Transform
        dx_meshgrid = np.real(ifft2(fft_data))
    elif method=="rfft":
        from scipy.fft import fft2, ifft2, fftshift
        # Perform 2D Fourier Transform and calculate Power Spectrum
        fft_data = fft2(data_meshgrid)
        fft_data_shifted = fftshift(fft_data)
        power_spectrum = np.abs(fft_data_shifted) ** 2
        # Determine wave numbers in x and y directions
        ny, nx = data_meshgrid.shape
        wave_numbers_x = 2 * np.pi * np.fft.fftfreq(nx, d=mesh_interval)
        # Reshape wave numbers to match the shape of fft_data
        wave_numbers_x_reshaped = wave_numbers_x.reshape(1, nx)
        # Calculate Regularization parameter 
        data_meshgrid_dx = calc_dx_meshgrid(data_meshgrid, mesh_interval, order=2, method="fft")
        data_meshgrid_dy = calc_dy_meshgrid(data_meshgrid, mesh_interval, order=2, method="fft")
        # 2nd order total horizontal derivative
        data_meshgrid_thd = calc_thd_meshgrid(data_meshgrid_dx, data_meshgrid_dy)

        alpha = rfactor * np.std(data_meshgrid_thd) * np.median(power_spectrum)

        regparam = 1 / (1 + alpha * ((wave_numbers_x_reshaped) ** (order + 1)))

        # Multiply Fourier coefficients by the wave number and regularization parameter
        fft_data *= regparam * ((1j*wave_numbers_x_reshaped) ** order)
        # Perform Inverse 2D Fourier Transform
        dx_meshgrid = np.real(ifft2(fft_data))
    return dx_meshgrid

#-------------------------#
def calc_dy_meshgrid(data_meshgrid, mesh_interval, order=1, method="fdiff", rfactor=1):
    if method=="fdiff":
        dy_meshgrid = np.gradient(data_meshgrid, mesh_interval, axis=0)
        if order > 1:
            i = 2
            while i<=order:
                dy_meshgrid = np.gradient(dy_meshgrid, mesh_interval, axis=0)
                i += 1
    elif method=="fft":
        from scipy.fft import fft2, ifft2
        # Perform 2D Fourier Transform
        fft_data = fft2(data_meshgrid)
        # Determine wave numbers in x and y directions
        ny, nx = data_meshgrid.shape
        wave_numbers_y = 2 * np.pi * np.fft.fftfreq(ny, d=mesh_interval)
        # Reshape wave numbers to match the shape of fft_data
        wave_numbers_y_reshaped = wave_numbers_y.reshape(ny, 1)
        # multiply by iKy to get dY data
        fft_data *= (1j*wave_numbers_y_reshaped)**order
        # Perform Inverse 2D Fourier Transform
        dy_meshgrid = np.real(ifft2(fft_data))
    elif method=="rfft":
        from scipy.fft import fft2, ifft2, fftshift
        # Perform 2D Fourier Transform and calculate Power Spectrum
        fft_data = fft2(data_meshgrid)
        fft_data_shifted = fftshift(fft_data)
        power_spectrum = np.abs(fft_data_shifted) ** 2
        # Determine wave numbers in x and y directions
        ny, nx = data_meshgrid.shape
        wave_numbers_y = 2 * np.pi * np.fft.fftfreq(ny, d=mesh_interval)
        # Reshape wave numbers to match the shape of fft_data
        wave_numbers_y_reshaped = wave_numbers_y.reshape(ny, 1)
        # Calculate Regularization parameter 
        data_meshgrid_dx = calc_dx_meshgrid(data_meshgrid, mesh_interval, order=2, method="fft")
        data_meshgrid_dy = calc_dy_meshgrid(data_meshgrid, mesh_interval, order=2, method="fft")
        # 2nd order total horizontal derivative
        data_meshgrid_thd = calc_thd_meshgrid(data_meshgrid_dx, data_meshgrid_dy)

        alpha = rfactor * np.std(data_meshgrid_thd) * np.median(power_spectrum)

        regparam = 1 / (1 + alpha * ((wave_numbers_y_reshaped) ** (order + 1)))

        # Multiply Fourier coefficients by the wave number and regularization parameter
        fft_data *= regparam * ((1j*wave_numbers_y_reshaped) ** order)
        # Perform Inverse 2D Fourier Transform
        dy_meshgrid = np.real(ifft2(fft_data))
    return dy_meshgrid



#-------------------------#
def calc_dz_meshgrid(data_meshgrid, mesh_interval, method="fft", order=1, rfactor=1):
    if method=="fft":
        from scipy.fft import fft2, ifft2
        # Perform 2D Fourier Transform
        fft_data = fft2(data_meshgrid)
        # Determine wave numbers in x and y directions
        ny, nx = data_meshgrid.shape
        wave_numbers_x = 2 * np.pi * np.fft.fftfreq(nx, d=mesh_interval)
        wave_numbers_y = 2 * np.pi * np.fft.fftfreq(ny, d=mesh_interval)
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
    elif method=="rfft":
        from scipy.fft import fft2, ifft2, fftshift
        # Perform 2D Fourier Transform and calculate Power Spectrum
        fft_data = fft2(data_meshgrid)
        fft_data_shifted = fftshift(fft_data)
        power_spectrum = np.abs(fft_data_shifted) ** 2
        # Determine wave numbers in x and y directions
        ny, nx = data_meshgrid.shape
        wave_numbers_x = 2 * np.pi * np.fft.fftfreq(nx, d=mesh_interval)
        wave_numbers_y = 2 * np.pi * np.fft.fftfreq(ny, d=mesh_interval)
        # Reshape wave numbers to match the shape of fft_data
        wave_numbers_x_reshaped = wave_numbers_x.reshape(1, nx)
        wave_numbers_y_reshaped = wave_numbers_y.reshape(ny, 1)
        wave_numbers_2D = np.sqrt(
                                  np.power(wave_numbers_x_reshaped,2) +\
                                  np.power(wave_numbers_y_reshaped,2)\
                          )
        # Calculate Regularization parameter 
        data_meshgrid_dx = calc_dx_meshgrid(data_meshgrid, mesh_interval, order=2, method="fft")
        data_meshgrid_dy = calc_dy_meshgrid(data_meshgrid, mesh_interval, order=2, method="fft")
        # 2nd order total horizontal derivative
        data_meshgrid_thd = calc_thd_meshgrid(data_meshgrid_dx, data_meshgrid_dy)

        alpha = rfactor * np.std(data_meshgrid_thd) * np.median(power_spectrum)


        regparam = 1 / (1 + alpha * (wave_numbers_2D ** (order + 1)))

        # Multiply Fourier coefficients by the wave number and regularization parameter
        fft_data *= regparam * (wave_numbers_2D ** order)
        # Perform Inverse 2D Fourier Transform
        vertical_derivative = np.real(ifft2(fft_data))
    elif method=="fdiff":
        upward_amount = mesh_interval / 10
        data_meshgrid_upward = calc_upward_meshgrid(data_meshgrid, mesh_interval, mesh_interval, upward_amount)
        vertical_derivative = (np.array(data_meshgrid, dtype=float) - np.array(data_meshgrid_upward, dtype=float)) / upward_amount
    return vertical_derivative

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
def calc_maxgap_mask(mag_data_x, mag_data_y, nodes_meshgrid_x, nodes_meshgrid_y, maxgap):
    ny, nx = nodes_meshgrid_x.shape
    nodes_meshgrid_mask = np.multiply(np.nan, nodes_meshgrid_x)
    for ix in range(nx):
        for iy in range(ny):
            xn = nodes_meshgrid_x[iy][ix]
            yn = nodes_meshgrid_y[iy][ix]
            indices = np.where( (mag_data_x >= (xn-maxgap)) &\
                                (mag_data_x <= (xn+maxgap)) &\
                                (mag_data_y >= (yn-maxgap)) &\
                                (mag_data_y <= (yn+maxgap)) )
            mag_data_x_win = mag_data_x[indices]
            mag_data_y_win = mag_data_y[indices]
            for idata, data_x in enumerate(mag_data_x_win):
                data_y = mag_data_y_win[idata]
                if dist([xn, yn], [data_x, data_y]) <= maxgap:
                    nodes_meshgrid_mask[iy][ix]=1.0
                    break
    return nodes_meshgrid_mask


#-------------------------#
def directional_derivatives(args):
    from alphashape import alphashape
    
    # JUST FOR TEST!
    # Cython tests
    # try: 
    #     from . import _funcs as funcs
    # except ImportError:
    #     print("WARNING! Could not use cythonized module: funcs")
    #     from . import funcs

    from . import funcs # non-cythonized version was faster!

    print("Reading input data ...")
    # read input data
    [[mag_x, mag_y],[mag_v], _] = io.read_numerical_data(args.input_file, args.header,
                                                         args.footer, args.fmt,
                                                         args.x, args.v, skipnan=True)
    mag_points = np.vstack((mag_x, mag_y)).T
    
    # max gap
    if args.maxgap == 9999:
        args.maxgap = 2 * args.interval
    elif args.maxgap <= 0:
        print("Error: Parameter 'maxgap' must be a positive value")
        exit(1)
    # find grid nodes
    min_x = np.floor(np.nanmin(mag_x) - args.maxgap - args.interval)
    max_x = np.ceil( np.nanmax(mag_x) + args.maxgap + args.interval)
    min_y = np.floor(np.nanmin(mag_y) - args.maxgap - args.interval)
    max_y = np.ceil( np.nanmax(mag_y) + args.maxgap + args.interval)
    nodes_all_x_meshgrid, nodes_all_y_meshgrid = np.meshgrid(np.arange(min_x, max_x, args.interval),
                                                             np.arange(min_y, max_y, args.interval))

    nodes_all_x = nodes_all_x_meshgrid.flatten()
    nodes_all_y = nodes_all_y_meshgrid.flatten()
    nodes_all_nx = len(nodes_all_x_meshgrid[0]) # number of uniq x nodes
    nodes_all_ny = len(nodes_all_x_meshgrid) # number of uniq y nodes
    
    # calculate adaptive smoothing values at grid nodes
    print("Calculating adaptive smoothing values ...")
    mag_x = np.array(mag_x, dtype=float)
    mag_y = np.array(mag_y, dtype=float)
    nodes_all_x = np.array(nodes_all_x, dtype=float)
    nodes_all_y = np.array(nodes_all_y, dtype=float)

    nodes_all_smth = funcs.calc_nodes_adaptive_smoothing(mag_x, mag_y, nodes_all_x, nodes_all_y, args.smoothfactor, 3*args.maxgap)

    # Gridding

    if args.fixedsmoothing <= 0:
        print("Interpolation (2D Gridding) ... (adaptive smoothing)")
    else:
        print("Interpolation (2D Gridding) ... (1st pass: adaptive smoothing)")
    nodes_all_mag_p1 = [] # pass 1
    for i, xn in enumerate(nodes_all_x):
        yn = nodes_all_y[i]
        # node value (adaptive smoothing)
        vn = funcs.get_grid_value(xn, yn, mag_x, mag_y, mag_v, nodes_all_smth[i]) 
        nodes_all_mag_p1.append(vn)

    if args.fixedsmoothing > 0:
        nodes_all_mag_p2 = [] # pass 2
        print("Interpolation (2D Gridding) ... (2nd pass: fixed smoothing)") # for denoising purpose
        if args.fixedsmoothing == 9999:
            smoothing = args.interval
        else:
            smoothing = args.fixedsmoothing
        for i, xn in enumerate(nodes_all_x):
            yn = nodes_all_y[i]
            # node value (fixed smoothing):
            vn = funcs.get_grid_value(xn, yn, nodes_all_x, nodes_all_y, nodes_all_mag_p1, smoothing)
            nodes_all_mag_p2.append(vn)
        nodes_all_mag = nodes_all_mag_p2
    else:
        nodes_all_mag = nodes_all_mag_p1

    nodes_all_mag_meshgrid = np.array(nodes_all_mag, dtype=float).reshape(nodes_all_ny, nodes_all_nx)

    # calculate mask
    print("Calculating polygon and maxgap masks  ...")
    polygon = alphashape(mag_points, 0.5) # prefer a relatively smooth bounding polygon
    if polygon.is_empty:
        polygon = alphashape(mag_points, 0.0)
    polygon_x, polygon_y = polygon.exterior.xy
    polygon_x, polygon_y = polygon_x.tolist(), polygon_y.tolist()
    polygon_mask = calc_polygon_mask(polygon_x, polygon_y, nodes_all_x_meshgrid, nodes_all_y_meshgrid)
    maxgap_mask = calc_maxgap_mask(mag_x, mag_y, nodes_all_x_meshgrid, nodes_all_y_meshgrid, args.maxgap)
    mask_final = np.multiply(polygon_mask, maxgap_mask)

    # directional derivatives
    print("Calculating 1st horizontal derivative along X-axis (dX) ...")
    nodes_all_dx_meshgrid_fdiff = calc_dx_meshgrid(nodes_all_mag_meshgrid, args.interval, method="fdiff")
    nodes_all_dx_meshgrid_fft = calc_dx_meshgrid(nodes_all_mag_meshgrid, args.interval, method="fft")
    nodes_all_dx_meshgrid_rfft = calc_dx_meshgrid(nodes_all_mag_meshgrid, args.interval, method="rfft", rfactor=args.rfactor)
    nodes_all_dx_meshgrid = calc_dx_meshgrid(nodes_all_mag_meshgrid, args.interval, method=args.hdmethod, rfactor=args.rfactor)

    print("Calculating higher order horizontal derivatives along X-axis (dXn) ...")
    nodes_all_dx2_meshgrid_fdiff = calc_dx_meshgrid(nodes_all_dx_meshgrid_fdiff, args.interval, method="fdiff")
    nodes_all_dx2_meshgrid_fft = calc_dx_meshgrid(nodes_all_dx_meshgrid_fft, args.interval, method="fft")
    nodes_all_dx2_meshgrid_rfft = calc_dx_meshgrid(nodes_all_dx_meshgrid_rfft, args.interval, method="rfft", rfactor=args.rfactor)
    nodes_all_dx2_meshgrid = calc_dx_meshgrid(nodes_all_dx_meshgrid, args.interval, method=args.hdmethod, rfactor=args.rfactor)

    print("Calculating 1st horizontal derivative along Y-axis (dY) ...")
    nodes_all_dy_meshgrid_fdiff = calc_dy_meshgrid(nodes_all_mag_meshgrid, args.interval, method="fdiff")
    nodes_all_dy_meshgrid_fft = calc_dy_meshgrid(nodes_all_mag_meshgrid, args.interval, method="fft")
    nodes_all_dy_meshgrid_rfft = calc_dy_meshgrid(nodes_all_mag_meshgrid, args.interval, method="rfft", rfactor=args.rfactor)
    nodes_all_dy_meshgrid = calc_dy_meshgrid(nodes_all_mag_meshgrid, args.interval, method=args.hdmethod, rfactor=args.rfactor)

    print("Calculating higher order horizontal derivatives along Y-axis (dYn) ...")
    nodes_all_dy2_meshgrid_fdiff = calc_dy_meshgrid(nodes_all_dy_meshgrid_fdiff, args.interval, method="fdiff")
    nodes_all_dy2_meshgrid_fft = calc_dy_meshgrid(nodes_all_dy_meshgrid_fft, args.interval, method="fft")
    nodes_all_dy2_meshgrid_rfft = calc_dy_meshgrid(nodes_all_dy_meshgrid_rfft, args.interval, method="rfft", rfactor=args.rfactor)
    nodes_all_dy2_meshgrid = calc_dy_meshgrid(nodes_all_dy_meshgrid, args.interval, method=args.hdmethod, rfactor=args.rfactor)

    print("Calculating 1st vertical derivative (dZ) ...")
    nodes_all_dz_meshgrid_fdiff = calc_dz_meshgrid(nodes_all_mag_meshgrid, args.interval, method="fdiff")
    nodes_all_dz_meshgrid_fft = calc_dz_meshgrid(nodes_all_mag_meshgrid, args.interval, method="fft")
    nodes_all_dz_meshgrid_rfft = calc_dz_meshgrid(nodes_all_mag_meshgrid, args.interval, method="rfft", rfactor=args.rfactor)
    nodes_all_dz_meshgrid = calc_dz_meshgrid(nodes_all_mag_meshgrid, args.interval, method=args.vdmethod, rfactor=args.rfactor)

    print("Calculating higher order vertical derivatives (dZn) ...")
    nodes_all_dz2_meshgrid_fdiff = calc_dz_meshgrid(nodes_all_dz_meshgrid_fdiff, args.interval, method="fdiff")
    nodes_all_dz2_meshgrid_fft = calc_dz_meshgrid(nodes_all_dz_meshgrid_fft, args.interval, method="fft")
    nodes_all_dz2_meshgrid_rfft = calc_dz_meshgrid(nodes_all_dz_meshgrid_rfft, args.interval, method="rfft", rfactor=args.rfactor)
    nodes_all_dz2_meshgrid = calc_dz_meshgrid(nodes_all_dz_meshgrid, args.interval, method=args.vdmethod, rfactor=args.rfactor)
    nodes_all_dz3_meshgrid = calc_dz_meshgrid(nodes_all_dz2_meshgrid, args.interval, method=args.vdmethod, rfactor=args.rfactor)

    # edge/source detection filters
    print("Calculating total horizontal derivative (THD) ...")
    nodes_all_thd_meshgrid = calc_thd_meshgrid(nodes_all_dx_meshgrid, nodes_all_dy_meshgrid)

    print("Calculating 2nd order total horizontal derivative (THD2) ...")
    nodes_all_thd2_meshgrid = calc_thd_meshgrid(nodes_all_dx2_meshgrid, nodes_all_dy2_meshgrid)
    
    print("Calculating analytic signal (AS) ...")
    nodes_all_as_meshgrid = calc_as_meshgrid(nodes_all_dx_meshgrid, nodes_all_dy_meshgrid, nodes_all_dz_meshgrid)
    
    print("Calculating tilt derivative (TDR) ...")
    nodes_all_tdr_meshgrid = calc_tdr_meshgrid(nodes_all_dz_meshgrid, nodes_all_thd_meshgrid)

    print("Calculating horizontal tilt angle (TDX) ...")
    nodes_all_tdx_meshgrid = calc_tdx_meshgrid(nodes_all_dz_meshgrid, nodes_all_thd_meshgrid)

    print("Calculating enhanced TDR (ETDR) ...")
    nodes_all_etdr_meshgrid = calc_etdr_meshgrid(nodes_all_dz_meshgrid, nodes_all_thd_meshgrid, args.interval, args.interval)

    print("Calculating enhanced THD (ETHD) ...")
    nodes_all_ethd_meshgrid = calc_ethd_meshgrid(nodes_all_dz_meshgrid, nodes_all_thd_meshgrid, args.interval, args.interval)

    print("Calculating theta map (Theta) ...")
    nodes_all_theta_meshgrid = calc_theta_meshgrid(nodes_all_thd_meshgrid, nodes_all_as_meshgrid)

    print("Calculating THD of TDR (THDTDR) ...")
    nodes_all_thdtdr_meshgrid = calc_thd_meshgrid(
        calc_dx_meshgrid(nodes_all_tdr_meshgrid, args.interval, method="fdiff"),
        calc_dy_meshgrid(nodes_all_tdr_meshgrid, args.interval, method="fdiff"))

    
    # apply final mask to the main meshgrids
    nodes_all_mag_meshgrid = np.multiply(mask_final, nodes_all_mag_meshgrid)
    # dX (different methods and orders)
    nodes_all_dx_meshgrid_fdiff = np.multiply(mask_final, nodes_all_dx_meshgrid_fdiff)
    nodes_all_dx_meshgrid_fft = np.multiply(mask_final, nodes_all_dx_meshgrid_fft)
    nodes_all_dx_meshgrid_rfft = np.multiply(mask_final, nodes_all_dx_meshgrid_rfft)
    nodes_all_dx_meshgrid = np.multiply(mask_final, nodes_all_dx_meshgrid)
    nodes_all_dx2_meshgrid_fdiff = np.multiply(mask_final, nodes_all_dx2_meshgrid_fdiff)
    nodes_all_dx2_meshgrid_fft = np.multiply(mask_final, nodes_all_dx2_meshgrid_fft)
    nodes_all_dx2_meshgrid_rfft = np.multiply(mask_final, nodes_all_dx2_meshgrid_rfft)
    nodes_all_dx2_meshgrid = np.multiply(mask_final, nodes_all_dx2_meshgrid)
    # dY (different methods and orders)
    nodes_all_dy_meshgrid_fdiff = np.multiply(mask_final, nodes_all_dy_meshgrid_fdiff)
    nodes_all_dy_meshgrid_fft = np.multiply(mask_final, nodes_all_dy_meshgrid_fft)
    nodes_all_dy_meshgrid_rfft = np.multiply(mask_final, nodes_all_dy_meshgrid_rfft)
    nodes_all_dy_meshgrid = np.multiply(mask_final, nodes_all_dy_meshgrid)
    nodes_all_dy2_meshgrid_fdiff = np.multiply(mask_final, nodes_all_dy2_meshgrid_fdiff)
    nodes_all_dy2_meshgrid_fft = np.multiply(mask_final, nodes_all_dy2_meshgrid_fft)
    nodes_all_dy2_meshgrid_rfft = np.multiply(mask_final, nodes_all_dy2_meshgrid_rfft)
    nodes_all_dy2_meshgrid = np.multiply(mask_final, nodes_all_dy2_meshgrid)
    # dZ (different methods and orders)
    nodes_all_dz_meshgrid_fdiff = np.multiply(mask_final, nodes_all_dz_meshgrid_fdiff)
    nodes_all_dz_meshgrid_fft = np.multiply(mask_final, nodes_all_dz_meshgrid_fft)
    nodes_all_dz_meshgrid_rfft = np.multiply(mask_final, nodes_all_dz_meshgrid_rfft)
    nodes_all_dz_meshgrid = np.multiply(mask_final, nodes_all_dz_meshgrid)
    nodes_all_dz2_meshgrid_fdiff = np.multiply(mask_final, nodes_all_dz2_meshgrid_fdiff)
    nodes_all_dz2_meshgrid_fft = np.multiply(mask_final, nodes_all_dz2_meshgrid_fft)
    nodes_all_dz2_meshgrid_rfft = np.multiply(mask_final, nodes_all_dz2_meshgrid_rfft)
    nodes_all_dz2_meshgrid = np.multiply(mask_final, nodes_all_dz2_meshgrid)
    nodes_all_dz3_meshgrid = np.multiply(mask_final, nodes_all_dz3_meshgrid)
    # other filters (using the specified ddr method)

    if not args.ddronly:
        nodes_all_thd_meshgrid = np.multiply(mask_final, nodes_all_thd_meshgrid)
        nodes_all_thd2_meshgrid = np.multiply(mask_final, nodes_all_thd2_meshgrid)
        nodes_all_as_meshgrid = np.multiply(mask_final, nodes_all_as_meshgrid)
        nodes_all_tdr_meshgrid = np.multiply(mask_final, nodes_all_tdr_meshgrid)
        nodes_all_tdx_meshgrid = np.multiply(mask_final, nodes_all_tdx_meshgrid)
        nodes_all_etdr_meshgrid = np.multiply(mask_final, nodes_all_etdr_meshgrid)
        nodes_all_ethd_meshgrid = np.multiply(mask_final, nodes_all_ethd_meshgrid)
        nodes_all_theta_meshgrid = np.multiply(mask_final, nodes_all_theta_meshgrid)
        nodes_all_thdtdr_meshgrid = np.multiply(mask_final, nodes_all_thdtdr_meshgrid)

    # Generate output files
    if not len(os.path.splitext(args.outfile)[1]):
        args.outfile += ".dat"
    fname, fext = os.path.splitext(args.outfile)

    print(f"Generating outputs ... ")
    args.sort = False
    args.uniq = False
    args.append = False

    if args.ddronly:
        output_datasets = {
            "MAG"    : nodes_all_mag_meshgrid,
            "dX"     : nodes_all_dx_meshgrid,
            "dY"     : nodes_all_dy_meshgrid,
            "dZ"     : nodes_all_dz_meshgrid,
            "dX2"     : nodes_all_dx2_meshgrid,
            "dY2"     : nodes_all_dy2_meshgrid,
            "dZ2"     : nodes_all_dz2_meshgrid,
        }
    else:
        output_datasets = {
            "MAG"    : nodes_all_mag_meshgrid,
            "dX"     : nodes_all_dx_meshgrid,
            "dY"     : nodes_all_dy_meshgrid,
            "dZ"     : nodes_all_dz_meshgrid,
            "dX2"     : nodes_all_dx2_meshgrid,
            "dY2"     : nodes_all_dy2_meshgrid,
            "dZ2"     : nodes_all_dz2_meshgrid,
            "AS"     : nodes_all_as_meshgrid,
            "THD"    : nodes_all_thd_meshgrid,
            "ETHD"   : nodes_all_ethd_meshgrid,
            "TDR"    : nodes_all_tdr_meshgrid,
            "ETDR"   : nodes_all_etdr_meshgrid,
            "TDX"    : nodes_all_tdx_meshgrid,
            "THETA"  : nodes_all_theta_meshgrid,
            "THD_of_TDR" : nodes_all_thdtdr_meshgrid
        }
    # initialize output lists
    try:
        xcollen = int(args.fmt[0].split(".")[0])
        vcollen = int(args.fmt[1].split(".")[0])
    except:
        xcollen = int(args.fmt[0].split(".")[1]) + 9
        vcollen = int(args.fmt[1].split(".")[1]) + 7
        args.fmt[0] = f"{xcollen}.{xcollen - 9}"
        args.fmt[1] = f"{vcollen}.{vcollen - 7}"

    output_lines = [f"%{xcollen}s%{xcollen}s" %("X", "Y")]
    for dataset_name in output_datasets.keys():
        output_lines[0] += f"%{vcollen}s" %(dataset_name)
    for i in np.arange(nodes_all_ny):
        for j in np.arange(nodes_all_nx):
            if mask_final[i][j] != 1:
                continue
            x = nodes_all_x_meshgrid[i][j]
            y = nodes_all_y_meshgrid[i][j]
            output_lines.append(f"%{args.fmt[0]}f%{args.fmt[0]}f" %(x, y))
    # append data to the intialized output_lines
    for dataset_name in output_datasets.keys():
        dataset = output_datasets[dataset_name]
        k = 1
        for i in np.arange(nodes_all_ny):
            for j in np.arange(nodes_all_nx):
                if mask_final[i][j] != 1:
                    continue
                output_lines[k] += f"%{args.fmt[1]}f" %(dataset[i][j])
                k += 1
    io.output_lines(output_lines, args)

    if args.noplots:
        print("Finished!")
        exit(0)

    ##########################
    # Generate plots
    import matplotlib
    matplotlib.use('TkAgg')

    import matplotlib.pyplot as plt

    aspect_ratio = (max_y - min_y)/(max_x - min_x)

    # ----- Original Data ----#
    import warnings # workaround for user warning for fixed axis tick label formatting
    warnings.filterwarnings("ignore")

    fig = plt.figure(figsize=(6+2,6*aspect_ratio), num=f'Original data (gridded at {args.interval} m interval)')
    fig.canvas.manager.window.attributes('-topmost', 1)

    ax1 = fig.add_subplot(1, 1, 1)
    ax1.set_title("MAG data")
    pc1=ax1.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_mag_meshgrid,
     cmap='rainbow', shading='nearest')

    yticks = plt.gca().get_yticks()
    xticks = plt.gca().get_xticks()
    plt.gca().set_xticklabels(['{:.0f}'.format(x) for x in xticks])
    plt.gca().set_yticklabels(['{:.0f}'.format(y) for y in yticks])

    ax1.set_xlabel("Easting (m)")
    ax1.set_ylabel("Northing (m)")
    fig.colorbar(pc1)

    plt.tight_layout()

    figout = f"{fname}_MAG.png"

    plt.savefig(figout, dpi=400, format="png")

    # ----- Directional Derivatives ----#

    ##########################
    # First order derivatives

    fig = plt.figure(figsize=(6+2,6*aspect_ratio), num=f'Directional Derivatives (1st order)')
    fig.canvas.manager.window.attributes('-topmost', 2)

    ax1 = fig.add_subplot(3, 3, 1)
    ax1.set_title("dM/dx (fdiff)")
    ax1.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc1=ax1.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dx_meshgrid_fdiff,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc1)

    ax2 = fig.add_subplot(3, 3, 2)
    ax2.set_title("dM/dx (fft)")
    ax2.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc2=ax2.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dx_meshgrid_fft,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc2)

    ax3 = fig.add_subplot(3, 3, 3)
    ax3.set_title(f"dM/dx (rfft; rfactor={args.rfactor})")
    ax3.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc3=ax3.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dx_meshgrid_rfft,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc3)

    ax4 = fig.add_subplot(3, 3, 4)
    ax4.set_title("dM/dy (fdiff)")
    ax4.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc4=ax4.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dy_meshgrid_fdiff,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc4)

    ax5 = fig.add_subplot(3, 3, 5)
    ax5.set_title("dM/dy (fft)")
    ax5.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc5=ax5.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dy_meshgrid_fft,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc5)

    ax6 = fig.add_subplot(3, 3, 6)
    ax6.set_title(f"dM/dy (rfft; rfactor={args.rfactor})")
    ax6.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc6=ax6.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dy_meshgrid_rfft,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc6)

    ax7 = fig.add_subplot(3, 3, 7)
    ax7.set_title("dM/dz (fdiff)")
    ax7.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc7=ax7.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dz_meshgrid_fdiff,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc7)

    ax8 = fig.add_subplot(3, 3, 8)
    ax8.set_title("dM/dz (fft)")
    ax8.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc8=ax8.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dz_meshgrid_fft,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc8)

    ax9 = fig.add_subplot(3, 3, 9)
    ax9.set_title(f"dM/dz (rfft; rfactor={args.rfactor})")
    ax9.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc9=ax9.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dz_meshgrid_rfft,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc9)

    plt.tight_layout()

    figout = f"{fname}_1st_DDR.png"
    plt.savefig(figout, dpi=400, format="png")

    ##########################
    # Second order derivatives
    fig = plt.figure(figsize=(6+2,6*aspect_ratio), num=f'Directional Derivatives (2nd order)')
    fig.canvas.manager.window.attributes('-topmost', 2)

    ax1 = fig.add_subplot(3, 3, 1)
    ax1.set_title("d2M/dx2 (fdiff)")
    ax1.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc1=ax1.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dx2_meshgrid_fdiff,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc1)

    ax2 = fig.add_subplot(3, 3, 2)
    ax2.set_title("d2M/dx2 (fft)")
    ax2.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc2=ax2.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dx2_meshgrid_fft,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc2)

    ax3 = fig.add_subplot(3, 3, 3)
    ax3.set_title(f"d2M/dx2 (rfft; rfactor={args.rfactor})")
    ax3.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc3=ax3.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dx2_meshgrid_rfft,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc3)

    ax4 = fig.add_subplot(3, 3, 4)
    ax4.set_title("d2M/dy2 (fdiff)")
    ax4.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc4=ax4.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dy2_meshgrid_fdiff,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc4)

    ax5 = fig.add_subplot(3, 3, 5)
    ax5.set_title("d2M/dy2 (fft)")
    ax5.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc5=ax5.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dy2_meshgrid_fft,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc5)

    ax6 = fig.add_subplot(3, 3, 6)
    ax6.set_title(f"d2M/dy2 (rfft; rfactor={args.rfactor})")
    ax6.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc6=ax6.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dy2_meshgrid_rfft,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc6)

    ax7 = fig.add_subplot(3, 3, 7)
    ax7.set_title("d2M/dz2 (fdiff)")
    ax7.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc7=ax7.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dz2_meshgrid_fdiff,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc7)

    ax8 = fig.add_subplot(3, 3, 8)
    ax8.set_title("d2M/dz2 (fft)")
    ax8.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc8=ax8.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dz2_meshgrid_fft,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc8)

    ax9 = fig.add_subplot(3, 3, 9)
    ax9.set_title(f"d2M/dz2 (rfft; rfactor={args.rfactor})")
    ax9.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc9=ax9.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dz2_meshgrid_rfft,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc9)

    plt.tight_layout()

    figout = f"{fname}_2nd_DDR.png"
    plt.savefig(figout, dpi=400, format="png")

    # ----- Filters ----#

    if args.ddronly:
        print("Finished!")
        if args.showplots:
            plt.show()
        plt.close()
        exit(0)

    fig = plt.figure(figsize=(9+4,6*aspect_ratio), num=f'Filters (H-derivative:{args.hdmethod} ,V-derivative: {args.vdmethod})')
    fig.canvas.manager.window.attributes('-topmost', 3)

    ax_mag = fig.add_subplot(3, 5, 1)
    ax_mag.set_title("MAG data")
    ax_mag.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc_mag=ax_mag.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_mag_meshgrid,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc_mag)

    ax_dx = fig.add_subplot(3, 5, 2)
    ax_dx.set_title("dM/dx (dX)")
    ax_dx.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc_dx=ax_dx.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dx_meshgrid,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc_dx)

    ax_dy = fig.add_subplot(3, 5, 3)
    ax_dy.set_title("dM/dy (dY)")
    ax_dy.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc_dy=ax_dy.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dy_meshgrid,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc_dy)

    ax_dz = fig.add_subplot(3, 5, 4)
    ax_dz.set_title("dM/dz (dZ)")
    ax_dz.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc_dz=ax_dz.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dz_meshgrid,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc_dz)

    
    ax_as = fig.add_subplot(3, 5, 5)
    ax_as.set_title("AS")
    ax_as.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc_as=ax_as.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_as_meshgrid,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc_as)

    ax_thd = fig.add_subplot(3, 5, 6)
    ax_thd.set_title("THD")
    ax_thd.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc_thd=ax_thd.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_thd_meshgrid,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc_thd)

    ax_ethd = fig.add_subplot(3, 5, 7)
    ax_ethd.set_title(f"ETHD")
    ax_ethd.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc_ethd=ax_ethd.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_ethd_meshgrid,
     cmap='hot', shading='nearest')
    fig.colorbar(pc_ethd)

    ax_tdr = fig.add_subplot(3, 5, 8)
    ax_tdr.set_title(f"TDR")
    ax_tdr.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc_tdr=ax_tdr.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_tdr_meshgrid,
     cmap='twilight', shading='nearest')
    fig.colorbar(pc_tdr)

    ax_etdr = fig.add_subplot(3, 5, 9)
    ax_etdr.set_title("ETDR")
    ax_etdr.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc_etdr=ax_etdr.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_etdr_meshgrid,
     cmap='hot', shading='nearest')
    fig.colorbar(pc_etdr)


    ax_thdtdr = fig.add_subplot(3, 5, 10)
    ax_thdtdr.set_title("THD of TDR")
    ax_thdtdr.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc_thdtdr=ax_thdtdr.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_thdtdr_meshgrid,
     cmap='hot', shading='nearest')
    fig.colorbar(pc_thdtdr)

    ax_th2 = fig.add_subplot(3, 5, 11)
    ax_th2.set_title("THD (2nd order)")
    ax_th2.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc_thd2=ax_th2.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_thd2_meshgrid,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc_thd2)

    ax_theta = fig.add_subplot(3, 5, 12)
    ax_theta.set_title("Theta map")
    ax_theta.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc_theta=ax_theta.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_theta_meshgrid,
     cmap='hot', shading='nearest')
    fig.colorbar(pc_theta)


    ax_tdx = fig.add_subplot(3, 5, 13)
    ax_tdx.set_title("TDX")
    ax_tdx.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc_tdx=ax_tdx.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_tdx_meshgrid,
     cmap='twilight', shading='nearest')
    fig.colorbar(pc_tdx)

    ax_dz2 = fig.add_subplot(3, 5, 14)
    ax_dz2.set_title("d2M/dz2 (dZ2)")
    ax_dz2.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc_dz2=ax_dz2.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dz2_meshgrid,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc_dz2)

    ax_dz3 = fig.add_subplot(3, 5, 15)
    ax_dz3.set_title("d3M/dz3 (dZ3)")
    ax_dz3.tick_params(left = False, labelleft = False,
                    right = False, labelright = False,
                    top = False, labeltop = False,
                    bottom = False, labelbottom = False)
    pc_dz2=ax_dz3.pcolormesh(nodes_all_x_meshgrid, nodes_all_y_meshgrid, nodes_all_dz3_meshgrid,
     cmap='rainbow', shading='nearest')
    fig.colorbar(pc_dz2)

    plt.tight_layout()

    figout = f"{fname}_FILTERS.png"
    plt.savefig(figout, dpi=400, format="png")
    
    print("Finished!")

    if args.showplots:
        plt.show()
    plt.close()



