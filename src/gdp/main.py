#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
from time import time

version = "0.0.2"
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
    data_cat = data_command.add_parser('cat', help='concatenate and reformat input data files',
    description="Concatenate and reformat input data files")
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
    
    # gdp data split
    data_split = data_command.add_parser('split', help='split concatenated dataset',
    description="split a concatenated dataset into multiple data files")
    data_split._positionals.title = 'required positional arguments'
    data_split._optionals.title = 'optional/required arguments'
    data_split.add_argument("input_file", nargs=1)
    data_split.add_argument(
        '--method',
        choices=['nrow','ncol'],
        required=True,
        help='REQUIRED: split method (choices: nrow/ncol); nrow: split data based on fixed number of rows/lines; ncol: split data based on fixed number of columns')
    data_split.add_argument(
        '-n',
        '--number',
        type=int,
        required=True,
        help='REQUIRED: number of rows (method=nrow), or columns (method=ncol) to identify data split')
    data_split.add_argument(
        '-o',
        '--outdir',
        type=str,
        action='store',
        help='output directory')
    data_split.add_argument(
        '--ext',
        type=str,
        action='store',
        default = 'dat',
        help='Output files extension (default=dat)')
    data_split.add_argument(
        '--name',
        type=int,
        default=1,
        help='output file name row/line in each split data (default=1)')
    data_split.add_argument(
        '--start',
        type=int,
        default=0,
        help='only for method=ncol; start row from the reference row (default=0)')
    data_split.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    data_split.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')

    # gdp data min
    data_min = data_command.add_parser('min', help='calculate min of numerical column(s)',
    description="Calculate minimum of row values in numerical column(s)")
    data_min.add_argument("input_files", nargs='+')
    data_min.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    data_min.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    data_min.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    data_min.add_argument(
        '--decimal',
        nargs=1,
        type=int,
        action='store',
        default=[2],
        help='number of decimals (default=2)')
    data_min.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    data_min.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')

    # gdp data max
    data_max = data_command.add_parser('max', help='calculate max of numerical column(s)',
    description="Calculate maximum of row values in numerical column(s)")
    data_max.add_argument("input_files", nargs='+')
    data_max.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    data_max.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    data_max.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    data_max.add_argument(
        '--decimal',
        nargs=1,
        type=int,
        action='store',
        default=[2],
        help='number of decimals (default=2)')
    data_max.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    data_max.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')

    # gdp data sum
    data_sum = data_command.add_parser('sum', help='calculate sum of numerical column(s)',
    description="Calculate summation of row values in numerical column(s)")
    data_sum.add_argument("input_files", nargs='+')
    data_sum.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    data_sum.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    data_sum.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    data_sum.add_argument(
        '--decimal',
        nargs=1,
        type=int,
        action='store',
        default=[2],
        help='number of decimals (default=2)')
    data_sum.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    data_sum.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    
    # gdp data mean
    data_mean = data_command.add_parser('mean', help='calculate mean of numerical column(s)',
    description="Calculate mean of row values in numerical column(s)")
    data_mean.add_argument("input_files", nargs='+')
    data_mean.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    data_mean.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    data_mean.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    data_mean.add_argument(
        '--decimal',
        nargs=1,
        type=int,
        action='store',
        default=[2],
        help='number of decimals (default=2)')
    data_mean.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    data_mean.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    
    # gdp data median
    data_median = data_command.add_parser('median', help='calculate median of numerical column(s)',
    description="Calculate median of row values in numerical column(s)")
    data_median.add_argument("input_files", nargs='+')
    data_median.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    data_median.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    data_median.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    data_median.add_argument(
        '--decimal',
        nargs=1,
        type=int,
        action='store',
        default=[2],
        help='number of decimals (default=2)')
    data_median.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    data_median.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    
    # gdp data std
    data_std = data_command.add_parser('std', help='calculate std of numerical column(s)',
    description="Calculate standard deviation of row values in numerical column(s)")
    data_std.add_argument("input_files", nargs='+')
    data_std.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    data_std.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    data_std.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    data_std.add_argument(
        '--decimal',
        nargs=1,
        type=int,
        action='store',
        default=[2],
        help='number of decimals (default=2)')
    data_std.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    data_std.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')

    # gdp data pip
    data_pip = data_command.add_parser('pip', help='points-in-polygon',
    description="Points-in-polygon (ray tracing method). usage: gdp data pip <points_file> <polygon_file>")
    data_pip._positionals.title = 'required arguments'
    data_pip._optionals.title = 'optional arguments/settings for points_file'
    data_pip.add_argument("points_file", nargs='+', type=str, help="path to points_file(s)")
    data_pip.add_argument("polygon_file", nargs='*', type=str,
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
        '--polygon',
        type=str,
        action='store',
        help='path to polygon file.')
    data_pip.add_argument(
        '--lonrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='x/longitude range: [minlon, maxlon]; this option could be used to specify polygon region if a polygon file is not available.')
    data_pip.add_argument(
        '--latrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='y/latitude range: [minlat, maxlat]; this option could be used to specify polygon region if a polygon file is not available.')
    data_pip.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file/folder')
    data_pip.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')

    # gdp data gridder
    data_gridder = data_command.add_parser('gridder', help='gridding/interpolation of 2D/map data',
    description="Gridding/interpolation of 2D/map data with Gaussian smoothing applied")
    data_gridder.add_argument("input_files", nargs='+')
    data_gridder.add_argument(
        '--spacing',
        nargs='+',
        type=float,
        action='store',
        required=True,
        help='REQUIRED: grid spacing along [longitude, latitude]'
    )
    data_gridder.add_argument(
        '--smoothing',
        type=float,
        required=True,
        help='REQUIRED: grid smoothing length (km)'
    )
    data_gridder.add_argument(
        '--lonrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='grid x/longitude range: [minlon, maxlon] (default=Auto)')
    data_gridder.add_argument(
        '--latrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='grid y/latitude range: [minlat, maxlat] (default=Auto)')
    data_gridder.add_argument(
        '-x',
        nargs=2,
        type=int,
        action='store',
        default=[1, 2],
        help='[longitude, latitude] column number(s) (default=[1, 2])')
    data_gridder.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    data_gridder.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    data_gridder.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    data_gridder.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for positional and value columns respectively (default=[".4",".4"])')
    data_gridder.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    data_gridder.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file/folder'
    )
    data_gridder.add_argument(
        '--polygon',
        type=str,
        action='store',
        help='polygon to run "points-in-polygon" process before outputing the results'
    )



    #===== Module: convert =====#
    convert_module = subparsers.add_parser('convert', help="data conversion module",
    description="Conversion of different data types or formats")
    convert_module._positionals.title = 'required argument choices'
    convert_command = convert_module.add_subparsers(dest='command')
    
    # # gdp convert 1Dto2D
    # convert_1Dto2D = convert_command.add_parser('1Dto2D', help='1Dto2D',
    # description="1Dto2D")
    
    # # gdp convert 1Dto3D
    # convert_1Dto3D = convert_command.add_parser('1Dto3D', help='1Dto3D',
    # description="1Dto3D")
    
    # # gdp convert 2Dto1D
    # convert_2Dto1D = convert_command.add_parser('2Dto1D', help='2Dto1D',
    # description="2Dto1D")
    
    # # gdp convert 2Dto3D
    # convert_2Dto3D = convert_command.add_parser('2Dto3D', help='2Dto3D',
    # description="2Dto3D")
    
    # # gdp convert 3Dto1D
    # convert_3Dto1D = convert_command.add_parser('3Dto1D', help='3Dto1D',
    # description="3Dto1D")
    
    # # gdp convert 3Dto2D
    # convert_3Dto2D = convert_command.add_parser('3Dto2D', help='3Dto2D',
    # description="3Dto2D")
    
    # gdp convert mseed2sac
    convert_mseed2sac = convert_command.add_parser('mseed2sac', help='convert mseed to sac',
    description="Convert mseed to sac. This script also handles data fragmentation issue. ")
    convert_mseed2sac.add_argument("input_files", nargs='+')
    convert_mseed2sac.add_argument(
        '-o',
        '--outdir',
        type=str,
        required=True,
        help='REQUIRED: path to output directory'
    )
    convert_mseed2sac.add_argument(
        '--reformat',
        action='store_true',
        help='reformat output sac files i.e. rename and output to related directories based on mseed start time, station & channel information'
    )
    convert_mseed2sac.add_argument(
        '--offset',
        type=float,
        default=0,
        help='output filename start time offset in seconds (only if rename=True; default=0)'
    )
    convert_mseed2sac.add_argument(
        '--resample',
        type=float,
        default=999,
        help='output sac files sampling frequency'
    )
    
    
    # gdp convert sac2dat
    convert_sac2dat = convert_command.add_parser('sac2dat', help='convert sac to dat (ascii)',
    description="Convert sac to dat (ascii); output format: time, amplitude")
    convert_sac2dat.add_argument("input_files", nargs='+')
    convert_sac2dat.add_argument(
        '-o',
        '--outdir',
        type=str,
        required=True,
        help='REQUIRED: path to output directory'
    )
    convert_sac2dat.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".2",".2"],
        help='float format for time and value columns respectively (default=[".2",".2"])')
    convert_sac2dat.add_argument(
        '--timerange',
        nargs=2,
        type=float,
        action='store',
        default=[999, 999],
        help='time range limit')
        
    # # gdp convert shp2dat
    # convert_shp2dat = convert_command.add_parser('shp2dat', help='convert shp to dat (ascii)',
    # description="Convert shape file to dat (ascii)")
    
    # gdp convert nc2dat
    convert_nc2dat = convert_command.add_parser('nc2dat', help='convert nc to dat (ascii)',
    description="Convert nc files to dat/ascii")
    convert_nc2dat.add_argument("input_file", type=str, action='store', nargs=1, help='input nc file')
    convert_nc2dat.add_argument(
        '--metadata',
        action='store_true',
        help='only output metadata'
    )
    convert_nc2dat.add_argument(
    	'-v',
        '--data',
        nargs='*',
        type=str,
        help="data field name(s) / vlue column(s); hint: use '--metadata' flag for more information"
    )
    convert_nc2dat.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output data to file')
    convert_nc2dat.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    convert_nc2dat.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for positional and value columns respectively (default=[".4",".4"])')
    
    # return arguments
    return parser.parse_args()

###############################################################

def main(*args, **kwargs):
    args = parse_args(*args, **kwargs)
    if args.about or len(sys.argv) == 1:
        clear_screen()
        print(f"{about}\n")
        exit(0)
        
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
        if args.command == 'split':
            # check arguments
            if args.number < 0 :
                print(f"\nError! Argument 'number' should be a positive integer\n")
                exit(1)
            if args.header < 0 :
                print(f"\nError! Argument 'header' should be a positive integer\n")
                exit(1)
            if args.footer < 0 :
                print(f"\nError! Argument 'footer' should be a positive integer\n")
                exit(1)
            if args.name < 1 :
                print(f"\nError! Argument 'name' should be a positive integer (> 0) for method=nrow\n")
                exit(1)
            if args.name > args.number:
                print(f"\nError! Argument 'name' should be less than or equal argument 'number' for method=nrow\n")
                exit(1)
            # start split
            if args.method == 'nrow':
                if args.start:
                    print(f"\nError! Argument 'start' is only for method=ncol\n")
                    exit(1)
                nan.split_data_nrow(args)
                exit(0)
            else:
                nan.split_data_ncol(args)
                exit(0)
        if args.command == 'gridder':
            if len(args.spacing) == 1:
                args.spacing = [args.spacing[0], args.spacing[0]]

            if args.spacing[0] <= 0 or args.spacing[1] <= 0:
                print(f"Error! 'spacing' should be positive.")
                exit(1)
            elif args.smoothing <= 0:
                print(f"Error! 'smoothing' should be positive.")
                exit(1)
            elif args.lonrange[0] >= args.lonrange[1]:
                print(f"Error! Argument 'lonrange' should be entered in [minlon, maxlon] format.")
                exit(1)
            elif args.latrange[0] >= args.latrange[1]:
                print(f"Error! Argument 'latrange' should be entered in [minlat, maxlat] format.")
                exit(1)
            elif args.lonrange[0] < -180:
                print(f"Error! minimum longitude is less than -180.")
                exit(1)
            elif args.lonrange[1] > 180:
                print(f"Error! maximum longitude is greater than 180.")
                exit(1)
            elif args.latrange[0] < -90:
                print(f"Error! minimum latitude is less than -90.")
                exit(1)
            elif args.latrange[1] > 90:
                print(f"Error! maximum latitude is greater than 90.")
                exit(1)

            dat.gridder(args)
            exit(0)
        if args.command == 'pip':
            dat.points_in_polygon(args)
            exit(0)
        if args.command == 'min':
            dat.calc_min(args)
            exit(0)
        if args.command == 'max':
            dat.calc_max(args)
            exit(0)
        if args.command == 'sum':
            dat.calc_sum(args)
            exit(0)
        if args.command == 'mean':
            dat.calc_mean(args)
            exit(0)
        if args.command == 'median':
            dat.calc_median(args)
            exit(0)
        if args.command == 'std':
            dat.calc_std(args)
            exit(0)
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
            conv.sac2dat(args)
            exit(0)
        if args.command == 'mseed2sac':
            conv.mseed2sac(args)
            exit(0)
        if args.command == 'shp2dat':
            subprocess.call('gdp convert shp2dat -h', shell=True)
            under_dev()
        if args.command == 'nc2dat':
            conv.nc2dat(args)
            exit(0)
        else:
            subprocess.call('gdp convert -h', shell=True)



if __name__ == "__main__":
    main(*args, **kwargs)
