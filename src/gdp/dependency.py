
import os
import subprocess

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


