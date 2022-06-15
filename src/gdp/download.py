import os
import re
import subprocess
import configparser


def isdate(text): # is a date value: 'YYYY-MM-DD'
    rexpr = re.compile("^[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]$")
    if rexpr.match(text):
        return True
    else:
        return False


def isfloat(text): # is a float
    try:
        val = float(text)
        return True
    except ValueError:
        return False



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

auspass = False
bgr = False
eth = False
geofon = False
icgc = False
ingv = False
iris = True
irisph5 = True
koeri = False
lmu = False
ncedc = False
niep = False
noa = False
odc = False
orfeus = False
raspishake = False
resif = False
resifph5 = False
scedc = False
texnet = False
usp = False

[dependencies]

perl = %s
sac = %s
gmt = %s \n""" %(
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
    download_setting_params = ["obspy_mdl_script", "iris_fetch_script", "startdate", "enddate"]
    station_setting_params = ["station_list", "station_channels", "station_location_codes",
                              "station_maxlat", "station_maxlon", "station_minlat", "station_minlon"]
    event_setting_params = ["event_list", "event_min_mag",
                            "event_minlon", "event_maxlon", "event_minlat", "event_maxlat"]
    datacenters_params = ["auspass", "bgr", "eth", "geofon", "icgc", "ingv",
                          "iris", "irisph5", "koeri", "lmu", "ncedc", "niep",
                          "noa", "odc", "orfeus", "raspishake", "resif",
                          "resifph5", "scedc", "texnet", "usp"]    
    dependencies_params = ["perl", "sac", "gmt"]
    float_params = ["station_maxlat", "station_maxlon", "station_minlat", "station_minlon"
                    "event_min_mag", "event_minlon", "event_maxlon", "event_minlat", "event_maxlat"]

    # read config file
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
    except Exception as e:
        print(f"Error reading config file!\n{e}\n")
        exit(1)

    # all sections available?
    for section in sections:
        if section not in config.sections():
            print(f"Error in read_download_config(): Config section was not available: '{section}'")
            exit(1)

    # download_setting
    download_setting = {}
    for param in download_setting_params:
        if param not in config.options('download_setting'):
            print(f"Error in read_download_config(): Config parameter not available in [download_setting]: '{param}'")
            exit(1)
        val = config.get('download_setting',f"{param}")
        if len(val):
            if param in ["obspy_mdl_script", "iris_fetch_script"]:
                if val.lower() == 'true':
                    download_setting[f"{param}"] = True
                elif val.lower() == 'false':
                    download_setting[f"{param}"] = False
                else:
                    print(f"Error in read_download_config()\nValue of parameter '{param}' must be a boolean (True/False)")
                    exit(1)

            if param in ["startdate", "enddate"] and not isdate(val):
                print(f"Error in read_download_config()\nValue of parameter '{param}' must be in 'YYYY-MM-DD' format.")
                exit(1)
        else:
            download_setting[f"{param}"] = val


    # station_setting
    station_setting = {}
    for param in station_setting_params:
        if param not in config.options('station_setting'):
            print(f"Error in read_download_config(): Config parameter not available in [station_setting]: '{param}'")
            exit(1)
        val = config.get('station_setting',f"{param}")
        if len(val):
            if param in ["station_channels", "station_location_codes"]:
                station_setting[f"{param}"] = val.split()
            if param in float_params:
                if isfloat(val):
                    station_setting[f"{param}"] = val
                else:
                    print(f"Error in read_download_config()\nValue of parameter '{param}' must be a float.")
                    exit(1)
        else:
            if param in ["station_channels", "station_location_codes"]:
                station_setting[f"{param}"] = []
            else:
                station_setting[f"{param}"] = val

    # event_setting
    event_setting = {}
    for param in event_setting_params:
        if param not in config.options('event_setting'):
            print(f"Error in read_download_config(): Config parameter not available in [event_setting]: '{param}'")
            exit(1)
        val = config.get('event_setting',f"{param}")
        if len(val):
            pass

    # datacenters
    datacenters = {}
    for param in datacenters_params:
        if param not in config.options('datacenters'):
            print(f"Error in read_download_config(): Config parameter not available in [datacenters]: '{param}'")
            exit(1)
        val = config.get('datacenters',f"{param}")
        if len(val):
            if val.lower() == 'true':
                datacenters[f"{param}"] = True
            elif val.lower() == 'false':
                datacenters[f"{param}"] = False
            else:
                print(f"Error in read_download_config()\nValue of parameter '{param}' must be a boolean (True/False)")
                exit(1)


    # dependencies
    dependencies = {}
    for param in dependencies_params:
        if param not in config.options('dependencies'):
            print(f"Error in read_download_config(): Config parameter not available in [dependencies]: '{param}'")
            exit(1)
        val = config.get('dependencies',f"{param}")
        if len(val) and not os.path.isfile(val):
            print(f"Error in read_download_config(): Could not find executable for {param.upper()}:\n{val}")
            exit(1)
        dependencies[f"{param}"] = val

    download_config = {}
    download_config["download_setting"] = download_setting
    download_config["station_setting"] = station_setting
    download_config["event_setting"] = event_setting
    download_config["datacenters"] = datacenters
    download_config["dependencies"] = dependencies
    print(download_config)
    return download_config
    


def events(args):
    config = read_download_config(args)
    


def stations(args):
    print(f"Hello from stations!")
    


def metadata(args):
    print(f"Hello from metadata!")
    


def mseeds(args):
    print(f"Hello from mseeds!")
    

