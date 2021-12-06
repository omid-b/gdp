#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
from time import time

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
        '--about',
        action='store_true',
        help='about this package and contact information'
    )
    parser.add_argument('--version', action='version', version=f'%(prog)s {version}')
    parser._positionals.title = 'list of modules'
    subparsers = parser.add_subparsers(dest='module')
    #===== Module: dat =====#
    dat_module = subparsers.add_parser('dat', help='data processing module',
    description="Geographic or NaN data type processing module")
    dat_module._positionals.title = 'required argument choices'
    dat_command = dat_module.add_subparsers(dest='command')
    # gdp dat out
    dat_out = dat_command.add_parser('out', help='output/show content of single data file',
    description="Output/show content of single data file")
    dat_out.add_argument("input_files", nargs=1)
    dat_out.add_argument(
        '--nan',
        action='store_true',
        help='not a numerical data type')
    dat_out.add_argument(
        '-x',
        nargs='+',
        type=int,
        action='store',
        default=[1, 2],
        help='positional column number(s) (e.g., x, y; default=[1, 2])')
    dat_out.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    dat_out.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    dat_out.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    dat_out.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    dat_out.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    dat_out.add_argument(
        '--decimal',
        nargs='+',
        type=int,
        action='store',
        default=[4,4],
        help='number of decimals for positional and value argumanet (default=[4,4])')
    dat_out.add_argument(
        '--novalue',
        action='store_true',
        help='no value/data column(s) available')
    dat_out.add_argument(
        '--noextra',
        action='store_true',
        help='do not output extra columns (other than numerical columns)')
    dat_out.add_argument(
        '--nosort',
        action='store_true',
        help='do not apply sort to output lines')
    dat_out.add_argument(
        '--nouniq',
        action='store_true',
        help='do not apply unique to output lines')
    dat_out.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    # gdp dat uni
    dat_uni = dat_command.add_parser('uni', help='generate the union of input data files',
    description="Generate the union of input data files")
    dat_uni.add_argument("input_files", nargs='+')
    dat_uni.add_argument(
        '--nan',
        action='store_true',
        help='not a numerical data type')
    dat_uni.add_argument(
        '-x',
        nargs='+',
        type=int,
        action='store',
        default=[1, 2],
        help='positional column number(s) (e.g., x, y; default=[1, 2])')
    dat_uni.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    dat_uni.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    dat_uni.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    dat_uni.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    dat_uni.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    dat_uni.add_argument(
        '--decimal',
        nargs='+',
        type=int,
        action='store',
        default=[4,4],
        help='number of decimals for positional and value argumanet (default=[4,4])')
    dat_uni.add_argument(
        '--novalue',
        action='store_true',
        help='no value/data column(s) available')
    dat_uni.add_argument(
        '--noextra',
        action='store_true',
        help='do not output extra columns (other than numerical columns)')
    dat_uni.add_argument(
        '-i',
        '--inverse',
        action='store_true',
        help='inverse operation')
    dat_uni.add_argument(
        '--nosort',
        action='store_true',
        help='do not apply sort to output lines')
    dat_uni.add_argument(
        '--nouniq',
        action='store_true',
        help='do not apply unique to output lines')
    dat_uni.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    # gdp dat int
    dat_int = dat_command.add_parser('int', help='generate the intersect of input data files',
    description="Generate the intersect of input data files")
    dat_int.add_argument("input_files", nargs='+')
    dat_int.add_argument(
        '--nan',
        action='store_true',
        help='not a numerical data type')
    dat_int.add_argument(
        '-x',
        nargs='+',
        type=int,
        action='store',
        default=[1, 2],
        help='positional column number(s) (e.g., x, y; default=[1, 2])')
    dat_int.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    dat_int.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    dat_int.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    dat_int.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    dat_int.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    dat_int.add_argument(
        '--decimal',
        nargs='+',
        type=int,
        action='store',
        default=[4,4],
        help='number of decimals for positional and value argumanet (default=[4,4])')
    dat_int.add_argument(
        '--novalue',
        action='store_true',
        help='no value/data column(s) available')
    dat_int.add_argument(
        '--noextra',
        action='store_true',
        help='do not output extra columns (other than numerical columns)')
    dat_int.add_argument(
        '-i',
        '--inverse',
        action='store_true',
        help='inverse operation')
    dat_int.add_argument(
        '--nosort',
        action='store_true',
        help='do not apply sort to output lines')
    dat_int.add_argument(
        '--nouniq',
        action='store_true',
        help='do not apply unique to output lines')
    dat_int.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    # gdp dat dif
    dat_dif = dat_command.add_parser('dif', help='generate the difference of input data files',
    description="Generate the difference of input data files")
    dat_dif.add_argument("input_files", nargs='+')
    dat_dif.add_argument(
        '--nan',
        action='store_true',
        help='not a numerical data type')
    dat_dif.add_argument(
        '-x',
        nargs='+',
        type=int,
        action='store',
        default=[1, 2],
        help='positional column number(s) (e.g., x, y; default=[1, 2])')
    dat_dif.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    dat_dif.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    dat_dif.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    dat_dif.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    dat_dif.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    dat_dif.add_argument(
        '--decimal',
        nargs='+',
        type=int,
        action='store',
        default=[4,4],
        help='number of decimals for positional and value argumanet (default=[4,4])')
    dat_dif.add_argument(
        '--novalue',
        action='store_true',
        help='no value/data column(s) available')
    dat_dif.add_argument(
        '--noextra',
        action='store_true',
        help='do not output extra columns (other than numerical columns)')
    dat_dif.add_argument(
        '-i',
        '--inverse',
        action='store_true',
        help='inverse operation')
    dat_dif.add_argument(
        '--nosort',
        action='store_true',
        help='do not apply sort to output lines')
    dat_dif.add_argument(
        '--nouniq',
        action='store_true',
        help='do not apply unique to output lines')
    dat_dif.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    # gdp dat 1Dto2D
    dat_1Dto2D = dat_command.add_parser('1Dto2D', help='1Dto2D',
    description="1Dto2D")
    # gdp dat 1Dto3D
    dat_1Dto3D = dat_command.add_parser('1Dto3D', help='1Dto3D',
    description="1Dto3D")
    # gdp dat 2Dto1D
    dat_2Dto1D = dat_command.add_parser('2Dto1D', help='2Dto1D',
    description="2Dto1D")
    # gdp dat 2Dto3D
    dat_2Dto3D = dat_command.add_parser('2Dto3D', help='2Dto3D',
    description="2Dto3D")
    # gdp dat 3Dto1D
    dat_3Dto1D = dat_command.add_parser('3Dto1D', help='3Dto1D',
    description="3Dto1D")
    # gdp dat 3Dto2D
    dat_3Dto2D = dat_command.add_parser('3Dto2D', help='3Dto2D',
    description="3Dto2D")
    # gdp dat grd
    dat_grd = dat_command.add_parser('grd', help='gridding data (interpolation)',
    description="Gridding data (interpolation) with Gaussian smoothing")
    # gdp dat pip
    dat_pip = dat_command.add_parser('pip', help='points-in-polygon',
    description="Points-in-polygon (ray tracing method)")
    # gdp dat sum
    dat_sum = dat_command.add_parser('sum', help='calculate sum of the z column',
    description="Calculate summation of row values in the z column")
    # gdp dat avg
    dat_avg = dat_command.add_parser('avg', help='calculate average of the z column',
    description="Calculate average of row values in the z column")
    # gdp dat med
    dat_med = dat_command.add_parser('med', help='calculate median of the z column',
    description="Calculate median of row values in the z column")
    # gdp dat mod
    dat_mod = dat_command.add_parser('mod', help='calculate mode of the z column',
    description="Calculate mode of row values in the z column")
    # gdp dat std
    dat_std = dat_command.add_parser('std', help='calculate std of the z column',
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

###############################################################

def main(*args, **kwargs):
    args = parse_args(*args, **kwargs)
    if args.about or len(sys.argv) == 1:
        clear_screen()
        print(f"{about}\n")
        exit(1)
    #===== Module: dat =====#
    if args.module == 'dat':
        from . import dat
        from . import nan
        if args.command == 'out':
            from . import io
            out_lines = io.dat_lines(args.input_files[0], args)
            io.output_lines(out_lines, args)
            exit(0)
        if args.command == 'uni':
            if args.nan:
                nan.union(args)
            else:
                dat.union(args)
            exit(0)
        if args.command == 'int':
            if args.nan:
                nan.intersect(args)
            else:
                dat.intersect(args)
            exit(0)
        if args.command == 'dif':
            if args.nan:
                nan.difference(args)
            else:
                dat.difference(args)
            exit(0)
        if args.command == '1Dto2D':
            dat.conv_1Dto2D(args)
            exit(0)
        if args.command == '1Dto3D':
            dat.conv_1Dto3D(args)
            exit(0)
        if args.command == '2Dto1D':
            dat.conv_2Dto1D(args)
            exit(0)
        if args.command == '2Dto3D':
            dat.conv_2Dto3D(args)
            exit(0)
        if args.command == '3Dto1D':
            dat.conv_3Dto1D(args)
            exit(0)
        if args.command == '3Dto2D':
            dat.conv_3Dto2D(args)
            exit(0)
        if args.command == 'grd':
            subprocess.call('gdp dat grd -h', shell=True)
            under_dev()
        if args.command == 'pip':
            subprocess.call('gdp dat pip -h', shell=True)
            under_dev()
        if args.command == 'sum':
            subprocess.call('gdp dat sum -h', shell=True)
            under_dev()
        if args.command == 'avg':
            subprocess.call('gdp dat avg -h', shell=True)
            under_dev()
        if args.command == 'med':
            subprocess.call('gdp dat med -h', shell=True)
            under_dev()
        if args.command == 'mod':
            subprocess.call('gdp dat mod -h', shell=True)
            under_dev()
        if args.command == 'std':
            subprocess.call('gdp dat std -h', shell=True)
            under_dev()
        else:
            subprocess.call('gdp dat -h', shell=True)
    #===== Module: conv =====#
    if args.module == 'conv':
        if args.command == 'sac2dat':
            subprocess.call('gdp conv sac2dat -h', shell=True)
            under_dev()
        if args.command == 'mseed2sac':
            subprocess.call('gdp conv mseed2sac -h', shell=True)
            under_dev()
        if args.command == 'shp2dat':
            subprocess.call('gdp conv shp2dat -h', shell=True)
            under_dev()
        if args.command == 'nc2dat':
            subprocess.call('gdp conv nc2dat -h', shell=True)
            under_dev()
        else:
            subprocess.call('gdp conv -h', shell=True)



if __name__ == "__main__":
    main(*args, **kwargs)
