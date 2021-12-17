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
    #===== Module: data =====#
    data_module = subparsers.add_parser('data', help='data processing module',
    description="Geographic or NaN data type processing module")
    data_module._positionals.title = 'required argument choices'
    data_command = data_module.add_subparsers(dest='command')
    # gdp data cat
    data_cat = data_command.add_parser('cat', help='concatenate and reformat input files',
    description="Concatenate and reformat input files")
    data_cat.add_argument("input_files", nargs='+')
    data_cat.add_argument(
        '--nan',
        action='store_true',
        help='not a numerical data type')
    data_cat.add_argument(
        '-x',
        nargs='*',
        type=int,
        action='store',
        default=[1, 2],
        help='positional column number(s) (default=[1, 2]; [] is also accepted)')
    data_cat.add_argument(
        '-v',
        nargs='*',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3]; [] is also accepted)')
    data_cat.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    data_cat.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    data_cat.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for positional and value columns respectively (default=[".4",".4"])')
    data_cat.add_argument(
        '--sort',
        action='store_true',
        help='apply sort to output lines')
    data_cat.add_argument(
        '--uniq',
        action='store_true',
        help='apply uniq to output lines')
    data_cat.add_argument(
        '--noextra',
        action='store_true',
        help='do not output extra columns (other than numerical columns)')
    data_cat.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    data_cat.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    data_cat.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    # gdp data union
    data_union = data_command.add_parser('union', help='generate the union of input data files',
    description="Generate the union of input data files")
    data_union.add_argument("input_files", nargs='+')
    data_union.add_argument(
        '--nan',
        action='store_true',
        help='not a numerical data type')
    data_union.add_argument(
        '-x',
        nargs='+',
        type=int,
        action='store',
        default=[1, 2],
        help='positional column number(s) (default=[1, 2]; [] is also accepted)')
    data_union.add_argument(
        '-v',
        nargs='*',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3]; [] is also accepted)')
    data_union.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    data_union.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    data_union.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for positional and value columns respectively (default=[".4",".4"])')
    data_union.add_argument(
        '--sort',
        action='store_true',
        help='apply sort to output lines')
    data_union.add_argument(
        '--uniq',
        action='store_true',
        help='apply uniq to output lines')
    data_union.add_argument(
        '--noextra',
        action='store_true',
        help='do not output extra columns (other than numerical columns)')
    data_union.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    data_union.add_argument(
        '-i',
        '--inverse',
        action='store_true',
        help='inverse operation')
    data_union.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    data_union.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    # gdp data intersect
    data_intersect = data_command.add_parser('intersect', help='generate the intersect of input data files',
    description="Generate the intersect of input data files")
    data_intersect.add_argument("input_files", nargs='+')
    data_intersect.add_argument(
        '--nan',
        action='store_true',
        help='not a numerical data type')
    data_intersect.add_argument(
        '-x',
        nargs='+',
        type=int,
        action='store',
        default=[1, 2],
        help='positional column number(s) (default=[1, 2]; [] is also accepted)')
    data_intersect.add_argument(
        '-v',
        nargs='*',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3]; [] is also accepted)')
    data_intersect.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    data_intersect.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    data_intersect.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for positional and value columns respectively (default=[".4",".4"])')
    data_intersect.add_argument(
        '--sort',
        action='store_true',
        help='apply sort to output lines')
    data_intersect.add_argument(
        '--uniq',
        action='store_true',
        help='apply uniq to output lines')
    data_intersect.add_argument(
        '--noextra',
        action='store_true',
        help='do not output extra columns (other than numerical columns)')
    data_intersect.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    data_intersect.add_argument(
        '-i',
        '--inverse',
        action='store_true',
        help='inverse operation')
    data_intersect.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    data_intersect.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    # gdp data difference
    data_difference = data_command.add_parser('difference', help='generate the difference of input data files',
    description="Generate the difference of input data files")
    data_difference.add_argument("input_files", nargs='+')
    data_difference.add_argument(
        '--nan',
        action='store_true',
        help='not a numerical data type')
    data_difference.add_argument(
        '-x',
        nargs='+',
        type=int,
        action='store',
        default=[1, 2],
        help='positional column number(s) (default=[1, 2]; [] is also accepted)')
    data_difference.add_argument(
        '-v',
        nargs='*',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3]; [] is also accepted)')
    data_difference.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    data_difference.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    data_difference.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for positional and value columns respectively (default=[".4",".4"])')
    data_difference.add_argument(
        '--sort',
        action='store_true',
        help='apply sort to output lines')
    data_difference.add_argument(
        '--uniq',
        action='store_true',
        help='apply uniq to output lines')
    data_difference.add_argument(
        '--noextra',
        action='store_true',
        help='do not output extra columns (other than numerical columns)')
    data_difference.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    data_difference.add_argument(
        '-i',
        '--inverse',
        action='store_true',
        help='inverse operation')
    data_difference.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    data_difference.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    # gdp data unmerge
    data_unmerge = data_command.add_parser('unmerge', help='unmerge concatenated data file',
    description="unmerge a concatenated data file into multiple data files")
    data_unmerge.add_argument("input_files", nargs=1)
    # gdp data gridder
    data_gridder = data_command.add_parser('gridder', help='gridding data (interpolation)',
    description="Gridding data (interpolation) with Gaussian smoothing")
    # gdp data pip
    data_pip = data_command.add_parser('pip', help='points-in-polygon',
    description="Points-in-polygon (ray tracing method). usage: gdp data pip <points_file> <polygon_file>")
    data_pip._positionals.title = 'required arguments'
    data_pip._optionals.title = 'optional arguments/settings for points_file'
    data_pip.add_argument("points_file", nargs=1, type=str, help="path to points_file")
    data_pip.add_argument("polygon_file", nargs=1, type=str,
        help="path to polygon_file; '*.shp' is also accepted (first polygon is read); if ascii: file content column format must be [lon, lat]")
    data_pip.add_argument(
        '-x',
        nargs=2,
        type=int,
        action='store',
        default=[1, 2],
        help='positional column number(s) (default=[1, 2])')
    data_pip.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    data_pip.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    data_pip.add_argument(
        '-i',
        '--inverse',
        action='store_true',
        help='inverse operation: points outside polygon')
    data_pip.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    data_pip.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    # gdp data sum
    data_sum = data_command.add_parser('sum', help='calculate sum of a numerical column',
    description="Calculate summation of row values in a numerical column")
    # gdp data mean
    data_mean = data_command.add_parser('mean', help='calculate mean of a numerical column',
    description="Calculate mean of row values in a numerical column")
    # gdp data median
    data_median = data_command.add_parser('median', help='calculate median of a numerical column',
    description="Calculate median of row values in a numerical column")
    # gdp data mode
    data_mode = data_command.add_parser('mode', help='calculate mode of a numerical column',
    description="Calculate mode of row values in a numerical column")
    # gdp data std
    data_std = data_command.add_parser('std', help='calculate std of a numerical column',
    description="Calculate standard deviation of row values in a numerical column")
    #===== Module: convert =====#
    convert_module = subparsers.add_parser('convert', help='data conversion module (file type/format)',
    description="Conversion of different data types or formats (e.g., mseed2sac, 2Dto1D etc.)")
    convert_module._positionals.title = 'required argument choices'
    convert_command = convert_module.add_subparsers(dest='command')
    # gdp data 1Dto2D
    convert_1Dto2D = convert_command.add_parser('1Dto2D', help='1Dto2D',
    description="1Dto2D")
    # gdp data 1Dto3D
    convert_1Dto3D = convert_command.add_parser('1Dto3D', help='1Dto3D',
    description="1Dto3D")
    # gdp data 2Dto1D
    convert_2Dto1D = convert_command.add_parser('2Dto1D', help='2Dto1D',
    description="2Dto1D")
    # gdp data 2Dto3D
    convert_2Dto3D = convert_command.add_parser('2Dto3D', help='2Dto3D',
    description="2Dto3D")
    # gdp data 3Dto1D
    convert_3Dto1D = convert_command.add_parser('3Dto1D', help='3Dto1D',
    description="3Dto1D")
    # gdp data 3Dto2D
    convert_3Dto2D = convert_command.add_parser('3Dto2D', help='3Dto2D',
    description="3Dto2D")
    # gdp convert sac2dat
    convert_sac2dat = convert_command.add_parser('sac2dat', help='convert sac to dat (ascii)',
    description="Convert sac to dat (ascii; output format: time, amplitude)")
    # gdp convert mseed2sac
    convert_mseed2sac = convert_command.add_parser('mseed2sac', help='convert mseed to sac',
    description="Convert mseed to sac. This script also handles data fragmentation issue. ")
    # gdp convert shp2dat
    convert_shp2dat = convert_command.add_parser('shp2dat', help='convert shp to dat',
    description="Convert shape file to dat (ascii)")
    # gdp convert nc2xyz
    convert_nc2xyz = convert_command.add_parser('nc2xyz', help='convert nc to xyz',
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
    #===== Module: data =====#
    if args.module == 'data':
        from . import dat
        from . import nan
        if args.command == 'cat':
            from . import io
            out_lines = []
            for inpfile in args.input_files:
                out_lines += io.data_lines(inpfile, args)
            io.output_lines(out_lines, args)
            exit(0)
        if args.command == 'union':
            if args.nan:
                nan.union(args)
            else:
                dat.union(args)
            exit(0)
        if args.command == 'intersect':
            if args.nan:
                nan.intersect(args)
            else:
                dat.intersect(args)
            exit(0)
        if args.command == 'difference':
            if args.nan:
                nan.difference(args)
            else:
                dat.difference(args)
            exit(0)
        if args.command == 'gridder':
            subprocess.call('gdp data gridder -h', shell=True)
            under_dev()
        if args.command == 'pip':
            dat.points_in_polygon(args)
            exit(0)
        if args.command == 'sum':
            subprocess.call('gdp data sum -h', shell=True)
            under_dev()
        if args.command == 'mean':
            subprocess.call('gdp data mean -h', shell=True)
            under_dev()
        if args.command == 'median':
            subprocess.call('gdp data median -h', shell=True)
            under_dev()
        if args.command == 'mode':
            subprocess.call('gdp data mode -h', shell=True)
            under_dev()
        if args.command == 'std':
            subprocess.call('gdp data std -h', shell=True)
            under_dev()
        else:
            subprocess.call('gdp data -h', shell=True)
    #===== Module: convert =====#
    if args.module == 'convert':
        from . import conv
        if args.command == '1Dto2D':
            subprocess.call('gdp convert 1Dto2D -h', shell=True)
            under_dev()
        if args.command == '1Dto3D':
            subprocess.call('gdp convert 1Dto3D -h', shell=True)
            under_dev()
        if args.command == '2Dto1D':
            subprocess.call('gdp convert 2Dto1D -h', shell=True)
            under_dev()
        if args.command == '2Dto3D':
            subprocess.call('gdp convert 2Dto3D -h', shell=True)
            under_dev()
        if args.command == '3Dto1D':
            subprocess.call('gdp convert 3Dto1D -h', shell=True)
            under_dev()
        if args.command == '3Dto2D':
            subprocess.call('gdp convert 3Dto2D -h', shell=True)
            under_dev()
        if args.command == 'sac2dat':
            subprocess.call('gdp convert sac2dat -h', shell=True)
            under_dev()
        if args.command == 'mseed2sac':
            subprocess.call('gdp convert mseed2sac -h', shell=True)
            under_dev()
        if args.command == 'shp2dat':
            subprocess.call('gdp convert shp2dat -h', shell=True)
            under_dev()
        if args.command == 'nc2dat':
            subprocess.call('gdp convert nc2dat -h', shell=True)
            under_dev()
        else:
            subprocess.call('gdp convert -h', shell=True)



if __name__ == "__main__":
    main(*args, **kwargs)
