#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
from time import time

version = "0.1.0"
about = """\
gdp: Geophysical Data Processing
\nContact information:
    Author: Omid Bagherpur
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
    parser._positionals.title = 'list of tools'
    subparsers = parser.add_subparsers(dest='module')
    #===== Module: data =====#
    
    # gdp data cat
    gdp_cat = subparsers.add_parser('cat', help='concatenate and reformat input data files',
    description="Concatenate and reformat input data files")
    gdp_cat.add_argument("input_files", nargs='+')
    gdp_cat.add_argument(
        '--nan',
        action='store_true',
        help='not a numerical data type')
    gdp_cat.add_argument(
        '-x',
        nargs='*',
        type=int,
        action='store',
        default=[1, 2],
        help='positional column number(s) (default=[1, 2]; [] is also accepted)')
    gdp_cat.add_argument(
        '-v',
        nargs='*',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3]; [] is also accepted)')
    gdp_cat.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    gdp_cat.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    gdp_cat.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for positional and value columns respectively (default=[".4",".4"])')
    gdp_cat.add_argument(
        '--sort',
        action='store_true',
        help='apply sort to output lines')
    gdp_cat.add_argument(
        '--uniq',
        action='store_true',
        help='apply uniq to output lines')
    gdp_cat.add_argument(
        '--noextra',
        action='store_true',
        help='do not output extra columns (other than numerical columns)')
    gdp_cat.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    gdp_cat.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    gdp_cat.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    
    # gdp data union
    gdp_union = subparsers.add_parser('union', help='generate the union of input data files',
    description="Generate the union of input data files")
    gdp_union.add_argument("input_files", nargs='+')
    gdp_union.add_argument(
        '--nan',
        action='store_true',
        help='not a numerical data type')
    gdp_union.add_argument(
        '-x',
        nargs='+',
        type=int,
        action='store',
        default=[1, 2],
        help='positional column number(s) (default=[1, 2]; [] is also accepted)')
    gdp_union.add_argument(
        '-v',
        nargs='*',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3]; [] is also accepted)')
    gdp_union.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    gdp_union.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    gdp_union.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for positional and value columns respectively (default=[".4",".4"])')
    gdp_union.add_argument(
        '--sort',
        action='store_true',
        help='apply sort to output lines')
    gdp_union.add_argument(
        '--uniq',
        action='store_true',
        help='apply uniq to output lines')
    gdp_union.add_argument(
        '--noextra',
        action='store_true',
        help='do not output extra columns (other than numerical columns)')
    gdp_union.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    gdp_union.add_argument(
        '-i',
        '--inverse',
        action='store_true',
        help='inverse operation')
    gdp_union.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    gdp_union.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    
    # gdp data intersect
    gdp_intersect = subparsers.add_parser('intersect', help='generate the intersect of input data files',
    description="Generate the intersect of input data files")
    gdp_intersect.add_argument("input_files", nargs='+')
    gdp_intersect.add_argument(
        '--nan',
        action='store_true',
        help='not a numerical data type')
    gdp_intersect.add_argument(
        '-x',
        nargs='+',
        type=int,
        action='store',
        default=[1, 2],
        help='positional column number(s) (default=[1, 2]; [] is also accepted)')
    gdp_intersect.add_argument(
        '-v',
        nargs='*',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3]; [] is also accepted)')
    gdp_intersect.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    gdp_intersect.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    gdp_intersect.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for positional and value columns respectively (default=[".4",".4"])')
    gdp_intersect.add_argument(
        '--sort',
        action='store_true',
        help='apply sort to output lines')
    gdp_intersect.add_argument(
        '--uniq',
        action='store_true',
        help='apply uniq to output lines')
    gdp_intersect.add_argument(
        '--noextra',
        action='store_true',
        help='do not output extra columns (other than numerical columns)')
    gdp_intersect.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    gdp_intersect.add_argument(
        '-i',
        '--inverse',
        action='store_true',
        help='inverse operation')
    gdp_intersect.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    gdp_intersect.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    
    # gdp data difference
    gdp_difference = subparsers.add_parser('difference', help='generate the difference of input data files',
    description="Generate the difference of input data files")
    gdp_difference.add_argument("input_files", nargs='+')
    gdp_difference.add_argument(
        '--nan',
        action='store_true',
        help='not a numerical data type')
    gdp_difference.add_argument(
        '-x',
        nargs='+',
        type=int,
        action='store',
        default=[1, 2],
        help='positional column number(s) (default=[1, 2]; [] is also accepted)')
    gdp_difference.add_argument(
        '-v',
        nargs='*',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3]; [] is also accepted)')
    gdp_difference.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    gdp_difference.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    gdp_difference.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for positional and value columns respectively (default=[".4",".4"])')
    gdp_difference.add_argument(
        '--sort',
        action='store_true',
        help='apply sort to output lines')
    gdp_difference.add_argument(
        '--uniq',
        action='store_true',
        help='apply uniq to output lines')
    gdp_difference.add_argument(
        '--noextra',
        action='store_true',
        help='do not output extra columns (other than numerical columns)')
    gdp_difference.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    gdp_difference.add_argument(
        '-i',
        '--inverse',
        action='store_true',
        help='inverse operation')
    gdp_difference.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    gdp_difference.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    
    # gdp data split
    gdp_split = subparsers.add_parser('split', help='split concatenated dataset',
    description="Split a concatenated dataset into multiple data files")
    gdp_split._positionals.title = 'required positional arguments'
    gdp_split._optionals.title = 'optional/required arguments'
    gdp_split.add_argument("input_file", nargs=1)
    gdp_split.add_argument(
        '--method',
        choices=['nrow','ncol'],
        required=True,
        help='REQUIRED: split method (choices: nrow/ncol); nrow: split data based on fixed number of rows/lines; ncol: split data based on fixed number of columns')
    gdp_split.add_argument(
        '-n',
        '--number',
        type=int,
        required=True,
        help='REQUIRED: number of rows (method=nrow), or columns (method=ncol) to identify data split')
    gdp_split.add_argument(
        '-o',
        '--outdir',
        type=str,
        action='store',
        help='output directory')
    gdp_split.add_argument(
        '--ext',
        type=str,
        action='store',
        default = 'dat',
        help='Output files extension (default=dat)')
    gdp_split.add_argument(
        '--name',
        type=int,
        default=1,
        help='output file name row/line in each split data (default=1)')
    gdp_split.add_argument(
        '--start',
        type=int,
        default=0,
        help='only for method=ncol; start row from the reference row (default=0)')
    gdp_split.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    gdp_split.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')

    # gdp data min
    gdp_min = subparsers.add_parser('min', help='calculate min of numerical column(s)',
    description="Calculate minimum of values in numerical column(s)")
    gdp_min.add_argument("input_files", nargs='+')
    gdp_min.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    gdp_min.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    gdp_min.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    gdp_min.add_argument(
        '--decimal',
        nargs=1,
        type=int,
        action='store',
        default=[2],
        help='number of decimals (default=2)')
    gdp_min.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    gdp_min.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')

    # gdp data max
    gdp_max = subparsers.add_parser('max', help='calculate max of numerical column(s)',
    description="Calculate maximum of values in numerical column(s)")
    gdp_max.add_argument("input_files", nargs='+')
    gdp_max.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    gdp_max.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    gdp_max.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    gdp_max.add_argument(
        '--decimal',
        nargs=1,
        type=int,
        action='store',
        default=[2],
        help='number of decimals (default=2)')
    gdp_max.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    gdp_max.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')

    # gdp data sum
    gdp_sum = subparsers.add_parser('sum', help='calculate sum of numerical column(s)',
    description="Calculate summation of values in numerical column(s)")
    gdp_sum.add_argument("input_files", nargs='+')
    gdp_sum.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    gdp_sum.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    gdp_sum.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    gdp_sum.add_argument(
        '--decimal',
        nargs=1,
        type=int,
        action='store',
        default=[2],
        help='number of decimals (default=2)')
    gdp_sum.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    gdp_sum.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    
    # gdp data mean
    gdp_mean = subparsers.add_parser('mean', help='calculate mean of numerical column(s)',
    description="Calculate mean of values in numerical column(s)")
    gdp_mean.add_argument("input_files", nargs='+')
    gdp_mean.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    gdp_mean.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    gdp_mean.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    gdp_mean.add_argument(
        '--decimal',
        nargs=1,
        type=int,
        action='store',
        default=[2],
        help='number of decimals (default=2)')
    gdp_mean.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    gdp_mean.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    
    # gdp data median
    gdp_median = subparsers.add_parser('median', help='calculate median of numerical column(s)',
    description="Calculate median of values in numerical column(s)")
    gdp_median.add_argument("input_files", nargs='+')
    gdp_median.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    gdp_median.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    gdp_median.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    gdp_median.add_argument(
        '--decimal',
        nargs=1,
        type=int,
        action='store',
        default=[2],
        help='number of decimals (default=2)')
    gdp_median.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    gdp_median.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    
    # gdp data std
    gdp_std = subparsers.add_parser('std', help='calculate std of numerical column(s)',
    description="Calculate standard deviation of values in numerical column(s)")
    gdp_std.add_argument("input_files", nargs='+')
    gdp_std.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    gdp_std.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    gdp_std.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    gdp_std.add_argument(
        '--decimal',
        nargs=1,
        type=int,
        action='store',
        default=[2],
        help='number of decimals (default=2)')
    gdp_std.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    gdp_std.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')

    # gdp data pip
    gdp_pip = subparsers.add_parser('pip', help='points-in-polygon',
    description="Points-in-polygon (ray tracing method). usage: gdp data pip <points_file> <polygon_file>")
    gdp_pip._positionals.title = 'required arguments'
    gdp_pip._optionals.title = 'optional arguments/settings for points_file'
    gdp_pip.add_argument("points_file", nargs='+', type=str, help="path to points_file(s)")
    gdp_pip.add_argument("polygon_file", nargs='*', type=str,
        help="path to polygon_file; '*.shp' is also accepted (first polygon is read); if ascii: file content column format must be [lon, lat]")
    gdp_pip.add_argument(
        '-x',
        nargs=2,
        type=int,
        action='store',
        default=[1, 2],
        help='positional column number(s) (default=[1, 2])')
    gdp_pip.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    gdp_pip.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    gdp_pip.add_argument(
        '-i',
        '--inverse',
        action='store_true',
        help='inverse operation: points outside polygon')
    gdp_pip.add_argument(
        '--polygon',
        type=str,
        action='store',
        help='path to polygon file.')
    gdp_pip.add_argument(
        '--lonrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='x/longitude range: [minlon, maxlon]; this option could be used to specify polygon region if a polygon file is not available.')
    gdp_pip.add_argument(
        '--latrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='y/latitude range: [minlat, maxlat]; this option could be used to specify polygon region if a polygon file is not available.')
    gdp_pip.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file/folder')
    gdp_pip.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')

    # gdp data gridder
    gdp_gridder = subparsers.add_parser('gridder', help='gridding/interpolation of 2D/map data',
    description="Gridding/interpolation of 2D/map data with Gaussian smoothing applied")
    gdp_gridder.add_argument("input_files", nargs='+')
    gdp_gridder.add_argument(
        '--spacing',
        nargs='+',
        type=float,
        action='store',
        required=True,
        help='REQUIRED: grid spacing along [longitude, latitude]'
    )
    gdp_gridder.add_argument(
        '--smoothing',
        type=float,
        required=True,
        help='REQUIRED: grid smoothing length (km)'
    )
    gdp_gridder.add_argument(
        '--lonrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='grid x/longitude range: [minlon, maxlon] (default=Auto)')
    gdp_gridder.add_argument(
        '--latrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='grid y/latitude range: [minlat, maxlat] (default=Auto)')
    gdp_gridder.add_argument(
        '-x',
        nargs=2,
        type=int,
        action='store',
        default=[1, 2],
        help='[longitude, latitude] column number(s) (default=[1, 2])')
    gdp_gridder.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    gdp_gridder.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    gdp_gridder.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    gdp_gridder.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for positional and value columns respectively (default=[".4",".4"])')
    gdp_gridder.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    gdp_gridder.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file/folder'
    )
    gdp_gridder.add_argument(
        '--polygon',
        type=str,
        action='store',
        help='polygon to run "points-in-polygon" process before outputing the results'
    )



    #===== Module: convert =====#
    
    # # gdp convert 1Dto2D
    # gdp_1Dto2D = subparsers.add_parser('1Dto2D', help='1Dto2D',
    # description="1Dto2D")
    
    # # gdp convert 1Dto3D
    # gdp_1Dto3D = subparsers.add_parser('1Dto3D', help='1Dto3D',
    # description="1Dto3D")
    
    # # gdp convert 2Dto1D
    # gdp_2Dto1D = subparsers.add_parser('2Dto1D', help='2Dto1D',
    # description="2Dto1D")
    
    # # gdp convert 2Dto3D
    # gdp_2Dto3D = subparsers.add_parser('2Dto3D', help='2Dto3D',
    # description="2Dto3D")
    
    # # gdp convert 3Dto1D
    # gdp_3Dto1D = subparsers.add_parser('3Dto1D', help='3Dto1D',
    # description="3Dto1D")
    
    # # gdp convert 3Dto2D
    # gdp_3Dto2D = subparsers.add_parser('3Dto2D', help='3Dto2D',
    # description="3Dto2D")
    
    # gdp convert mseed2sac
    gdp_mseed2sac = subparsers.add_parser('mseed2sac', help='convert mseed to sac',
    description="Convert mseed to sac. This script also handles data fragmentation issue. ")
    gdp_mseed2sac.add_argument("input_files", nargs='+')
    gdp_mseed2sac.add_argument(
        '-o',
        '--outdir',
        type=str,
        required=True,
        help='REQUIRED: path to output directory'
    )
    gdp_mseed2sac.add_argument(
        '--reformat',
        action='store_true',
        help='reformat output sac files i.e. rename and output to related directories based on mseed start time, station & channel information'
    )
    gdp_mseed2sac.add_argument(
        '--offset',
        type=float,
        default=0,
        help='output filename start time offset in seconds (only if rename=True; default=0)'
    )
    gdp_mseed2sac.add_argument(
        '--resample',
        type=float,
        default=999,
        help='output sac files sampling frequency'
    )
    
    
    # gdp convert sac2dat
    gdp_sac2dat = subparsers.add_parser('sac2dat', help='convert sac to dat (ascii)',
    description="Convert sac to dat (ascii); output format: time, amplitude")
    gdp_sac2dat.add_argument("input_files", nargs='+')
    gdp_sac2dat.add_argument(
        '-o',
        '--outdir',
        type=str,
        required=True,
        help='REQUIRED: path to output directory'
    )
    gdp_sac2dat.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".2",".2"],
        help='float format for time and value columns respectively (default=[".2",".2"])')
    gdp_sac2dat.add_argument(
        '--timerange',
        nargs=2,
        type=float,
        action='store',
        default=[999, 999],
        help='time range limit')
        
    # # gdp convert shp2dat
    # gdp_shp2dat = subparsers.add_parser('shp2dat', help='convert shp to dat (ascii)',
    # description="Convert shape file to dat (ascii)")
    
    # gdp convert nc2dat
    gdp_nc2dat = subparsers.add_parser('nc2dat', help='convert nc to dat (ascii)',
    description="Convert nc data to dat/ascii")
    gdp_nc2dat.add_argument("input_file", type=str, action='store', nargs=1, help='input nc file')
    gdp_nc2dat.add_argument(
        '--metadata',
        action='store_true',
        help='only output metadata'
    )
    gdp_nc2dat.add_argument(
    	'-v',
        '--data',
        nargs='*',
        type=str,
        help="data field name(s) / vlue column(s); hint: use '--metadata' flag for more information"
    )
    gdp_nc2dat.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output data to file')
    gdp_nc2dat.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    gdp_nc2dat.add_argument(
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
    from . import dat
    from . import nan
    from . import conv
    if args.module == 'cat':
        from . import io
        out_lines = []
        for inpfile in args.input_files:
            out_lines += io.data_lines(inpfile, args)
        io.output_lines(out_lines, args)
        exit(0)
    elif args.module == 'union':
        if args.nan:
            nan.union(args)
        else:
            dat.union(args)
        exit(0)
    elif args.module == 'intersect':
        if args.nan:
            nan.intersect(args)
        else:
            dat.intersect(args)
        exit(0)
    elif args.module == 'difference':
        if args.nan:
            nan.difference(args)
        else:
            dat.difference(args)
        exit(0)
    elif args.module == 'split':
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
    elif args.module == 'gridder':
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
    elif args.module == 'pip':
        dat.points_in_polygon(args)
        exit(0)
    elif args.module == 'min':
        dat.calc_min(args)
        exit(0)
    elif args.module == 'max':
        dat.calc_max(args)
        exit(0)
    elif args.module == 'sum':
        dat.calc_sum(args)
        exit(0)
    elif args.module == 'mean':
        dat.calc_mean(args)
        exit(0)
    elif args.module == 'median':
        dat.calc_median(args)
        exit(0)
    elif args.module == 'std':
        dat.calc_std(args)
        exit(0)
    elif args.module == '1Dto2D':
        subprocess.call('gdp 1Dto2D -h', shell=True)
        under_dev()
    elif args.module == '1Dto3D':
        subprocess.call('gdp 1Dto3D -h', shell=True)
        under_dev()
    elif args.module == '2Dto1D':
        subprocess.call('gdp 2Dto1D -h', shell=True)
        under_dev()
    elif args.module == '2Dto3D':
        subprocess.call('gdp 2Dto3D -h', shell=True)
        under_dev()
    elif args.module == '3Dto1D':
        subprocess.call('gdp 3Dto1D -h', shell=True)
        under_dev()
    elif args.module == '3Dto2D':
        subprocess.call('gdp 3Dto2D -h', shell=True)
        under_dev()
    elif args.module == 'sac2dat':
        conv.sac2dat(args)
        exit(0)
    elif args.module == 'mseed2sac':
        conv.mseed2sac(args)
        exit(0)
    elif args.module == 'shp2dat':
        subprocess.call('gdp shp2dat -h', shell=True)
        under_dev()
    elif args.module == 'nc2dat':
        conv.nc2dat(args)
        exit(0)
    else:
        subprocess.call('gdp -h', shell=True)



if __name__ == "__main__":
    main(*args, **kwargs)
