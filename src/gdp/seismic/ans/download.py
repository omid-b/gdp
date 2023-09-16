from . import config as ans_config

import os
import obspy
import shutil
import subprocess
from urllib import request

from obspy.clients.fdsn.client import Client
from obspy.clients.fdsn.mass_downloader import RectangularDomain
from obspy.clients.fdsn.mass_downloader import Restrictions
from obspy.clients.fdsn.mass_downloader import MassDownloader


pkg_dir, _ = os.path.split(__file__)
fetch_data_script = os.path.join(pkg_dir, 'files', "FetchData-2018.337")


#==== MAIN FUNCTIONS ====#

def download_stations(maindir):
    maindir = os.path.abspath(maindir)
    if not os.path.isdir(os.path.join(maindir, '.ans')):
        os.mkdir(os.path.join(maindir, '.ans'))
    stalist = os.path.split(ans_config.read_config(maindir)['download']['le_stalist'])[1]
    print(f"  Generating list of stations: '{stalist}'")
    stations = STATIONS(maindir) 
    datacenters = stations.get_datacenters()
    stalist = stations.request_stalist()
    stations.write_stalist(stalist, datacenters)
    nsta = len(stations.read_stalist()['sta'])
    print(f"  #Stations: {nsta}\n\nDone!\n")


def download_metadata(maindir,update_stations=False):
    maindir = os.path.abspath(maindir)
    if not os.path.isdir(os.path.join(maindir, '.ans')):
        os.mkdir(os.path.join(maindir, '.ans'))
    stations = STATIONS(maindir) 
    stations.download_xml_files()
    if update_stations:
        conf = ans_config.read_config(maindir)
        metadatadir = conf['download']['le_stameta']
        datacenters = stations.get_datacenters()
        current_stalist = stations.read_stalist()
        new_stalist = {
        'net':[],
        'sta':[],
        'lat':[],
        'lon':[],
        'elv':[],
        'site':[],
        'start':[],
        'end':[]
        }
        xml_list_sta = []
        for xml in sorted(os.listdir(metadatadir)):
            xml_list_sta.append(xml.split('.')[1])
        for i, sta in enumerate(current_stalist['sta']):
            if sta in xml_list_sta:
                new_stalist['net'].append(current_stalist['net'][i])
                new_stalist['sta'].append(current_stalist['sta'][i])
                new_stalist['lat'].append(current_stalist['lat'][i])
                new_stalist['lon'].append(current_stalist['lon'][i])
                new_stalist['elv'].append(current_stalist['elv'][i])
                new_stalist['site'].append(current_stalist['site'][i])
                new_stalist['start'].append(current_stalist['start'][i])
                new_stalist['end'].append(current_stalist['end'][i])
        stations.write_stalist(new_stalist, datacenters)

    print("\nDone!\n")


def download_mseeds(maindir):
    maindir = os.path.abspath(maindir)
    if not os.path.isdir(os.path.join(maindir, '.ans')):
        os.mkdir(os.path.join(maindir, '.ans'))
    mseeds = MSEEDS(maindir)
    mseeds.download_all()
    print("\nDone!\n")

#========================#


class STATIONS:

    def __init__(self,maindir):
        self.maindir = os.path.abspath(maindir)
        self.conf = ans_config.read_config(self.maindir)
        self.stalist_file = self.conf['download']['le_stalist']
        self.stalist_fname = os.path.split(self.stalist_file)[1]


    def get_datacenters(self):
        datacenters = []
        if self.conf['download']['chb_dc_auspass_edu_au']:
            datacenters.append("http://auspass.edu.au:8080/fdsnws/station/1")
        if self.conf['download']['chb_dc_eida_sc3_infp_ro']:
            datacenters.append("http://eida-sc3.infp.ro/fdsnws/station/1")
        if self.conf['download']['chb_dc_eida_service_koeri_boun_edu_tr']:
            datacenters.append("http://eida-service.koeri.boun.edu.tr/fdsnws/station/1")
        if self.conf['download']['chb_dc_eida_bgr_de']:
            datacenters.append("http://eida.bgr.de/fdsnws/station/1")
        if self.conf['download']['chb_dc_eida_ethz_ch']:
            datacenters.append("http://eida.ethz.ch/fdsnws/station/1")
        if self.conf['download']['chb_dc_eida_gein_noa_gr']:
            datacenters.append("http://eida.gein.noa.gr/fdsnws/station/1")
        if self.conf['download']['chb_dc_eida_ipgp_fr']:
            datacenters.append("http://eida.ipgp.fr/fdsnws/station/1")
        if self.conf['download']['chb_dc_erde_geophysik_uni_muenchen_de']:
            datacenters.append("http://erde.geophysik.uni-muenchen.de/fdsnws/station/1")
        if self.conf['download']['chb_dc_geofon_gfz_potsdam_de']:
            datacenters.append("http://geofon.gfz-potsdam.de/fdsnws/station/1")
        if self.conf['download']['chb_dc_rtserve_beg_utexas_edu']:
            datacenters.append("http://rtserve.beg.utexas.edu/fdsnws/station/1")
        if self.conf['download']['chb_dc_seisrequest_iag_usp_br']:
            datacenters.append("http://seisrequest.iag.usp.br/fdsnws/station/1")
        if self.conf['download']['chb_dc_service_iris_edu']:
            datacenters.append("http://service.iris.edu/fdsnws/station/1")
        if self.conf['download']['chb_dc_service_ncedc_org']:
            datacenters.append("http://service.ncedc.org/fdsnws/station/1")
        if self.conf['download']['chb_dc_service_scedc_caltech_edu']:
            datacenters.append("http://service.scedc.caltech.edu/fdsnws/station/1")
        if self.conf['download']['chb_dc_webservices_ingv_it']:
            datacenters.append("http://webservices.ingv.it/fdsnws/station/1")
        if self.conf['download']['chb_dc_ws_icgc_cat']:
            datacenters.append("http://ws.icgc.cat/fdsnws/station/1")
        if self.conf['download']['chb_dc_ws_resif_fr']:
            datacenters.append("http://ws.resif.fr/fdsnws/station/1")
        if self.conf['download']['chb_dc_www_orfeus_eu_org']:
            datacenters.append("http://www.orfeus-eu.org/fdsnws/station/1")
        if self.conf['download']['chb_dc_fdsnws_raspberryshakedata_com']:
            datacenters.append("https://fdsnws.raspberryshakedata.com/fdsnws/station/1")
        return datacenters


    def get_channels(self):
        channels = self.conf['download']['le_stachns'].split()
        if not len(channels):
            print("Error! Station channels to download are not specified!\n")
            exit(1)
        return channels


    def get_dates(self):
        startdate = self.conf['setting']['le_startdate']
        enddate = self.conf['setting']['le_enddate']
        if not len(startdate) or not len(enddate):
            print("\nError! Project start/end dates are not specified!\n")
            exit(1)
        return [startdate, enddate]


    def get_latitudes(self):
        minlat = self.conf['setting']['le_minlat']
        maxlat = self.conf['setting']['le_maxlat']
        return [minlat, maxlat]


    def get_longitude(self):
        minlon = self.conf['setting']['le_minlon']
        maxlon = self.conf['setting']['le_maxlon']
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
        for k, chn in enumerate(channels):
            for datacenter in datacenters:
                stations_xml = os.path.join(self.maindir, '.ans',f"{self.stalist_fname}.{chn}_{datacenter.split('/')[2]}.xml")
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
                            sta = inv[i][j].code
                            if sta not in stalist['sta']:
                                stalist['net'].append(inv[i].code)
                                stalist['sta'].append(inv[i][j].code)
                                stalist['lat'].append(inv[i][j]._latitude)
                                stalist['lon'].append(inv[i][j]._longitude)
                                stalist['elv'].append(inv[i][j]._elevation)
                                stalist['site'].append(inv[i][j].site.name)
                                stalist['start'].append(str(inv[i][j].start_date).split('.')[0])
                                stalist['end'].append(str(inv[i][j].end_date).split('.')[0])
                except Exception:
                    if os.path.isfile(stations_xml):
                        os.remove(stations_xml)
        return stalist


    def write_stalist(self, stalist, datacenters):
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
        fopen = open(os.path.join(self.maindir, self.stalist_fname),'w')
        for line in output_lines_headers:
            fopen.write(f"{line}\n")
        for line in output_lines_main:
            fopen.write(f"{line}\n")
        fopen.close()


    def read_stalist(self):

        if not os.path.isfile(self.stalist_file):
            print(f"Error! Could not find station list: '{self.stalist_fname}'")
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


    def download_xml_files(self):
        dates = self.get_dates()
        channels = self.get_channels()
        stalist = self.read_stalist()
        download_list = self.gen_download_list(stalist)
        PERL = self.conf['setting']['le_perl']
        # make metadatadir
        metadatadir = self.conf['download']['le_stameta']
        if not os.path.isdir(metadatadir):
            os.mkdir(metadatadir)

        # start downloading
        starttime = f"{dates[0]},00:00:00"
        endtime = f"{dates[1]},23:59:59"

        for i, chn in enumerate(channels):
            print(f"\nDownload station meta files for channel: {chn}\n")
            for j, netsta in enumerate(download_list[i]):
                net = netsta.split('.')[0]
                sta = netsta.split('.')[1]
                outfile = os.path.join(metadatadir, f"{net}.{sta}.{chn}")
                bash_cmd = f"{PERL} {fetch_data_script} -S {sta} -N {net} -C {chn} -s {starttime} -e {endtime} -X {outfile} -q\n"
                print(f" metadata ({j+1} of {len(download_list[i])}):  {net}.{sta}.{chn}")
                subprocess.call(bash_cmd, shell=True)



    def gen_download_list(self, stalist):
        datacenters = self.get_datacenters()
        channels = self.get_channels()
        dates = self.get_dates()
        region_lat = self.get_latitudes()
        region_lon = self.get_longitude()
        metadatadir = self.conf['download']['le_stameta']
        download_list = [[] for i in range(len(channels))]
        for k, chn in enumerate(channels):
            for datacenter in datacenters:
                stations_xml = os.path.join(self.maindir, '.ans', f"{self.stalist_fname}.{chn}_{datacenter.split('/')[2]}.xml")
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
                    if os.path.isfile(stations_xml):
                        os.remove(stations_xml)
        return download_list



#------------#


class MSEEDS:
    def __init__(self, maindir):
        self.maindir = os.path.abspath(maindir)
        self.conf = ans_config.read_config(self.maindir)
        self.mseeds_dir = os.path.join(self.maindir, "mseeds")
        self.channels = self.conf['download']['le_stachns'].split()
        self.locations = self.conf['download']['le_stalocs'].split()
        self.timelen = self.conf['download']['le_timelen']
        self.locations.insert(0, "")
        self.stalist_file = self.conf['download']['le_stalist']
        self.startdate = self.conf['setting']['le_startdate']
        self.enddate = self.conf['setting']['le_enddate']
        if not len(self.startdate) or not len(self.enddate):
            print("Error! Project start and end dates are not specified!\n")
            exit(1)
        if not len(f"{self.timelen}"):
            print("Error! Parameter 'Timeseries length' is not specified!\n")
            exit(1)
        if not len(self.channels):
            print("Error! Station channels to download are not specified!\n")
            exit(1)


    def get_datacenters(self):
        datacenters = []
        if self.conf['download']['chb_dc_auspass_edu_au']:
            datacenters.append("AUSPASS")
        if self.conf['download']['chb_dc_eida_sc3_infp_ro']:
            datacenters.append("NIEP")
        if self.conf['download']['chb_dc_eida_service_koeri_boun_edu_tr']:
            datacenters.append("KOERI")
        if self.conf['download']['chb_dc_eida_bgr_de']:
            datacenters.append("BGR")
        if self.conf['download']['chb_dc_eida_ethz_ch']:
            datacenters.append("ETH")
        if self.conf['download']['chb_dc_eida_gein_noa_gr']:
            datacenters.append("NOA")
        if self.conf['download']['chb_dc_erde_geophysik_uni_muenchen_de']:
            datacenters.append("LMU")
        if self.conf['download']['chb_dc_geofon_gfz_potsdam_de']:
            datacenters.append("GEOFON")
        if self.conf['download']['chb_dc_rtserve_beg_utexas_edu']:
            datacenters.append("TEXNET")
        if self.conf['download']['chb_dc_seisrequest_iag_usp_br']:
            datacenters.append("USP")
        if self.conf['download']['chb_dc_service_iris_edu']:
            datacenters.append("IRIS")
            datacenters.append("IRISPH5")
        if self.conf['download']['chb_dc_service_ncedc_org']:
            datacenters.append("NCEDC")
        if self.conf['download']['chb_dc_service_scedc_caltech_edu']:
            datacenters.append("SCEDC")
        if self.conf['download']['chb_dc_webservices_ingv_it']:
            datacenters.append("INGV")
        if self.conf['download']['chb_dc_ws_icgc_cat']:
            datacenters.append("ICGC")
        if self.conf['download']['chb_dc_ws_resif_fr']:
            datacenters.append("RESIF")
            datacenters.append("RESIFPH5")
        if self.conf['download']['chb_dc_www_orfeus_eu_org']:
            datacenters.append("ODC")
            datacenters.append("ORFEUS")
        if self.conf['download']['chb_dc_fdsnws_raspberryshakedata_com']:
            datacenters.append("RASPISHAKE")
        return datacenters


    def get_utc_times(self):
        utc_times = []
        starttime = obspy.UTCDateTime(f"{self.startdate}T00:00:00Z")
        endtime = obspy.UTCDateTime(f"{self.enddate}T23:59:59Z")
        while starttime < endtime:
            utc_times.append([starttime, starttime + self.timelen])
            starttime += self.timelen
        return utc_times


    def get_iris_times(self):
        iris_times = []
        utc_times = self.get_utc_times()
        for i, tt in enumerate(utc_times):
            starttime = ','.join(str(tt[0]).split('Z')[0].split('T'))
            endtime = ','.join(str(tt[1]).split('Z')[0].split('T'))
            iris_times.append([starttime, endtime])
        return iris_times


    def get_mseed_event_dirs(self):
        mseed_folder_names = []
        utc_times = self.get_utc_times()
        for tt in utc_times:
            year = f"{tt[0].year}"
            jday = "%03d" %(tt[0].julday)
            hour = "%02d" %(tt[0].hour)
            minute = "%02d" %(tt[0].minute)
            second = "%02d" %(tt[0].second)
            mseed_folder_names.append(f"{year[2:]}{jday}{hour}{minute}{second}")
        return mseed_folder_names


    def get_mseed_filename(self,net,sta,chn,loc,utc_times):
        filename = "%s.%s.%s.%s__%4d%02d%02dT%02d%02d%02dZ__%4d%02d%02dT%02d%02d%02dZ.mseed" % (
        net,sta,loc,chn,
        utc_times[0].year,
        utc_times[0].month,
        utc_times[0].day,
        utc_times[0].hour,
        utc_times[0].minute,
        utc_times[0].second,
        utc_times[1].year,
        utc_times[1].month,
        utc_times[1].day,
        utc_times[1].hour,
        utc_times[1].minute,
        utc_times[1].second)
        return filename


    def check_IRIS_availability(self,net,sta,chn,loc,iris_times):
        PERL = self.conf['setting']['le_perl']
        # a trick to find out if data is available: If metafile is created, data is available!
        metafile = os.path.join(self.maindir,'.ans', 'check_iris.tmp')
        if os.path.isfile(metafile):
            os.remove(metafile)
        if len(loc):
            shell_cmd = f"{PERL} {fetch_data_script} -S {sta} -N {net} -C {chn} -L {loc} -s {iris_times[0]} -e {iris_times[1]} --lon -180:180 --lat -90:90 -m {metafile} -q\n"
        else:
            shell_cmd = f"{PERL} {fetch_data_script} -S {sta} -N {net} -C {chn} -s {iris_times[0]} -e {iris_times[1]} --lon -180:180 --lat -90:90 -m {metafile} -q\n"
        subprocess.call(shell_cmd, shell=True)
        if os.path.isfile(metafile):
            os.remove(metafile)
            return True
        else:
            return False


    def download_mseed_IRIS(self,net,sta,chn,loc,iris_times,download_dir):
        PERL = self.conf['setting']['le_perl']
        utc_starttime = obspy.UTCDateTime(f"{'T'.join(iris_times[0].split(','))}Z")
        utc_endtime = obspy.UTCDateTime(f"{'T'.join(iris_times[1].split(','))}Z")
        utc_times = [utc_starttime, utc_endtime]
        mseed = os.path.join(download_dir ,self.get_mseed_filename(net,sta,chn,loc,utc_times))
        if self.check_IRIS_availability(net,sta,chn,loc,iris_times):
            if len(loc):
                shell_cmd = f"{PERL} {fetch_data_script} -S {sta} -N {net} -C {chn} -L {loc} -s {iris_times[0]} -e {iris_times[1]} --lon -180:180 --lat -90:90 -o {mseed} -v\n"
            else:
                shell_cmd = f"{PERL} {fetch_data_script} -S {sta} -N {net} -C {chn} -s {iris_times[0]} -e {iris_times[1]} --lon -180:180 --lat -90:90 -o {mseed} -v\n"
            if not os.path.isfile(mseed):
                subprocess.call(shell_cmd, shell=True)
        else:
            pass


    def download_mseed_FDSN(self,net,sta,chn,loc,utc_times,download_dir):
        os.chdir(self.maindir)
        domain = RectangularDomain(minlatitude=-90, maxlatitude=90,minlongitude=-180, maxlongitude=180)
        restrictions = Restrictions(
        starttime=utc_times[0],
        endtime=utc_times[1],
        chunklength_in_sec=self.timelen,
        network=net,
        station=sta,
        location=loc,
        channel=chn,
        reject_channels_with_gaps=False,  # we will take care of data fragmentation later!
        minimum_length=0.0,  # all data is usefull!
        minimum_interstation_distance_in_m=0)
        datacenters = self.get_datacenters()
        for datacenter in datacenters:
            mseed_filename = self.get_mseed_filename(net,sta,chn,loc,utc_times)
            if mseed_filename not in os.listdir(download_dir):
                xml_file = os.path.join(download_dir,f"{net}.{sta}.xml")
                xml_file_renamed = os.path.join(download_dir,f"{net}.{sta}.{chn}")
                try:
                    client = Client(datacenter)
                    mdl = MassDownloader(providers=[client])
                    mdl.download(domain, restrictions, mseed_storage=download_dir,
                    stationxml_storage=download_dir, print_report=False)
                except:
                    pass
                if os.path.isfile(xml_file):
                    metafile = os.path.join(self.conf['download']['le_stameta'], f"{net}.{sta}.{chn}")
                    if os.path.isfile(metafile):
                        os.remove(xml_file) # not useful for response removal in most cases!
                    else:
                        os.rename(xml_file, xml_file_renamed) # keep it if metafile was not previousely downloaded


    def download_all(self):
        stations = STATIONS(self.maindir)
        stalist = stations.read_stalist()
        sta = stalist['sta']
        net = stalist['net']
        if not os.path.isdir(self.mseeds_dir):
            os.mkdir(self.mseeds_dir)
        mseed_events = self.get_mseed_event_dirs()
        utc_times = self.get_utc_times()
        iris_times = self.get_iris_times()
        for i, event in enumerate(mseed_events):
            download_dir = os.path.join(self.mseeds_dir, event)
            if not os.path.isdir(download_dir):
                os.mkdir(download_dir)
            ###Download####
            for loc in self.locations:
                for chn in self.channels:
                    for k in range(len(sta)):
                        if "IRIS" in self.get_datacenters() and self.conf['download']['chb_fetch']:
                            self.download_mseed_IRIS(net[k],sta[k],chn,loc,iris_times[i],download_dir)
                        if len(self.get_datacenters()) and self.conf['download']['chb_obspy']:
                            self.download_mseed_FDSN(net[k],sta[k],chn,loc,utc_times[i],download_dir)
            ###############
            if not len(os.listdir(download_dir)):
                shutil.rmtree(download_dir)




