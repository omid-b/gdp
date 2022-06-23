#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
from time import time

version = "0.1.2b"
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
    
    #===== Modules =====#
    
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

    # gdp data add
    gdp_add = subparsers.add_parser('add', help='add value comumn(s) of input data files',
    description="Add value comumn(s) of input data files")
    gdp_add.add_argument("input_files", nargs='+', help='input numerical data files')
    gdp_add.add_argument(
        '-x',
        nargs='+',
        type=int,
        action='store',
        default=[1, 2],
        help='positional column number(s) (default=[1, 2]; [] is also accepted)')
    gdp_add.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3]; [] is also accepted)')
    gdp_add.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for positional and value columns respectively (default=[".4",".4"]); the first value is specially important')
    gdp_add.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    gdp_add.add_argument(
        '--sort',
        action='store_true',
        help='sort output lines')
    gdp_add.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    gdp_add.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    gdp_add.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')


    # gdp data pip
    gdp_pip = subparsers.add_parser('pip', help='points-in-polygon',
    description="Points-in-polygon (ray tracing method).")
    gdp_pip.add_argument(
        '--point',
        type=str,
        nargs='+',
        action='store',
        help='path to points file (single or multiple allowed)')
    gdp_pip.add_argument(
        '--polygon',
        type=str,
        action='store',
        help='path to polygon file (only single allowed)')
    gdp_pip.add_argument(
        '-x',
        nargs=2,
        type=int,
        action='store',
        default=[1, 2],
        help='positional column number(s) (default=[1, 2]); does not apply to ascii polygon')
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
        help='inverse operation: points outside polygon (only if one polygon is given)')
    gdp_pip.add_argument(
        '--xrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='x/longitude range: [minX/minlon, maxX/maxlon]; this option could be used to specify polygon region if a polygon file is not available.')
    gdp_pip.add_argument(
        '--yrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='y/latitude range: [minY/minlat, maxY/maxlat]; this option could be used to specify polygon region if a polygon file is not available.')
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
        '--utm',
        action='store_true',
        help='specify if data is given in UTM/Cartesian format (default=False)')
    gdp_gridder.add_argument(
        '--xrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='grid x/longitude range: [minX/minlon, minY/maxlon] (default=Auto)')
    gdp_gridder.add_argument(
        '--yrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='grid y/latitude range: [minY/minlat, minY/maxlat] (default=Auto)')
    gdp_gridder.add_argument(
        '-x',
        nargs=2,
        type=int,
        action='store',
        default=[1, 2],
        help='[x/longitude, y/latitude] column number(s) (default=[1, 2])')
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


    # gdp data chull
    gdp_chull = subparsers.add_parser('chull', help='convex-hull/minimum bounding polygon',
    description="convex-hull / minimum bounding polygon for a set of points")
    gdp_chull._positionals.title = 'required arguments'
    gdp_chull.add_argument("points_file", type=str, help="path to points_file")
    gdp_chull.add_argument(
        '-x',
        nargs=2,
        type=int,
        action='store',
        default=[1, 2],
        help='[x/lon, y/lat] column number(s) (default=[1, 2])')
    gdp_chull.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    gdp_chull.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    gdp_chull.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file/folder')
    gdp_chull.add_argument(
        '--smooth',
        type=int,
        action='store',
        default=0,
        help='number of Bezier points to smooth the output convex-hull polygon')
    # gdp_chull.add_argument(
    #     '--offset',
    #     type=float,
    #     action='store',
    #     default=0,
    #     help='inflate (positive float) or deflate (negative float) the output convex-hull polygon')

    gdp_chull.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for output convex-hull (default=".4")'
    )

    # gdp convert shp2dat
    gdp_shp2dat = subparsers.add_parser('shp2dat', help='convert shp to dat (ascii)',
    description="Convert shape file to dat (ascii)")
    gdp_shp2dat.add_argument(
        '--point',
        type=str,
        nargs='*',
        action='store',
        help='point(s): shape file(s)')
    gdp_shp2dat.add_argument(
        '--polygon',
        type=str,
        nargs='*',
        action='store',
        help='polygon(s): shape file(s)')
    gdp_shp2dat.add_argument(
        '-o',
        '--outdir',
        type=str,
        required=True,
        action='store',
        help='output directory')
    gdp_shp2dat.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for output convex-hull (default=".4")'
    )
    
    # gdp convert nc2dat
    gdp_nc2dat = subparsers.add_parser('nc2dat', help='convert nc to dat (ascii)',
    description="Convert nc data to dat/ascii")
    gdp_nc2dat.add_argument(
        "input_file",
        type=str,
        action='store',
        nargs=1,
        help='input nc file')
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

    # gdp convert dat2nc
    gdp_dat2nc = subparsers.add_parser('dat2nc', help='convert dat/ascii (gridded) to nc format',
    description="Convert dat/ascii (must be gridded) to nc format")
    gdp_dat2nc._positionals.title = 'required arguments'
    gdp_dat2nc.add_argument("input_file", type=str, action='store', help='input ascii file')
    gdp_dat2nc.add_argument(
        'output_file',
        type=str,
        action='store',
        help='output nc file')
    gdp_dat2nc.add_argument(
        '-x',
        nargs=2,
        type=int,
        action='store',
        default=[1, 2],
        help='[x, y] column number(s) (default=[1, 2])')
    gdp_dat2nc.add_argument(
        '-v',
        '--data',
        nargs=1,
        type=int,
        action='store',
        default=[3],
        help="data/value column (default=3)"
    )
    gdp_dat2nc.add_argument(
        '--polygon',
        type=str,
        action='store',
        help='polygon to apply points-in-polygon')
    gdp_dat2nc.add_argument(
        '--xrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='grid x/longitude range: [minX/minlon, minY/maxlon] (default=Auto)')
    gdp_dat2nc.add_argument(
        '--yrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='grid y/latitude range: [minY/minlat, minY/maxlat] (default=Auto)')
    gdp_dat2nc.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format (to store) for positional and value columns respectively (default=[".4",".4"])')
    
    # gdp convert 1Dto2D
    gdp_1Dto2D = subparsers.add_parser('1Dto2D', help='combine/convert 1D datasets into 2D datasets',
    description="Combine/convert 1D datasets into 2D datasets. Example use cases:\
     (1) building phase velocity map datasets from point/1D dispersion curve datasets,\
     (2) building shear velocity map datasets from 1D shear velocity profiles.")
    gdp_1Dto2D.add_argument("datalist", type=str, action='store', help='1D dataset datalist')
    gdp_1Dto2D.add_argument(
        '-o',
        '--outdir',
        type=str,
        action='store',
        required=True,
        help='output directory')
    gdp_1Dto2D.add_argument(
        '-x',
        nargs=1,
        type=int,
        action='store',
        default=[1],
        help='positional column number in 1D data files (default=1)')
    gdp_1Dto2D.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[2],
        help="value column(s) in 1D data files (default=[2])"
    )
    gdp_1Dto2D.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    gdp_1Dto2D.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4", "03.0"],
        help='float format (to store) for positional, value, and the identifier columns respectively (default=[".4",".4","03.0"])')
    gdp_1Dto2D.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    gdp_1Dto2D.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    gdp_1Dto2D.add_argument(
        '--prefix',
        type=str,
        action='store',
        default = 'model_',
        help='output file name prefix (default="model_")')
    gdp_1Dto2D.add_argument(
        '--suffix',
        type=str,
        action='store',
        default = '',
        help='output file name suffix (default="")')
    gdp_1Dto2D.add_argument(
        '--ext',
        type=str,
        action='store',
        default = 'dat',
        help='output file extension (default="dat")')
    
    # # gdp convert 1Dto3D
    # gdp_1Dto3D = subparsers.add_parser('1Dto3D', help='1Dto3D',
    # description="1Dto3D")
    
    # gdp convert 2Dto1D
    gdp_2Dto1D = subparsers.add_parser('2Dto1D', help='extract/convert 2D datasets into 1D datasets',
    description="Extract/convert 2D datasets into 1D datasets. Example use cases:\
     (1) extracting point dispersion curves from phase velocity maps,\
     (2) extracing 1D shear velocity profiles from shear velocity map datasets")
    gdp_2Dto1D.add_argument("datalist", type=str, action='store', help='2D dataset datalist')
    gdp_2Dto1D.add_argument(
        '-o',
        '--outdir',
        type=str,
        action='store',
        required=True,
        help='output directory')
    gdp_2Dto1D.add_argument(
        '-x',
        nargs=1,
        type=int,
        action='store',
        default=[1],
        help='positional column number in 1D data files (default=1)')
    gdp_2Dto1D.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[2],
        help="value column(s) in 1D data files (default=[2])"
    )
    gdp_2Dto1D.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    gdp_2Dto1D.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4", "03.0"],
        help='float format (to store) for positional, value, and the identifier columns respectively (default=[".4",".4","03.0"])')
    gdp_2Dto1D.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    gdp_2Dto1D.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    
    # # gdp convert 2Dto3D
    # gdp_2Dto3D = subparsers.add_parser('2Dto3D', help='2Dto3D',
    # description="2Dto3D")
    
    # # gdp convert 3Dto1D
    # gdp_3Dto1D = subparsers.add_parser('3Dto1D', help='3Dto1D',
    # description="3Dto1D")
    
    # # gdp convert 3Dto2D
    # gdp_3Dto2D = subparsers.add_parser('3Dto2D', help='3Dto2D',
    # description="3Dto2D")


    #====gdp seismic=====#
    seismic = subparsers.add_parser('seismic', help='seismic data acquisition and processing module (requires SAC)',
    description="seismic data acquisition and processing module (requires SAC)")
    seismic_subparsers = seismic.add_subparsers(dest='submodule')

    # gdp seismic download
    seismic_download = seismic_subparsers.add_parser('download', help='seismic data acquisition module',
    description="seismic data acquisition module")
    download_subparsers = seismic_download.add_subparsers(dest='subsubmodule')

    # gdp seismic download init
    download_init = download_subparsers.add_parser('init', help='initialize download project',
    description='initialize download project and create "download.config" file')
    download_init.add_argument(
        '--maindir',
        type=str,
        default='./',
        help="path to directory containing 'download.config' (default='./')"
    )

    # gdp seismic download events
    download_events = download_subparsers.add_parser('events', help='download list of events',
    description="download list of events")
    download_events.add_argument(
        '--maindir',
        type=str,
        default='./',
        help="path to directory containing 'download.config' (default='./')"
    )

    # gdp seismic download stations
    download_stations = download_subparsers.add_parser('stations', help='download list of stations',
    description="download list of stations")
    download_stations.add_argument(
        '--maindir',
        type=str,
        default='./',
        help="path to directory containing 'download.config' (default='./')"
    )

    # gdp seismic download metadata
    download_metadata = download_subparsers.add_parser('metadata', help='download station metadata',
    description="download station metadata")
    download_metadata.add_argument(
        '--maindir',
        type=str,
        default='./',
        help="path to directory containing 'download.config' (default='./')"
    )
    download_metadata.add_argument(
        '--metadata',
        type=str,
        default='./metadata',
        help="path to output metadata directory' (default='./metadata')"
    )

    # gdp seismic download mseeds
    download_mseeds = download_subparsers.add_parser('mseeds', help='download mseed files',
    description="download mseed files")
    download_mseeds.add_argument(
        '--maindir',
        type=str,
        default='./',
        help="path to directory containing 'download.config' (default='./')"
    )
    download_mseeds.add_argument(
        '--duration',
        type=int,
        required=True,
        help="REQUIRED: timeseries length/duration in seconds."
    )
    download_mseeds.add_argument(
        '--offset',
        type=int,
        default=0,
        help="Timeseries starttime offset (relative to events) in seconds (default=0)."
    )
    download_mseeds.add_argument(
        '--mseeds',
        type=str,
        default='./mseeds',
        help="Path to output mseeds directory (default=./mseeds)."
    )
    download_mseeds.add_argument(
        '--ant',
        action='store_true',
        help='download for ambient-noise-tomography; do not read events list (default=False)'
    )


    # gdp seismic mseed2sac

    seismic_mseed2sac = seismic_subparsers.add_parser('mseed2sac', help='convert mseed to sac',
    description="Convert mseed to sac. This script also handles data fragmentation issue. ")
    seismic_mseed2sac.add_argument("input_files", nargs='+', help='input mseed files')
    seismic_mseed2sac.add_argument(
        '-o',
        '--outdir',
        type=str,
        required=True,
        help='REQUIRED: path to output directory'
    )
    seismic_mseed2sac.add_argument(
        '--reformat',
        action='store_true',
        help='reformat output sac files: rename and output to related directories based on mseed start time, station & channel information'
    )
    seismic_mseed2sac.add_argument(
        '--offset',
        type=float,
        default=0,
        help='output event starttime offset in seconds (only if "reformat" is enabled; default=0); same offset value that was used for data acquisition'
    )
    seismic_mseed2sac.add_argument(
        '--resample',
        type=float,
        default=999,
        help='output sac files sampling frequency'
    )
    seismic_mseed2sac.add_argument(
        '--noprocess',
        action='store_true',
        help='by default, detrend(spline degree 4) and taper(percentage=0.005) are applied; enabling this option will skip these processes (not recommended!)'
    )
    
    
    # gdp seismic sac2dat
    seismic_sac2dat = seismic_subparsers.add_parser('sac2dat', help='convert sac to dat (ascii)',
    description="Convert sac to dat (ascii); output format: time, amplitude")
    seismic_sac2dat.add_argument("input_files", nargs='+')
    seismic_sac2dat.add_argument(
        '-o',
        '--outdir',
        type=str,
        required=True,
        help='REQUIRED: path to output directory'
    )
    seismic_sac2dat.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".2",".2"],
        help='float format for time and value columns respectively (default=[".2",".2"])')
    seismic_sac2dat.add_argument(
        '--timerange',
        nargs=2,
        type=float,
        action='store',
        default=[999, 999],
        help='time range limit')


    # gdp seismic writehdr
    seismic_writehdr = seismic_subparsers.add_parser('writehdr', help='write sac headers using xml metadata',
    description="Write sac headers using xml metadata")
    seismic_writehdr.add_argument("input_files", nargs='+', help='input sac files')
    seismic_writehdr.add_argument(
        '--metadata',
        type=str,
        default='./metadata',
        help="path to xml (metadata) dataset directory (default='./metadata')"
    )
    seismic_writehdr.add_argument(
        '--maindir',
        type=str,
        default='./',
        help="path to directory containing 'download.config' (default='./')"
    )
    seismic_writehdr.add_argument(
        '--ant',
        action='store_true',
        help='ambient noise tomography dataset: do not update events information (default=False)'
    )
    seismic_writehdr.add_argument(
        '--sac',
        type=str,
        default='auto',
        help='path to sac software executable (default=auto)'
    )

    # gdp seismic remresp
    seismic_remresp = seismic_subparsers.add_parser('remresp', help='remove sac instrument response using xml metadata',
    description="Remove instrument response of sacfiles using xml metadata (see obspy documentation for 'unit' (output), 'pre_filt', and 'water_level' information)")
    seismic_remresp.add_argument("input_files", nargs='+', help='input sac files')
    seismic_remresp.add_argument(
        '--metadata',
        type=str,
        default='./metadata',
        help="path to xml (metadata) dataset directory (default='./metadata')"
    )
    seismic_remresp.add_argument(
        '--unit',
        type=str,
        choices=['DISP','VEL','ACC'],
        default='VEL',
        help="output unit; (default='VEL')"
    )
    seismic_remresp.add_argument(
        '--pre_filt',
        type=float,
        nargs=4,
        default=(0.005, 0.006, 30.0, 35.0),
        help="deconvolution prefilter;  default=(0.005, 0.006, 30.0, 35.0); enter 4 zeros for 'pre_filt=None'"
    )
    seismic_remresp.add_argument(
        '--water_level',
        type=int,
        default=60,
        help="deconvolution water level; default=60"
    )


    # gdp seismic resample
    seismic_resample = seismic_subparsers.add_parser('resample', help='resample sac files',
    description="Resample sac files using obspy")
    seismic_resample.add_argument("input_files", nargs='+', help='input sac files')
    seismic_resample.add_argument(
        '--sf',
        type=int,
        required=True,
        help='REQUIRED: output sampling frequency (Hz)'
    )
    seismic_resample.add_argument(
        '--sac',
        type=str,
        default='auto',
        help='path to sac software executable (default=auto)'
    )


    # gdp seismic bandpass
    seismic_bandpass = seismic_subparsers.add_parser('bandpass', help='apply bandpass filter to sac files',
    description="Apply bandpass filter to sac files")
    seismic_bandpass.add_argument("input_files", nargs='+', help='input sac files')
    seismic_bandpass.add_argument(
        '--cp1',
        type=float,
        required=True,
        help='REQUIRED: corner period 1 (s)'
    )
    seismic_bandpass.add_argument(
        '--cp2',
        type=float,
        required=True,
        help='REQUIRED: corner period 2 (s)'
    )
    seismic_bandpass.add_argument(
        '-n',
        type=int,
        default=3,
        help='number of poles (default: n=3)'
    )
    seismic_bandpass.add_argument(
        '-p',
        type=int,
        default=2,
        help='number of passes (default: p=2)'
    )
    seismic_bandpass.add_argument(
        '--sac',
        type=str,
        default='auto',
        help='path to sac software executable (default=auto)'
    )

    # gdp seismic cut
    seismic_cut = seismic_subparsers.add_parser('cut', help='cut sac files (also applies cutter fillz)',
    description="Cut sac files (also applies cutter fillz)")
    seismic_cut.add_argument("input_files", nargs='+', help='input sac files')
    seismic_cut.add_argument(
        '--begin',
        type=float,
        required=True,
        help='REQUIRED: cut begin time (s)'
    )
    seismic_cut.add_argument(
        '--end',
        type=float,
        required=True,
        help='REQUIRED: cut end time (s)'
    )
    seismic_cut.add_argument(
        '--sac',
        type=str,
        default='auto',
        help='path to sac software executable (default=auto)'
    )


    # gdp seismic remchan
    seismic_remchan = seismic_subparsers.add_parser('remchan', help='remove extra channels from event directories',
    description="remove extra channels from event directories")
    seismic_remchan.add_argument("input_files", nargs='+', help='input sac files')
    seismic_remchan.add_argument(
        '--channels',
        type=str,
        required=True,
        nargs='+',
        help='REQUIRED: list of similar channels'
    )
    seismic_remchan.add_argument(
        '--onlykeep',
        type=str,
        required=True,
        nargs='+',
        help='REQUIRED: if all similar channels are available, only keep these channels'
    )



    #====mag submodules=====#
    # mag = subparsers.add_parser('mag', help='geomagnetic data processing and modeling module',
    # description="geomagnetic data processing and modeling module")
    # mag_subparsers = mag.add_subparsers(dest='submodule')

    # # gdp mag igrf
    # mag_igrf = mag_subparsers.add_parser('igrf', help='calculate igrf',
    # description="calculate igrf (TFI, Inc, Dec ...) at a point (or multiple points)")

    # # gdp mag gem2dat
    # mag_gem2dat = mag_subparsers.add_parser('gem2dat', help='convert raw data format from a GEM proton magnetometer to ascii format',
    # description="convert raw data format from a GEM proton magnetometer to ascii format")

    # # gdp mag sphere
    # mag_sphere = mag_subparsers.add_parser('sphere', help='forward modeling of uniformly magnetized sphere(s)',
    # description="forward modeling of uniformly magnetized sphere(s) over a local grid")
        
    

    #====plot submodules=====#
    plot = subparsers.add_parser('plot', help='plot module (requires GMT)',
    description="Plot module (requires GMT)")
    plot_subparsers = plot.add_subparsers(dest='submodule')

    # gdp plot stations
    plot_stations = plot_subparsers.add_parser('stations', help='plot seismic stations on a map',
    description="Plot seismic stations on a map")
    plot_stations.add_argument("stalist", type=str, help='input station list file')
    plot_stations.add_argument(
        '--labels',
        action='store_true',
        help='print station labels on the output map')
    plot_stations.add_argument(
        '--gmt',
        type=str,
        default='auto',
        help='path to GMT software executable (default=auto)'
    )

    # gdp plot events
    plot_events = plot_subparsers.add_parser('events', help='plot seismic events on a map',
    description="Plot seismic events on a map")
    plot_events.add_argument("eventlist", type=str, help='input event list file')
    plot_events.add_argument(
        '--lon',
        type=float,
        required=True,
        help='REQUIRED: study region longitude')
    plot_events.add_argument(
        '--lat',
        type=float,
        required=True,
        help='REQUIRED: study region latitude')
    plot_events.add_argument(
        '--gmt',
        type=str,
        default='auto',
        help='path to GMT software executable (default=auto)'
    )

    # gdp plot hist
    plot_hist = plot_subparsers.add_parser('hist', help='generate histogram plots',
    description="Generate histogram plots")
    plot_hist.add_argument(
        "input_files",
        type=str,
        nargs='+',
        help='input data files'
    )
    plot_hist.add_argument(
        '-o',
        type=str,
        help='output file name')
    plot_hist.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[1],
        help='value/data column number(s) (default=[1])')
    plot_hist.add_argument(
        '-n',
        '--nbins',
        type=int,
        default=999,
        help='number of bins (default=auto)')
    plot_hist.add_argument(
        '--legend',
        type=str,
        nargs='+',
        action='store',
        default=[],
        help='legend text; number of elements must be equal to input data items (note: use underline for space)')
    plot_hist.add_argument(
        '--xlabel',
        type=str,
        nargs='*',
        action='store',
        default=['Values'],
        help='x-axis label')
    plot_hist.add_argument(
        '--ylabel',
        type=str,
        nargs='*',
        action='store',
        default=['Count'],
        help='y-axis label')
    plot_hist.add_argument(
        '--title',
        type=str,
        nargs='*',
        action='store',
        default=[],
        help='plot title')
    plot_hist.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for positional and value columns respectively (default=0.4)')
    plot_hist.add_argument(
        '--mean',
        action='store_true',
        help='enable plotting distribution mean (dashed line)')
    plot_hist.add_argument(
        '--median',
        action='store_true',
        help='enable plotting distribution median (dashed line)')
    plot_hist.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    plot_hist.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')

    # gdp plot features
    # plot_features = plot_subparsers.add_parser('features', help='plot geographical features (e.g., points, polygons)',
    # description="Plot geographical features (e.g., points, polygons)")
    # plot_features.add_argument(
    #     '--point',
    #     type=str,
    #     nargs='*',
    #     action='store',
    #     help='point(s): ascii or shape file(s)')
    # plot_features.add_argument(
    #     '--polygon',
    #     type=str,
    #     nargs='*',
    #     action='store',
    #     help='polygon(s): ascii or shape file(s)')
    
    # return arguments
    return parser.parse_args()

###############################################################

def main(*args, **kwargs):
    args = parse_args(*args, **kwargs)
    if args.about or len(sys.argv) == 1:
        clear_screen()
        print(f"{about}\n")
        exit(0)
        
    from . import dat
    from . import nan
    from . import conv
    from . import sacproc
    from . import download
    from . import mag
    from . import plot

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

        if args.utm:
            dat.gridder_utm(args)
        else:
            dat.gridder(args)
        exit(0)
        
    elif args.module == 'chull':
        dat.convex_hull(args)
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
    elif args.module == 'add':
        dat.add_intersect_values(args)
        exit(0)
    elif args.module == '1Dto2D':
        conv.datasets_1Dto2D(args)
        exit(0)
    elif args.module == '1Dto3D':
        subprocess.call('gdp 1Dto3D -h', shell=True)
        under_dev()
    elif args.module == '2Dto1D':
        conv.datasets_2Dto1D(args)
        exit(0)
    elif args.module == '2Dto3D':
        subprocess.call('gdp 2Dto3D -h', shell=True)
        under_dev()
    elif args.module == '3Dto1D':
        subprocess.call('gdp 3Dto1D -h', shell=True)
        under_dev()
    elif args.module == '3Dto2D':
        subprocess.call('gdp 3Dto2D -h', shell=True)
        under_dev()
    elif args.module == 'shp2dat':
        if args.point == None and args.polygon == None:
            print("Error! At least one shape file must be given")
            exit(1)
        conv.shp2dat(args)
        exit(0)
    elif args.module == 'nc2dat':
        conv.nc2dat(args)
        exit(0)
    elif args.module == 'dat2nc':
        conv.dat2nc(args)
        exit(0)
    elif args.module == 'seismic':

        if args.submodule == 'download':
            if args.subsubmodule == 'init':
                download.write_download_config(args)
                exit(0)
            elif args.subsubmodule == 'events':
                download.download_events(args)
                exit(0)
            elif args.subsubmodule == 'stations':
                download.download_stations(args)
                exit(0)
            elif args.subsubmodule == 'metadata':
                download.download_metadata(args)
                exit(0)
            elif args.subsubmodule == 'mseeds':
                download.download_mseeds(args)
                exit(0)
            else:
                subprocess.call('gdp seismic download -h', shell=True)

        elif args.submodule == 'mseed2sac':
            conv.mseed2sac(args)
            exit(0)
        elif args.submodule == 'sac2dat':
            conv.sac2dat(args)
            exit(0)
        elif args.submodule == 'writehdr':
            sacproc.writehdr(args)
            exit(0)
        elif args.submodule == 'remresp':
            sacproc.remresp(args)
            exit(0)
        elif args.submodule == 'resample':
            sacproc.resample(args)
            exit(0)
        elif args.submodule == 'bandpass':
            sacproc.bandpass(args)
            exit(0)
        elif args.submodule == 'cut':
            sacproc.cut(args)
            exit(0)
        elif args.submodule == 'remchan':
            sacproc.remchan(args)
            exit(0)
        else:
            subprocess.call('gdp seismic -h', shell=True)

    elif args.module == 'mag':
        if args.submodule == 'igrf':
            mag.igrf(args)
            exit(0)
        elif args.submodule == 'gem2dat':
            mag.gem2dat(args)
            exit(0)
        elif args.submodule == 'sphere':
            mag.sphere(args)
            exit(0)
        else:
            subprocess.call('gdp mag -h', shell=True)
    elif args.module == 'plot':
        if args.submodule == 'stations':
            plot.plot_stations(args.stalist, args.labels, GMT=args.gmt)
            exit(0)
        elif args.submodule == 'events':
            plot.plot_events(args.eventlist, args.lon, args.lat, GMT=args.gmt)
            exit(0)
        elif args.submodule == 'hist':
            plot.plot_hist(args)
            exit(0)
        elif args.submodule == 'features':
            if args.point == None and args.polygon == None:
               print("Error! At least one input feature is required!")
               exit(1)
            plot.plot_features(args)
            exit(0)
        else:
            subprocess.call('gdp plot -h', shell=True)
    else:
        subprocess.call('gdp -h', shell=True)



if __name__ == "__main__":
    main(*args, **kwargs)
