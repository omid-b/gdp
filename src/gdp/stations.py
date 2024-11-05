 
import os
import obspy
import subprocess
from urllib import request


pkg_dir, _ = os.path.split(__file__)
fetch_data_script = os.path.join(pkg_dir, "FetchData-2018.337")



class STATIONS:

    def __init__(self,config,stalist_input=False):
        if stalist_input:
            self.stalist_file = config
        else:
            self.config = config
            self.stalist_file = config['station_setting']['station_list']
        
        self.stalist_fname = os.path.split(self.stalist_file)[1]
        self.maindir = os.path.abspath(os.path.split(self.stalist_file)[0])




    def get_datacenters(self):
        datacenters = []
        if self.config['datacenters']['auspass']:
            datacenters.append("http://auspass.edu.au:8080/fdsnws/station/1")
        if self.config['datacenters']['koeri']:
            datacenters.append("http://eida-service.koeri.boun.edu.tr/fdsnws/station/1")
        if self.config['datacenters']['bgr']:
            datacenters.append("http://eida.bgr.de/fdsnws/station/1")
        if self.config['datacenters']['eth']:
            datacenters.append("http://eida.ethz.ch/fdsnws/station/1")
        if self.config['datacenters']['noa']:
            datacenters.append("http://eida.gein.noa.gr/fdsnws/station/1")
        if self.config['datacenters']['geofon']:
            datacenters.append("http://geofon.gfz-potsdam.de/fdsnws/station/1")
        if self.config['datacenters']['usp']:
            datacenters.append("http://seisrequest.iag.usp.br/fdsnws/station/1")
        if self.config['datacenters']['iris']:
            datacenters.append("http://service.iris.edu/fdsnws/station/1")
        if self.config['datacenters']['ncedc']:
            datacenters.append("http://service.ncedc.org/fdsnws/station/1")
        if self.config['datacenters']['nrcan']:
            datacenters.append("https://www.earthquakescanada.nrcan.gc.ca/fdsnws/station/1")
        if self.config['datacenters']['scedc']:
            datacenters.append("http://service.scedc.caltech.edu/fdsnws/station/1")
        if self.config['datacenters']['ingv']:
            datacenters.append("http://webservices.ingv.it/fdsnws/station/1")
        if self.config['datacenters']['icgc']:
            datacenters.append("http://ws.icgc.cat/fdsnws/station/1")
        if self.config['datacenters']['resif']:
            datacenters.append("http://ws.resif.fr/fdsnws/station/1")
        if self.config['datacenters']['orfeus']:
            datacenters.append("http://www.orfeus-eu.org/fdsnws/station/1")
        if self.config['datacenters']['raspishake']:
            datacenters.append("https://fdsnws.raspberryshakedata.com/fdsnws/station/1")
        return datacenters


    def get_channels(self):
        channels = self.config['station_setting']['station_channels']
        if not len(channels):
            print("Error! Station channels to download are not specified!\n")
            exit(1)
        return channels


    def get_dates(self):
        startdate = self.config['download_setting']['startdate']
        enddate = self.config['download_setting']['enddate']
        if not len(startdate) or not len(enddate):
            print("\nError! Project start/end dates are not specified!\n")
            exit(1)
        return [startdate, enddate]


    def get_latitudes(self):
        minlat = self.config['station_setting']['station_minlat']
        maxlat = self.config['station_setting']['station_maxlat']
        if not len(str(minlat)) or not len(str(maxlat)):
            print("\nError! Station latitudes are not specified!\n")
            exit(1)
        return [minlat, maxlat]


    def get_longitude(self):
        minlon = self.config['station_setting']['station_minlon']
        maxlon = self.config['station_setting']['station_maxlon']
        if not len(str(minlon)) or not len(str(maxlon)):
            print("\nError! Station longitudes are not specified!\n")
            exit(1)
        return [minlon, maxlon]


    def request_stalist(self):
        datacenters = self.get_datacenters()
        channels = self.get_channels()
        dates = self.get_dates()
        region_lat = self.get_latitudes()
        region_lon = self.get_longitude()
        stalist = {
        'net':[],
        'sta':[],
        'lat':[],
        'lon':[],
        'elv':[],
        'site':[],
        'start':[],
        'end':[]
        }
        for datacenter in datacenters:
            print(f"request list of stations from datacenter: {datacenter}")
            for k, chn in enumerate(channels):
                stations_xml = os.path.join(f"{self.stalist_file}.{chn}_{datacenter.split('/')[2]}.xml")
                url = f"{datacenter}/query?starttime={dates[0]}T00:00:00&endtime={dates[1]}T23:59:59&minlat={region_lat[0]}&maxlat={region_lat[1]}&minlon={region_lon[0]}&maxlon={region_lon[1]}&channel={chn}"
                try:
                    req = request.Request(url)
                    resp = request.urlopen(req).read().decode('utf-8')
                    fopen = open(stations_xml,'w')
                    fopen.write(f"{resp}")
                    fopen.close()
                    inv = obspy.read_inventory(stations_xml,format="STATIONXML")
                    # store requested information
                    for i in range(len(inv)):
                        for j in range(len(inv[i])):
                            net = inv[i].code
                            sta = inv[i][j].code
                            if sta not in stalist['sta']:
                                if len(self.config["station_setting"]["stations"]) \
                                and sta not in self.config["station_setting"]["stations"]:
                                    continue
                                if len(self.config["station_setting"]["networks"]) \
                                and net not in self.config["station_setting"]["networks"]:
                                    continue
                                stalist['net'].append(inv[i].code)
                                stalist['sta'].append(inv[i][j].code)
                                stalist['lat'].append(inv[i][j]._latitude)
                                stalist['lon'].append(inv[i][j]._longitude)
                                stalist['elv'].append(inv[i][j]._elevation)
                                stalist['site'].append(inv[i][j].site.name)
                                stalist['start'].append(str(inv[i][j].start_date).split('.')[0])
                                stalist['end'].append(str(inv[i][j].end_date).split('.')[0])
                except Exception:
                    pass

                if os.path.isfile(stations_xml):
                        os.remove(stations_xml)
        return stalist


    def write_stalist(self, stalist):
        datacenters = self.get_datacenters()
        nsta = len(stalist['sta'])
        output_lines_headers = ["#Datacenters:"]
        for dc in datacenters:
            output_lines_headers.append(f"#{dc}")
        output_lines_headers.append("")
        output_lines_headers.append("#Network | Station | Latitude | Longitude | Elevation | Sitename | StartTime | EndTime")
        output_lines_main = []
        for i in range(nsta):
            net = str(stalist['net'][i]).strip()
            sta = str(stalist['sta'][i]).strip()
            lat = str(stalist['lat'][i]).strip()
            lon = str(stalist['lon'][i]).strip()
            elv = str(stalist['elv'][i]).strip()
            site = str(stalist['site'][i]).strip()
            start = str(stalist['start'][i]).strip()
            end = str(stalist['end'][i]).strip()
            output_lines_main.append(f"{net}|{sta}|{lat}|{lon}|{elv}|{site}|{start}|{end}")
        output_lines_main = sorted(output_lines_main)
        # write output
        fopen = open(self.stalist_file,'w')
        for line in output_lines_headers:
            fopen.write(f"{line}\n")
        for line in output_lines_main:
            fopen.write(f"{line}\n")
        fopen.close()


    def read_stalist(self):

        if not os.path.isfile(self.stalist_file):
            print(f"Error! Could not find station list: '{self.stalist_file}'")
            exit(1)
        fopen = open(self.stalist_file,'r')
        flines = fopen.read().splitlines()
        fopen.close()
        stalist_lines = []
        for line in flines:
            line = line.strip()
            if line not in stalist_lines \
            and len(line) \
            and line[0] != '#':
                stalist_lines.append(line)
        # generate stalist dict
        stalist = {
        'net':[],
        'sta':[],
        'lat':[],
        'lon':[],
        'elv':[],
        'site':[],
        'start':[],
        'end':[]
        }
        try:
            for line in stalist_lines:
                line = line.split('|')
                stalist['net'].append(line[0])
                stalist['sta'].append(line[1])
                stalist['lat'].append(line[2])
                stalist['lon'].append(line[3])
                stalist['elv'].append(line[4])
                stalist['site'].append(line[5])
                stalist['start'].append(line[6])
                stalist['end'].append(line[7])
        except Exception:
            print(f"Read station list format Error!")
            exit(1)
        return stalist


    def download_xml_files(self, metadatadir):
        dates = self.get_dates()
        channels = self.get_channels()
        stalist = self.read_stalist()
        download_list = self.gen_download_list(stalist)
        PERL = self.config['dependencies']['perl']

        # make metadatadir
        metadatadir = os.path.abspath(metadatadir)
        if not os.path.isdir(metadatadir):
            os.mkdir(metadatadir)

        # start downloading
        starttime = f"{dates[0]},00:00:00"
        endtime = f"{dates[1]},23:59:59"

        ndl = 0
        for i, chn in enumerate(channels):
            print(f"\ndownload station metadata for channel: {chn}\n")
            for j, netsta in enumerate(download_list[i]):
                net = netsta.split('.')[0]
                sta = netsta.split('.')[1]
                outfile = os.path.join(metadatadir, f"{net}.{sta}.{chn}")
                bash_cmd = f"{PERL} {fetch_data_script} -S {sta} -N {net} -C {chn} -s {starttime} -e {endtime} -X {outfile} -q\n"
                print(f"    metadata {j+1} of {len(download_list[i])}:  {net}.{sta}.{chn}")
                subprocess.call(bash_cmd, shell=True)
                ndl += 1
        print(f"\nnumber of downloaded metadata: {ndl}")
        print(f"output metadata directory: {metadatadir}\n")


    def gen_download_list(self, stalist):
        datacenters = self.get_datacenters()
        channels = self.get_channels()
        dates = self.get_dates()
        region_lat = self.get_latitudes()
        region_lon = self.get_longitude()
        download_list = [[] for i in range(len(channels))]
        for k, chn in enumerate(channels):
            for datacenter in datacenters:
                stations_xml = os.path.join(f"{self.stalist_file}.{chn}_{datacenter.split('/')[2]}.xml")
                url = f"{datacenter}/query?starttime={dates[0]}T00:00:00&endtime={dates[1]}T23:59:59&minlat={region_lat[0]}&maxlat={region_lat[1]}&minlon={region_lon[0]}&maxlon={region_lon[1]}&channel={chn}"
                try:
                    req = request.Request(url)
                    resp = request.urlopen(req).read().decode('utf-8')
                    fopen = open(stations_xml,'w')
                    fopen.write(f"{resp}")
                    fopen.close()
                    inv = obspy.read_inventory(stations_xml,format="STATIONXML")
                    for i in range(len(inv)):
                        for j in range(len(inv[i])):
                            net = inv[i].code
                            sta = inv[i][j].code
                            if net in stalist['net'] and sta in stalist['sta']:
                                download_list[k].append(f"{net}.{sta}")
                except Exception:
                    pass
                if os.path.isfile(stations_xml):
                        os.remove(stations_xml)
        return download_list


