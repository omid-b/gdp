import os
import subprocess
import configparser

def find_perl_path():
    p = subprocess.run( [ 'which', 'perl' ], stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    if p.returncode == 0:
        PERL = p.stdout.decode().split('\n')[0]
    else:
        PERL = ""
    return PERL


def find_sac_path():
    if os.path.isfile("/usr/local/sac/bin/sac"):
        SAC = "/usr/local/sac/bin/sac"
    elif os.path.isfile("/usr/local/bin/sac"):
        SAC = "/usr/local/bin/sac"
    elif os.path.isfile("/usr/bin/sac"):
        SAC = "/usr/bin/sac"
    else:
        p = subprocess.run( [ 'which', 'sac' ], stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        if p.returncode == 0:
            SAC = p.stdout.decode().split('\n')[0]
        else:
            SAC = ""
    return SAC


def find_gmt_path():
    if os.path.isfile("/usr/local/gmt/bin/gmt"):
        GMT = "/usr/local/gmt/bin/gmt"
    elif os.path.isfile("/usr/local/bin/gmt"):
        GMT = "/usr/local/bin/gmt"
    elif os.path.isfile("/usr/bin/gmt"):
        GMT = "/usr/bin/gmt"
    elif os.path.isfile("/home/marco/Documents/GMT/bin/gmt"):
        GMT = "/home/marco/Documents/GMT/bin/gmt"
    else:
        p = subprocess.run( [ 'which', 'gmt' ], stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        if p.returncode == 0:
            GMT = p.stdout.decode().split('\n')[0]
        else:
            GMT = ""
    return GMT



def write_download_config(args):
    maindir = os.path.abspath(args.maindir)
    if not os.path.exists(maindir):
        os.makedirs(maindir)
    station_list = os.path.join(maindir, 'stations.dat')
    event_list = os.path.join(maindir, 'events.dat')
    config_file = os.path.join(maindir, 'download.config')
    config_text = """
[download_setting]

obspy_mdl_script = True
iris_fetch_script = True
startdate = 
enddate =

[station_setting]

station_list = %s
station_channels = BHZ HHZ
station_location_codes = 00 10
station_maxlat =
station_maxlon =
station_minlat =
station_minlon =

[event_setting]

event_list = %s
event_min_mag = 
event_minlon = -180.0
event_maxlon = 180.0
event_minlat = -90.0
event_maxlat = 90.0

[datacenters]

AUSPASS = False
BGR = False
ETH = False
GEOFON = False
ICGC = False
INGV = False
IRIS = True
IRISPH5 = True
KOERI = False
LMU = False
NCEDC = False
NIEP = False
NOA = False
ODC = False
ORFEUS = False
RASPISHAKE = False
RESIF = False
RESIFPH5 = False
SCEDC = False
TEXNET = False
USP = False

[dependencies]

perl = %s
sac = %s
gmt = %s
    """ %(
        station_list,
        event_list,
        find_perl_path(),
        find_sac_path(),
        find_gmt_path()
    )
    fopen = open(config_file, 'w')
    fopen.write(config_text)
    fopen.close()
    print(f"'download.config' was created successfully!\n\nPlease set all parameters in file:\n{config_file}\n")


def read_download_config(args):
    maindir = os.path.abspath(args.maindir)
    config_file = os.path.join(maindir, 'download.config')
    if not os.path.isfile(config_file):
        print(f"Error! Could not find 'download.config' in the following path:\n{config_file}\n")
        exit(1)

    sections = ["download_setting", "station_setting", "event_setting", "datacenters", "dependencies"]
    download_setting = ["obspy_mdl_script", "iris_fetch_script", "startdate", "enddate"]
    station_setting = ["station_list", "station_channels", "station_location_codes",
                       "station_maxlat", "station_maxlon", "station_minlat", "station_minlon"]
    event_setting = ["event_list", "event_min_mag",
                     "event_minlon", "event_maxlon", "event_minlat", "event_maxlat"]
    datacenters = ["AUSPASS", "BGR", "ETH", "GEOFON", "ICGC", "INGV",
                   "IRIS", "IRISPH5", "KOERI", "LMU", "NCEDC", "NIEP",
                   "NOA", "ODC", "ORFEUS", "RASPISHAKE", "RESIF",
                   "RESIFPH5", "SCEDC", "TEXNET", "USP"]    
    dependencies = ["perl", "sac", "gmt"]

    # read config file
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
    except Exception as e:
        print(f"Error reading config file!\n{e}\n")

    # all sections available?
    for section in sections:
        if section not in config.sections():
            print(f"Error in read_download_config(): Config section was not available: '{section}'")

    # download_setting
    download_setting = {}
    for param in setting_params:
        if param not in config.options('setting'):
            print(f"read_config(): Config parameter not available in [setting]: '{param}'")
            return False


    return download_config
    


def events(args):
    config = read_download_config(args)
    


def stations(args):
    print(f"Hello from stations!")
    


def metadata(args):
    print(f"Hello from metadata!")
    


def mseeds(args):
    print(f"Hello from mseeds!")
    

