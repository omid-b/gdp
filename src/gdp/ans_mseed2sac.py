
import os
import obspy
import re
import shutil
from . import ans_config
from . import ans_proc
from . import ans_download

#==== MAIN FUNCTION ====#

regex_mseeds = re.compile('^.*[1-2][0-9][0-9][0-9][0-1][0-9][0-3][0-9]T[0-2][0-9][0-5][0-9][0-5][0-9]Z\.(mseed)$')
regex_events = re.compile('^[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$')


def mseed2sac_run_all(maindir, input_mseeds_dir, output_sacs_dir, all=True):
    conf = ans_config.read_config(maindir)
    SAC = conf['setting']['le_sac']
    if not os.path.isfile(SAC):
        print(f"Error! could not find SAC software in the following path:\n{SAC}")
        exit(1)
    input_mseeds_dir = os.path.abspath(input_mseeds_dir)
    output_sacs_dir = os.path.abspath(output_sacs_dir)
    if not os.path.isdir(output_sacs_dir):
        os.mkdir(output_sacs_dir)

    mseeds = generate_mseed_list(input_mseeds_dir)

    stations = ans_download.STATIONS(maindir)
    stalist = stations.read_stalist()

    num_outputs = 0
    num_deleted = 0
    for mseed in mseeds:
        event_name = get_event_name(mseed)
        if not os.path.isdir(os.path.join(output_sacs_dir, event_name)):
            os.mkdir(os.path.join(output_sacs_dir, event_name))

        sacfile = os.path.join(output_sacs_dir, event_name, get_sac_name(mseed))
        sacfile_staname = get_sac_name(mseed).split('.')[0].split('_')[1]
        if all == False and sacfile_staname not in stalist['sta']:
            continue
            
        if not os.path.isfile(sacfile):
            print(f"\nsac file: {os.path.split(sacfile)[1]}")
            success = True
            for i, process in enumerate(conf['mseed2sac']['mseed2sac_procs']):
                pid = process['pid']
                if success and pid == [1,1]:
                    print(f"    Process #{i+1}: MSEED to SAC")
                    taper = is_true(process['chb_mseed2sac_taper'])
                    taper_type = process['cmb_mseed2sac_taper_method']
                    taper_max_perc = float(process['dsb_mseed2sac_max_taper'])
                    
                    detrend = is_true(process['chb_mseed2sac_detrend'])
                    detrend_method = process['cmb_mseed2sac_detrend_method']
                    detrend_order = int(process['sb_mseed2sac_detrend_order'])
                    dspline = int(process['le_mseed2sac_dspline'])
                    
                    if detrend_method == 0:
                        detrend_method = "demean"
                    elif detrend_method == 1:
                        detrend_method = "linear"
                    elif detrend_method == 2:
                        detrend_method = "polynomial"
                    elif detrend_method == 3:
                        detrend_method = "spline"
                    
                    if taper_type == 0:
                        taper_type = 'hann'

                    success = ans_proc.mseed2sac(mseed, sacfile,
                    detrend=detrend, detrend_method=detrend_method,
                    detrend_order=detrend_order, dspline=dspline,
                    taper=taper, taper_type=taper_type, taper_max_perc=taper_max_perc,
                    SAC=SAC)


                elif success and pid == [2,1]:
                    print(f"    Process #{i+1}: Decimate (SAC method)")

                    final_sampling_freq = process['cmb_mseed2sac_final_sf']
                    if final_sampling_freq == 1:
                        final_sampling_freq = 2
                    elif final_sampling_freq == 2:
                        final_sampling_freq = 5
                    elif final_sampling_freq == 3:
                        final_sampling_freq = 10
                    elif final_sampling_freq == 4:
                        final_sampling_freq = 20
                    else:
                        final_sampling_freq = 1

                    success = ans_proc.sac_decimate(sacfile, sacfile, final_sampling_freq,
                    SAC=SAC)

                elif success and pid == [2,2]:
                    print(f"    Process #{i+1}: Decimate (ObsPy method)")

                    final_sampling_freq = process['cmb_mseed2sac_final_sf']
                    if final_sampling_freq == 1:
                        final_sampling_freq = 2
                    elif final_sampling_freq == 2:
                        final_sampling_freq = 5
                    elif final_sampling_freq == 3:
                        final_sampling_freq = 10
                    elif final_sampling_freq == 4:
                        final_sampling_freq = 20
                    else:
                        final_sampling_freq = 1

                    success = ans_proc.obspy_decimate(sacfile, sacfile, final_sampling_freq, SAC=SAC)

                elif success and pid == [3,1]:
                    print(f"    Process #{i+1}: Remove instrument response")

                    # find appropriate xml file
                    xmldir = process['le_mseed2sac_stametadir']
                    xmldir_2 = os.path.join(maindir, 'mseeds', get_event_name(mseed))
                    unit = process['cmb_mseed2sac_resp_output']
                    prefilter = process['cmb_mseed2sac_resp_prefilter']
                    if unit == 0:
                        unit = 'DISP'
                    elif unit == 1:
                        unit = 'VEL'
                    elif unit == 2:
                        unit = 'ACC'

                    if prefilter == 0:
                        prefilter = None
                    elif prefilter == 1:
                        prefilter = (0.005, 0.006, 30.0, 35.0)

                    st = obspy.read(sacfile, headonly=True)
                    net = st[0].stats.network
                    sta = st[0].stats.station
                    chn = st[0].stats.channel
                    xml_fname = f"{net}.{sta}.{chn}"
                    if os.path.isfile(os.path.join(xmldir, xml_fname)):
                        xml_file = os.path.join(xmldir, xml_fname)
                    elif os.path.isfile(os.path.join(xmldir_2, xml_fname)):
                        xml_file = os.path.join(xmldir_2, xml_fname)
                    else:
                        print(f"    Error! Meta data was not found: {xml_fname}")
                        success = False
                        continue

                    success = ans_proc.sac_remove_response(sacfile, sacfile, xml_file,
                                                       unit=unit, prefilter=prefilter,
                                                       SAC=SAC)

                elif success and pid == [4,1]:
                    print(f"    Process #{i+1}: Bandpass filter")

                    cp1 = process['le_mseed2sac_bp_cp1']
                    cp2 = process['le_mseed2sac_bp_cp2']
                    n = process['sb_mseed2sac_bp_poles']
                    p = process['sb_mseed2sac_bp_passes']
                    
                    success = ans_proc.sac_bandpass_filter(sacfile, sacfile,
                                        cp1=cp1, cp2=cp2, n=n, p=p,
                                        SAC=SAC)

                elif success and pid == [5,1]:
                    print(f"    Process #{i+1}: Cut seismograms")
                    try:
                        cut_begin = float(process['le_mseed2sac_cut_begin'])
                        cut_end = float(process['le_mseed2sac_cut_end'])
                    except Exception as e:
                        print(f"    Error! Cut begin/end values are not set properly!")
                        success = False

                    success = ans_proc.sac_cut_fillz(sacfile, sacfile, cut_begin, cut_end, SAC=SAC)

                elif success and pid == [6,1]:
                    print(f"    Process #{i+1}: Detrend seismograms")

                    detrend_method = process['cmb_mseed2sac_detrend_method']
                    detrend_order = int(process['sb_mseed2sac_detrend_order'])
                    dspline = int(process['le_mseed2sac_dspline'])
                    
                    if detrend_method == 0:
                        detrend_method = "demean"
                    elif detrend_method == 1:
                        detrend_method = "linear"
                    elif detrend_method == 2:
                        detrend_method = "polynomial"
                    elif detrend_method == 3:
                        detrend_method = "spline"


                    success = ans_proc.sac_detrend(sacfile, sacfile,
                              detrend_method=detrend_method, detrend_order=detrend_order, dspline=dspline)

                elif success and pid == [7,1]:
                    print(f"    Process #{i+1}: Write SAC headers")

                    xmldir = process['le_mseed2sac_stametadir']
                    xmldir_2 = os.path.join(maindir, 'mseeds', get_event_name(mseed))

                    st = obspy.read(sacfile, headonly=True)
                    net = st[0].stats.network
                    sta = st[0].stats.station
                    chn = st[0].stats.channel
                    xml_fname = f"{net}.{sta}.{chn}"
                    if os.path.isfile(os.path.join(xmldir, xml_fname)):
                        xml_file = os.path.join(xmldir, xml_fname)
                    elif os.path.isfile(os.path.join(xmldir_2, xml_fname)):
                        xml_file = os.path.join(xmldir_2, xml_fname)
                    else:
                        print(f"    Error! Meta data was not found: {xml_fname}")
                        success = False
                        continue

                    inv = obspy.read_inventory(xml_file)
                    headers = {}
                    headers['knetwk'] = inv[0].code.split()[0]
                    headers['kstnm'] = inv[0][0].code.split()[0]
                    headers['kcmpnm'] = inv[0][0][0].code.split()[0]
                    headers['stla'] = float(inv[0][0].latitude)
                    headers['stlo'] = float(inv[0][0].longitude)
                    headers['stel'] = float(inv[0][0].elevation)
                    headers['cmpaz'] = float(inv[0][0][0].azimuth)
                    headers['cmpinc'] = float(inv[0][0][0].dip)+90

                    success = ans_proc.write_sac_headers(sacfile, headers, SAC=SAC)

                elif success and pid == [8,1]:
                    print(f"    Process #{i+1}: Remove extra channels")

                    event_folder = os.path.join(output_sacs_dir, get_event_name(mseed))
                    similar_channels = process['le_mseed2sac_similar_channels'].split()
                    channels2keep = process['le_mseed2sac_channels2keep'].split()
                    num_deleted += ans_proc.sac_remove_extra_channels(sacs_event_dir=event_folder,
                                                   similar_channels=similar_channels,
                                                   channels2keep=channels2keep)

            if not success and os.path.isfile(sacfile):
                os.remove(sacfile)
            else:
                num_outputs += 1

    print(f"\nSAC dataset: {output_sacs_dir}\nTotal number of MSEED files: {len(mseeds)}\nNumber of final output SAC files: {num_outputs - num_deleted}\n\nDone!\n")

    finalize_sac_directories(output_sacs_dir, mseeds)


#========================#


def generate_mseed_list(mseeds_dir):
    mseed_list = []
    if not os.path.isdir(mseeds_dir):
        print("\nError! Could not find mseeds_dir:\n{mseeds_dir}\n\n")
    for x in os.listdir(mseeds_dir):

        if os.path.isdir(os.path.join(mseeds_dir, x)):
            if regex_events.match(x):
                for xx in os.listdir(os.path.join(mseeds_dir, x)):
                    if regex_mseeds.match(xx):
                        mseed_list.append(os.path.join(mseeds_dir, x, xx)) 
        else:
            if regex_mseeds.match(x):
                mseed_list.append(os.path.join(mseeds_dir, x))
    return sorted(mseed_list)


def get_sac_name(mseed_file):
    event_name = get_event_name(mseed_file)
    mseed_file = os.path.split(mseed_file)[1]
    sac_name = "%s_%s.%s" %(event_name, mseed_file.split('_')[0].split('.')[1], mseed_file.split('_')[0].split('.')[3])
    return sac_name



def get_event_name(mseed_file):
    mseed_file = os.path.split(mseed_file)[1]
    event_utc_time = obspy.UTCDateTime(mseed_file.split('_')[2])
    event_name = "%02d%03d%02d%02d%02d" %(int(str(event_utc_time.year)[2:]),
                                        event_utc_time.julday,
                                        event_utc_time.hour,
                                        event_utc_time.minute,
                                        event_utc_time.second)
    return event_name



def initialize_sac_directories(sacs_maindir, mseed_list):
    if not os.path.isdir(sacs_maindir):
        os.mkdir(sacs_maindir)
    for mseed in mseed_list:
        event_name = get_event_name(mseed)
        event_dir = os.path.join(sacs_maindir, event_name)
        if not os.path.isdir(event_dir):
            os.mkdir(event_dir)



def is_true(value):
    value = int(value)
    if value < 1:
        return False
    else:
        return True



def finalize_sac_directories(sacs_maindir, mseed_list):
    for mseed in mseed_list:
        event_dir = os.path.join(sacs_maindir, get_event_name(mseed))
        if os.path.isdir(event_dir):
            if not len(os.listdir(event_dir)):
                shutil.rmtree(event_dir)
    if not len(os.listdir(sacs_maindir)):
        shutil.rmtree(sacs_maindir)
        print("Error! No sac files were generated!\n")



