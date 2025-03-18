
import os
import obspy
import re
import shutil
import subprocess
from . import ans_config
from . import ans_proc
from . import ans_download

#==== MAIN FUNCTION ====#

regex_events = re.compile('^[1-2][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$')
regex_sacs = re.compile('^[1-2][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]\_.*\..*$')
regex_xcorr_RTZ = re.compile('^.*\_.*\.(R|T|Z)$') # xcorr, R, T, and Z components
regex_xcorr = re.compile('^.*\_.*\.(RR|TT|ZZ)$')

def sac2ncf_run_all(maindir, input_sacs_dir, output_ncfs_dir, all=True):
    input_sacs_dir = os.path.abspath(input_sacs_dir)
    output_ncfs_dir = os.path.abspath(output_ncfs_dir)
    conf = ans_config.read_config(maindir)
    SAC = conf['setting']['le_sac']

    stations = ans_download.STATIONS(maindir)
    stalist = stations.read_stalist()

    if not os.path.isdir(output_ncfs_dir):
        os.mkdir(output_ncfs_dir)
    
    events = get_events(input_sacs_dir)
    for event in events:
        xcorr = False
        inp_event = os.path.join(input_sacs_dir, event)
        out_event = os.path.join(output_ncfs_dir, event)
        copy_event(inp_event, out_event)
        for sacfile in get_event_sacs(out_event):
            sacfile_staname = sacfile.split('.')[0].split('_')[1]
            if all == False and sacfile_staname not in stalist['sta']:
                continue

            print(f"\nsac file: {sacfile}")
            sacfile = os.path.join(out_event, sacfile)
            success = True
            for i, process in enumerate(conf['sac2ncf']['sac2ncf_procs']):
                pid = process['pid']
                if success and pid == [1,1]:
                    print(f"    Process #{i+1}: Decimate (SAC method)")

                    final_sampling_freq = process['cmb_sac2ncf_final_sf']
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

                    if not success and os.path.isfile(sacfile):
                        os.remove(sacfile)

                elif success and pid == [1,2]:
                    print(f"    Process #{i+1}: Decimate (ObsPy method)")

                    final_sampling_freq = process['cmb_sac2ncf_final_sf']
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

                    if not success and os.path.isfile(sacfile):
                        os.remove(sacfile)

                elif success and pid == [2,1]:
                    print(f"    Process #{i+1}: Remove instrument response")
                    mseeds = conf['download']['le_mseeds']
                    xmldir = process['le_sac2ncf_stametadir']
                    xmldir_2 = os.path.join(maindir, mseeds, event)
                    unit = process['cmb_sac2ncf_resp_output']
                    prefilter = process['cmb_sac2ncf_resp_prefilter']
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

                    if not success and os.path.isfile(sacfile):
                        os.remove(sacfile)

                elif success and pid == [3,1]:
                    print(f"    Process #{i+1}: Bandpass filter")

                    cp1 = process['le_sac2ncf_bp_cp1']
                    cp2 = process['le_sac2ncf_bp_cp2']
                    n = process['sb_sac2ncf_bp_poles']
                    p = process['sb_sac2ncf_bp_passes']
                    
                    success = ans_proc.sac_bandpass_filter(sacfile, sacfile,
                                        cp1=cp1, cp2=cp2, n=n, p=p,
                                        SAC=SAC)

                    if not success and os.path.isfile(sacfile):
                        os.remove(sacfile)

                elif success and pid == [4,1]:
                    print(f"    Process #{i+1}: Cut seismograms")

                    try:
                        cut_begin = float(process['le_sac2ncf_cut_begin'])
                        cut_end = float(process['le_sac2ncf_cut_end'])
                    except Exception as e:
                        print(f"    Error! Cut begin/end values are not set properly!")
                        success = False

                    success = ans_proc.sac_cut_fillz(sacfile, sacfile, cut_begin, cut_end, SAC=SAC)

                    if not success and os.path.isfile(sacfile):
                        os.remove(sacfile)

                elif success and pid == [5,1]:
                    print(f"    Process #{i+1}: Detrend seismograms")

                    detrend_method = process['cmb_sac2ncf_detrend_method']
                    detrend_order = int(process['sb_sac2ncf_detrend_order'])
                    dspline = int(process['le_sac2ncf_dspline'])
                    
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

                elif success and pid == [6,1]:
                    print(f"    Process #{i+1}: Write SAC headers")

                    xmldir = process['le_sac2ncf_stametadir']

                    st = obspy.read(sacfile, headonly=True)
                    net = st[0].stats.network
                    sta = st[0].stats.station
                    chn = st[0].stats.channel
                    xml_fname = f"{net}.{sta}.{chn}"
                    if os.path.isfile(os.path.join(xmldir, xml_fname)):
                        xml_file = os.path.join(xmldir, xml_fname)
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

                elif success and pid == [7,1]:
                    print(f"    Process #{i+1}: Remove extra channels")

                    similar_channels = process['le_sac2ncf_similar_channels'].split()
                    channels2keep = process['le_sac2ncf_channels2keep'].split()

                    ans_proc.sac_remove_extra_channels(sacs_event_dir=out_event,
                                                   similar_channels=similar_channels,
                                                   channels2keep=channels2keep)

                elif success and pid == [8,1]:
                    print(f"    Process #{i+1}: One-bit normalization")

                    success = ans_proc.sac_one_bit_normalize(sacfile, sacfile, SAC=SAC)

                    if not success and os.path.isfile(sacfile):
                        os.remove(sacfile)

                elif success and pid == [9,1]:
                    print(f"    Process #{i+1}: Spectral whitening")

                    whiten_order = int(process['sb_sac2ncf_whiten_order'])
                    success = ans_proc.sac_whiten(sacfile, sacfile, whiten_order, SAC=SAC)

                    if not success and os.path.isfile(sacfile):
                        os.remove(sacfile)
                elif success and pid == [10,1]:
                    proc_id_xcorr = i+1
                    xcorr =True

        if xcorr:
            print(f"\nProcess #{proc_id_xcorr}: Cross-correlation; Event dir: '{event}'\n")

            generate_xcorr_RTZ_files(out_event, SAC=SAC)
            perform_xcorr_RTZ(out_event, SAC=SAC)
            # remove extra files after cross-correlation
            remove_all_files_except_regex(out_event, regex_xcorr)


    print("\nDone!\n")
        

#=======================#

def perform_xcorr_RTZ(event_dir, SAC='/usr/local/sac/bin/sac'):
    event_RTZs = get_event_RTZs(event_dir)
    event_sta_pairs = get_event_sta_pairs(event_dir)
    for sta_pair in event_sta_pairs:
        sta1_sta2_R = os.path.join(event_dir, f"{sta_pair[0]}_{sta_pair[1]}.R")
        sta2_sta1_R = os.path.join(event_dir, f"{sta_pair[1]}_{sta_pair[0]}.R")
        sta1_sta2_RR = os.path.join(event_dir, f"{sta_pair[0]}_{sta_pair[1]}.RR")
        sta1_sta2_T = os.path.join(event_dir, f"{sta_pair[0]}_{sta_pair[1]}.T")
        sta2_sta1_T = os.path.join(event_dir, f"{sta_pair[1]}_{sta_pair[0]}.T")
        sta1_sta2_TT = os.path.join(event_dir, f"{sta_pair[0]}_{sta_pair[1]}.TT")
        sta1_sta2_Z = os.path.join(event_dir, f"{sta_pair[0]}_{sta_pair[1]}.Z")
        sta2_sta1_Z = os.path.join(event_dir, f"{sta_pair[1]}_{sta_pair[0]}.Z")
        sta1_sta2_ZZ = os.path.join(event_dir, f"{sta_pair[0]}_{sta_pair[1]}.ZZ")
        tempsac = os.path.join(event_dir, f"temp.sac") # auto correlation file

        # RR
        if os.path.isfile(sta1_sta2_R) and os.path.isfile(sta2_sta1_R):
            shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
            shell_cmd.append(f"r {sta1_sta2_R} {sta2_sta1_R}")
            shell_cmd.append(f"correlate master 1 number 1 normalized")
            shell_cmd.append(f"w {tempsac} {sta1_sta2_RR}")
            shell_cmd.append(f"q")
            shell_cmd.append('EOF')
            shell_cmd = '\n'.join(shell_cmd)
            subprocess.call(shell_cmd, shell=True)
            # update headers
            st1 = obspy.read(sta1_sta2_R, format="SAC", headonly=True)
            st2 = obspy.read(sta2_sta1_R, format="SAC", headonly=True)
            headers = {}
            headers['stla'] = f"{st2[0].stats.sac.stla}"
            headers['stlo'] = f"{st2[0].stats.sac.stlo}"
            headers['stel'] = f"{st2[0].stats.sac.stel}"
            headers['evla'] = f"{st1[0].stats.sac.stla}"
            headers['evlo'] = f"{st1[0].stats.sac.stlo}"
            headers['evel'] = f"{st1[0].stats.sac.stel}"
            headers['kstnm'] = f"{st1[0].stats.sac.kstnm[0:3]}-{st2[0].stats.sac.kstnm[0:3]}"
            headers['knetwk'] = f"{st1[0].stats.sac.knetwk}-{st2[0].stats.sac.knetwk}"
            headers['kcmpnm'] = "RR"
            headers['kevnm'] = f"{st1[0].stats.sac.kstnm}_{st2[0].stats.sac.kstnm}_RR"
            ans_proc.write_sac_headers(sta1_sta2_RR, headers, SAC=SAC)

        # TT
        if os.path.isfile(sta1_sta2_T) and os.path.isfile(sta2_sta1_T):
            shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
            shell_cmd.append(f"r {sta1_sta2_T} {sta2_sta1_T}")
            shell_cmd.append(f"correlate master 1 number 1 normalized")
            shell_cmd.append(f"w {tempsac} {sta1_sta2_TT}")
            shell_cmd.append(f"q")
            shell_cmd.append('EOF')
            shell_cmd = '\n'.join(shell_cmd)
            subprocess.call(shell_cmd, shell=True)
            # update headers
            st1 = obspy.read(sta1_sta2_T, format="SAC", headonly=True)
            st2 = obspy.read(sta2_sta1_T, format="SAC", headonly=True)
            headers = {}
            headers['stla'] = f"{st2[0].stats.sac.stla}"
            headers['stlo'] = f"{st2[0].stats.sac.stlo}"
            headers['stel'] = f"{st2[0].stats.sac.stel}"
            headers['evla'] = f"{st1[0].stats.sac.stla}"
            headers['evlo'] = f"{st1[0].stats.sac.stlo}"
            headers['evel'] = f"{st1[0].stats.sac.stel}"
            headers['kstnm'] = f"{st1[0].stats.sac.kstnm[0:3]}-{st2[0].stats.sac.kstnm[0:3]}"
            headers['knetwk'] = f"{st1[0].stats.sac.knetwk}-{st2[0].stats.sac.knetwk}"
            headers['kcmpnm'] = "TT"
            headers['kevnm'] = f"{st1[0].stats.sac.kstnm}_{st2[0].stats.sac.kstnm}_TT"
            ans_proc.write_sac_headers(sta1_sta2_TT, headers, SAC=SAC)

        # ZZ
        if os.path.isfile(sta1_sta2_Z) and os.path.isfile(sta2_sta1_Z):
            shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
            shell_cmd.append(f"r {sta1_sta2_Z} {sta2_sta1_Z}")
            shell_cmd.append(f"correlate master 1 number 1 normalized")
            shell_cmd.append(f"w {tempsac} {sta1_sta2_ZZ}")
            shell_cmd.append(f"q")
            shell_cmd.append('EOF')
            shell_cmd = '\n'.join(shell_cmd)
            subprocess.call(shell_cmd, shell=True)
            # update headers
            st1 = obspy.read(sta1_sta2_Z, format="SAC", headonly=True)
            st2 = obspy.read(sta2_sta1_Z, format="SAC", headonly=True)
            headers = {}
            headers['stla'] = f"{st2[0].stats.sac.stla}"
            headers['stlo'] = f"{st2[0].stats.sac.stlo}"
            headers['stel'] = f"{st2[0].stats.sac.stel}"
            headers['evla'] = f"{st1[0].stats.sac.stla}"
            headers['evlo'] = f"{st1[0].stats.sac.stlo}"
            headers['evel'] = f"{st1[0].stats.sac.stel}"
            headers['kstnm'] = f"{st1[0].stats.sac.kstnm[0:3]}-{st2[0].stats.sac.kstnm[0:3]}"
            headers['knetwk'] = f"{st1[0].stats.sac.knetwk}-{st2[0].stats.sac.knetwk}"
            headers['kcmpnm'] = "ZZ"
            headers['kevnm'] = f"{st1[0].stats.sac.kstnm}_{st2[0].stats.sac.kstnm}_ZZ"
            ans_proc.write_sac_headers(sta1_sta2_ZZ, headers, SAC=SAC)



def get_event_sta_components(event_dir):
    event_sta_components = {}
    sacfiles = get_event_sacs(event_dir)
    for sacfile in sacfiles:
        try:
            st = obspy.read(os.path.join(event_dir, sacfile), headonly=True)
            kstnm = st[0].stats.sac.kstnm
            if kstnm not in event_sta_components.keys():
                event_sta_components[f'{kstnm}'] = [[], [], []]
        except Exception as e:
            continue

        try:
            cmpaz = float(st[0].stats.sac.cmpaz)
        except:
            kcmpnm = st[0].stats.sac.kcmpnm
            if kcmpnm[-1].upper() == 'E':
                cmpaz = 90.0
            elif kcmpnm[-1].upper() in['N', 'Z']:
                cmpaz = 0.0

        try:
            cmpinc = float(st[0].stats.sac.cmpinc)
        except:
            kcmpnm = st[0].stats.sac.kcmpnm
            if kcmpnm[-1].upper() == 'Z':
                cmpinc = 0.0
            elif kcmpnm[-1].upper() in ['E', 'N']:
                cmpinc = 90.0

        # for ??1 and ??2 components
        if cmpaz> 315 or cmpaz< 45:
            cmpaz = 0
        if cmpaz> 45 and cmpaz< 135:
            cmpaz = 90

        if cmpaz == 0 and cmpinc == 90:
            event_sta_components[f'{kstnm}'][0].append(sacfile)
        elif cmpaz == 90 and cmpinc == 90:
            event_sta_components[f'{kstnm}'][1].append(sacfile)
        elif cmpaz == 0 and cmpinc == 0:
            event_sta_components[f'{kstnm}'][2].append(sacfile)

    return event_sta_components


def get_event_sta_pairs(event_dir):
    event_sta_pairs = []
    event_sta_list = []
    sacfiles = get_event_sacs(event_dir)
    for sacfile in sacfiles:
        try:
            st = obspy.read(os.path.join(event_dir, sacfile), headonly=True)
            kstnm = st[0].stats.sac.kstnm

            if kstnm not in event_sta_list:
                event_sta_list.append(kstnm)
        except:
            pass

    for i, sta1 in enumerate(event_sta_list):
        for j, sta2 in enumerate(event_sta_list):
            if i != j and [sta1, sta2] not in event_sta_pairs\
                      and [sta2, sta1] not in event_sta_pairs:
                event_sta_pairs.append([sta1, sta2])

    return event_sta_pairs




def generate_xcorr_RTZ_files(event_dir, SAC='/usr/local/sac/bin/sac'):
    # generate radial (R), tangential (T), and vertical (Z) components

    event_sta_components = get_event_sta_components(event_dir)
    event_sta_pairs = get_event_sta_pairs(event_dir)

    for sta_pair in event_sta_pairs:
        sta1 = sta_pair[0]
        sta2 = sta_pair[1]

        sta1_Hdata_available = len(event_sta_components[f"{sta1}"][0]) and len(event_sta_components[f"{sta1}"][1])
        sta2_Hdata_available = len(event_sta_components[f"{sta2}"][0]) and len(event_sta_components[f"{sta2}"][1])
        sta1_sta2_Zdata_available = len(event_sta_components[f"{sta1}"][2]) and len(event_sta_components[f"{sta2}"][2])
        
        # generate PPN and PPE (northern and eastern cross-correlation perporcessing sac files)
        if sta1_Hdata_available and sta2_Hdata_available:
            try:
                st_sta1 = obspy.read(os.path.join(event_dir, event_sta_components[f"{sta1}"][0][0]), headonly=True)
                st_sta2 = obspy.read(os.path.join(event_dir, event_sta_components[f"{sta2}"][0][0]), headonly=True)
                sta1_stla = float(st_sta1[0].stats.sac.stla)
                sta1_stlo = float(st_sta1[0].stats.sac.stlo)
                sta1_stel = float(st_sta1[0].stats.sac.stel)

                sta2_stla = float(st_sta2[0].stats.sac.stla)
                sta2_stlo = float(st_sta2[0].stats.sac.stlo)
                sta2_stel = float(st_sta2[0].stats.sac.stel)
            except Exception as e:
                continue
            # sta1_sta2.PPN
            sta1_sta2_PPN = os.path.join(event_dir, f"{sta1}_{sta2}.PPN")
            sta1_sta2_PPN_src = os.path.join(event_dir, event_sta_components[f"{sta1}"][0][0])
            shutil.copyfile(sta1_sta2_PPN_src, sta1_sta2_PPN)
            shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
            shell_cmd.append(f"r {sta1_sta2_PPN}")
            shell_cmd.append(f"chnhdr evla {sta2_stla}")
            shell_cmd.append(f"chnhdr evlo {sta2_stlo}")
            shell_cmd.append(f"chnhdr evel {sta2_stel}")
            shell_cmd.append(f"wh")
            shell_cmd.append('quit')
            shell_cmd.append('EOF')
            shell_cmd = '\n'.join(shell_cmd)
            subprocess.call(shell_cmd, shell=True)

            # sta1_sta2.PPE
            sta1_sta2_PPE = os.path.join(event_dir, f"{sta1}_{sta2}.PPE")
            sta1_sta2_PPE_src = os.path.join(event_dir, event_sta_components[f"{sta1}"][1][0])
            shutil.copyfile(sta1_sta2_PPE_src, sta1_sta2_PPE)
            shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
            shell_cmd.append(f"r {sta1_sta2_PPE}")
            shell_cmd.append(f"chnhdr evla {sta2_stla}")
            shell_cmd.append(f"chnhdr evlo {sta2_stlo}")
            shell_cmd.append(f"chnhdr evel {sta2_stel}")
            shell_cmd.append(f"wh")
            shell_cmd.append('quit')
            shell_cmd.append('EOF')
            shell_cmd = '\n'.join(shell_cmd)
            subprocess.call(shell_cmd, shell=True)

            # sta2_sta1.PPN
            sta2_sta1_PPN = os.path.join(event_dir, f"{sta2}_{sta1}.PPN")
            sta2_sta1_PPN_src = os.path.join(event_dir, event_sta_components[f"{sta2}"][0][0])
            shutil.copyfile(sta2_sta1_PPN_src, sta2_sta1_PPN)
            shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
            shell_cmd.append(f"r {sta2_sta1_PPN}")
            shell_cmd.append(f"chnhdr evla {sta1_stla}")
            shell_cmd.append(f"chnhdr evlo {sta1_stlo}")
            shell_cmd.append(f"chnhdr evel {sta1_stel}")
            shell_cmd.append(f"wh")
            shell_cmd.append('quit')
            shell_cmd.append('EOF')
            shell_cmd = '\n'.join(shell_cmd)
            subprocess.call(shell_cmd, shell=True)

            # sta2_sta1.PPE
            sta2_sta1_PPE = os.path.join(event_dir, f"{sta2}_{sta1}.PPE")
            sta2_sta1_PPE_src = os.path.join(event_dir, event_sta_components[f"{sta2}"][1][0])
            shutil.copyfile(sta2_sta1_PPE_src, sta2_sta1_PPE)
            shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
            shell_cmd.append(f"r {sta2_sta1_PPE}")
            shell_cmd.append(f"chnhdr evla {sta1_stla}")
            shell_cmd.append(f"chnhdr evlo {sta1_stlo}")
            shell_cmd.append(f"chnhdr evel {sta1_stel}")
            shell_cmd.append(f"wh")
            shell_cmd.append('quit')
            shell_cmd.append('EOF')
            shell_cmd = '\n'.join(shell_cmd)
            subprocess.call(shell_cmd, shell=True)

        # generate Z (vertical component cross-correlation perporcessing sac files)
        if sta1_sta2_Zdata_available:
            try:
                st_sta1 = obspy.read(os.path.join(event_dir, event_sta_components[f"{sta1}"][2][0]), headonly=True)
                st_sta2 = obspy.read(os.path.join(event_dir, event_sta_components[f"{sta2}"][2][0]), headonly=True)
                sta1_stla = float(st_sta1[0].stats.sac.stla)
                sta1_stlo = float(st_sta1[0].stats.sac.stlo)
                sta1_stel = float(st_sta1[0].stats.sac.stel)
                
                sta2_stla = float(st_sta2[0].stats.sac.stla)
                sta2_stlo = float(st_sta2[0].stats.sac.stlo)
                sta2_stel = float(st_sta2[0].stats.sac.stel)
            except Exception as e:
                continue

            # sta1_sta2.Z
            sta1_sta2_Z = os.path.join(event_dir, f"{sta1}_{sta2}.Z")
            sta1_sta2_Z_src = os.path.join(event_dir, event_sta_components[f"{sta1}"][2][0])
            shutil.copyfile(sta1_sta2_Z_src, sta1_sta2_Z)
            shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
            shell_cmd.append(f"r {sta1_sta2_Z}")
            shell_cmd.append(f"chnhdr evla {sta2_stla}")
            shell_cmd.append(f"chnhdr evlo {sta2_stlo}")
            shell_cmd.append(f"chnhdr evel {sta2_stel}")
            shell_cmd.append(f"wh")
            shell_cmd.append('quit')
            shell_cmd.append('EOF')
            shell_cmd = '\n'.join(shell_cmd)
            subprocess.call(shell_cmd, shell=True)

            # sta2_sta1.Z
            sta2_sta1_Z = os.path.join(event_dir, f"{sta2}_{sta1}.Z")
            sta2_sta1_Z_src = os.path.join(event_dir, event_sta_components[f"{sta2}"][2][0])
            shutil.copyfile(sta2_sta1_Z_src, sta2_sta1_Z)
            shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
            shell_cmd.append(f"r {sta2_sta1_Z}")
            shell_cmd.append(f"chnhdr evla {sta1_stla}")
            shell_cmd.append(f"chnhdr evlo {sta1_stlo}")
            shell_cmd.append(f"chnhdr evel {sta1_stel}")
            shell_cmd.append(f"wh")
            shell_cmd.append('quit')
            shell_cmd.append('EOF')
            shell_cmd = '\n'.join(shell_cmd)
            subprocess.call(shell_cmd, shell=True)

    # generate radial and tangential components:
    for sta_pair in event_sta_pairs:
        # sta1_sta2
        sta1_sta2_PPN = os.path.join(event_dir, f"{sta_pair[0]}_{sta_pair[1]}.PPN")
        sta1_sta2_PPE = os.path.join(event_dir, f"{sta_pair[0]}_{sta_pair[1]}.PPE")
        sta1_sta2_R = os.path.join(event_dir, f"{sta_pair[0]}_{sta_pair[1]}.R")
        sta1_sta2_T = os.path.join(event_dir, f"{sta_pair[0]}_{sta_pair[1]}.T")
        if os.path.isfile(sta1_sta2_PPN) and os.path.isfile(sta1_sta2_PPE):
            st_PPN = obspy.read(sta1_sta2_PPN, headonly=True)
            st_PPE = obspy.read(sta1_sta2_PPE, headonly=True)
            cmpaz_PPN = float(st_PPN[0].stats.sac.cmpaz)
            cmpaz_PPE = float(st_PPE[0].stats.sac.cmpaz)
            cmpaz_dif = int(round(abs(cmpaz_PPN - cmpaz_PPE), 0))
            if cmpaz_dif in [90, 270]:
                shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
                shell_cmd.append(f"r {sta1_sta2_PPN} {sta1_sta2_PPE}")
                shell_cmd.append("rotate to gcp")
                shell_cmd.append(f"w {sta1_sta2_R} {sta1_sta2_T}")
                shell_cmd.append('quit')
                shell_cmd.append('EOF')
                shell_cmd = '\n'.join(shell_cmd)
                subprocess.call(shell_cmd, shell=True)
            else:
                print(f"ERROR! Horizontal component azimuths are not 90 degrees apart for '{sta_pair[0]}' >> {cmpaz_dif}")

        # sta2_sta1
        sta2_sta1_PPN = os.path.join(event_dir, f"{sta_pair[1]}_{sta_pair[0]}.PPN")
        sta2_sta1_PPE = os.path.join(event_dir, f"{sta_pair[1]}_{sta_pair[0]}.PPE")
        sta2_sta1_R = os.path.join(event_dir, f"{sta_pair[1]}_{sta_pair[0]}.R")
        sta2_sta1_T = os.path.join(event_dir, f"{sta_pair[1]}_{sta_pair[0]}.T")
        if os.path.isfile(sta2_sta1_PPN) and os.path.isfile(sta2_sta1_PPE):
            st_PPN = obspy.read(sta2_sta1_PPN, headonly=True)
            st_PPE = obspy.read(sta2_sta1_PPE, headonly=True)
            cmpaz_PPN = float(st_PPN[0].stats.sac.cmpaz)
            cmpaz_PPE = float(st_PPE[0].stats.sac.cmpaz)
            cmpaz_dif = int(round(abs(cmpaz_PPN - cmpaz_PPE), 0))
            if cmpaz_dif in [90, 270]:
                shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
                shell_cmd.append(f"r {sta2_sta1_PPN} {sta2_sta1_PPE}")
                shell_cmd.append("rotate to gcp")
                shell_cmd.append(f"w {sta2_sta1_R} {sta2_sta1_T}")
                shell_cmd.append('quit')
                shell_cmd.append('EOF')
                shell_cmd = '\n'.join(shell_cmd)
                subprocess.call(shell_cmd, shell=True)
            else:
                print(f"ERROR! Horizontal component azimuths are not 90 degrees apart for '{sta_pair[1]}' >> {cmpaz_dif}")
    



def get_events(dataset_dir):
    event_list = []
    for x in os.listdir(dataset_dir):
        if regex_events.match(x):
            event_list.append(x)
    return sorted(event_list)


def get_event_sacs(event_dir):
    sac_files = []
    for x in os.listdir(event_dir):
        if regex_sacs.match(x):
            sac_files.append(x)
    return sorted(sac_files)


def get_event_RTZs(event_dir):
    rtz_files = []
    for x in os.listdir(event_dir):
        if regex_xcorr_RTZ.match(x):
            rtz_files.append(x)
    return rtz_files


def copy_event(src_event, dst_event):
    if not os.path.isdir(dst_event):
        os.mkdir(dst_event)
    sac_files = get_event_sacs(src_event)
    for sac_file in sac_files:
        src_sac = os.path.join(src_event, sac_file)
        dst_sac = os.path.join(dst_event, sac_file)
        shutil.copyfile(src_sac, dst_sac)


def remove_all_files_except_regex(directory, regex):
    for f in os.listdir(directory):
        if not regex.match(f):
            os.remove(os.path.join(directory, f))

