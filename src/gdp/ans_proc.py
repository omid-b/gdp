# sac and mseed file process functions using SAC and ObsPy

import os
import sys
import obspy
import numpy as np
import subprocess


def mseed2sac(input_mseed_file, output_sac_file,
    detrend=True, detrend_method='spline', detrend_order=4, dspline=86400,
    taper=True, taper_type='hann', taper_max_perc=0.050,
    SAC='/usr/local/sac/bin/sac'):
    
    try:
        st = obspy.read(input_mseed_file, format="MSEED")

        # start handling data fragmentation issue
        st.sort(['starttime'])
        
        data_starttime = obspy.UTCDateTime(st[0].stats.starttime)
        data_endtime = obspy.UTCDateTime(st[-1].stats.endtime)
        request_starttime = obspy.UTCDateTime(os.path.split(input_mseed_file)[1].split('_')[2]) # obspy.UTCDateTime()
        request_endtime = obspy.UTCDateTime(os.path.split(input_mseed_file)[1].split('_')[4].split('.')[0]) # obspy.UTCDateTime()
        request_length = int(request_endtime - request_starttime)
        begin_data = int(data_starttime.hour*3600 +
                         data_starttime.minute*60 +
                         data_starttime.second)
        begin_request = int(request_starttime.hour*3600 +
                            request_starttime.minute*60 +
                            request_starttime.second)

        if detrend:
            if detrend_method == 'spline':
                try:
                    st.detrend(detrend_method, order=detrend_order, dspline=dspline)
                except:
                    st.detrend('demean')
            elif detrend_method == 'polynomial':
                try:
                    st.detrend(detrend_method, order=detrend_order)
                except:
                    st.detrend('demean')
            else:
                st.detrend(detrend_method)

        if taper:
            st.taper(taper_max_perc)

        if len(st) > 1:# fix data fragmentation issue
            st.merge(method=1, fill_value=0)

        
        # set sac begin time and write to file
        st[0].stats.sac = obspy.core.AttribDict()
        st[0].stats.sac.b = begin_data
        st[0].stats.sac.iztype = 9
        st[0].stats.sac.lovrok = True
        st[0].stats.sac.lcalda = True
        st[0].write(output_sac_file, format='SAC')
        
        # cut to correct b to e and fill with zeros
        shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
        shell_cmd.append(f"cuterr fillz")
        shell_cmd.append(f"cut {begin_request} {begin_request + request_length}")
        shell_cmd.append(f"r {output_sac_file}")
        shell_cmd.append(f"w over")
        shell_cmd.append(f"q")
        shell_cmd.append('EOF')
        shell_cmd = '\n'.join(shell_cmd)
        subprocess.call(shell_cmd, shell=True)

        # reload sac file, set sac begin time to zero, correct sac kztime, and write to file
        st = obspy.read(output_sac_file, format='SAC')
        st[0].stats.sac = obspy.core.AttribDict()
        st[0].stats.sac.b = 0
        st[0].stats.starttime = request_starttime
        st[0].write(output_sac_file, format='SAC')

        return True
    
    except Exception as e:
        return False



def sac_detrend(input_mseed_file, output_sac_file,
    detrend_method='spline', detrend_order=4, dspline=86400):
    try:
        st = obspy.read(input_mseed_file, format="SAC")
        if detrend_method == 'spline':
            try:
                st.detrend(detrend_method, order=detrend_order, dspline=dspline)
            except:
                st.detrend('demean')
        elif detrend_method == 'polynomial':
            try:
                st.detrend(detrend_method, order=detrend_order)
            except:
                st.detrend('demean')
        else:
            st.detrend(detrend_method)

        st.write(output_sac_file, format='SAC')

        return True
    
    except Exception as e:
        return False



def sac_remove_extra_channels(sacs_event_dir, similar_channels, channels2keep):
    for channel in channels2keep:
        if channel not in similar_channels:
            print("return 0")
            return 0

    event_name = os.path.basename(sacs_event_dir)
    num_deleted = 0
    fname_uniq = []
    for f in os.listdir(sacs_event_dir):
        fname = os.path.splitext(f)[0]
        if fname not in fname_uniq:
            fname_uniq.append(fname)
    for fname in fname_uniq:
        fname_exist = []
        for channel in similar_channels:
            if os.path.isfile(os.path.join(sacs_event_dir, f"{fname}.{channel}")):
                fname_exist.append(True)
            else:
                fname_exist.append(False)
        if all(fname_exist):
            for channel in similar_channels:
                if channel not in  channels2keep:
                    os.remove(os.path.join(sacs_event_dir, f"{fname}.{channel}"))
                    num_deleted += 1
    return num_deleted



def sac_decimate(input_sacfile, output_sacfile, final_sampling_freq,
    SAC='/usr/local/sac/bin/sac'):
    try:
        st = obspy.read(input_sacfile, format="SAC", headonly=True)
        initial_sf = int(st[0].stats.sampling_rate)
        f0 = initial_sf
        # find divisors
        divisors = []
        for d in range(2, initial_sf+1):
            if initial_sf % d == 0 and d <= 7:
                divisors.append(d)
        divisors.sort(reverse=True)

        # find decimate factors
        decimate_factors = []
        while initial_sf != final_sampling_freq:
            for divisor in divisors:
                if (initial_sf/divisor) % final_sampling_freq == 0:
                    decimate_factors.append(divisor)
                    break
            initial_sf = int(initial_sf/decimate_factors[-1])

        # build and run shell script
        shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF", f"r {input_sacfile}"]
        for df in decimate_factors:
            shell_cmd.append(f"decimate {df}")

        if input_sacfile == output_sacfile:
            shell_cmd.append("w over")
        else:
            shell_cmd.append(f"w {output_sacfile}")

        shell_cmd.append('quit')
        shell_cmd.append('EOF')
        shell_cmd = '\n'.join(shell_cmd)
        subprocess.call(shell_cmd, shell=True)
        
        # check the output file
        # st = obspy.read(output_sacfile, format="SAC", headonly=True)
        # if not float(st[0].stats.sampling_rate) == float(final_sampling_freq):
        #     return False

        return True

    except Exception as e:
        return False



def obspy_decimate(input_sacfile, output_sacfile, final_sampling_freq, SAC='/usr/local/sac/bin/sac'):
    try:
        st = obspy.read(input_sacfile, format="SAC")
        sac_begin = st[0].stats.sac.b
        sac_end = st[0].stats.sac.e
        st.resample(float(final_sampling_freq))
        st.write(output_sacfile, format='SAC')

        # obspy would mess with sac end time, let's fix that!
        sac_cut_fillz(output_sacfile, output_sacfile, sac_begin, sac_end, SAC=SAC)

        # check the output file
        st = obspy.read(output_sacfile, format="SAC", headonly=True)
        if float(st[0].stats.sampling_rate) == float(final_sampling_freq):
            return True
        else:
            return False

    except Exception as e:
        return False



def sac_remove_response(input_sacfile, output_sacfile, xml_file,
    unit='VEL', prefilter=(0.005, 0.006, 30.0, 35.0), SAC='/usr/local/sac/bin/sac', update_headers=True):
    try:
        inv = obspy.read_inventory(xml_file)
        st = obspy.read(input_sacfile)
        st.remove_response(inventory=inv, output=unit, pre_filt=prefilter)
        st.write(output_sacfile, format='SAC')
        # update sac headers
        if update_headers:
            headers = {}
            headers['knetwk'] = inv[0].code.split()[0]
            headers['kstnm'] = inv[0][0].code.split()[0]
            headers['kcmpnm'] = inv[0][0][0].code.split()[0]
            headers['stla'] = float(inv[0][0].latitude)
            headers['stlo'] = float(inv[0][0].longitude)
            headers['stel'] = float(inv[0][0].elevation)
            headers['cmpaz'] = float(inv[0][0][0].azimuth)
            headers['cmpinc'] = float(inv[0][0][0].dip)+90
            write_sac_headers(output_sacfile, headers, SAC=SAC)
        return True
    except Exception as e:
        return False



def sac_bandpass_filter(input_sacfile, output_sacfile,
    cp1, cp2, n=3, p=2,
    SAC='/usr/local/sac/bin/sac'):
    try:
        if cp1 > cp2:
            return False
        else:
            cf1 = 1 / cp2
            cf2 = 1 / cp1
        shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF", f"r {input_sacfile}"]
        shell_cmd.append(f'bp co {cf1} {cf2} n {n} p {p}')
        if input_sacfile == output_sacfile:
            shell_cmd.append('w over')
        else:
            shell_cmd.append(f'w {output_sacfile}')
        shell_cmd.append('quit')
        shell_cmd.append('EOF')
        shell_cmd = '\n'.join(shell_cmd)
        subprocess.call(shell_cmd, shell=True)
        
        return True
    except Exception as e:
        return False


def sac_cut_fillz(input_sacfile, output_sacfile,
    cut_begin, cut_end, SAC='/usr/local/sac/bin/sac'):
    try:
        if cut_begin > cut_end:
            return False

        shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
        shell_cmd.append(f"cuterr fillz")
        shell_cmd.append(f"cut {cut_begin} {cut_end}")
        shell_cmd.append(f"r {input_sacfile}")
        if input_sacfile == output_sacfile:
            shell_cmd.append('w over')
        else:
            shell_cmd.append(f'w {output_sacfile}')
        shell_cmd.append('quit')
        shell_cmd.append('EOF')
        shell_cmd = '\n'.join(shell_cmd)
        subprocess.call(shell_cmd, shell=True)


        return True
    except Exception as e:
        return False



def sac_one_bit_normalize(input_sacfile, output_sacfile, SAC='/usr/local/sac/bin/sac'):
    try:
        abssac = os.path.join(os.path.split(output_sacfile)[0], 'abs.sac')
        shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
        shell_cmd.append(f'r {input_sacfile}')
        shell_cmd.append(f'abs')
        shell_cmd.append(f'add 1e-10')
        shell_cmd.append(f'w {abssac}')
        shell_cmd.append(f'r {input_sacfile}')
        shell_cmd.append(f'divf {abssac}')
        shell_cmd.append(f'w {output_sacfile}')
        shell_cmd.append('quit')
        shell_cmd.append('EOF')
        shell_cmd = '\n'.join(shell_cmd)
        subprocess.call(shell_cmd, shell=True)
        os.remove(abssac)
        return True
    except Exception as e:
        return False



def sac_whiten(input_sacfile, output_sacfile, whiten_order, SAC='/usr/local/sac/bin/sac'):
    try:
        shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
        shell_cmd.append(f"r {input_sacfile}")
        shell_cmd.append(f"whiten {whiten_order}")
        if input_sacfile == output_sacfile:
            shell_cmd.append('w over')
        else:
            shell_cmd.append(f'w {output_sacfile}')
        shell_cmd.append('quit')
        shell_cmd.append('EOF')
        shell_cmd = '\n'.join(shell_cmd)
        subprocess.call(shell_cmd, shell=True)

        return True
    except Exception as e:
        return False


def write_sac_headers(sacfile, headers, SAC='/usr/local/sac/bin/sac'):
    # INPUTS: full path to sac file; sac headers in python dictionary format
    # OUTPUT: the same sacfile with modified headers
    try:
        shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
        shell_cmd.append(f"r {sacfile}")
        for hdr in headers:
            shell_cmd.append(f"chnhdr {hdr} {headers[hdr]}")
        shell_cmd.append(f"wh")
        shell_cmd.append(f"q")
        shell_cmd.append('EOF')
        shell_cmd = '\n'.join(shell_cmd)
        subprocess.call(shell_cmd, shell=True)

        return True
    except Exception as e:
        return False



