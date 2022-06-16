
import os
import shutil
import subprocess

from . import io
from . import dependency



def dat2nc(args):
    import warnings
    import numpy as np
    import netCDF4 as nc
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        try:
            from . import _geographic as geographic
        except ImportError:
            print("WARNING! Could not use cythonized module: geographic")
            from . import geographic

    if len(args.fmt) == 1:
        args.fmt.append(args.fmt[0])

    read_input_data = io.read_numerical_data(args.input_file, 0, 0, [".10",".10"], args.x, args.data)
    read_data_points = np.vstack((read_input_data[0][0], read_input_data[0][1])).T.tolist()
    read_data_values = read_input_data[1][0]
    if args.polygon:
        polygon_file = args.polygon
        if os.path.splitext(polygon_file)[1] == ".shp":
            # if polygon_file is *.shp
            import geopandas as gpd
            from shapely.geometry import mapping
            try:
                shp = gpd.read_file(polygon_file)
                polygon_x = np.array(mapping(shp)['features'][0]['geometry']['coordinates'][0]).flatten()[0::2]
                polygon_y = np.array(mapping(shp)['features'][0]['geometry']['coordinates'][0]).flatten()[1::2]
            except Exception as e:
                print(f"Error reading shapefile! {e}")
                exit(1)
        else:
            # else if polygon_file is not *.shp (ascii file)
            polygon_data = io.read_numerical_data(polygon_file, 0, 0, [".10",".10"], args.x, [])
            polygon_x = polygon_data[0][0]
            polygon_y = polygon_data[0][1]

        if len(polygon_x): 
            polygon = geographic.Polygon(polygon_x, polygon_y)
        else:
            print(f"Error: polygon is not specified. Please check polygon file.")
            exit(1)

    data = {}
    x_uniq = []
    y_uniq = []
    for ip, point in enumerate(read_data_points):
        point = np.around(point, decimals=int(args.fmt[0][-1]))
        point = geographic.Point(point[0], point[1])
        if point.lon not in x_uniq:
            x_uniq.append(point.lon)
        if point.lat not in y_uniq:
            y_uniq.append(point.lat)
        key = f"%{args.fmt[0]}f_%{args.fmt[0]}f" %(point.lon, point.lat)
        val = f"%{args.fmt[1]}f" %(read_data_values[ip])
        if args.polygon:
            if polygon.is_point_in(point):
                data[f"{key}"] = val
        else:
            data[f"{key}"] = val

    xSpacing = np.unique( np.around(np.diff(sorted(x_uniq)), decimals=int(args.fmt[0][-1])) )
    ySpacing = np.unique( np.around(np.diff(sorted(y_uniq)), decimals=int(args.fmt[0][-1])) )
    if len(xSpacing) > 1 or len(ySpacing) > 1:
        print("Error! Input data should be in uniformly gridded format. Use 'gridder' first!")
        print(f"\n  x_spacing = {xSpacing}")
        print(f"  y_spacing = {ySpacing}\n")
        exit(1)
    else:
        xSpacing = xSpacing[0]
        ySpacing = ySpacing[0]

    minX = np.nanmin(x_uniq)
    maxX = np.nanmax(x_uniq)
    minY = np.nanmin(y_uniq)
    maxY = np.nanmax(y_uniq)

    nc_x = np.arange(minX, maxX+xSpacing, xSpacing)
    nc_y = np.arange(minY, maxY+ySpacing, ySpacing)

    # silly fix of a bug!
    if np.around(nc_x[-1], decimals=int(args.fmt[0][-1])) \
    != np.around(maxX, decimals=int(args.fmt[0][-1]) ):
        nc_x = nc_x[:-1]
    if np.around(nc_y[-1], decimals=int(args.fmt[0][-1])) \
    != np.around(maxY, decimals=int(args.fmt[0][-1]) ):
        nc_y = nc_y[:-1]

    nc_z = np.ndarray((len(nc_x), len(nc_y)), dtype=float)
    for ix, x in enumerate(nc_x):
        for iy, y in enumerate(nc_y):
            key = f"%{args.fmt[0]}f_%{args.fmt[0]}f" %(x, y)
            if key in data.keys():
                nc_z[ix][iy] = data[key]
            else:
                nc_z[ix][iy] = np.nan

    ncfile = nc.Dataset(args.output_file, mode='w', format='NETCDF4_CLASSIC')
    ncfile.createDimension('x', len(nc_x))
    ncfile.createDimension('y', len(nc_y))
    ncfile.createDimension('z', None)

    x = ncfile.createVariable('x', np.float64, ('x',))
    y = ncfile.createVariable('y', np.float64, ('y',))
    z = ncfile.createVariable('z', np.float64, ('x','y',))

    x.actual_range = (minX, maxX)
    x.long_name = 'x'
    y.actual_range = (minY, maxY)
    y.long_name = 'y'
    z.actual_range = (np.nanmin(np.nanmin(nc_z)), np.nanmax(np.nanmax(nc_z)))
    z.long_name = 'z'

    x[:] = nc_x
    y[:] = nc_y
    z[:,:] = nc_z

    ncfile.close()









#################

def nc2dat(args):
    import random
    import numpy as np
    import netCDF4 as nc

    try:
        ncfile = args.input_file[0]
        ds = nc.Dataset(ncfile)
    except Exception as e:
        print(f"Error reading '{os.path.split(ncfile)[1]}': {e}")
        exit(1)

    if len(args.fmt) == 1:
        fmt = [args.fmt[0], args.fmt[0]]
    else:
        fmt = args.fmt
    
    out_lines = []
    if args.metadata:
        for key in ds.__dict__.keys():
            out_lines.append(f"{key}: {ds.__dict__[key]}")
        out_lines.append(f"\nVariables:")
        for key in ds.variables.keys():
            out_lines.append(f"\nData field: '{key}'\n {ds.variables[key]}")
    else:
        all_fields = list(ds.variables.keys())
        selected_fields = args.data
        if not selected_fields:
            print(f"Error! At least one data field name must be given using flag '--data'.\nCheck metadata for more information.")
            exit(1)

        ndf = len(selected_fields) # number of data fields
        data_val = []
        for df in selected_fields:
            if df not in all_fields:
                print(f"Error! Could not find data field: '{df}'")
                exit(1)
            else:
                data_val.append(ds[df][:].data)
        
        data_pos = []
        for key in all_fields:
            if len(np.shape(ds[key][:])) == 1:
                data_pos.append([])
                for x in ds[key][:]:
                    data_pos[-1].append(x)

        # match shapes for data_pos and data_val
        for iv in range(ndf):
            ntry = 0
            while True:
                ntry += 1
                pos_shape = []
                for pos in data_pos:
                    pos_shape.append(len(pos))
                if list(np.shape(data_val[iv])) == pos_shape:
                    break
                else:
                    random.shuffle(data_pos)
                if ntry == 100:
                    break
            if ntry == 100:
                print(f"Error! Could not figure out data format for '{os.path.split(ncfile)[1]}'")
                exit(1)
        
        out_lines = gen_nc_dataset_outlines(data_pos, data_val, fmt)

    args.uniq = False
    args.sort = False
    io.output_lines(out_lines, args)
        




def gen_nc_dataset_outlines(positional_matrix, values_matrix, fmt = ['.4', '.4']):
    import numpy as np
    outlines = []
    ndim = len(positional_matrix) # number of dimension
    ndf = len(values_matrix) # number of data fields
    shape = list(np.shape(values_matrix[0])) # dimension shape

    if ndim == 2:
        for i, x in enumerate(positional_matrix[0]):
            for j, y in enumerate(positional_matrix[1]):
                outlines.append(f"%{fmt[0]}f %{fmt[0]}f" %(x, y))
    elif ndim == 3:
        for i, x in enumerate(positional_matrix[0]):
            for j, y in enumerate(positional_matrix[1]):
                for k, z in enumerate(positional_matrix[2]):
                    outlines.append(f"%{fmt[0]}f %{fmt[0]}f %{fmt[0]}f" %(x, y, z))
    else:
        print(f"Error! This is not a 2D or 3D dataset.\nCurrrent version of the program only works for 2D and 3D datasets.")
        exit(1)

    if ndim == 2:
        for idf in range(ndf):
            for i in range(len(outlines)):
                ix = int(np.floor(i / shape[1]))
                iy = i % shape[1]
                outlines[i] += f" %{fmt[1]}f" %(values_matrix[idf][ix][iy])
    elif ndim == 3:
        for idf in range(ndf):
            for i in range(len(outlines)):
                ix = int(np.floor(i / (shape[1] * shape[2]) ))
                iy = int(np.floor(i / (shape[0] * shape[2]) ))
                iz = i % shape[2]
                outlines[i] += f" %{fmt[1]}f" %(values_matrix[idf][ix][iy][iz])

    return outlines



def sac2dat(args):
    import obspy
    outdir = os.path.abspath(args.outdir)

    if len(args.fmt) == 1:
        fmt = [args.fmt[0], args.fmt[0]]
    else:
        fmt = args.fmt

    for sac in args.input_files:
        sac_fname = os.path.split(sac)[1]

        if not os.path.isfile(sac):
            print(f"Error! sac file does not exist: '{sac_fname}'")
            continue

        try:
            st_test = obspy.read(sac, format='SAC', headonly=True)
        except Exception as e:
            print(f"Error! Cannot read sac file: '{sac_fname}'")
            continue

        # output directory path
        if not os.path.isdir(outdir):
            os.makedirs(outdir)

        # output file path
        outfile = f"{sac_fname.replace('.', '_')}.dat"

        ########################
        print(f"'{sac_fname}' >> '{outfile}'")
        st = obspy.read(sac)
        time = st[0].times()
        data = st[0].data
        fopen = open(os.path.join(outdir, outfile), 'w')
        for i in range(len(time)):
            if args.timerange == [999, 999]:
                fopen.write(f"%{fmt[0]}f %{fmt[1]}f\n" %(time[i], data[i]))
            else:
                if time[i] >= args.timerange[0] and time[i] <= args.timerange[1]:
                    fopen.write(f"%{fmt[0]}f %{fmt[1]}f\n" %(time[i], data[i]))
        fopen.close()



def mseed2sac(args):
    import re
    import obspy
    datetime = '[1-2][0-9][0-9][0-9][0-1][0-9][0-3][0-9]T[0-2][0-9][0-5][0-9][0-5][0-9]Z'
    mseeds = f'^.*{datetime}\_\_{datetime}.*$'
    regex_mseeds = re.compile(mseeds)
    outdir_orig = os.path.abspath(args.outdir)

    for mseed in args.input_files:
        mseed_fname = os.path.split(mseed)[1]

        if not os.path.isfile(mseed):
            print(f"Error! MSeed file does not exist: '{mseed_fname}'")
            continue

        try:
            st_test = obspy.read(mseed, headonly=True)
        except Exception as e:
            print(f"Error! Cannot read mseed file: '{mseed_fname}'")
            continue

        # output directory path
        if regex_mseeds.match(mseed_fname) and args.reformat:
            outdir = os.path.join(outdir_orig, get_event_name(mseed, args.offset))
        else:
            outdir = outdir_orig
        if not os.path.isdir(outdir):
            os.makedirs(outdir)

        # output file path
        if regex_mseeds.match(mseed_fname) and args.reformat:
            outfile = get_sac_name_from_mseed(mseed, args.offset)
        else:
            outfile = f"{os.path.splitext(mseed_fname)[0]}.sac"

        ########################
        print(f"'{mseed_fname}' >> '{outfile}'")
        try:
            st = obspy.read(mseed)

            data_starttime = obspy.UTCDateTime(st[0].stats.starttime)
            data_endtime = obspy.UTCDateTime(st[-1].stats.endtime)
            data_length = int(data_endtime - data_starttime)
            begin_data = int(data_starttime.hour*3600 +
                         data_starttime.minute*60 +
                         data_starttime.second)
            if regex_mseeds.match(mseed_fname):
                request_starttime = obspy.UTCDateTime(os.path.split(mseed)[1].split('_')[2]) # obspy.UTCDateTime()
                request_endtime = obspy.UTCDateTime(os.path.split(mseed)[1].split('_')[4].split('.')[0]) # obspy.UTCDateTime()
                request_length = int(request_endtime - request_starttime)
                begin_request = int(request_starttime.hour*3600 +
                            request_starttime.minute*60 +
                            request_starttime.second)

            # apply detrend and taper
            if not args.noprocess:
                try:
                    st.detrend('spline', order=4, dspline=int(data_length * 10))
                except:
                    st.detrend('demean')
                st.taper(0.005)

            if len(st) > 1:# fix data fragmentation issue
                st.sort(['starttime'])
                st.merge(method=1, fill_value=0)

            # modify some sac headers and write to file
            st[0].stats.sac = obspy.core.AttribDict()
            st[0].stats.sac.b = begin_data
            st[0].stats.sac.iztype = 9
            st[0].stats.sac.lovrok = True
            st[0].stats.sac.lcalda = True

            # resample?
            if args.resample != 999:
                st.resample(float(args.resample))

            st[0].write(os.path.join(outdir, outfile), format='SAC')

        except Exception as e:
            print(f"  Error: {e}")

        # make sure timeseries length is correct (sac cutter fillz)
        SAC = dependency.find_sac_path()
        if len(SAC):
            if regex_mseeds.match(mseed_fname):
                # cut to correct b to e and fill with zeros
                shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
                shell_cmd.append(f"cuterr fillz")
                shell_cmd.append(f"cut {begin_request} {begin_request + request_length}")
                shell_cmd.append(f"r {os.path.join(outdir, outfile)}")
                shell_cmd.append(f"w over")
                shell_cmd.append(f"q")
                shell_cmd.append('EOF')
                shell_cmd = '\n'.join(shell_cmd)
                subprocess.call(shell_cmd, shell=True)

                # reload sac file, set sac begin time to zero, correct sac kztime, and write to file
                st = obspy.read(os.path.join(outdir, outfile), format='SAC')
                st[0].stats.sac = obspy.core.AttribDict()
                st[0].stats.sac.b = 0
                st[0].stats.starttime = request_starttime
                st[0].write(os.path.join(outdir, outfile), format='SAC')
        else:
            print("WARNING! SAC was not found in current terminal environment. 'cutter fillz' cannot be aplied to the output sac files.")
        ########################

        if len(os.listdir(outdir)) == 0:
            shutil.rmtree(outdir)

    # if zero outputs
    if os.path.isdir(outdir_orig):
        if len(os.listdir(outdir_orig)) == 0:
            shutil.rmtree(outdir_orig)



def get_event_name(mseed_file, time_offset):
    import obspy
    mseed_file = os.path.split(mseed_file)[1]
    event_utc_time = obspy.UTCDateTime(mseed_file.split('_')[2]) + float(time_offset)
    event_name = "%02d%03d%02d%02d%02d" %(int(str(event_utc_time.year)[2:]),
                                        event_utc_time.julday,
                                        event_utc_time.hour,
                                        event_utc_time.minute,
                                        event_utc_time.second)
    return event_name


def get_sac_name_from_mseed(mseed_file, time_offset):
    import obspy
    event_name = get_event_name(mseed_file, time_offset)
    st = obspy.read(mseed_file, headonly=True)
    station = st[0].stats.station
    channel = st[0].stats.channel
    filename = f"{event_name}_{station}.{channel}"
    return filename







