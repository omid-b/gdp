
import os
import obspy
import shutil
import subprocess
from urllib import request

from obspy.clients.fdsn.client import Client
from obspy.clients.fdsn.mass_downloader import RectangularDomain
from obspy.clients.fdsn.mass_downloader import Restrictions
from obspy.clients.fdsn.mass_downloader import MassDownloader

from . import stations
from . import events

pkg_dir, _ = os.path.split(__file__)
fetch_data_script = os.path.join(pkg_dir, "FetchData-2018.337")

class MSEEDS:
    def __init__(self, config, args):
        self.config = config
        self.mseeds_dir = args.mseeds
        self.maindir = args.maindir
        self.channels = self.config['station_setting']['station_channels']
        self.locations = [""] + self.config['station_setting']['station_location_codes']
        self.stalist_file = self.config['station_setting']['station_list']
        self.startdate = self.config['download_setting']['startdate']
        self.enddate = self.config['download_setting']['enddate']
        self.duration = args.duration
        self.offset = args.offset
        self.ant = args.ant

        if not len(self.startdate) or not len(self.enddate):
            print("Error! 'startdate' and/or 'enddate' are not specified in 'download.config'!\n")
            exit(1)
        if self.duration <= 0:
            print("Error! Argument 'duration' must be a positive integer.\n")
            exit(1)
        if not len(self.channels):
            print("Error! Station channels to download are not specified.\n")
            exit(1)

        if self.config['download_setting']['iris_fetch_script'] == False and  \
            self.config['download_setting']['obspy_mdl_script'] == False:
            print("Error! Both 'iris_fetch_script' and 'obspy_mdl_script' are disabled.")
            print("Check section 'download_setting' in 'download.config'.\n")
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
        if self.config['datacenters']['nrcan']:
            datacenters.append('NRCAN')
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


    def get_utc_times(self):
        utc_times = []
        if self.ant:
            starttime = obspy.UTCDateTime(f"{self.startdate}T00:00:00Z") + self.offset
            endtime = obspy.UTCDateTime(f"{self.enddate}T23:59:59Z") + self.offset
            while starttime < endtime:
                utc_times.append([starttime, starttime + self.duration])
                starttime += self.duration
        else:
            events_obj = events.EVENTS(self.config)
            events_list = events_obj.read_events()
            for i, date in enumerate(events_list['date']):
                event_datetime = obspy.UTCDateTime(f"{date}T{events_list['time'][i]}")
                starttime = event_datetime + self.offset
                utc_times.append([starttime, starttime + self.duration])
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
            tt[0] = tt[0] - self.offset
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
        PERL = self.config['dependencies']['perl']
        if not len(PERL):
            print("Error! Perl executable is not set in 'download.config'")
            exit(1)
        # a trick to find out if data is available: If metafile is created, data is available!
        metafile = os.path.join(self.maindir, 'check_iris.tmp')
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
        PERL = self.config['dependencies']['perl']
        if not len(PERL):
            print("Error! Perl executable is not set in 'download.config'")
            exit(1)
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
        chunklength_in_sec=self.duration,
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
                    if datacenter.lower() == 'nrcan':
                        client = Client(base_url='https://www.earthquakescanada.nrcan.gc.ca')
                    else:
                        client = Client(datacenter)
                    mdl = MassDownloader(providers=[client])
                    mdl.download(domain, restrictions, mseed_storage=download_dir,
                    stationxml_storage=download_dir, print_report=False)
                except:
                    pass
                if os.path.isfile(xml_file):
                    os.remove(xml_file) # not useful


    def download_all(self):
        stations_obj = stations.STATIONS(self.config)
        stalist = stations_obj.read_stalist()
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
                        if len(self.get_datacenters()) and self.config['download_setting']['obspy_mdl_script']:
                            self.download_mseed_FDSN(net[k],sta[k],chn,loc,utc_times[i],download_dir)
                        if "IRIS" in self.get_datacenters() and self.config['download_setting']['iris_fetch_script']:
                            self.download_mseed_IRIS(net[k],sta[k],chn,loc,iris_times[i],download_dir)
            ###############
            if not len(os.listdir(download_dir)):
                shutil.rmtree(download_dir)




