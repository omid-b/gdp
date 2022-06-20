
import os
import re
import obspy
import subprocess

from . import dependency
from . import download
from . import events

def get_metadata_info(metadata_dir):
    metadata_dir = os.path.abspath(metadata_dir)
    if not os.path.isdir(metadata_dir):
        print(f"Error! Could not find metadata directory:\n{metadata_dir}\n")
        exit(1)
    metadata_info = {}
    for x in os.listdir(metadata_dir):
        xml_file = os.path.join(metadata_dir, x)
        try:
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
            xml_tag = f"{headers['knetwk']}.{headers['kstnm']}.{headers['kcmpnm']}"
            metadata_info[f"{xml_tag}"] = [xml_file, headers]
        except:
            continue
    return metadata_info


def get_sacfiles_info(sacfiles):
    for sacfile in sacfiles:
        if not os.path.isfile(sacfile):
            print(f"Error! Could not find/read sacfile:\n{sacfile}\n")
            exit(1)
    sacfiles_info = {}
    warnings = 0
    for sacfile in sacfiles:
        event_dir = os.path.basename(os.path.split(sacfile)[0])
        try:
            st = obspy.read(sacfile, format="SAC", headonly=True)
            tr = st[0]
            net = tr.stats.sac.knetwk
            sta = tr.stats.sac.kstnm
            chn = tr.stats.sac.kcmpnm
            tag = f"{net}.{sta}.{chn}"
            sacfiles_info[f"{sacfile}"] = {}
            sacfiles_info[f"{sacfile}"]['tag'] = tag
            sacfiles_info[f"{sacfile}"]['event'] = event_dir
        except:
            print(f"WARNING! Could not read sacfile headers: {sacfile}")
            warnings += 1
    if warnings > 0:
        uans = input("\nSome sacfiles could not be read (those will be skipped).\nDo you want to continue (y/n)? ")
        if uans.lower() in ['y', 'yes']:
            print("")
        else:
            print("\nExit program!\n")
            exit(1)
    return sacfiles_info



def get_events_info(sacfiles_info, config):
    # dataset (sacfiles): sacfile and event tags
    dataset_events = []
    events_pattern = '^[0-9][0-9][0-3][0-9][0-9][0-2][0-9][0-5][0-9][0-5][0-9]$'
    events_regex = re.compile(events_pattern)
    for sacfile in sacfiles_info.keys():
        event = sacfiles_info[sacfile]['event']
        if event not in dataset_events and events_regex.match(event):
            dataset_events.append(event)

    # event list (events.dat): event tags
    events_info = {}
    eventlist_events = []
    events_obj = events.EVENTS(config)
    events_read = events_obj.read_events()
    for i, date in enumerate(events_read['date']):
        datetime = f"{date}T{events_read['time'][i]}"
        utcdatetime = obspy.UTCDateTime(datetime)
        event_name = "%02.0f%03d%02d%02d%02d" %(float(str(utcdatetime.year)[2:]),
                                              utcdatetime.julday,
                                              utcdatetime.hour,
                                              utcdatetime.minute,
                                              utcdatetime.second)
        eventlist_events.append(event_name)
        evla = float(events_read['lat'][i])
        evlo = float(events_read['lon'][i])
        evdp = float(events_read['dep'][i])
        mag = float(events_read['mag'][i])
        mag_type = events_read['mag_type'][i]
        if mag_type.lower() == 'mb':
            imagtyp=52
        elif mag_type.lower() == 'ms':
            imagtyp=53
        elif mag_type.lower() == 'ml':
            imagtyp=54
        elif mag_type.lower() == 'mw':
            imagtyp=55
        elif mag_type.lower() == 'md':
            imagtyp=56
        else:
            imagtyp=57
        events_info[f"{event_name}"] = {
            'evla': evla,
            'evlo': evlo,
            'evdp': evdp,
            'mag': mag,
            'imagtyp': int(imagtyp)
        }
    # check if all 'dataset_events' are in 'eventlist_events'
    for dataset_event in dataset_events:
        if dataset_event not in eventlist_events:
            print("  checking event information ... Failed\n")
            print(f"Error! Could not find event information for event '{dataset_event}'")
            print("hint: did you set 'offset' and 'reformat' parameters correctly when running 'mseed2sac'?\n")
            exit(1)

    return events_info


def writehdr(args):
    if args.sac == 'auto':
        SAC = dependency.find_sac_path()
    else:
        SAC = args.sac
    if not len(SAC):
        print("Error! Could not find SAC executable! Use flag 'sac' to fix this issue.")
        print("This operation requires SAC to be installed.")
        exit(1)

    metadata_dir = os.path.abspath(args.metadata)
    print(f"metadata directory: {metadata_dir}\n")
    metadata_info = get_metadata_info(metadata_dir)
    sacfiles_info = get_sacfiles_info(args.input_files)
    sacfiles = list(sacfiles_info.keys())
    # check metadata
    nerr = 0
    errors = []
    print("  checking metadata information ...", end="\r")
    for sacfile in sacfiles:
        tag = sacfiles_info[sacfile]['tag']
        if tag not in metadata_info.keys():
            nerr += 1
            err = f"Error! metadata is not available: '{tag}'"
            if err not in errors:
                errors.append(err)
    if nerr > 0:
        print("  checking metadata information ... Failed\n")
        for err in errors:
            print(err)
        print('\nExit program!\n')
        exit(1)
    else:
        print("  checking metadata information ... OK")
    # check events
    if not args.ant:
        print("  checking event information ...", end="\r")
        config = download.read_download_config(args)
        events_info = get_events_info(sacfiles_info, config)
        print("  checking event information ... OK")


    # start writting sac headers
    print("")
    nerr = 0
    for sacfile in sacfiles:
        tag = sacfiles_info[sacfile]['tag']
        xml = metadata_info[tag][0]
        headers = {}
        headers['knetwk'] = metadata_info[tag][1]['knetwk']
        headers['kstnm'] = metadata_info[tag][1]['kstnm']
        headers['kcmpnm'] = metadata_info[tag][1]['kcmpnm']
        headers['stla'] = metadata_info[tag][1]['stla']
        headers['stlo'] = metadata_info[tag][1]['stlo']
        headers['stel'] = metadata_info[tag][1]['stel']
        headers['cmpaz'] = metadata_info[tag][1]['cmpaz']
        headers['cmpinc'] = metadata_info[tag][1]['cmpinc']
        if not args.ant:
            event_name = sacfiles_info[f"{sacfile}"]['event']
            headers['evla'] = events_info[f"{event_name}"]['evla']
            headers['evlo'] = events_info[f"{event_name}"]['evlo']
            headers['evdp'] = events_info[f"{event_name}"]['evdp']
            headers['mag'] = events_info[f"{event_name}"]['mag']
            headers['imagtyp'] = events_info[f"{event_name}"]['imagtyp']

        print(f"writing sac header: '{sacfile}' ... ", end="\r")
        wh_success = write_sac_headers(sacfile, headers, SAC=SAC)
        if wh_success:
            print(f"writing sac header: '{sacfile}' ... OK")
        else:
            nerr += 1
            print(f"writing sac header: '{sacfile}' ... Failed")

    if nerr == 0:
        print("\nall successful!\n")
    else:
        print("\nnumber of errors: {nerr}\n")
    exit(0)





    
def remresp(args):
    metadata_dir = os.path.abspath(args.metadata)
    print(f"metadata directory: {metadata_dir}\n")
    metadata_info = get_metadata_info(metadata_dir)
    sacfiles_info = get_sacfiles_info(args.input_files)
    sacfiles = list(sacfiles_info.keys())
    # check metadata
    nerr = 0
    errors = []
    print("  checking metadata information ...", end="\r")
    for sacfile in sacfiles:
        tag = sacfiles_info[sacfile]['tag']
        if tag not in metadata_info.keys():
            nerr += 1
            err = f"Error! metadata is not available: '{tag}'"
            if err not in errors:
                errors.append(err)
    if nerr > 0:
        print("  checking metadata information ... Failed\n")
        for err in errors:
            print(err)
        print('\nExit program!\n')
        exit(1)
    else:
        print("  checking metadata information ... OK")

    # start writting sac headers
    args.prefilter = (args.prefilter[0],
                      args.prefilter[1],
                      args.prefilter[2],
                      args.prefilter[3])
    if args.prefilter == (0., 0., 0., 0.):
        args.prefilter = None
    print("")
    nerr = 0
    errors = []
    for sacfile in sacfiles:
        tag = sacfiles_info[sacfile]['tag']
        xml = metadata_info[tag][0]
        print(f"remresp: '{sacfile}' ... ", end="\r")
        remresp_success = sac_remove_response(sacfile, sacfile, xml,
                                              unit=args.unit,
                                              prefilter=args.prefilter,
                                              update_headers=False)
        if remresp_success:
            print(f"remresp: '{sacfile}' ... OK")
        else:
            nerr += 1
            errors.append(sacfile)
            print(f"remresp: '{sacfile}' ... Failed")

    if nerr == 0:
        print("\nall successful!\n")
    else:
        print("\nnumber of errors: {nerr}\nsee 'remresp_errors.txt'")
        fopen = open('remresp_errors.txt', 'a')
        for err in errors:
            fopen.write(f"{err}\n")
        fopen.close()



    
def decimate(args):
    print("Hello from decimate!")
    exit(0)

    
def bandpass(args):
    print("Hello from bandpass!")
    exit(0)

    
def cut(args):
    print("Hello from cut!")
    exit(0)

    
def detrend(args):
    print("Hello from detrend!")
    exit(0)

    
def remchannel(args):
    print("Hello from remchannel!")
    exit(0)



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

