#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess

version = "0.0.1"
about = """\
gdp: Geophysical Data Processing
\nContact information:
    Author: Omid Bagherpur Mojaver
    Email: omid.bagherpur@gmail.com
    GitHub: https://github.com/omid-b/gdp
    PyPI: https://pypi.org/project/gdp
\nPlease enter 'gdp -h' or 'gdp --help' for usage information.\
"""


def under_dev():
    print("\nNOT DEVELOPED YET!\n")
    exit(1)


def clear_screen():
    if sys.platform in ["linux","linux2","darwin"]:
        os.system('clear')
    elif sys.platform == "win32":
        os.system('cls')


def parse_args(*args, **kwargs):
    # gdp
    parser = argparse.ArgumentParser('gdp',
    description="gdp: Geophysical Data Processing",
    conflict_handler='resolve')
    parser.add_argument(
        '-a',
        '--about',
        action='store_true',
        help='about this package and contact information'
    )
    parser.add_argument('--version', action='version', version=f'%(prog)s {version}')
    parser._positionals.title = 'list of modules'
    subparsers = parser.add_subparsers(dest='module')
    #===== Module: dat =====#
    dat_module = subparsers.add_parser('dat', help='general data type processing module',
    description="General ascii data type processing module (e.g., datalist files: 'datalist.dat')")
    dat_module._positionals.title = 'required argument choices'
    dat_command = dat_module.add_subparsers(dest='command')
    # gdp dat uni
    dat_uni = dat_command.add_parser('uni', help='generate uniform of data files',
    description="Generate the uniform of data files (lines)")
    # gdp dat int
    dat_int = dat_command.add_parser('int', help='generate intersect of data files',
    description="Generate the intersect of data files (lines)")
    # gdp dat dif
    dat_dif = dat_command.add_parser('dif', help='generate difference of data files',
    description="Generate the difference of data files (lines)")    
    #===== Module: xyz =====#
    xyz_module = subparsers.add_parser('xyz', help='xyz data type processing module',
    description="Geographic XYZ (lon, lat, ...) ascii data processing module\
    (e.g., velocity models, topography data). Data could have more than three columns.")
    xyz_module._positionals.title = 'required argument choices'
    xyz_command = xyz_module.add_subparsers(dest='command')
    # gdp xyz uni
    xyz_uni = xyz_command.add_parser('uni', help='generate uniform of xyz files',
    description="Generate the uniform of xyz files")
    # gdp xyz int
    xyz_int = xyz_command.add_parser('int', help='generate intersect of xyz files',
    description="Generate the intersect of xyz files")
    # gdp xyz dif
    xyz_dif = xyz_command.add_parser('dif', help='generate difference of xyz files',
    description="Generate the difference of xyz files")
    # gdp xyz grd
    xyz_grd = xyz_command.add_parser('grd', help='gridding data (interpolation)',
    description="Gridding data (interpolation) with Gaussian smoothing")
    # gdp xyz pip
    xyz_pip = xyz_command.add_parser('pip', help='points-in-polygon',
    description="Points-in-polygon (ray tracing method)")
    # gdp xyz sum
    xyz_sum = xyz_command.add_parser('sum', help='calculate sum of the z column',
    description="Calculate summation of row values in the z column")
    # gdp xyz avg
    xyz_avg = xyz_command.add_parser('avg', help='calculate average of the z column',
    description="Calculate average of row values in the z column")
    # gdp xyz med
    xyz_med = xyz_command.add_parser('med', help='calculate median of the z column',
    description="Calculate median of row values in the z column")
    # gdp xyz mod
    xyz_mod = xyz_command.add_parser('mod', help='calculate mode of the z column',
    description="Calculate mode of row values in the z column")
    # gdp xyz std
    xyz_std = xyz_command.add_parser('std', help='calculate std of the z column',
    description="Calculate standard deviation of row values in the z column")
    #===== Module: convert =====#
    conv_module = subparsers.add_parser('conv', help='data conversion module module',
    description="Conversion of different data types (e.g., mseed to sac)")
    conv_module._positionals.title = 'required argument choices'
    conv_command = conv_module.add_subparsers(dest='command')
    # gdp conv sac2dat
    conv_sac2dat = conv_command.add_parser('sac2dat', help='convert sac to dat (ascii)',
    description="Convert sac to dat (ascii; output format: time, amplitude)")
    # gdp conv mseed2sac
    conv_mseed2sac = conv_command.add_parser('mseed2sac', help='convert mseed to sac',
    description="Convert mseed to sac. This script also handles data fragmentation issue. ")
    # gdp conv shp2xyz
    conv_shp2xyz = conv_command.add_parser('shp2xyz', help='convert shp to xyz',
    description="Convert shape file to xyz/ascii (shp to xyz")
    # gdp conv nc2xyz
    conv_nc2xyz = conv_command.add_parser('nc2xyz', help='convert nc to xyz',
    description="Convert nc to xyz/ascii")
    # return arguments
    return parser.parse_args()



def main(*args, **kwargs):
    clear_screen()
    args = parse_args(*args, **kwargs)
    if args.about or len(sys.argv) == 1:
        print(f"{about}\n")
        exit(1)
    #===== Module: dat =====#
    if args.module == 'dat':
        if args.command == 'uni':
            subprocess.call('gdp dat uni -h', shell=True)
            under_dev()
        if args.command == 'int':
            subprocess.call('gdp dat int -h', shell=True)
            under_dev()
        if args.command == 'dif':
            subprocess.call('gdp dat dif -h', shell=True)
            under_dev()
        else:
            subprocess.call('gdp dat -h', shell=True)
    #===== Module: xyz =====#
    if args.module == 'xyz':
        if args.command == 'uni':
            subprocess.call('gdp xyz uni -h', shell=True)
            under_dev()
        if args.command == 'int':
            subprocess.call('gdp xyz int -h', shell=True)
            under_dev()
        if args.command == 'dif':
            subprocess.call('gdp xyz dif -h', shell=True)
            under_dev()
        if args.command == 'grd':
            subprocess.call('gdp xyz grd -h', shell=True)
            under_dev()
        if args.command == 'pip':
            subprocess.call('gdp xyz pip -h', shell=True)
            under_dev()
        if args.command == 'sum':
            subprocess.call('gdp xyz sum -h', shell=True)
            under_dev()
        if args.command == 'avg':
            subprocess.call('gdp xyz avg -h', shell=True)
            under_dev()
        if args.command == 'med':
            subprocess.call('gdp xyz med -h', shell=True)
            under_dev()
        if args.command == 'mod':
            subprocess.call('gdp xyz mod -h', shell=True)
            under_dev()
        if args.command == 'std':
            subprocess.call('gdp xyz std -h', shell=True)
            under_dev()
        else:
            subprocess.call('gdp xyz -h', shell=True)
    #===== Module: conv =====#
    if args.module == 'conv':
        if args.command == 'sac2dat':
            subprocess.call('gdp conv sac2dat -h', shell=True)
            under_dev()
        if args.command == 'mseed2sac':
            subprocess.call('gdp conv mseed2sac -h', shell=True)
            under_dev()
        if args.command == 'shp2xyz':
            subprocess.call('gdp conv shp2xyz -h', shell=True)
            under_dev()
        if args.command == 'nc2xyz':
            subprocess.call('gdp conv nc2xyz -h', shell=True)
            under_dev()
        else:
            subprocess.call('gdp conv -h', shell=True)



if __name__ == "__main__":
    main(*args, **kwargs)
