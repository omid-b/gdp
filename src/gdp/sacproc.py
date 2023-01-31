
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


def get_sacfiles_info(sacfiles, header=False, read_headers=False, read_data=False):
    for sacfile in sacfiles:
        if not os.path.isfile(sacfile):
            print(f"Error! Could not find/read sacfile:\n{sacfile}\n")
            exit(1)
    sacfiles_info = {}
    warnings = 0
    for sacfile in sacfiles:
        event_dir = os.path.basename(os.path.split(sacfile)[0])
        try:
            if read_data:
                st = obspy.read(sacfile, format="SAC")
            else:
                st = obspy.read(sacfile, format="SAC", headonly=True)
            tr = st[0]
            knetwk = tr.stats.sac.knetwk
            kstnm = tr.stats.sac.kstnm
            kcmpnm = tr.stats.sac.kcmpnm
            tag = f"{knetwk}.{kstnm}.{kcmpnm}"
            sacfiles_info[f"{sacfile}"] = {}
            sacfiles_info[f"{sacfile}"]['tag'] = tag
            sacfiles_info[f"{sacfile}"]['event'] = event_dir
            if header != False:
                sacfiles_info[f"{sacfile}"][header] = tr.stats.sac[header]

            if read_headers:
                stla = tr.stats.sac.stla
                stlo = tr.stats.sac.stlo
                stel = tr.stats.sac.stel
                evla = tr.stats.sac.evla
                evlo = tr.stats.sac.evlo
                evdp = tr.stats.sac.evdp
                o = tr.stats.sac.o
                gcarc = tr.stats.sac.gcarc
                az = tr.stats.sac.az
                baz = tr.stats.sac.baz
                sacfiles_info[f"{sacfile}"]['knetwk'] = knetwk
                sacfiles_info[f"{sacfile}"]['kstnm'] = kstnm
                sacfiles_info[f"{sacfile}"]['kcmpnm'] = kcmpnm
                sacfiles_info[f"{sacfile}"]['stla'] = float(stla)
                sacfiles_info[f"{sacfile}"]['stlo'] = float(stlo)
                sacfiles_info[f"{sacfile}"]['stel'] = float(stel)
                sacfiles_info[f"{sacfile}"]['evla'] = float(evla)
                sacfiles_info[f"{sacfile}"]['evlo'] = float(evlo)
                sacfiles_info[f"{sacfile}"]['evdp'] = float(evdp)
                sacfiles_info[f"{sacfile}"]['o'] = float(o)
                sacfiles_info[f"{sacfile}"]['gcarc'] = float(gcarc)
                sacfiles_info[f"{sacfile}"]['az'] = float(az)
                sacfiles_info[f"{sacfile}"]['baz'] = float(baz)
            if read_data:
                times = st[0].times()
                data = st[0].data
                sacfiles_info[f"{sacfile}"]['times'] = times
                sacfiles_info[f"{sacfile}"]['data'] = data

        except:
            print(f"WARNING! Could not read sacfile headers/data: {sacfile}")
            warnings += 1
    if warnings == len(sacfiles):
        print('\nError! All sacfiles were skipped due to header/data issue.\nHint: make sure all station and event-related headers are written into sacfiles (use "saclst").\n')
        exit()
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
        # mag_type = events_read['mag_type'][i]
        # if mag_type.lower() == 'mb':
        #     imagtyp=52
        # elif mag_type.lower() == 'ms':
        #     imagtyp=53
        # elif mag_type.lower() == 'ml':
        #     imagtyp=54
        # elif mag_type.lower() == 'mw':
        #     imagtyp=55
        # elif mag_type.lower() == 'md':
        #     imagtyp=56
        # else:
        #     imagtyp=57
        events_info[f"{event_name}"] = {
            'evla': evla,
            'evlo': evlo,
            'evdp': evdp,
            'mag': mag
            # 'imagtyp': int(imagtyp)
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
    import operator
    from obspy.taup import TauPyModel
    try:
        from . import _geographic as geographic
    except ImportError:
        print("WARNING! Could not use cythonized module: geographic")
        from . import geographic
    
    if args.sac == 'auto':
        SAC = dependency.find_sac_path()
    else:
        SAC = args.sac
    if not len(SAC):
        print("Error! Could not find SAC executable! This operation requires SAC to be installed.")
        print("Use flag 'sac' to fix this issue.")
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
            #headers['imagtyp'] = events_info[f"{event_name}"]['imagtyp']
            if args.refmodel != None:
                model = TauPyModel(model=args.refmodel)
                point1 = geographic.Point(headers['evlo'], headers['evla'])
                point2 = geographic.Point(headers['stlo'], headers['stla'])
                line = geographic.Line(point1, point2)
                gcarc = line.calc_gcarc()

                # P arrivals
                ttp = model.get_travel_times(
                    source_depth_in_km=events_info[f"{event_name}"]['evdp'],
                    distance_in_degree=gcarc,
                    phase_list=["ttp"]
                )
                arrivals_p = {}
                for i in range(len(ttp)):
                    arrivals_p[f"{ttp[i].name}"] = float(ttp[i].time)
                # sort by value:
                sorted_arrivals_p = sorted(arrivals_p.items(), key=operator.itemgetter(1))
                arrivals_p = {}
                for (key, val) in sorted_arrivals_p:
                    arrivals_p[key] = val

                # S arrivals
                tts = model.get_travel_times(
                    source_depth_in_km=events_info[f"{event_name}"]['evdp'],
                    distance_in_degree=gcarc,
                    phase_list=["tts"]
                )
                arrivals_s = {}
                for i in range(len(tts)):
                    arrivals_s[f"{tts[i].name}"] = float(tts[i].time)
                # sort by value:
                sorted_arrivals_s = sorted(arrivals_s.items(), key=operator.itemgetter(1))
                arrivals_s = {}
                for (key, val) in sorted_arrivals_s:
                    arrivals_s[key] = val

                # store arrival times into 'headers' dictionaries
                iP = 1
                for p_phase in arrivals_p.keys():
                    if iP <= 2:
                        headers[f"T{iP}"] = arrivals_p[p_phase]
                        headers[f"KT{iP}"] = p_phase
                        iP += 1
                iS = 3
                for s_phase in arrivals_s.keys():
                    if iS <= 4 and s_phase not in ['SKKS', 'PKS']:
                        headers[f"T{iS}"] = arrivals_s[s_phase]
                        headers[f"KT{iS}"] = s_phase
                        iS += 1
                iS = 5
                for s_phase in arrivals_s.keys():
                    if s_phase in ['SKKS', 'PKS']:
                        headers[f"T{iS}"] = arrivals_s[s_phase]
                        headers[f"KT{iS}"] = s_phase
                        iS += 1

                arrivals_saved = []
                for key in headers.keys():
                    if key[0:2] == 'KT':
                        arrivals_saved.append(headers[key])
                i=7
                for p_phase in arrivals_p.keys():
                    if i <= 9 and p_phase not in arrivals_saved:
                        headers[f"T{i}"] = arrivals_p[p_phase]
                        headers[f"KT{i}"] = p_phase
                        i += 1
                for s_phase in arrivals_s.keys():
                    if i <= 9 and s_phase not in arrivals_saved:
                        headers[f"T{i}"] = arrivals_s[s_phase]
                        headers[f"KT{i}"] = s_phase
                        i += 1
        else:
            headers['o'] = ""

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
    args.pre_filt = (args.pre_filt[0],
                      args.pre_filt[1],
                      args.pre_filt[2],
                      args.pre_filt[3])
    if args.pre_filt == (0., 0., 0., 0.):
        args.pre_filt = None
    print("")
    nerr = 0
    errors = []
    for sacfile in sacfiles:
        tag = sacfiles_info[sacfile]['tag']
        xml = metadata_info[tag][0]
        print(f"remresp: '{sacfile}' ... ", end="\r")
        remresp_success = sac_remove_response(sacfile, sacfile, xml,
                                              unit=args.unit,
                                              pre_filt=args.pre_filt,
                                              water_level=args.water_level,
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



    
def resample(args):
    if args.sac == 'auto':
        SAC = dependency.find_sac_path()
    else:
        SAC = args.sac
    if not len(SAC):
        print("Error! Could not find SAC executable! This operation requires SAC to be installed.")
        print("Use flag 'sac' to fix this issue.")
        exit(1)

    sacfiles_info = get_sacfiles_info(args.input_files)
    sacfiles = list(sacfiles_info.keys())

    # start resample process
    nerr = 0
    errors = []
    for sacfile in sacfiles:
        print(f"resample: '{sacfile}' ... ", end="\r")
        resample_success = obspy_decimate(sacfile, sacfile, args.sf, SAC=SAC)

        if resample_success:
            print(f"resample: '{sacfile}' ... OK")
        else:
            nerr += 1
            errors.append(sacfile)
            print(f"resample: '{sacfile}' ... Failed")

    if nerr == 0:
        print("\nall successful!\n")
    else:
        print("\nnumber of errors: {nerr}\nsee 'resample_errors.txt'")
        fopen = open('resample_errors.txt', 'a')
        for err in errors:
            fopen.write(f"{err}\n")
        fopen.close()

    
def bandpass(args):
    if args.sac == 'auto':
        SAC = dependency.find_sac_path()
    else:
        SAC = args.sac
    if not len(SAC):
        print("Error! Could not find SAC executable! This operation requires SAC to be installed.")
        print("Use flag 'sac' to fix this issue.")
        exit(1)

    if args.c1 > args.c2:
        print(f"Error! argument 'c2' must be larger than 'c1'.\n")
        exit(1)

    if args.n not in range(1,11):
        print(f"Error! Number of poles ('n') must be in 1-10 range.\n")
        exit(1)

    if args.p not in [1, 2]:
        print(f"Error! Number of passes ('p') must be in [1, 2].\n")
        exit(1)

    sacfiles_info = get_sacfiles_info(args.input_files)
    sacfiles = list(sacfiles_info.keys())

    # start bandpass filtering process
    nerr = 0
    errors = []
    if args.unit.lower() == 'p':
        cp1 = args.c1
        cp2 = args.c2
    elif args.unit.lower() == 'f':
        cp1 = 1 / args.c2
        cp2 = 1 / args.c1

    for sacfile in sacfiles:
        print(f"bandpass: '{sacfile}' ... ", end="\r")



        bandpass_success = sac_bandpass_filter(sacfile, sacfile,
                           cp1, cp2, n=args.n, p=args.p, SAC=SAC)

        if bandpass_success:
            print(f"bandpass: '{sacfile}' ... OK")
        else:
            nerr += 1
            errors.append(sacfile)
            print(f"bandpass: '{sacfile}' ... Failed")

    if nerr == 0:
        print("\nall successful!\n")
    else:
        print("\nnumber of errors: {nerr}\nsee 'bandpass_errors.txt'")
        fopen = open('bandpass_errors.txt', 'a')
        for err in errors:
            fopen.write(f"{err}\n")
        fopen.close()

    
def cut(args):
    if args.sac == 'auto':
        SAC = dependency.find_sac_path()
    else:
        SAC = args.sac
    if not len(SAC):
        print("Error! Could not find SAC executable! This operation requires SAC to be installed.")
        print("Use flag 'sac' to fix this issue.")
        exit(1)

    if args.begin > args.end:
        print(f"Error! 'end' must be larger than 'begin'.\n")
        exit(1)

    sacfiles_info = get_sacfiles_info(args.input_files)
    sacfiles = list(sacfiles_info.keys())

    # start cut process
    nerr = 0
    errors = []
    for sacfile in sacfiles:
        print(f"cut: '{sacfile}' ... ", end="\r")

        cut_success = sac_cut_fillz(sacfile, sacfile,
                      args.begin, args.end, SAC=SAC)

        if cut_success:
            print(f"cut: '{sacfile}' ... OK")
        else:
            nerr += 1
            errors.append(sacfile)
            print(f"cut: '{sacfile}' ... Failed")

    if nerr == 0:
        print("\nall successful!\n")
    else:
        print("\nnumber of errors: {nerr}\nsee 'cut_errors.txt'")
        fopen = open('cut_errors.txt', 'a')
        for err in errors:
            fopen.write(f"{err}\n")
        fopen.close()


def cut_relative(args):
    if args.sac == 'auto':
        SAC = dependency.find_sac_path()
    else:
        SAC = args.sac
    if not len(SAC):
        print("Error! Could not find SAC executable! This operation requires SAC to be installed.")
        print("Use flag 'sac' to fix this issue.")
        exit(1)

    if args.begin > args.end:
        print(f"Error! 'end' must be larger than 'begin'.\n")
        exit(1)

    sacfiles_info = get_sacfiles_info(args.input_files, header=args.relative)
    sacfiles = list(sacfiles_info.keys())

    # start cut process
    nerr = 0
    errors = []
    for sacfile in sacfiles:
        print(f"cut: '{sacfile}' ... ", end="\r")

        if args.relative not in sacfiles_info[sacfile].keys():
            continue

        try:
            cut_beg = float(sacfiles_info[sacfile][args.relative]) + args.begin
            cut_end = float(sacfiles_info[sacfile][args.relative]) + args.end
        except:
            nerr += 1
            errors.append(sacfile)
            print(f"cut: '{sacfile}' ... Failed")
            continue

        cut_success = sac_cut_fillz(sacfile, sacfile,
                      cut_beg, cut_end, SAC=SAC)

        if cut_success:
            print(f"cut: '{sacfile}' ... OK")
        else:
            nerr += 1
            errors.append(sacfile)
            print(f"cut: '{sacfile}' ... Failed")

    if nerr == 0:
        print("\nall successful!\n")
    else:
        print("\nnumber of errors: {nerr}\nsee 'cut_errors.txt'")
        fopen = open('cut_errors.txt', 'a')
        for err in errors:
            fopen.write(f"{err}\n")
        fopen.close()
    
    
def remchan(args):
    for channel in args.onlykeep:
        if channel not in args.channels:
            print(f"Error for channel '{channel}'! Channels listed in 'onlykeep' must be all in 'channels'.")
            exit(1)

    sacfiles_info = get_sacfiles_info(args.input_files)
    sacfiles = list(sacfiles_info.keys())

    # store events_sacs
    events_sacs = {}
    for sacfile in sacfiles:
        tag = sacfiles_info[sacfile]['tag']
        event = sacfiles_info[sacfile]['event']
        event_path = os.path.split(sacfile)[0]
        if event_path not in events_sacs.keys():
            events_sacs[f"{event_path}"] = []
        events_sacs[f"{event_path}"].append(sacfile)
    
    # start sac_remove_extra_channels process
    removed = []
    for event_dir in events_sacs.keys():
        print(f"remchan: '{event_dir}'")
        sacfiles = events_sacs[event_dir]
        removed += remove_extra_channels(sacfiles, sacfiles_info,
                                             args.channels, args.onlykeep)

    print(f"\nnumber of removed files: {len(removed)}\n")
    if len(removed) != 0:
        print("list of removed files are appended to 'remchan_removed.txt'\n")
        fopen = open('remchan_removed.txt', 'a')
        for f in removed:
            fopen.write(f"{f}\n")
        fopen.close()



def remove_extra_channels(sacfiles, sacfiles_info, channels, onlykeep):
    removed = []
    netsta_uniq = []
    for sacfile in sacfiles:
        tag = sacfiles_info[sacfile]['tag']
        netsta = '.'.join(tag.split('.')[0:2])
        if netsta not in netsta_uniq:
            netsta_uniq.append(netsta)
    netsta_uniq = sorted(netsta_uniq)

    for netsta in netsta_uniq:

        # tags of interest for this netsta
        tags_of_interest = []
        for channel in channels:
            tags_of_interest.append(f"{netsta}.{channel}")
        
        # available tags for this netsta
        tags_available = []
        for sacfile in sacfiles:
            tag = sacfiles_info[sacfile]['tag']
            if netsta in tag and tag not in tags_available:
                tags_available.append(tag)

        # check if all channels of interest are available for this netsta
        all_tags_available = True
        for tag in tags_of_interest:
            if tag not in tags_available:
                all_tags_available = False

        # start remove extra channels
        if all_tags_available:
            for sacfile in sacfiles:
                tag = sacfiles_info[sacfile]['tag']
                chn = tag.split('.')[-1]
                if tag in tags_of_interest and chn not in onlykeep:
                    os.remove(sacfile)
                    removed.append(sacfile)
    return removed



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
    unit='VEL', pre_filt=(0.005, 0.006, 30.0, 35.0), water_level=60, SAC='/usr/local/sac/bin/sac', update_headers=True):
    try:
        inv = obspy.read_inventory(xml_file)
        st = obspy.read(input_sacfile)
        st.remove_response(inventory=inv, output=unit, pre_filt=pre_filt, water_level=water_level)
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

