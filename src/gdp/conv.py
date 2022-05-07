
import os
import shutil

def nc2dat(args):
    import netCDF4 as nc
    import numpy as np
    input_files = args.input_files
    
    for ncfile in input_files:
        try:
            ds = nc.Dataset(ncfile)
        except Exception as e:
            print(f"Error reading '{os.path.split(ncfile)[1]}': {e}")
            continue

        out_lines = []
        if args.metadata:
            for key in ds.__dict__.keys():
                print(f"{key}: {ds.__dict__[key]}")
            print(f"\nVariables:")
            for i, key in enumerate(ds.variables.keys(), start=1):
                print(f"\nData column {i}: '{key}'\n {ds.variables[key]}")

        else:
            all_keys = list(ds.variables.keys())
            data_pos = []
            data_val = []

            for key in all_keys:
                ndim = len(np.shape(ds[key][:]))
                if ndim == 1:
                    data_pos.append([])
                    for x in ds[key][:]:
                        data_pos[-1].append(x)
                else:
                    data_val = ds[key][:]

            # position columns shape
            pos_shape = []
            for pos in data_pos:
                pos_shape.append(len(pos))
            
            if list(np.shape(data_val)) == pos_shape:
                print('yes')
            else:
                print('no', pos_shape)
                data_pos = data_pos[::-1]
                pos_shape = []
                for pos in data_pos:
                    pos_shape.append(len(pos))
                print('yes now?', pos_shape)









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
            st.detrend('demean')
            st.taper(0.005)
            if len(st) > 1:# fix data fragmentation issue
                st.sort(['starttime'])
                st.merge(method=1, fill_value=0)

            # modify some sac headers and write to file
            st[0].stats.sac = obspy.core.AttribDict()
            st[0].stats.sac.iztype = 9
            st[0].stats.sac.lovrok = True
            st[0].stats.sac.lcalda = True
            # resample?
            if args.resample != 999:
                st.resample(float(args.resample))
            st[0].write(os.path.join(outdir, outfile), format='SAC')
        except Exception as e:
            print(f"  Error: {e}")
        ########################

        if len(os.listdir(outdir)) == 0:
            shutil.rmtree(outdir)

    # if zero outputs
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







