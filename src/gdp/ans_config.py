import os
import sys
import subprocess
import configparser
from numpy import array

setting_params = ["le_maindir","le_startdate","le_enddate",
                  "le_maxlat","le_minlon","le_maxlon","le_minlat",
                  "le_sac","le_gmt","le_perl"]

download_params = ["chb_dc_service_iris_edu","chb_dc_service_ncedc_org","chb_dc_service_scedc_caltech_edu",
                   "chb_dc_rtserve_beg_utexas_edu","chb_dc_eida_bgr_de","chb_dc_ws_resif_fr","chb_dc_seisrequest_iag_usp_br",
                   "chb_dc_eida_service_koeri_boun_edu_tr","chb_dc_eida_ethz_ch","chb_dc_geofon_gfz_potsdam_de",
                   "chb_dc_ws_icgc_cat","chb_dc_eida_ipgp_fr","chb_dc_fdsnws_raspberryshakedata_com",
                   "chb_dc_webservices_ingv_it","chb_dc_erde_geophysik_uni_muenchen_de","chb_dc_eida_sc3_infp_ro",
                   "chb_dc_eida_gein_noa_gr","chb_dc_www_orfeus_eu_org","chb_dc_auspass_edu_au",
                   "le_stalist","le_stameta","le_mseeds","le_stalocs","le_stachns","le_timelen","chb_obspy","chb_fetch"]

mseed2sac_params = ["mseed2sac_procs"]


sac2ncf_params = ["sac2ncf_procs"]


ncf2egf_params = ["chb_ncf2egf_symmetrize", "chb_ncf2egf_cut", "le_ncf2egf_cut_begin", "le_ncf2egf_cut_end",
                  "chb_ncf2egf_bp", "le_ncf2egf_bp_cp1", "le_ncf2egf_bp_cp2",
                  "sb_ncf2egf_bp_poles", "sb_ncf2egf_bp_passes"]


integer_params = ["chb_dc_service_iris_edu","chb_dc_service_ncedc_org","chb_dc_service_scedc_caltech_edu",
                  "chb_dc_rtserve_beg_utexas_edu","chb_dc_eida_bgr_de","chb_dc_ws_resif_fr",
                  "chb_dc_seisrequest_iag_usp_br","chb_dc_eida_service_koeri_boun_edu_tr",
                  "chb_dc_eida_ethz_ch","chb_dc_geofon_gfz_potsdam_de","chb_dc_ws_icgc_cat",
                  "chb_dc_eida_ipgp_fr","chb_dc_fdsnws_raspberryshakedata_com","chb_dc_webservices_ingv_it",
                  "chb_dc_erde_geophysik_uni_muenchen_de","chb_dc_eida_sc3_infp_ro",
                  "chb_dc_eida_gein_noa_gr","chb_dc_www_orfeus_eu_org","chb_dc_auspass_edu_au",
                  "chb_obspy","chb_fetch","chb_mseed2sac_detrend","chb_mseed2sac_taper",
                  "cmb_mseed2sac_detrend_method","cmb_mseed2sac_taper_method","sb_mseed2sac_detrend_order",
                  "cmb_mseed2sac_final_sf","cmb_mseed2sac_resp_output","cmb_mseed2sac_resp_prefilter",
                  "sb_mseed2sac_bp_poles","sb_mseed2sac_bp_passes", "le_timelen", "le_mseed2sac_dspline",
                  "cmb_sac2ncf_final_sf","cmb_sac2ncf_resp_output","cmb_sac2ncf_resp_prefilter",
                  "sb_sac2ncf_bp_poles","sb_sac2ncf_bp_passes", "le_sac2ncf_dspline", "sb_sac2ncf_whiten_order",
                  "chb_ncf2egf_symmetrize", "chb_ncf2egf_cut", "chb_ncf2egf_bp",
                  "sb_ncf2egf_bp_poles", "sb_ncf2egf_bp_passes",
                  "cmb_sac2ncf_detrend_method", "sb_sac2ncf_detrend_order"]

float_params = ["dsb_mseed2sac_max_taper", "le_minlat","le_maxlat","le_minlon","le_maxlon",
                "le_mseed2sac_bp_cp1", "le_mseed2sac_bp_cp2", "le_sac2ncf_bp_cp1", "le_sac2ncf_bp_cp2",
                "le_ncf2egf_cut_begin", "le_ncf2egf_cut_end", "le_ncf2egf_bp_cp1", "le_ncf2egf_bp_cp2"]

intlist_params = ["pid"]



def read_config(maindir):
    maindir = os.path.abspath(maindir)
    config_file = os.path.join(maindir, 'ans.config')
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
    except Exception as e:
        print(f"Error reading config file!\n{e}\n")
        return False
    if not os.path.isfile(config_file):
        print("Error! Could not find 'ans.config' in project directory.\n")
        exit(1)
    # all main sections available?
    for section in ["setting","download","mseed2sac"]:
        if section not in config.sections():
            print(f"read_config(): Config section not available: '{section}'")
            return False
    # setting
    setting = {}
    for param in setting_params:
        if param not in config.options('setting'):
            print(f"read_config(): Config parameter not available in [setting]: '{param}'")
            return False
        val = config.get('setting',f"{param}")
        if param in integer_params and len(val):
            setting[f"{param}"] = int(val)
        elif param in float_params and len(val):
            setting[f"{param}"] = float(val)
        elif param in intlist_params and len(val):
            setting[f"{param}"] = array(val.split(), dtype=int).tolist()
        else:
            setting[f"{param}"] = val
    # download
    download = {}
    for param in download_params:
        if param not in config.options('download'):
            print(f"read_config(): Config parameter not available in [download]: '{param}'")
            return False
        if param in integer_params:
            download[f"{param}"] = int(config.get('download',f"{param}"))
        elif param in float_params:
            download[f"{param}"] = float(config.get('download',f"{param}"))
        elif param in intlist_params:
            download[f"{param}"] = config.get('download',f"{param}")
            download[f"{param}"] = array(download[f"{param}"].split(), dtype=int).tolist()
        else:
            download[f"{param}"] = config.get('download',f"{param}")
    # mseed2sac
    mseed2sac = {}
    for param in mseed2sac_params:
        if param not in config.options('mseed2sac'):
            print(f"read_config(): Config parameter not available in [mseed2sac]: '{param}'")
            return False
        mseed2sac[f"{param}"] = config.get('mseed2sac',f"{param}")
    mseed2sac_proc_sections = mseed2sac['mseed2sac_procs'].split()
    mseed2sac['mseed2sac_procs'] = []
    for section in mseed2sac_proc_sections:
        proc_params = {}
        for param in config.options(f'{section}'):
            if param in integer_params:
                proc_params[f"{param}"] = int(config.get(f"{section}",f"{param}"))
            elif param in float_params:
                proc_params[f"{param}"] = float(config.get(f"{section}",f"{param}"))
            elif param in intlist_params:
                proc_params[f"{param}"] = config.get(f"{section}",f"{param}")
                proc_params[f"{param}"] = array(proc_params[f"{param}"].split(), dtype=int).tolist()
            else:
                proc_params[f"{param}"] = config.get(f"{section}",f"{param}")
        mseed2sac['mseed2sac_procs'].append(proc_params)

    # sac2ncf
    sac2ncf = {}
    for param in sac2ncf_params:
        if param not in config.options('sac2ncf'):
            print(f"read_config(): Config parameter not available in [sac2ncf]: '{param}'")
            return False
        sac2ncf[f"{param}"] = config.get('sac2ncf',f"{param}")
    sac2ncf_proc_sections = sac2ncf['sac2ncf_procs'].split()
    sac2ncf['sac2ncf_procs'] = []
    for section in sac2ncf_proc_sections:
        proc_params = {}
        for param in config.options(f'{section}'):
            if param in integer_params:
                proc_params[f"{param}"] = int(config.get(f"{section}",f"{param}"))
            elif param in float_params:
                proc_params[f"{param}"] = float(config.get(f"{section}",f"{param}"))
            elif param in intlist_params:
                proc_params[f"{param}"] = config.get(f"{section}",f"{param}")
                proc_params[f"{param}"] = array(proc_params[f"{param}"].split(), dtype=int).tolist()
            else:
                proc_params[f"{param}"] = config.get(f"{section}",f"{param}")
        sac2ncf['sac2ncf_procs'].append(proc_params)

    # ncf2egf
    ncf2egf = {}
    for param in ncf2egf_params:
        if param not in config.options('ncf2egf'):
            print(f"read_config(): Config parameter not available in [ncf2egf]: '{param}'")
            return False
        val = config.get('ncf2egf',f"{param}")
        if param in integer_params and len(val):
            ncf2egf[f"{param}"] = int(val)
        elif param in float_params and len(val):
            ncf2egf[f"{param}"] = float(val)
        elif param in intlist_params and len(val):
            ncf2egf[f"{param}"] = array(val.split(), dtype=int).tolist()
        else:
            ncf2egf[f"{param}"] = val


    # put together the return dictionary
    parameters = {}
    parameters['setting'] = setting
    parameters['download'] = download
    parameters['mseed2sac'] = mseed2sac
    parameters['sac2ncf'] = sac2ncf
    parameters['ncf2egf'] = ncf2egf
    return parameters



def write_config(maindir, parameters):
    maindir = os.path.abspath(maindir)
    config_file = os.path.join(maindir, 'ans.config')
    if not parameters:
        return False
    fopen = open(config_file, "w") 
    # setting
    fopen.write("[setting]\n")
    for key in parameters['setting'].keys():
        fopen.write(f"{key} = {parameters['setting'][key]}\n")
    # download
    fopen.write("\n[download]\n")
    for key in parameters['download'].keys():
        fopen.write(f"{key} = {parameters['download'][key]}\n")
    
    # mseed2sac
    fopen.write("\n[mseed2sac]\n")
    mseed2sac_nprocs = len(parameters['mseed2sac']['mseed2sac_procs'])
    mseed2sac_proc_sections = []
    for i in range(mseed2sac_nprocs):
        mseed2sac_proc_sections.append(f"mseed2sac_proc_{i+1}")
    fopen.write(f"mseed2sac_procs = {' '.join(mseed2sac_proc_sections)}\n")
    for i, section in enumerate(mseed2sac_proc_sections):
        fopen.write(f"\n[{section}]\n")
        for key in parameters['mseed2sac']['mseed2sac_procs'][i].keys():
            if key in intlist_params:
                fopen.write(f"{key} = {' '.join(array(parameters['mseed2sac']['mseed2sac_procs'][i][key], dtype=str))}\n")
            else:
                fopen.write(f"{key} = {parameters['mseed2sac']['mseed2sac_procs'][i][key]}\n")
    
    # sac2ncf 
    fopen.write("\n[sac2ncf]\n")
    sac2ncf_nprocs = len(parameters['sac2ncf']['sac2ncf_procs'])
    sac2ncf_proc_sections = []
    for i in range(sac2ncf_nprocs):
        sac2ncf_proc_sections.append(f"sac2ncf_proc_{i+1}")
    fopen.write(f"sac2ncf_procs = {' '.join(sac2ncf_proc_sections)}\n")
    for i, section in enumerate(sac2ncf_proc_sections):
        fopen.write(f"\n[{section}]\n")
        for key in parameters['sac2ncf']['sac2ncf_procs'][i].keys():
            if key in intlist_params:
                fopen.write(f"{key} = {' '.join(array(parameters['sac2ncf']['sac2ncf_procs'][i][key], dtype=str))}\n")
            else:
                fopen.write(f"{key} = {parameters['sac2ncf']['sac2ncf_procs'][i][key]}\n")

    # ncf2egf
    fopen.write("\n[ncf2egf]\n")
    fopen.write(f"chb_ncf2egf_symmetrize = {parameters['ncf2egf']['chb_ncf2egf_symmetrize']}\n")
    fopen.write(f"chb_ncf2egf_cut = {parameters['ncf2egf']['chb_ncf2egf_cut']}\n")
    fopen.write(f"le_ncf2egf_cut_begin = {parameters['ncf2egf']['le_ncf2egf_cut_begin']}\n")
    fopen.write(f"le_ncf2egf_cut_end = {parameters['ncf2egf']['le_ncf2egf_cut_end']}\n")
    fopen.write(f"chb_ncf2egf_bp = {parameters['ncf2egf']['chb_ncf2egf_bp']}\n")
    fopen.write(f"le_ncf2egf_bp_cp1 = {parameters['ncf2egf']['le_ncf2egf_bp_cp1']}\n")
    fopen.write(f"le_ncf2egf_bp_cp2 = {parameters['ncf2egf']['le_ncf2egf_bp_cp2']}\n")
    fopen.write(f"sb_ncf2egf_bp_poles = {parameters['ncf2egf']['sb_ncf2egf_bp_poles']}\n")
    fopen.write(f"sb_ncf2egf_bp_passes = {parameters['ncf2egf']['sb_ncf2egf_bp_passes']}\n")


    fopen.close()
    return True



class Defaults:
    def __init__(self, maindir):
        self.maindir = os.path.abspath(maindir)

    
    def parameters(self):
        parameters = {}
        parameters['setting'] = self.setting()
        parameters['download'] = self.download()
        parameters['mseed2sac'] = self.mseed2sac()
        parameters['sac2ncf'] = self.sac2ncf()
        parameters['ncf2egf'] = self.ncf2egf()
        return parameters



    def setting(self):
        setting = {}
        setting['le_maindir'] = self.maindir
        setting['le_startdate'] = ""
        setting['le_enddate'] = ""
        setting['le_maxlat'] = ""
        setting['le_minlon'] = ""
        setting['le_maxlon'] = ""
        setting['le_minlat'] = ""
        if sys.platform in ['darwin', 'linux', 'linux2', 'cygwin']:
            if os.path.isfile("/usr/local/sac/bin/sac"):
                SAC = "/usr/local/sac/bin/sac"
            elif os.path.isfile("/usr/local/bin/sac"):
                SAC = "/usr/local/bin/sac"
            elif os.path.isfile("/usr/bin/sac"):
                SAC = "/usr/bin/sac"
            else:
                SAC = "sac"

            if os.path.isfile("/usr/local/gmt/bin/gmt"):
                GMT = "/usr/local/gmt/bin/gmt"
            if os.path.isfile("/usr/gmt/bin/gmt"):
                GMT = "/usr/local/gmt/bin/gmt"
            elif os.path.isfile("/usr/local/bin/gmt"):
                GMT = "/usr/local/bin/gmt"
            elif os.path.isfile("/usr/bin/gmt"):
                GMT = "/usr/bin/gmt"
            else:
                GMT = "gmt"
                
            setting['le_sac'] = SAC
            setting['le_gmt'] = GMT
            setting['le_perl'] = '/usr/bin/perl'
        else:
            setting['le_sac'] = "sac"
            setting['le_gmt'] = "gmt"
            setting['le_perl'] = "perl"
        return setting


    def download(self):
        download = {}
        # data centers
        download['chb_dc_service_iris_edu'] = 2
        download['chb_dc_service_ncedc_org'] = 0
        download['chb_dc_service_scedc_caltech_edu'] = 0
        download['chb_dc_rtserve_beg_utexas_edu'] = 0
        download['chb_dc_eida_bgr_de'] = 0
        download['chb_dc_ws_resif_fr'] = 0
        download['chb_dc_seisrequest_iag_usp_br'] = 0
        download['chb_dc_eida_service_koeri_boun_edu_tr'] = 0
        download['chb_dc_eida_ethz_ch'] = 0
        download['chb_dc_geofon_gfz_potsdam_de'] = 0
        download['chb_dc_ws_icgc_cat'] = 0
        download['chb_dc_eida_ipgp_fr'] = 0
        download['chb_dc_fdsnws_raspberryshakedata_com'] = 0
        download['chb_dc_webservices_ingv_it'] = 0
        download['chb_dc_erde_geophysik_uni_muenchen_de'] = 0
        download['chb_dc_eida_sc3_infp_ro'] = 0
        download['chb_dc_eida_gein_noa_gr'] = 0
        download['chb_dc_www_orfeus_eu_org'] = 0
        download['chb_dc_auspass_edu_au'] = 0
        # download setting
        download['le_stalist'] = os.path.join(self.maindir, 'stations.dat')
        download['le_stameta'] = os.path.join(self.maindir, 'metadata')
        download['le_mseeds'] = os.path.join(self.maindir, 'mseeds')
        download['le_stalocs'] = "00 10"
        download['le_stachns'] = "BHZ HHZ"
        download['le_timelen'] = 86400
        # download scripts
        download['chb_obspy'] = 2
        download['chb_fetch'] = 2
        return download


    def mseed2sac(self):
        mseed2sac = {}
        mseed2sac['mseed2sac_procs'] = []
        # process 1 
        mseed2sac_proc_1 = {}
        mseed2sac_proc_1['pid'] = [1,1] # MSEED to SAC
        mseed2sac_proc_1['chb_mseed2sac_detrend'] = 2
        mseed2sac_proc_1['chb_mseed2sac_taper'] = 2
        mseed2sac_proc_1['cmb_mseed2sac_detrend_method'] = 3
        mseed2sac_proc_1['sb_mseed2sac_detrend_order'] = 4
        mseed2sac_proc_1['le_mseed2sac_dspline'] = 864000
        mseed2sac_proc_1['cmb_mseed2sac_taper_method'] = 0
        mseed2sac_proc_1['dsb_mseed2sac_max_taper'] = 0.005
        # process 2  
        mseed2sac_proc_2 = {}
        mseed2sac_proc_2['pid'] = [2,2] # Decimate
        mseed2sac_proc_2['cmb_mseed2sac_final_sf'] = 0 # 1 Hz
        # process 3 
        mseed2sac_proc_3 = {}
        mseed2sac_proc_3['pid'] = [3,1] # Remove response
        mseed2sac_proc_3['le_mseed2sac_stametadir'] = os.path.join(self.maindir, 'metadata')
        mseed2sac_proc_3['cmb_mseed2sac_resp_output'] = 1 # velocity
        mseed2sac_proc_3['cmb_mseed2sac_resp_prefilter'] = 1 # [0.001, 0.005, 45, 50]
        # append processes to the list
        mseed2sac['mseed2sac_procs'].append(mseed2sac_proc_1)
        mseed2sac['mseed2sac_procs'].append(mseed2sac_proc_2)
        mseed2sac['mseed2sac_procs'].append(mseed2sac_proc_3)
        return mseed2sac

    def sac2ncf(self):
        sac2ncf = {}
        sac2ncf['sac2ncf_procs'] = []
        # process 1: Temporal normalize
        sac2ncf_proc_1 = {}
        sac2ncf_proc_1['pid'] = [8,1]
        # process 2 
        sac2ncf_proc_2 = {}
        sac2ncf_proc_2['pid'] = [9,1]
        sac2ncf_proc_2['sb_sac2ncf_whiten_order'] = 6
        # process 3 
        sac2ncf_proc_3 = {}
        sac2ncf_proc_3['pid'] = [10,1]
        # append processes to the list
        sac2ncf['sac2ncf_procs'].append(sac2ncf_proc_1)
        sac2ncf['sac2ncf_procs'].append(sac2ncf_proc_2)
        sac2ncf['sac2ncf_procs'].append(sac2ncf_proc_3)
        return sac2ncf

    def ncf2egf(self):
        ncf2egf = {}
        ncf2egf['chb_ncf2egf_symmetrize'] = 0
        ncf2egf['chb_ncf2egf_cut'] = 0
        ncf2egf['le_ncf2egf_cut_begin'] = -3000
        ncf2egf['le_ncf2egf_cut_end'] = 3000
        ncf2egf['chb_ncf2egf_bp'] = 0
        ncf2egf['le_ncf2egf_bp_cp1'] = 3
        ncf2egf['le_ncf2egf_bp_cp2'] = 300
        ncf2egf['sb_ncf2egf_bp_poles'] = 3
        ncf2egf['sb_ncf2egf_bp_passes'] = 2
        return ncf2egf

