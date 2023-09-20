
import obspy
import os
import re
import shutil
import subprocess

from .. import programs
from ..ascii_procs import io


def sac_to_ascii(args):
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
    
    args.offset = -1 * args.offset
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
                event_time = request_starttime + args.offset
                event_origin = f"gmt %4.0f %03.0f %02.0f %02.0f %02.0f 000" %(
                                float(event_time.year),
                                float(event_time.julday),
                                float(event_time.hour),
                                float(event_time.minute),
                                float(event_time.second))

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
        SAC = programs.find_sac_path()
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
                st[0].stats.sac.o = args.offset
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

    mseed_file = os.path.split(mseed_file)[1]
    event_utc_time = obspy.UTCDateTime(mseed_file.split('_')[2]) + float(time_offset)
    event_name = "%02d%03d%02d%02d%02d" %(int(str(event_utc_time.year)[2:]),
                                        event_utc_time.julday,
                                        event_utc_time.hour,
                                        event_utc_time.minute,
                                        event_utc_time.second)
    return event_name


def get_sac_name_from_mseed(mseed_file, time_offset):
    event_name = get_event_name(mseed_file, time_offset)
    st = obspy.read(mseed_file, headonly=True)
    station = st[0].stats.station
    channel = st[0].stats.channel
    filename = f"{event_name}_{station}.{channel}"
    return filename







