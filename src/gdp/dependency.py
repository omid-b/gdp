
import os
import subprocess

def check_all():
    num_errors = 0
    perl = find_perl_path()
    sac = find_sac_path()
    gmt = find_gmt_path()
    print("\nChecking all dependencies... This might take a while...\n")
    if len(perl) == 0:
        print("WARNING! Could not find PERL interperter.")
        num_errors += 1
    if len(sac) == 0:
        print("WARNING! Could not find SAC (Seismic Analysis Code) in this environment.")
        num_errors += 1
    if len(gmt) == 0:
        print("WARNING! Could not find GMT (Generic Mapping Tools) in this environment.")
        num_errors += 1
    try:
        import argparse
    except:
        print("Import Error: 'import argparse'")
        num_errors += 1
    try:
        import configparser
    except:
        print("Import Error: 'import configparser'")
        num_errors += 1
    try:
        import earthpy.mask as em
    except:
        print("Import Error: 'import earthpy.mask as em'")
        num_errors += 1
    try:
        import earthpy.plot as ep
    except:
        print("Import Error: 'import earthpy.plot as ep'")
        num_errors += 1
    try:
        import geopandas as gpd
    except:
        print("Import Error: 'import geopandas as gpd'")
        num_errors += 1
    try:
        import matplotlib
    except:
        print("Import Error: 'import matplotlib'")
        num_errors += 1
    try:
        import matplotlib
    except:
        print("Import Error: 'import matplotlib'")
        num_errors += 1
    try:
        import matplotlib.backends.backend_tkagg as tkagg
    except:
        print("Import Error: 'import matplotlib.backends.backend_tkagg as tkagg'")
        num_errors += 1
    try:
        import matplotlib.pyplot as plt
    except:
        print("Import Error: 'import matplotlib.pyplot as plt'")
        num_errors += 1
    try:
        import matplotlib.transforms as mtrans
    except:
        print("Import Error: 'import matplotlib.transforms as mtrans'")
        num_errors += 1
    try:
        import netCDF4 as nc
    except:
        print("Import Error: 'import netCDF4 as nc'")
        num_errors += 1
    try:
        import numpy as np
    except:
        print("Import Error: 'import numpy as np'")
        num_errors += 1
    try:
        import obspy
    except:
        print("Import Error: 'import obspy'")
        num_errors += 1
    try:
        import operator
    except:
        print("Import Error: 'import operator'")
        num_errors += 1
    try:
        import os
    except:
        print("Import Error: 'import os'")
        num_errors += 1
    try:
        import pyclipper
    except:
        print("Import Error: 'import pyclipper'")
        num_errors += 1
    try:
        import pyproj
    except:
        print("Import Error: 'import pyproj'")
        num_errors += 1
    try:
        import random
    except:
        print("Import Error: 'import random'")
        num_errors += 1
    try:
        import rasterio
    except:
        print("Import Error: 'import rasterio'")
        num_errors += 1
    try:
        import re
    except:
        print("Import Error: 'import re'")
        num_errors += 1
    try:
        import requests
    except:
        print("Import Error: 'import requests'")
        num_errors += 1
    try:
        import seaborn as sns
    except:
        print("Import Error: 'import seaborn as sns'")
        num_errors += 1
    try:
        import shutil
    except:
        print("Import Error: 'import shutil'")
        num_errors += 1
    try:
        import subprocess
    except:
        print("Import Error: 'import subprocess'")
        num_errors += 1
    try:
        import sys
    except:
        print("Import Error: 'import sys'")
        num_errors += 1
    try:
        import tkinter as tk
    except:
        print("Import Error: 'import tkinter as tk'")
        num_errors += 1
    try:
        import tkinter.messagebox
    except:
        print("Import Error: 'import tkinter.messagebox'")
        num_errors += 1
    try:
        import warnings
    except:
        print("Import Error: 'import warnings'")
        num_errors += 1
    try:
        from bs4 import BeautifulSoup
    except:
        print("Import Error: 'from bs4 import BeautifulSoup'")
        num_errors += 1
    try:
        from osgeo import gdal, osr
    except:
        print("Import Error: 'from osgeo import gdal, osr'")
        num_errors += 1
    if num_errors:
        print(f"\nNumber of errors found: {num_errors}\n")
        exit(1)
    else:
        print("All tests ran successfully!")
        exit(0)


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


