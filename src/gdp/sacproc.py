
import os
import re
import obspy

from . import download
from . import events

def get_metadata_info(metadata_dir):
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
    sacfiles_info = []
    for sacfile in sacfiles:
        st = obspy.read(sacfile, format="SAC", headonly=True)
        tr = st[0]
        net = tr.stats.sac.knetwk
        sta = tr.stats.sac.kstnm
        chn = tr.stats.sac.kcmpnm
        sacfile_tag = f"{net}{sta}{chn}"

        sac_info = []
        sac_info.append(sacfile)



def get_dataset_parent_dirs(sacfiles):
    dataset_parent_dirs = []
    for sacfile in sacfiles:
        parent_dir = os.path.basename(os.path.split(sacfile)[0])
        if parent_dir not in dataset_parent_dirs:
            dataset_parent_dirs.append(parent_dir)
    return sorted(dataset_parent_dirs)


def get_event_info(sacfiles, config):
    dataset_events = []
    events_pattern = '^[0-9][0-9][0-3][0-9][0-9][0-2][0-9][0-5][0-9][0-5][0-9]$'
    events_regex = re.compile(events_pattern)
    dataset_parent_dirs = get_dataset_parent_dirs(sacfiles)
    for x in dataset_parent_dirs:
        if events_regex.match(x):
            dataset_events.append(x)

    event_info = {}
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
        event_info[f"{event_name}"] = {
            'evla': evla,
            'evlo': evlo,
            'evdp': evdp,
            'mag': mag,
            'imagtyp': imagtyp
        }

    # check if all 'dataset_events' are in 'eventlist_events'
    for dataset_event in dataset_events:
        if dataset_event not in eventlist_events:
            print(f"Error! Could not find event information for event '{dataset_event}'")
            exit(1)

    return event_info



def writehdr(args):
    metadata_dir = os.path.abspath(args.metadata)
    print(f"metadata directory: {metadata_dir}\n")
    metadata_info = get_metadata_info(metadata_dir)
    if not args.ant:
        config = download.read_download_config(args)
        event_info = get_event_info(args.input_files, config)

    # start writting sac headers
    for sacfile in args.input_files:
        headers = {}
    exit(0)

    
def remresp(args):
    print("Hello from remresp!")
    exit(0)

    
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

    