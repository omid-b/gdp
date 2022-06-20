
import os
import re
import shutil
import subprocess
from math import floor
from urllib import request
import obspy
from obspy.clients.fdsn.client import Client
from obspy.clients.fdsn.mass_downloader import RectangularDomain
from obspy.clients.fdsn.mass_downloader import Restrictions
from obspy.clients.fdsn.mass_downloader import MassDownloader

from . import io

import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    try:
        from . import _geographic as geographic
    except ImportError:
        print("WARNING! Could not use cythonized module: geographic")
        from . import geographic

class EVENTS:

    def __init__(self, config):
        self.config = config

        event_list = config['event_setting']['event_list']
        starttime = config['download_setting']['startdate']
        endtime = config['download_setting']['enddate']
        min_mag = config['event_setting']['event_min_mag']
        min_gcarc = config['event_setting']['event_min_gcarc']
        max_gcarc = config['event_setting']['event_max_gcarc']
        minlon = config['event_setting']['event_minlon']
        maxlon = config['event_setting']['event_maxlon']
        minlat = config['event_setting']['event_minlat']
        maxlat = config['event_setting']['event_maxlat']

        if len(event_list):
            self.event_list = event_list
        else:
            print("Error! Parameter 'event_list' is not specified in 'download.config'.")
            exit(1)

        if len(starttime):
            self.starttime = obspy.UTCDateTime(f"{starttime}T00:00:00")
        else:
            print(f"Error! Parameter 'startdate' is not specified in 'download.config'")
            exit(1)

        if len(endtime):
            self.endtime = obspy.UTCDateTime(f"{endtime}T00:00:00")
        else:
            print(f"Error! Parameter 'enddate' is not specified in 'download.config'")
            exit(1)

        if len(str(min_mag)):
            self.min_mag = str(min_mag)
        else:
            print(f"Error! Parameter 'event_min_mag' is not specified in 'download.config'")
            exit(1)

        if len(str(minlon)):
            self.minlon = float(minlon)
        else:
            print(f"Error! Parameter 'event_minlon' is not specified in 'download.config'")
            exit(1)

        if len(str(maxlon)):
            self.maxlon = float(maxlon)
        else:
            print(f"Error! Parameter 'event_maxlon' is not specified in 'download.config'")
            exit(1)

        if len(str(minlat)):
            self.minlat = float(minlat)
        else:
            print(f"Error! Parameter 'event_minlat' is not specified in 'download.config'")
            exit(1)

        if len(str(maxlat)):
            self.maxlat = float(maxlat)
        else:
            print(f"Error! Parameter 'event_maxlat' is not specified in 'download.config'")
            exit(1)

        if len(str(min_gcarc)):
            self.min_gcarc = float(min_gcarc)
        else:
            print(f"Error! Parameter 'event_min_gcarc' is not specified in 'download.config'")
            exit(1)

        if len(str(max_gcarc)):
            self.max_gcarc = float(max_gcarc)
        else:
            print(f"Error! Parameter 'event_max_gcarc' is not specified in 'download.config'")
            exit(1)

        for param in ['event_minlon','event_maxlon','event_minlat','event_maxlat']:
            if len(str(config['event_setting'][param])) == 0:
                print(f"Error! Parameter '{param}' is not specified in 'download.config'")
                exit(1)

        calc_baz_gcarc = True
        for param in ['station_minlon','station_maxlon','station_minlat','station_maxlat']:
            if len(str(config['station_setting'][param])) == 0:
                calc_baz_gcarc = False

        if calc_baz_gcarc:
            self.region_lat = (config['station_setting']['station_minlat'] + config['station_setting']['station_maxlat']) / 2
            self.region_lon = (config['station_setting']['station_minlon'] + config['station_setting']['station_maxlon']) / 2
        else:
            print("Error! Study area coordinates are not specified.")
            print("This information is required to calculate BAZ and GCARC values.")
            print("Check section 'station_setting' in 'download.config'.")
            exit(1)


    def get_datacenters(self):
        datacenters = []
        if self.config['datacenters']['auspass']:
            datacenters.append('AUSPASS')
        if self.config['datacenters']['bgr']:
            datacenters.append('BGR')
        if self.config['datacenters']['eth']:
            datacenters.append('ETH')
        if self.config['datacenters']['geofon']:
            datacenters.append('GEOFON')
        if self.config['datacenters']['icgc']:
            datacenters.append('ICGC')
        if self.config['datacenters']['ingv']:
            datacenters.append('INGV')
        if self.config['datacenters']['iris']:
            datacenters.append('IRIS')
        if self.config['datacenters']['irisph5']:
            datacenters.append('IRISPH5')
        if self.config['datacenters']['koeri']:
            datacenters.append('KOERI')
        if self.config['datacenters']['lmu']:
            datacenters.append('LMU')
        if self.config['datacenters']['ncedc']:
            datacenters.append('NCEDC')
        if self.config['datacenters']['niep']:
            datacenters.append('NIEP')
        if self.config['datacenters']['noa']:
            datacenters.append('NOA')
        if self.config['datacenters']['odc']:
            datacenters.append('ODC')
        if self.config['datacenters']['orfeus']:
            datacenters.append('ORFEUS')
        if self.config['datacenters']['raspishake']:
            datacenters.append('RASPISHAKE')
        if self.config['datacenters']['resif']:
            datacenters.append('RESIF')
        if self.config['datacenters']['resifph5']:
            datacenters.append('RESIFPH5')
        if self.config['datacenters']['scedc']:
            datacenters.append('SCEDC')
        if self.config['datacenters']['texnet']:
            datacenters.append('TEXNET')
        if self.config['datacenters']['usp']:
            datacenters.append('USP')
        return datacenters

    def request_events(self):
        datacenters = self.get_datacenters()
        events_saved = []
        events = {
            'date': [],
            'time': [],
            'lat': [],
            'lon': [],
            'dep': [],
            'mag': [],
            'mag_type': [],
            'julday': [],
            'baz': [],
            'gcarc': []
        }
        for datacenter in datacenters:
            data_exist = True
            print(f"Request list of events from datacenter: {datacenter}")
            try:
                client=Client(datacenter)
                cat = client.get_events(starttime=self.starttime,
                endtime=self.endtime,
                minmagnitude=str(self.min_mag),
                minlongitude=self.minlon,
                maxlongitude=self.maxlon,
                minlatitude=self.minlat,
                maxlatitude=self.maxlat)
            except ValueError:
                print("- request faild: ValueError!")
                data_exist = False
            except TypeError:
                print("- request faild: TypeError!")
                data_exist = False
            except Exception as e:
                print(f" - service outage for: {datacenter}")
                data_exist = False

            if data_exist:
                for i in range(cat.count()):
                    origins=str(cat[i].origins[0])
                    origins=re.split("\n|\s|,|\=|\:|\(|\)",origins)
                    while '' in origins:
                        origins.remove('')
                    lat   = "%8.4f" %(float(origins[origins.index('latitude')+1]))
                    lon   = "%9.4f" %(float(origins[origins.index('longitude')+1]))
                    # event depth
                    try:
                        dep   = "%6.2f" %(float(origins[origins.index('depth')+1])/1000)
                    except:
                        dep   = "%6s" %('xxx')
                    # event second (time)
                    try:
                        sec   = "%02d" %(float(origins[origins.index('UTCDateTime')+6]))
                    except:
                        sec   = "00"
                    try: #sometime second fraction data is missing!
                        sec = f"{sec}.%03d" %(float(origins[origins.index('UTCDateTime')+7][:3]))
                    except:
                        sec = f"{sec}.000"
                    # final event date and time
                    date = "%4d-%02d-%02d" %(\
                        float(origins[origins.index('UTCDateTime')+1]),
                        float(origins[origins.index('UTCDateTime')+2]),
                        float(origins[origins.index('UTCDateTime')+3])
                    )
                    time = "%02d:%02d:%s" %(\
                        float(origins[origins.index('UTCDateTime')+4]),
                        float(origins[origins.index('UTCDateTime')+5]),
                        sec
                    )
                    datetime = obspy.UTCDateTime(f"{date}T{time}")
                    julday = "%3d" %(datetime.julday)
                    # event magnitude
                    magnitude=str(cat[i].magnitudes[0])
                    magnitude=re.split("\n|\s|,|\=|\:|\(|\)",magnitude)
                    while '' in magnitude:
                        magnitude.remove('')
                    mag   = "%3.1f" %(float(magnitude[magnitude.index('mag')+1]))
                    try:
                        mag_type   = "%3s" %(magnitude[magnitude.index('magnitude_type')+1][1:-1])
                    except:
                        mag_type = "%3s" %('xxx')
                    # GCARC and BAZ
                    point1 = geographic.Point(self.region_lon, self.region_lat)
                    point2 = geographic.Point(float(lon), float(lat))
                    gcline = geographic.Line(point2, point1)
                    baz = gcline.calc_baz()
                    gcarc = gcline.calc_gcarc()
                    # append data to output dictionary
                    event_id = f"%s_%.0f_%.0f" %(date,floor(float(lat)),floor(float(lon)))
                    if event_id not in events_saved and gcarc >= self.min_gcarc and gcarc <= self.max_gcarc:
                        events['date'].append(date)
                        events['time'].append(time)
                        events['lat'].append(float(lat))
                        events['lon'].append(float(lon))
                        events['dep'].append(dep)
                        events['mag'].append(float(mag))
                        events['mag_type'].append(mag_type)
                        events['julday'].append(int(julday))
                        events['baz'].append(float(baz))
                        events['gcarc'].append(float(gcarc))
        return events


    def write_events(self,events):
        header_lines = ["#Datacenters:"]
        main_lines = []
        datacenters = self.get_datacenters()

        for dc in datacenters:
            header_lines.append(f"#{dc}")
        header_lines.append("")
        header_lines.append("#Date, Time, Latitude, Longitude, Depth(km), Mag, Mag_type, Julday, BAZ, GCARC")

        for i in range(len(events['date'])):
            main_lines.append("%s %s %8.4f %9.4f %6s %3.1f %s %3d %3.0f %6.2f" %(\
                events['date'][i],
                events['time'][i],
                events['lat'][i],
                events['lon'][i],
                events['dep'][i],
                events['mag'][i],
                events['mag_type'][i],
                events['julday'][i],
                events['baz'][i],
                events['gcarc'][i]
            ))
        main_lines = sorted(main_lines)

        outlines = header_lines + main_lines
        
        args = ARGS(False, False, False, self.event_list)
        io.output_lines(outlines, args)
        


    def read_events(self):
        if not os.path.isfile(self.event_list):
            print(f"Error! Could not find events list file:\n {self.event_list}\n")
            exit(1)
        fopen = open(self.event_list,'r')
        flines = fopen.read().splitlines()
        fopen.close()
        events = {
            'date': [],
            'time': [],
            'lat': [],
            'lon': [],
            'dep': [],
            'mag': [],
            'mag_type': [],
            'julday': [],
            'baz': [],
            'gcarc': []
        }
        for line in flines:
            line = line.strip()
            if len(line) and line[0] != '#':
                events['date'].append(str(line.split()[0]))
                events['time'].append(str(line.split()[1]))
                events['lat'].append(float(line.split()[2]))
                events['lon'].append(float(line.split()[3]))
                events['dep'].append(str(line.split()[4]))
                events['mag'].append(float(line.split()[5]))
                events['mag_type'].append(str(line.split()[6]))
                events['julday'].append(int(line.split()[7]))
                events['baz'].append(float(line.split()[8]))
                events['gcarc'].append(float(line.split()[9]))
        return events


class ARGS:
    def __init__(self, uniq, sort, append, outfile):
        self.uniq = uniq
        self.sort = sort
        self.append = append
        self.outfile = outfile
