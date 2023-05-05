#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess

version = "0.2.0a"
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

    parser = argparse.ArgumentParser('gdp',
    description="gdp: Geophysical Data Processing",
    conflict_handler='resolve')
    parser.add_argument(
        '--about',
        action='store_true',
        help='about this package and contact information'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {version}')
    parser.add_argument(
        '--check',
        action='store_true',
        help='check all dependencies')
    parser._positionals.title = 'list of modules'
    subparsers = parser.add_subparsers(dest='module')
    
    #=====MODULE: DATA=====#

    data = subparsers.add_parser('data',
        help='data manipulation and processing module',
        description="General and geographic data manipulation and processing module")
    data_subparsers = data.add_subparsers(dest='submodule')
    
    #------------------------# 
    # $> gdp data cat
    data_cat = data_subparsers.add_parser('cat', help='concatenate and reformat input data files',
    description="Concatenate and reformat input data files")
    data_cat.add_argument("input_files", nargs='+', help='input ascii files (can use wildcards)')
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
    
    #------------------------# 
    # $> gdp data union
    data_union = data_subparsers.add_parser('union', help='generate the union of input data files',
        description="Generate the union of input data files")
    data_union.add_argument("input_files", nargs='+', help='input ascii files (can use wildcards)')
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
    
    #------------------------# 
    # $> gdp data intersect
    data_intersect = data_subparsers.add_parser('intersect', help='generate the intersect of input data files',
    description="Generate the intersect of input data files")
    data_intersect.add_argument("input_files", nargs='+', help='input ascii files (can use wildcards)')
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
    
    #------------------------#    
    # $> gdp data difference
    data_difference = data_subparsers.add_parser('difference', help='generate the difference of input data files',
    description="Generate the difference of input data files")
    data_difference.add_argument("input_files", nargs='+', help='input ascii files (can use wildcards)')
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

    #------------------------#
    # $> gdp data add
    data_add = data_subparsers.add_parser(
        'add',
        help='add value column(s) of the same coordinates',
        description="Add value column(s) of the same coordinates")
    data_add.add_argument(
        "input_files",
        nargs='+',
        help='input numerical data files (can use wildcards)')
    data_add.add_argument(
        '-x',
        nargs='+',
        type=int,
        action='store',
        default=[1, 2],
        help='positional column number(s) (default=[1, 2]; [] is also accepted)')
    data_add.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3]; [] is also accepted)')
    data_add.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for positional and value columns respectively (default=[".4",".4"]); the first value is specially important')
    data_add.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    data_add.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    data_add.add_argument(
        '--sort',
        action='store_true',
        help='sort output lines')
    data_add.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    data_add.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    data_add.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')

    #------------------------#
    # $> gdp data split
    data_split = data_subparsers.add_parser('split', help='split concatenated dataset',
    description="Split a concatenated dataset into multiple data files")
    data_split._positionals.title = 'required positional arguments'
    data_split._optionals.title = 'optional/Required arguments'
    data_split.add_argument("input_file", nargs=1, help='input ascii file')
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

    #------------------------#
    # $> gdp data cs
    data_cs = data_subparsers.add_parser('cs',
        help='coordinate systems information and transformation module',
        description='Coordinate systems information and transformation module')
    data_cs_subparsers = data_cs.add_subparsers(dest='subsubmodule')

    #------------------------#
    # $> gdp data cs info
    data_cs_info = data_cs_subparsers.add_parser('info',
        help='get coordinate system information',
        description='Get coordinate system information. For more information visit https://spatialreference.org/ref/epsg/')
    data_cs_info.add_argument(
        '--keywords',
        nargs='+',
        required=True,
        help='REQUIRED: keywords to be used in searching offline/online databases')

    #------------------------#
    # $> gdp data cs transform
    data_cs_transform = data_cs_subparsers.add_parser('transform', help='transform/reproject coordinate system',
    description="Transform/reproject coordinate system")
    data_cs_transform.add_argument(
        'input_file',
        type=str,
        help='input file (ascii format)')
    data_cs_transform.add_argument(
        '-x',
        nargs=2,
        type=int,
        required=True,
        help='REQUIRED: x/lon and y/lat column numbers e.g., "1 2"')
    data_cs_transform.add_argument(
        '--cs',
        type=str,
        required=True,
        nargs=2,
        help='REQUIRED: input and output coordinate systems: INPUT_CS OUTPUT_CS')
    data_cs_transform.add_argument(
        '--fmt',
        nargs=2,
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for transformed and original coordinates respectively (default=[".4",".4"])')
    data_cs_transform.add_argument(
        '--skiporig',
        action='store_true',
        help='do not output original coordintes')
    data_cs_transform.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    data_cs_transform.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    data_cs_transform.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    data_cs_transform.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')

    #------------------------#
    # $> gdp data cs fix
    data_cs_fix = data_cs_subparsers.add_parser('fix', help='fix coordinate system mismatch',
    description="fix coordinate system mismatch: compare two datasets and find best matching coordinate systems based on minimizing distance")
    data_cs_fix.add_argument(
        '--known',
        type=str,
        required=True,
        help='REQUIRED: scattered dataset ascii file with an already known coordinate system')
    data_cs_fix.add_argument(
        '--unknown',
        type=str,
        required=True,
        help='REQUIRED: scattered dataset ascii file with an unknown coordinate system')
    data_cs_fix.add_argument(
        '--cs',
        type=str,
        required=True,
        nargs=1,
        help='REQUIRED: coordinate system for the known dataset')
    data_cs_fix.add_argument(
        '--trylist',
        type=str,
        default="",
        help='path to ascii file containing a list of EPSG codes to try')
    data_cs_fix.add_argument(
        '--tryall',
        action='store_true',
        help='try all available EPSG codes (~4000 EPSG codes to try)')    
    data_cs_fix.add_argument(
        '-x',
        nargs=2,
        type=int,
        action='store',
        default=[1, 2],
        help='[x/lon, y/lat] column number(s) for the input files (default=[1, 2])')



    #------------------------#
    # $> gdp data chull
    data_chull = data_subparsers.add_parser('chull', help='convex-hull/minimum bounding polygon',
    description="convex-hull / minimum bounding polygon for a set of points")
    data_chull._positionals.title = 'Required arguments'
    data_chull.add_argument("points_file", type=str, help="path to points_file")
    data_chull.add_argument(
        '-x',
        nargs=2,
        type=int,
        action='store',
        default=[1, 2],
        help='[x/lon, y/lat] column number(s) (default=[1, 2])')
    data_chull.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    data_chull.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    data_chull.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file/folder')
    data_chull.add_argument(
        '--smooth',
        type=int,
        action='store',
        default=0,
        help='number of Bezier points to smooth the output convex-hull polygon')
    data_chull.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for output convex-hull (default=".4")' )

    #------------------------#
    # $> gdp data pip
    data_pip = data_subparsers.add_parser('pip', help='points-in-polygon',
    description="Points-in-polygon (ray tracing method)")
    data_pip._positionals.title = 'Required arguments'
    data_pip.add_argument(
        'points',
        type=str,
        nargs='+',
        action='store',
        help='path to point files (single or multiple allowed)')
    data_pip.add_argument(
        '--polygon',
        type=str,
        action='store',
        help='path to polygon file (ascii(x,y)=[1, 2] or shape file); if ascii, positional column fixed to (x,y)=[1,2]')
    data_pip.add_argument(
        '-x',
        nargs=2,
        type=int,
        action='store',
        default=[1, 2],
        help='positional column number(s) (default=[1, 2]); does not apply to ascii polygon')
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
        help='inverse operation: points outside polygon (only if one polygon is given)')
    data_pip.add_argument(
        '--xrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='x/longitude range: [minX/minlon, maxX/maxlon]; this option could be used to specify polygon region if a polygon file is not available.')
    data_pip.add_argument(
        '--yrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='y/latitude range: [minY/minlat, maxY/maxlat]; this option could be used to specify polygon region if a polygon file is not available.')
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

    #------------------------#
    # $> gdp data nodes
    data_nodes = data_subparsers.add_parser('nodes', help='output a 2D/3D list of regularly spaced nodes',
    description="Output a 2D/3D list of regularly spaced nodes")
    data_nodes._positionals.title = 'Required arguments'
    data_nodes.add_argument(
        '--xrange',
        type=float,
        nargs=2,
        required=True,
        help='REQUIRED: x/longitude min & max values',
    )
    data_nodes.add_argument(
        '--xstep',
        type=float,
        required=True,
        help='REQUIRED: x/longitude step size/interval',
    )
    data_nodes.add_argument(
        '--yrange',
        type=float,
        nargs=2,
        required=True,
        help='REQUIRED: y/latitude min & max values',
    )
    data_nodes.add_argument(
        '--ystep',
        type=float,
        required=True,
        help='REQUIRED: y/latitude step size/interval',
    )
    data_nodes.add_argument(
        '--zrange',
        type=float,
        nargs=2,
        required=False,
        help='z/depth min & max values',
    )
    data_nodes.add_argument(
        '--zstep',
        type=float,
        required=False,
        help='REQUIRED: z/depth step size/interval',
    )
    data_nodes.add_argument(
        '--polygon',
        type=str,
        action='store',
        help='polygon to run "points-in-polygon" process before outputing the results'
    )
    data_nodes.add_argument(
        '--fmt',
        nargs=3,
        type=str,
        default=["","",""],
        help='output x y z float format',
    )
    data_nodes.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file name/path' )

    #------------------------#
    # $> gdp data gridder
    data_gridder = data_subparsers.add_parser('gridder', help='gridding/interpolation of 2D/map data',
    description="Gridding/interpolation of 2D/map data with Gaussian smoothing applied")
    data_gridder._positionals.title = 'Required arguments'
    data_gridder.add_argument(
        "input_files",
        nargs='+',
        help='input ascii files (can use wildcards)')
    data_gridder.add_argument(
        '--spacing',
        nargs='+',
        type=float,
        action='store',
        help="REQUIRED (if 'nodes' not given): grid spacing along [longitude, latitude]"
    )
    data_gridder.add_argument(
        '--nodes',
        type=str,
        help="REQUIRED (if 'spacing' not given): path to grid nodes ascii file; format=(x, y)")
    data_gridder.add_argument(
        '--smoothing',
        type=float,
        required=True,
        help='REQUIRED: grid smoothing length (if not utm, unit=km; if utm, unit=m)'
    )
    data_gridder.add_argument(
        '--utm',
        action='store_true',
        help='specify if data is given in UTM/Cartesian format (default=False)')
    data_gridder.add_argument(
        '--xrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='grid x/longitude range: [minX/minlon, minY/maxlon] (default=Auto)')
    data_gridder.add_argument(
        '--yrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='grid y/latitude range: [minY/minlat, minY/maxlat] (default=Auto)')
    data_gridder.add_argument(
        '-x',
        nargs=2,
        type=int,
        action='store',
        default=[1, 2],
        help='[x/longitude, y/latitude] column number(s) (default=[1, 2])')
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

    #------------------------#
    # $> gdp data plot
    data_plot = data_subparsers.add_parser('plot', help='plot module for geographic data types',
    description="Plot module for geographic data types")
    data_plot._positionals.title = 'Required arguments'
    data_plot_subparsers = data_plot.add_subparsers(dest='subsubmodule')

    #------------------------#
    # $> gdp data plot scatter
    data_plot_scatter = data_plot_subparsers.add_parser(
        'scatter',
        help='plot geographic scatter points',
        description='Plot geographic scatter points')
    data_plot_scatter.add_argument(
        'input_file',
        help='path to input scatter data file (shp files also accepted)')
    data_plot_scatter.add_argument(
        '-x',
        type=int,
        nargs=2,
        default=[1,2],
        help='positionals (x,y) column numbers (ascii only); default=[1, 2]' )
    data_plot_scatter.add_argument(
        '-v',
        nargs='*',
        type=int,
        default=[],
        help='value column numbers for color and size respectively (ascii only); default=[]' )
    data_plot_scatter.add_argument(
        '--cs',
        type=str,
        default='wgs84',
        help='coordinate system (default=wgs84/4326)')
    data_plot_scatter.add_argument(
        '--padding',
        type=float,
        default=0.1,
        help='map region padding factor; default=0.1')
    data_plot_scatter.add_argument(
        '--size',
        type=float,
        default=50.0,
        help='scatter point size (or maximum size); default=50.0')
    data_plot_scatter.add_argument(
        '--area_thresh',
        type=int,
        default=1000,
        help='minimum area threshold for showing basemap features; default=1000'
    )
    data_plot_scatter.add_argument(
        '--crange',
        type=float,
        nargs=2,
        default=[-999.99, 999.99],
        help='color-scale range (only if first value column given; default=Auto)')
    data_plot_scatter.add_argument(
        '--invert_color',
        action='store_true',
        help='invert color map (only if first value column given; smaller values will be red colors)')
    data_plot_scatter.add_argument(
        '--invert_size',
        action='store_true',
        help='invert size (only if second value column given; smaller values will be larger)')
    data_plot_scatter.add_argument(
        '--dpi',
        type=int,
        help='output dpi (dot per inch; default=150)',
        default=150)
    data_plot_scatter.add_argument(
        '-o',
        '--outfile',
        type=str,
        help="output plot file; default file extension, if not specified from ['pdf','png','jpg'] will be set to 'pdf'")


    

    #=====MODULE: STATS=====#

    stats = subparsers.add_parser('stats',
        help='statistics module',
        description="Statistics module")
    stats_subparsers = stats.add_subparsers(dest='submodule')

    #------------------------#
    # $> gdp stats min
    stats_min = stats_subparsers.add_parser(
        'min',
        help='calculate min of numerical column(s)',
        description="Calculate minimum of values in numerical column(s)")
    stats_min.add_argument(
        "input_files",
        nargs='+',
        help='input ascii files (can use wildcards)')
    stats_min.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    stats_min.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    stats_min.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    stats_min.add_argument(
        '--decimal',
        nargs=1,
        type=int,
        action='store',
        default=[2],
        help='number of decimals (default=2)')
    stats_min.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    stats_min.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')

    #------------------------#
    # $> gdp stats max
    stats_max = stats_subparsers.add_parser('max', help='calculate max of numerical column(s)',
    description="Calculate maximum of values in numerical column(s)")
    stats_max.add_argument("input_files", nargs='+', help='input ascii files (can use wildcards)')
    stats_max.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    stats_max.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    stats_max.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    stats_max.add_argument(
        '--decimal',
        nargs=1,
        type=int,
        action='store',
        default=[2],
        help='number of decimals (default=2)')
    stats_max.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    stats_max.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')

    #------------------------#
    # $> gdp stats sum
    stats_sum = stats_subparsers.add_parser('sum', help='calculate sum of numerical column(s)',
    description="Calculate summation of values in numerical column(s)")
    stats_sum.add_argument("input_files", nargs='+', help='input ascii files (can use wildcards)')
    stats_sum.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    stats_sum.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    stats_sum.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    stats_sum.add_argument(
        '--decimal',
        nargs=1,
        type=int,
        action='store',
        default=[2],
        help='number of decimals (default=2)')
    stats_sum.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    stats_sum.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')

    #------------------------#
    # $> gdp stats mean
    stats_mean = stats_subparsers.add_parser('mean', help='calculate mean of numerical column(s)',
    description="Calculate mean of values in numerical column(s)")
    stats_mean.add_argument("input_files", nargs='+', help='input ascii files (can use wildcards)')
    stats_mean.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    stats_mean.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    stats_mean.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    stats_mean.add_argument(
        '--decimal',
        nargs=1,
        type=int,
        action='store',
        default=[2],
        help='number of decimals (default=2)')
    stats_mean.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    stats_mean.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')
    
    #------------------------#
    # $> gdp stats median
    stats_median = stats_subparsers.add_parser('median', help='calculate median of numerical column(s)',
    description="Calculate median of values in numerical column(s)")
    stats_median.add_argument("input_files", nargs='+',help='input ascii files (can use wildcards)')
    stats_median.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    stats_median.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    stats_median.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    stats_median.add_argument(
        '--decimal',
        nargs=1,
        type=int,
        action='store',
        default=[2],
        help='number of decimals (default=2)')
    stats_median.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    stats_median.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')

    #------------------------#
    # $> gdp stats std
    stats_std = stats_subparsers.add_parser('std', help='calculate std of numerical column(s)',
    description="Calculate standard deviation of values in numerical column(s)")
    stats_std.add_argument("input_files", nargs='+', help='input ascii files (can use wildcards)')
    stats_std.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help='value/data column number(s) (default=[3])')
    stats_std.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    stats_std.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    stats_std.add_argument(
        '--decimal',
        nargs=1,
        type=int,
        action='store',
        default=[2],
        help='number of decimals (default=2)')
    stats_std.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    stats_std.add_argument(
        '-a',
        '--append',
        action='store_true',
        help='append to output')

    #------------------------#
    # $> gdp stats plot
    stats_plot = stats_subparsers.add_parser('plot',
        help='plot module for statiscal analysis of data',
        description='Plot module for statiscal analysis of data')
    stats_plot_subparsers = stats_plot.add_subparsers(dest='subsubmodule')

    #------------------------#
    # $> gdp stats plot hist
    stats_plot_hist = stats_plot_subparsers.add_parser('hist',
        help='generate histogram plots',
        description="Generate histogram plots")
    stats_plot_hist.add_argument(
        "input_files",
        type=str,
        nargs='+',
        help='input data files (can use wildcards)'
    )
    stats_plot_hist.add_argument(
        '-o',
        '--outfile',
        type=str,
        help='output file name')
    stats_plot_hist.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[1],
        help='value/data column number(s) (default=[1])')
    stats_plot_hist.add_argument(
        '-n',
        '--nbins',
        type=int,
        default=999,
        help='number of bins (default=auto)')
    stats_plot_hist.add_argument(
        '--legend',
        type=str,
        nargs='+',
        action='store',
        default=[],
        help='legend text; number of elements must be equal to input data items (note: use underline for space)')
    stats_plot_hist.add_argument(
        '--xlabel',
        type=str,
        nargs='*',
        action='store',
        default=['Values'],
        help='x-axis label')
    stats_plot_hist.add_argument(
        '--ylabel',
        type=str,
        nargs='*',
        action='store',
        default=['Count'],
        help='y-axis label')
    stats_plot_hist.add_argument(
        '--title',
        type=str,
        nargs='*',
        action='store',
        default=[],
        help='plot title')
    stats_plot_hist.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for positional and value columns respectively (default=0.4)')
    stats_plot_hist.add_argument(
        '--mean',
        action='store_true',
        help='enable plotting distribution mean (dashed line)')
    stats_plot_hist.add_argument(
        '--median',
        action='store_true',
        help='enable plotting distribution median (dashed line)')
    stats_plot_hist.add_argument(
        '--palette',
        type=str,
        default='Set1',
        choices=['BrBG','PRGn','PiYG','PuOr','RdBu','RdGy','RdYlBu',
                 'RdYlGn','Spectral','Accent','Dark2','Paired',
                 'Pastel1','Pastel2','Set1','Set2','Set3',
                 'Blues','BuGn','BuPu','GnBu','Greens','Greys',
                 'OrRd','Oranges','PuBu','PuBuGn','PuRd','Purples',
                 'RdPu','Reds','YlGn','YlGnBu','YlGnBu','YlOrBr','YlOrRd'],
        help="color palette (see https://www.codecademy.com/article/seaborn-design-ii)"
    )
    stats_plot_hist.add_argument(
        '--figsize',
        type=float,
        nargs=2,
        default=[8,6],
        help="output plot size dimention along x and y (default=[8,6])"
    )
    stats_plot_hist.add_argument(
        '--transparency',
        type=float,
        default=0.75,
        help='transparency value (between 0 and 1; default=0.75)')
    stats_plot_hist.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    stats_plot_hist.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')

    #=====MODULE: RASTER=====#

    raster = subparsers.add_parser('raster',
        help='raster data processing module',
        description="Raster data processing module")
    raster_subparsers = raster.add_subparsers(dest='submodule')

    #------------------------#
    # $> gdp raster georef
    raster_georef = raster_subparsers.add_parser('georef', help='georeference maps',
    description="Georeference maps. Coordinate system could be defined using the EPSG code (visit 'epsg.io' for more information).")
    raster_georef.add_argument(
        '--cs',
        type=str,
        action='store',
        default=4326,
        help='coordinate system or EPSG code (default=wgs84/4326)')

    #------------------------#
    # $> gdp raster plot
    raster_plot = raster_subparsers.add_parser('plot',
        help='plot module for raster data type',
        description='plot module for raster data type')
    raster_plot_subparsers = raster_plot.add_subparsers(dest='subsubmodule')

    #------------------------#
    # $> gdp raster plot geotiff
    raster_plot_geotiff = raster_plot_subparsers.add_parser('geotiff',
        help='generate a map using georeferenced geotiff format',
        description='generate a map using georeferenced geotiff format')

    #=====MODULE: CONVERT=====#
    convert = subparsers.add_parser('convert',
        help='data conversion module',
        description="Data conversion module")
    convert_subparsers = convert.add_subparsers(dest='submodule')

    #------------------------#
    # $> gdp convert 1Dto2D
    convert_1Dto2D = convert_subparsers.add_parser('1Dto2D', help='combine/convert 1D datasets into 2D datasets',
    description="Combine/convert 1D datasets into 2D datasets. Example use cases:\
     (1) building phase velocity map datasets from point/1D dispersion curve datasets,\
     (2) building shear velocity map datasets from 1D shear velocity profiles.")
    convert_1Dto2D.add_argument("datalist", type=str, action='store', help='1D dataset datalist')
    convert_1Dto2D.add_argument(
        '-o',
        '--outdir',
        type=str,
        action='store',
        required=True,
        help='REQUIRED: output directory')
    convert_1Dto2D.add_argument(
        '-x',
        nargs=1,
        type=int,
        action='store',
        default=[1],
        help='positional column number in 1D data files (default=1)')
    convert_1Dto2D.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[2],
        help="value column(s) in 1D data files (default=[2])"
    )
    convert_1Dto2D.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    convert_1Dto2D.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4", "03.0"],
        help='float format (to store) for positional, value, and the identifier columns respectively (default=[".4",".4","03.0"])')
    convert_1Dto2D.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    convert_1Dto2D.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    convert_1Dto2D.add_argument(
        '--prefix',
        type=str,
        action='store',
        default = 'model_',
        help='output file name prefix (default="model_")')
    convert_1Dto2D.add_argument(
        '--suffix',
        type=str,
        action='store',
        default = '',
        help='output file name suffix (default="")')
    convert_1Dto2D.add_argument(
        '--ext',
        type=str,
        action='store',
        default = 'dat',
        help='output file extension (default="dat")')

    #------------------------#
    # $> gdp convert 1Dto3D
    convert_1Dto3D = convert_subparsers.add_parser('1Dto3D', help='combine/convert 1D datasets into a 3D dataset',
    description="Combine/convert 1D datasets into a 3D dataset. Example use case:\
     - building 3D shear velocity model, to be converted into a voxel, from 1D shear velocity profiles.")
    convert_1Dto3D.add_argument("datalist", type=str, action='store', help='1D dataset datalist')
    convert_1Dto3D.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output file')
    convert_1Dto3D.add_argument(
        '-x',
        nargs=1,
        type=int,
        action='store',
        default=[1],
        help='positional column number in 1D data files (default=1)')
    convert_1Dto3D.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[2],
        help="value column(s) in 1D data files (default=[2])"
    )
    convert_1Dto3D.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    convert_1Dto3D.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4", "03.0"],
        help='float format (to store) for positional, value, and the identifier columns respectively (default=[".4",".4","03.0"])')
    convert_1Dto3D.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    convert_1Dto3D.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')


    #------------------------#
    # $> gdp convert 2Dto1D
    convert_2Dto1D = convert_subparsers.add_parser('2Dto1D', help='extract/convert 2D datasets into 1D datasets',
    description="Extract/convert 2D datasets into 1D datasets. Example use cases:\
     (1) extracting point dispersion curves from phase velocity maps,\
     (2) extracing 1D shear velocity profiles from shear velocity map datasets")
    convert_2Dto1D.add_argument("datalist", type=str, action='store', help='2D dataset datalist')
    convert_2Dto1D.add_argument(
        '-o',
        '--outdir',
        type=str,
        action='store',
        required=True,
        help='REQUIRED: output directory')
    convert_2Dto1D.add_argument(
        '-x',
        nargs=2,
        type=int,
        action='store',
        default=[1,2],
        help='positional column number in 2D data files (default=[1,2])')
    convert_2Dto1D.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help="value column(s) in 2D data files (default=[3])"
    )
    convert_2Dto1D.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    convert_2Dto1D.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4", "03.0"],
        help='float format (to store) for positional, value, and the identifier columns respectively (default=[".4",".4","03.0"])')
    convert_2Dto1D.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    convert_2Dto1D.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')
    convert_2Dto1D.add_argument(
        '--ext',
        type=str,
        action='store',
        default = 'dat',
        help='output file extension (default="dat")')

    #------------------------#
    # $> gdp convert 2Dto3D
    convert_2Dto3D = convert_subparsers.add_parser('2Dto3D', help='combine/convert 2D datasets into a 3D dataset',
    description="Combine/convert 2D datasets into a 3D dataset. Example use case:\
     - building a 3D/voxel shear wave velocity model from shear wave velocity map data")
    convert_2Dto3D.add_argument("datalist", type=str, action='store', help='2D dataset datalist')
    convert_2Dto3D.add_argument(
        '-o',
        '--outfile',
        type=str,
        action='store',
        help='output directory')
    convert_2Dto3D.add_argument(
        '-x',
        nargs=2,
        type=int,
        action='store',
        default=[1,2],
        help='positional column number in 2D data files (default=[1,2])')
    convert_2Dto3D.add_argument(
        '-v',
        nargs='+',
        type=int,
        action='store',
        default=[3],
        help="value column(s) in 2D data files (default=[3])"
    )
    convert_2Dto3D.add_argument(
        '--skipnan',
        action='store_true',
        help='do not output lines with nan value(s)')
    convert_2Dto3D.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4", "03.0"],
        help='float format (to store) for positional, value, and the identifier columns respectively (default=[".4",".4","03.0"])')
    convert_2Dto3D.add_argument(
        '--header',
        type=int,
        action='store',
        default=0,
        help='number of header lines to ignore (default=0)')
    convert_2Dto3D.add_argument(
        '--footer',
        type=int,
        action='store',
        default=0,
        help='number of footer lines to ignore (default=0)')


    #------------------------#
    # $> gdp convert anomaly1D
    convert_anomaly1D = convert_subparsers.add_parser(
        'anomaly1D',
        help='calculate 1D anomaly model from 1D absolute model (can also define anomaly marker proxies e.g., LAB seismic proxy)',
        description='Calculate 1D/depth anomaly model from 1D absolute model using a 1D reference model. This tool also generates profile plots and can be used to define depth markers (e.g. LAB depth proxy)')
    convert_anomaly1D.add_argument(
        'absmodel',
        type=str,
        help='input absolute value 1D model')
    convert_anomaly1D.add_argument(
        '-x',
        type=int,
        nargs=1,
        required=True,
        help='REQUIRED: column number for the depth column in the input abosolute model')
    convert_anomaly1D.add_argument(
        '-v',
        '--value',
        required=True,
        type=int,
        nargs=1,
        help='REQUIRED: column number for the value column (e.g., velocity) in the input abosolute model')
    convert_anomaly1D.add_argument(
        '--refmodel',
        type=str,
        required=True,
        help='REQUIRED: input 1D reference model; MUST only have two columns (depth, value)')
    convert_anomaly1D.add_argument(
        '--header',
        type=int,
        default=0,
        help='number of header lines to be ignored in the input abosolute value model; default=0')
    convert_anomaly1D.add_argument(
        '--footer',
        type=int,
        default=0,
        help='number of footer lines to be ignored in the input abosolute value model; default=0')
    convert_anomaly1D.add_argument(
        '--fmt',
        type=str,
        nargs=2,
        default=['03.0', '8.4'],
        help="float format for output model; default=['03.0', '8.4']")
    convert_anomaly1D.add_argument(
        '--type',
        choices=['percentage','difference'],
        default='percentage',
        help="output anomaly data type; choices=['percentage' (default), 'difference']")
    convert_anomaly1D.add_argument(
        '--vlabel',
        nargs='+',
        default=['Value'],
        type=str,
        help='value label' )
    convert_anomaly1D.add_argument(
        '--depthlabel',
        type=str,
        nargs='+',
        default=['Depth','(km)'],
        help='depth label (default="Depth (km)")',)
    convert_anomaly1D.add_argument(
        '--invert_yaxis',
        choices=['True','False'],
        default='True',
        help="invert y-axis in the plot (default='True'); choices=[True,False]")
    convert_anomaly1D.add_argument(
        '--legend_loc',
        type=str,
        default='lower left',
        choices=['best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center'],        
        help='legend location')
    convert_anomaly1D.add_argument(
        '-o',
        '--outfile',
        action='store',
        help='output file path')
    convert_anomaly1D.add_argument(
        '--ext',
        type=str,
        choices=['pdf','png','jpg'],
        default='pdf',
        help="output plot file extension/format; choices=['pdf' (default),'png','jpg']")
    convert_anomaly1D.add_argument(
        '--dpi',
        type=int,
        default=150,
        help='output plot dpi (dot per inch; default=150)')
    convert_anomaly1D.add_argument(
        '--markers',
        type=float,
        nargs='+',
        default=[],
        help='mark position of specific values in 1D profiles (e.g., values between 1 and 2 percent perturbations are used to locate the  LAB depth)')
    convert_anomaly1D.add_argument(
        '--markers_depths',
        type=float,
        nargs=2,
        help='depth range to search the given markers for')
    convert_anomaly1D.add_argument(
        '--markers_case',
        type=str,
        choices=['increase', 'decrease', 'both'],
        default='both', 
        help='consider it a marker if the two consecutive values increase/decrease/both[default]')

    #------------------------#
    # $> gdp convert anomaly2D
    convert_anomaly2D = convert_subparsers.add_parser(
        'anomaly2D',
        help='calculate 2D anomaly model from 2D absolute model',
        description='Calculate 2D anomaly model from 2D absolute model using a 1D reference model')
    convert_anomaly2D.add_argument(
        'absmodel',
        type=str,
        help='input absolute value 2D model')
    convert_anomaly2D.add_argument(
        '-x',
        required=True,
        type=int,
        nargs=2,
        help='REQUIRED: column number for x/lon and y/lat columns respectively in the input abosolute model')
    convert_anomaly2D.add_argument(
        '-v',
        '--value',
        required=True,
        type=int,
        nargs=1,
        help='REQUIRED: column number for the value column in the input abosolute model')
    convert_anomaly2D.add_argument(
        '--depth',
        type=float,
        required=True,
        help='REQUIRED: depth value for the 2D absolute data')
    convert_anomaly2D.add_argument(
        '--refmodel',
        type=str,
        required=True,
        help='REQUIRED: input 1D reference model; MUST only have two columns (depth, value)')
    convert_anomaly2D.add_argument(
        '--header',
        type=int,
        default=0,
        help='number of header lines to be ignored in the input abosolute value model; default=0')
    convert_anomaly2D.add_argument(
        '--footer',
        type=int,
        default=0,
        help='number of footer lines to be ignored in the input abosolute value model; default=0')
    convert_anomaly2D.add_argument(
        '--type',
        choices=['percentage','difference'],
        default='percentage',
        help="output anomaly data type; choices=['percentage' (default), 'difference']")
    convert_anomaly2D.add_argument(
        '--fmt',
        type=str,
        nargs=2,
        default=['.4', '8.4'],
        help="float format for output model coordinates and value respectively; default=['.4', '8.4']")
    convert_anomaly2D.add_argument(
        '-o',
        '--outfile',
        action='store',
        help='output file path')

    #------------------------#
    # $> gdp convert shp2dat
    convert_shp2dat = convert_subparsers.add_parser('shp2dat',
        help='convert shp to dat (ascii)',
        description="Convert shape file to dat (ascii)")
    convert_shp2dat.add_argument(
        '--point',
        type=str,
        nargs='+',
        action='store',
        help='point(s): shape file(s)')
    convert_shp2dat.add_argument(
        '--polygon',
        type=str,
        nargs='+',
        action='store',
        help='polygon(s): shape file(s)')
    convert_shp2dat.add_argument(
        '-o',
        '--outdir',
        type=str,
        required=True,
        action='store',
        help='REQUIRED: output directory')
    convert_shp2dat.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for output convex-hull (default=".4")')

    #------------------------#
    # $> gdp convert nc2dat
    convert_nc2dat = convert_subparsers.add_parser('nc2dat',
        help='convert nc to dat (ascii)',
        description="Convert nc data to dat/ascii")
    convert_nc2dat.add_argument(
        "input_file",
        type=str,
        action='store',
        nargs=1,
        help='input nc file')
    convert_nc2dat.add_argument(
        '--metadata',
        action='store_true',
        help='only output metadata')
    convert_nc2dat.add_argument(
        '-v',
        '--data',
        nargs='*',
        type=str,
        help="data field name(s) / vlue column(s); hint: use '--metadata' flag for more information" )
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
        help='append to output' )
    convert_nc2dat.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format for positional and value columns respectively (default=[".4",".4"])')

    #------------------------#
    # $> gdp convert dat2nc
    convert_dat2nc = convert_subparsers.add_parser(
        'dat2nc',
        help='convert dat/ascii (gridded) to nc format',
        description="Convert dat/ascii (must be gridded) to nc format")
    convert_dat2nc.add_argument("input_file", type=str, action='store', help='input ascii file')
    convert_dat2nc.add_argument(
        'output_file',
        type=str,
        action='store',
        help='output nc file')
    convert_dat2nc.add_argument(
        '-x',
        nargs=2,
        type=int,
        action='store',
        default=[1, 2],
        help='[x, y] column number(s) (default=[1, 2])')
    convert_dat2nc.add_argument(
        '-v',
        '--data',
        nargs=1,
        type=int,
        action='store',
        default=[3],
        help="data/value column (default=3)" )
    convert_dat2nc.add_argument(
        '--polygon',
        type=str,
        action='store',
        help='polygon to apply points-in-polygon')
    convert_dat2nc.add_argument(
        '--xrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='grid x/longitude range: [minX/minlon, minY/maxlon] (default=Auto)')
    convert_dat2nc.add_argument(
        '--yrange',
        nargs=2,
        type=float,
        action='store',
        default=[-0.999, 0.999],
        help='grid y/latitude range: [minY/minlat, minY/maxlat] (default=Auto)')
    convert_dat2nc.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".4",".4"],
        help='float format (to store) for positional and value columns respectively (default=[".4",".4"])')
    
    #=====MODULE: UBC=====#

    ubc = subparsers.add_parser('ubc',
        help='UBC code data processing and illustration module',
        description="UBC code data processing and illustration module")
    ubc_subparsers = ubc.add_subparsers(dest='submodule')

    #------------------------#
    # $> gdp ubc mod2xyz
    ubc_mod2xyz = ubc_subparsers.add_parser(
        'mod2xyz',
        help='convert UBC SUS or DEN models to xyz format using 3D mesh',
        description="Convert UBC SUS or DEN models to xyz format using 3D mesh" )
    ubc_mod2xyz.add_argument(
        "mesh",
        type=str,
        help='3D mesh to be used for models' )
    ubc_mod2xyz.add_argument(
        "models",
        type=str,
        nargs='+',
        help='inversion model file/files (can use wildcards)' )
    ubc_mod2xyz.add_argument(
        '-o',
        '--outdir',
        type=str,
        help='by default, the output xyz files are placed in the same directory as the model files; this option can be used to change this behaviour')
    ubc_mod2xyz.add_argument(
        '--fmt',
        nargs=2,
        type=str,
        action='store',
        default=["10.2","13.8"],
        help='float format for positional and model value columns respectively (default=["10.2","13.8"])')
    ubc_mod2xyz.add_argument(
        '--skipdummy',
        action='store_true',
        help='do not output dummy cells with a value of -100.0')
    ubc_mod2xyz.add_argument(
        '--label',
        type=str,
        default="Value",
        help='model parameter label e.g. Susceptibility, Density etc.; default="Value"' )
    ubc_mod2xyz.add_argument(
        '--polygon',
        nargs='+',
        default=[],
        help="polygon/polygons to apply point-in-polygon before output" )

    #------------------------#
    # $> gdp ubc mvi2xyz
    ubc_mvi2xyz = ubc_subparsers.add_parser(
        'mvi2xyz',
        help='convert UBC MVI models to xyz format using 3D mesh',
        description="Convert UBC MVI models models to xyz format using 3D mesh" )
    ubc_mvi2xyz.add_argument(
        "mesh",
        type=str,
        help='3D mesh to be used for models' )
    ubc_mvi2xyz.add_argument(
        "models",
        type=str,
        nargs='+',
        help='inversion model file/files (can use wildcards)' )
    ubc_mvi2xyz.add_argument(
        '-o',
        '--outdir',
        type=str,
        help='by default, the output xyz files are placed in the same directory as the model files; this option can be used to change this behaviour')
    ubc_mvi2xyz.add_argument(
        '--fmt',
        nargs=2,
        type=str,
        action='store',
        default=["10.2","13.8"],
        help='float format for positional and model value columns respectively (default=["10.2","13.8"])')
    ubc_mvi2xyz.add_argument(
        '--skipdummy',
        action='store_true',
        help='do not output dummy cells with a value of -100.0 (or 0.0 in the case of 3-component model)')
    ubc_mvi2xyz.add_argument(
        '--polygon',
        nargs='+',
        default=[],
        help="polygon/polygons to apply point-in-polygon before output" )

    #------------------------#
    # $> gdp ubc plot
    ubc_plot = ubc_subparsers.add_parser(
        'plot',
        help='plot module for UBC code projects',
        description='Plot module for UBC code projects')
    ubc_plot_subparsers = ubc_plot.add_subparsers(dest='subsubmodule')

    #------------------------#
    # $> gdp ubc plot invcurves
    ubc_plot_invcurves = ubc_plot_subparsers.add_parser(
        'invcurves',
        help='generate plots for inversion curves',
        description="Generate plots for inversion curves")
    ubc_plot_invcurves.add_argument(
        "invdir",
        type=str,
        help='inversion directory')
    ubc_plot_invcurves.add_argument(
        '-o',
        '--outdir',
        type=str,
        help='by default, the output plot are placed in the same inversion directory; this option can be used to change this behaviour')
    ubc_plot_invcurves.add_argument(
        '--ext',
        choices=['pdf', 'png', 'jpg'],
        default='pdf',
        help='output file extension; choices: pdf (default), jpg, png ')
    ubc_plot_invcurves.add_argument(
        '--dpi',
        type=int,
        help='output dpi (dot per inch; default=150)',
        default=150)


    #=====MODULE: SEISMIC=====#

    seismic = subparsers.add_parser('seismic',
        help='seismic data acquisition and processing module',
        description="Seismic data acquisition and processing module")
    seismic_subparsers = seismic.add_subparsers(dest='submodule')

    #------------------------#
    # $> gdp seismic download
    seismic_download = seismic_subparsers.add_parser('download',
        help='seismic data acquisition module',
        description="Seismic data acquisition module")
    seismic_download_subparsers = seismic_download.add_subparsers(dest='subsubmodule')

    #------------------------#
    # $> gdp seismic download init
    seismic_download_init = seismic_download_subparsers.add_parser('init',
        help='initialize download project',
        description='Initialize download project and create "download.config" file')
    seismic_download_init.add_argument(
        '--maindir',
        type=str,
        default='./',
        help="path to maindir containing 'download.config' (default='./')")

    #------------------------#
    # $> gdp seismic download events
    seismic_download_events = seismic_download_subparsers.add_parser('events',
        help='download list of events',
        description="Download list of events")
    seismic_download_events.add_argument(
        '--maindir',
        type=str,
        default='./',
        help="path to maindir containing 'download.config' (default='./')")

    #------------------------#
    # $> gdp seismic download stations
    seismic_download_stations = seismic_download_subparsers.add_parser('stations',
        help='download list of stations',
        description="Download list of stations")
    seismic_download_stations.add_argument(
        '--maindir',
        type=str,
        default='./',
        help="path to maindir containing 'download.config' (default='./')")

    #------------------------#
    # $> gdp seismic download metadata
    seismic_download_metadata = seismic_download_subparsers.add_parser('metadata',
        help='download station metadata',
        description="Download station metadata")
    seismic_download_metadata.add_argument(
        '--maindir',
        type=str,
        default='./',
        help="path to maindir containing 'download.config' (default='./')" )
    seismic_download_metadata.add_argument(
        '--metadata',
        type=str,
        default='./metadata',
        help="path to output metadata directory' (default='./metadata')" )

    #------------------------#
    # $> gdp seismic download mseeds
    seismic_download_mseeds = seismic_download_subparsers.add_parser('mseeds',
        help='download mseed files',
        description="Download mseed files")
    seismic_download_mseeds.add_argument(
        '--maindir',
        type=str,
        default='./',
        help="path to maindir containing 'download.config' (default='./')" )
    seismic_download_mseeds.add_argument(
        '--duration',
        type=int,
        required=True,
        help="REQUIRED: timeseries length/duration in seconds." )
    seismic_download_mseeds.add_argument(
        '--offset',
        type=int,
        default=0,
        help="Timeseries starttime offset (relative to events) in seconds (default=0)." )
    seismic_download_mseeds.add_argument(
        '--mseeds',
        type=str,
        default='./mseeds',
        help="Path to output mseeds directory (default=./mseeds)." )
    seismic_download_mseeds.add_argument(
        '--ant',
        action='store_true',
        help='download for ambient-noise-tomography; do not read events list (default=False)' )

    #------------------------#
    # $> gdp seismic mseed2sac
    seismic_mseed2sac = seismic_subparsers.add_parser('mseed2sac',
        help='convert mseed to sac',
        description="Convert mseed to sac. This script also handles data fragmentation issue. ")
    seismic_mseed2sac.add_argument("input_files",
        nargs='+',
        help='input mseed files (can use wildcards e.g., mseeds/*/*)')
    seismic_mseed2sac.add_argument(
        '-o',
        '--outdir',
        type=str,
        required=True,
        help='REQUIRED: path to output directory')
    seismic_mseed2sac.add_argument(
        '--reformat',
        action='store_true',
        help='reformat output sac files: rename and output to related directories based on mseed start time, station & channel information' )
    seismic_mseed2sac.add_argument(
        '--offset',
        type=float,
        default=0,
        help='output event starttime offset in seconds (only if "reformat" is enabled; default=0); same offset value that was used for data acquisition' )
    seismic_mseed2sac.add_argument(
        '--resample',
        type=float,
        default=999,
        help='output sac files sampling frequency' )
    seismic_mseed2sac.add_argument(
        '--noprocess',
        action='store_true',
        help='by default, detrend(spline degree 4) and taper(percentage=0.005) are applied; enabling this option will skip these processes (not recommended!)' )
    
    #------------------------#
    # $> gdp seismic sac2dat
    seismic_sac2dat = seismic_subparsers.add_parser('sac2dat',
        help='convert sac to dat (ascii)',
        description="Convert sac to dat (ascii); output format: time, amplitude")
    seismic_sac2dat.add_argument("input_files",
        nargs='+',
        help='input sac files (can use wildcards e.g., sacfiles/*/*)')
    seismic_sac2dat.add_argument(
        '-o',
        '--outdir',
        type=str,
        required=True,
        help='REQUIRED: path to output directory' )
    seismic_sac2dat.add_argument(
        '--fmt',
        nargs='+',
        type=str,
        action='store',
        default=[".2",".2"],
        help='float format for time and value columns respectively (default=[".2",".2"])' )
    seismic_sac2dat.add_argument(
        '--timerange',
        nargs=2,
        type=float,
        action='store',
        default=[999, 999],
        help='time range limit' )

    #------------------------#
    # $> gdp seismic writehdr
    seismic_writehdr = seismic_subparsers.add_parser('writehdr',
        help='write sac headers using xml metadata',
        description="Write sac headers using xml metadata")
    seismic_writehdr.add_argument("input_files",
        nargs='+',
        help='input sac files (can use wildcards e.g., sacfiles/*/*)')
    seismic_writehdr.add_argument(
        '--metadata',
        type=str,
        default='./metadata',
        help="path to xml (metadata) dataset directory (default='./metadata')" )
    seismic_writehdr.add_argument(
        '--refmodel',
        type=str,
        choices=['1066a','1066b','ak135','ak135f','ak135f_no_mud','iasp91','herrin','jb','prem','pwdk','sp6'],
        default=None,
        help="reference model to write theoretical arrivals into headers (default: None)")
    seismic_writehdr.add_argument(
        '--maindir',
        type=str,
        default='./',
        help="path to maindir containing 'download.config' (default='./')")
    seismic_writehdr.add_argument(
        '--ant',
        action='store_true',
        help='ambient noise tomography dataset: do not update events information (default=False)' )
    seismic_writehdr.add_argument(
        '--sac',
        type=str,
        default='auto',
        help='path to sac software executable (default=auto)' )

    #------------------------#
    # $> gdp seismic remresp
    seismic_remresp = seismic_subparsers.add_parser('remresp',
        help='remove sac instrument response using xml metadata',
        description="Remove instrument response of sacfiles using xml metadata (see obspy documentation for 'unit' (output), 'pre_filt', and 'water_level' information)")
    seismic_remresp.add_argument("input_files",
        nargs='+',
        help='input sac files (can use wildcards e.g., sacfiles/*/*)')
    seismic_remresp.add_argument(
        '--metadata',
        type=str,
        default='./metadata',
        help="path to xml (metadata) dataset directory (default='./metadata')" )
    seismic_remresp.add_argument(
        '--unit',
        type=str,
        choices=['DISP','VEL','ACC'],
        default='VEL',
        help="output unit; (default='VEL')" )
    seismic_remresp.add_argument(
        '--pre_filt',
        type=float,
        nargs=4,
        default=(0.005, 0.006, 30.0, 35.0),
        help="deconvolution prefilter;  default=(0.005, 0.006, 30.0, 35.0); enter 4 zeros for 'pre_filt=None'" )
    seismic_remresp.add_argument(
        '--water_level',
        type=int,
        default=60,
        help="deconvolution water level; default=60" )

    #------------------------#
    # $> gdp seismic resample
    seismic_resample = seismic_subparsers.add_parser('resample',
        help='resample sac files',
        description="Resample sac files using obspy")
    seismic_resample.add_argument("input_files",
        nargs='+',
        help='input sac files (can use wildcards e.g., sacfiles/*/*)')
    seismic_resample.add_argument(
        '--sf',
        type=int,
        required=True,
        help='REQUIRED: output sampling frequency (Hz)' )
    seismic_resample.add_argument(
        '--sac',
        type=str,
        default='auto',
        help='path to sac software executable (default=auto)' )

    #------------------------#
    # $> gdp seismic bandpass
    seismic_bandpass = seismic_subparsers.add_parser('bandpass',
        help='apply bandpass filter to sac files',
        description="Apply bandpass filter to sac files")
    seismic_bandpass.add_argument("input_files",
        nargs='+',
        help='input sac files (can use wildcards e.g., sacfiles/*/*)')
    seismic_bandpass.add_argument(
        '-u',
        '--unit',
        type=str,
        required=True,
        choices=['p','f'],
        help='REQUIRED: corner unit; choices=("p": period, "f":frequency)' )
    seismic_bandpass.add_argument(
        '--c1',
        type=float,
        required=True,
        help='REQUIRED: corner period (s) / frequency (Hz) 1' )
    seismic_bandpass.add_argument(
        '--c2',
        type=float,
        required=True,
        help='REQUIRED: corner period (s) / frequency (Hz) 2' )
    seismic_bandpass.add_argument(
        '-n',
        type=int,
        default=3,
        help='number of poles (default: n=3)' )
    seismic_bandpass.add_argument(
        '-p',
        type=int,
        default=2,
        help='number of passes (default: p=2)' )
    seismic_bandpass.add_argument(
        '--sac',
        type=str,
        default='auto',
        help='path to sac software executable (default=auto)' )

    #------------------------#
    # $> gdp seismic cut
    seismic_cut = seismic_subparsers.add_parser(
        'cut',
        help='cut sac files (also applies cutter fillz)',
        description="Cut sac files (also applies cutter fillz)")
    seismic_cut.add_argument(
        "input_files",
        nargs='+',
        help='input sac files (can use wildcards e.g., sacfiles/*/*)')
    seismic_cut.add_argument(
        '--begin',
        type=float,
        required=True,
        help='REQUIRED: cut begin time (s)' )
    seismic_cut.add_argument(
        '--end',
        type=float,
        required=True,
        help='REQUIRED: cut end time (s)' )
    seismic_cut.add_argument(
        '--relative',
        type=str,
        default=None,
        help='cut relative to header ... e.g. t1-t9 (default=None)' )
    seismic_cut.add_argument(
        '--sac',
        type=str,
        default='auto',
        help='path to sac software executable (default=auto)' )

    #------------------------#
    # $> gdp seismic remchan
    seismic_remchan = seismic_subparsers.add_parser(
        'remchan',
        help='remove extra channels from event directories',
        description="remove extra channels from event directories")
    seismic_remchan.add_argument(
        "input_files",
        nargs='+',
        help='input sac files (can use wildcards e.g., sacfiles/*/*)')
    seismic_remchan.add_argument(
        '--channels',
        type=str,
        required=True,
        nargs='+',
        help='REQUIRED: list of similar channels' )
    seismic_remchan.add_argument(
        '--onlykeep',
        type=str,
        required=True,
        nargs='+',
        help='REQUIRED: if all similar channels are available, only keep these channels' )

    #------------------------#
    # $> gdp seismic sws
    seismic_sws = seismic_subparsers.add_parser(
        'sws',
        help='shear wave splitting (sws) processing module',
        description="shear wave splitting (sws) processing module")
    seismic_sws_subparsers = seismic_sws.add_subparsers(dest='subsubmodule')

    #------------------------#
    # $> gdp seismic sws init
    seismic_sws_init = seismic_sws_subparsers.add_parser(
        'init',
        help='initialize sws project: write XKS phase travel times, make copies, and initial QC',
        description='initialize sws project: write XKS phase travel times using "obspy.taup()", make copies, and initial QC')
    seismic_sws_init.add_argument("input_files",
        nargs='+',
        help='input sac files (can use wildcards e.g., sacfiles/*/*)')
    seismic_sws_init.add_argument(
        '--hdronly',
        action='store_true',
        help='only update header information')
    seismic_sws_init.add_argument(
        '--refmodel',
        type=str,
        choices=['1066a','1066b','ak135','ak135f','ak135f_no_mud','iasp91','herrin','jb','prem','pwdk','sp6'],
        default='iasp91',
        help="reference model (default: 'iasp91')")
    seismic_sws_init.add_argument(
        '--sac',
        type=str,
        default='auto',
        help='path to sac software executable (default=auto)' )

    #------------------------#
    # $> gdp seismic ans
    seismic_ans = seismic_subparsers.add_parser(
        'ans',
        help='ambient-noise-seismology module',
        description="Ambient-noise-seismology module: generate Rayleigh and Love wave empirical Green's functions (zero to hero!).")
    seismic_ans_subparsers = seismic_ans.add_subparsers(dest='subsubmodule')

    #------------------------#
    # $> gdp seismic ans init
    seismic_ans_init = seismic_ans_subparsers.add_parser(
        'init',
        help='initialize ans project',
        description="Initialize project directory. Example: $ ans init <PATH>")
    seismic_ans_init.add_argument(
        'maindir',
        type=str,
        help='path to the main project directory',
        action='store' )

    #------------------------#
    # $> gdp seismic ans config
    seismic_ans_config = seismic_ans_subparsers.add_parser(
        'config',
        help='configure project settings',
        description="Configure project settings in a GUI")
    seismic_ans_config.add_argument(
        '--maindir',
        type=str,
        help='path to the main project directory (default=".")',
        action='store',
        default='.' )

    #------------------------#
    # $> gdp seismic ans download
    seismic_ans_download = seismic_ans_subparsers.add_parser(
        'download',
        help='download module',
        description="Download station list, station meta files, and mseed files.")
    seismic_ans_download.add_argument(
        '--maindir',
        type=str,
        help='path to the main project directory (default=".")',
        action='store',
        default='.' )
    seismic_ans_download_subparsers = seismic_ans_download.add_subparsers(dest='subsubsubmodule')

    #------------------------#
    # $> gdp seismic ans download stations
    seismic_ans_download_stations = seismic_ans_download_subparsers.add_parser(
        'stations',
        help="download station list",
        description="Download station list")
    seismic_ans_download_stations.add_argument(
        '--maindir',
        type=str,
        help='path to the main project directory (default=".")',
        action='store',
        default='.' )

    #------------------------#
    # $> gdp seismic ans download metadata
    seismic_ans_download_metadata = seismic_ans_download_subparsers.add_parser(
        'metadata',
        help="download station meta files",
        description="Download '*.xml' meta files")
    seismic_ans_download_metadata.add_argument(
        '--maindir',
        type=str,
        help='path to the main project directory (default=".")',
        action='store',
        default='.' )
    seismic_ans_download_metadata.add_argument(
        '--update_stations',
        help='update the list of stations based on the content of metadata directory after download',
        action='store_true',
        default=False
    )

    #------------------------#
    # $> gdp seismic ans download mseeds
    seismic_ans_download_mseeds = seismic_ans_download_subparsers.add_parser(
        'mseeds',
        help="download mseed files",
        description="Download '*.mseed' data files")
    seismic_ans_download_mseeds.add_argument(
        '--maindir',
        type=str,
        help='path to the main project directory (default=".")',
        action='store',
        default='.'
    )

    #------------------------#
    # $> gdp seismic ans mseed2sac
    seismic_ans_mseed2sac = seismic_ans_subparsers.add_parser(
        'mseed2sac',
        help='mseed2sac processes module',
        description="mseed2sac processes module.")
    seismic_ans_mseed2sac.add_argument(
        'mseeds_dir',
        type=str,
        help='path to the downloaded MSEED files dataset directory',
        action='store',
    )
    seismic_ans_mseed2sac.add_argument(
        'sacs_dir',
        type=str,
        help='path to the output SAC files dataset directory',
        action='store',
    )
    seismic_ans_mseed2sac.add_argument(
        '--maindir',
        type=str,
        help='path to the main project directory (default=".")',
        action='store',
        default='.'
    )
    seismic_ans_mseed2sac.add_argument(
        '--all',
        help='output all and ignore station list',
        action='store_true',
    )


    #------------------------#
    # $> gdp seismic ans sac2ncf
    seismic_ans_sac2ncf = seismic_ans_subparsers.add_parser(
        'sac2ncf',
        help='sac2ncf processes module',
        description="sac2ncf processes module.")
    seismic_ans_sac2ncf.add_argument(
        'sacs_dir',
        type=str,
        help='path to the input SAC files dataset directory',
        action='store' )
    seismic_ans_sac2ncf.add_argument(
        'ncfs_dir',
        type=str,
        help='path to the output NCF files dataset directory',
        action='store' )
    seismic_ans_sac2ncf.add_argument(
        '--maindir',
        type=str,
        help='path to the main project directory (default=".")',
        action='store',
        default='.' )
    seismic_ans_sac2ncf.add_argument(
        '--all',
        help='output all and ignore station list',
        action='store_true' )

    #------------------------#
    # $> gdp seismic ans ncf2egf
    seismic_ans_ncf2egf = seismic_ans_subparsers.add_parser(
        'ncf2egf',
        help='ncf2egf processes module',
        description="ncf2egf processes module.")
    seismic_ans_ncf2egf.add_argument(
        'ncfs_dir',
        type=str,
        help='path to the input NCF files dataset directory',
        action='store' )
    seismic_ans_ncf2egf.add_argument(
        'egfs_dir',
        type=str,
        help='path to the output EGF files dataset directory',
        action='store' )
    seismic_ans_ncf2egf.add_argument(
        '--cmp',
        nargs='+',
        type=str,
        action='store',
        default=['ZZ','TT','RR'],
        help='cross-correlation component(s) (default: ZZ TT RR)')
    seismic_ans_ncf2egf.add_argument(
        '--maindir',
        type=str,
        help='path to the main project directory (default=".")',
        action='store',
        default='.' )

    #------------------------#
    # $> gdp seismic plot
    seismic_plot = seismic_subparsers.add_parser(
        'plot',
        help='plot module for seismic data',
        description="Plot module for seismic data")
    seismic_plot_subparsers = seismic_plot.add_subparsers(dest='subsubmodule')

    #------------------------#
    # $> gdp seismic plot stations
    seismic_plot_stations = seismic_plot_subparsers.add_parser(
        'stations',
        help='plot seismic stations on a map',
        description="Plot seismic stations on a map")
    seismic_plot_stations.add_argument(
        "stalist",
        type=str,
        help='input station list file')
    seismic_plot_stations.add_argument(
        '--labels',
        action='store_true',
        help='print station labels on the output map (if not global scale map)')
    seismic_plot_stations.add_argument(
        '--boundaries',
        action='store_true',
        help='plot major tectonic boundaries')
    seismic_plot_stations.add_argument(
        '-g',
        '--glob',
        action='store_true',
        help='enable global scale map')
    seismic_plot_stations.add_argument(
        '--meridian',
        type=float,
        default=0,
        help='map central meridian (only if global scale map)')
    seismic_plot_stations.add_argument(
        '--gmt',
        type=str,
        default='auto',
        help='path to GMT software executable (default=auto)'
    )


     #------------------------#
    # $> gdp seismic plot events
    seismic_plot_events = seismic_plot_subparsers.add_parser(
        'events',
        help='plot seismic events on a map',
        description="Plot seismic events on a map")
    seismic_plot_events.add_argument(
        "eventlist",
        type=str,
        help='input event list file')
    seismic_plot_events.add_argument(
        '--lon',
        type=float,
        required=True,
        help='REQUIRED: study region longitude')
    seismic_plot_events.add_argument(
        '--lat',
        type=float,
        required=True,
        help='REQUIRED: study region latitude')
    seismic_plot_events.add_argument(
        '--gmt',
        type=str,
        default='auto',
        help='path to GMT software executable (default=auto)' )

    # return arguments
    return parser.parse_args()

###############################################################

def main(*args, **kwargs):
    args = parse_args(*args, **kwargs)
    if args.about or len(sys.argv) == 1:
        clear_screen()
        print(f"{about}\n")
        exit(0)
    elif args.check:
        from . import dependency
        dependency.check_all()
    
    from . import io    
    from . import dat
    from . import nan
    from . import conv
    from . import sacproc
    from . import download
    from . import mag
    from . import plot
    from . import ubc

    if args.module == 'data':

        if args.submodule == 'cat':
            out_lines = []
            for inpfile in args.input_files:
                out_lines += io.data_lines(inpfile, args)
            io.output_lines(out_lines, args)
            exit(0)
        elif args.submodule == 'union':
            if args.nan:
                nan.union(args)
            else:
                dat.union(args)
            exit(0)
        elif args.submodule == 'intersect':
            if args.nan:
                nan.intersect(args)
            else:
                dat.intersect(args)
            exit(0)
        elif args.submodule == 'difference':
            if args.nan:
                nan.difference(args)
            else:
                dat.difference(args)
            exit(0)
        elif args.submodule == 'add':
            dat.add_intersect_values(args)
            exit(0)
        elif args.submodule == 'split':
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
        
        elif args.submodule == 'cs':
            
            if args.subsubmodule == 'info':
                from . import epsg
                epsg.get_csinfo(args)
                exit(0)
            elif args.subsubmodule == 'transform':
                dat.csproj_ascii(args)
                exit(0)
            elif args.subsubmodule == 'fix':
                if (args.tryall == False and args.trylist==""):
                    print("Error: either of these flags must be used: '--tryall' or '--trylist'")
                    exit(1)
                dat.csproj_fix(args)
                exit(0)

        elif args.submodule == 'chull':
            dat.convex_hull(args)
            exit(0)
        elif args.submodule == 'pip':
            dat.points_in_polygon(args)
            exit(0)
        elif args.submodule == 'nodes':
            dat.nodes(args)
            exit(0)
        elif args.submodule == 'gridder':
            if args.nodes == None and args.spacing == None:
                print("Either of these arguments is required: 'spacing' or 'nodes'")
                exit(1)
            elif args.nodes != None and args.spacing != None:
                print("Only one of these arguments should be given: 'spacing' or 'nodes'")
                exit(1)
            if args.utm:
                dat.gridder_utm(args)
            else:
                dat.gridder(args)
            exit(0)
        elif args.submodule == 'plot':

            if args.subsubmodule == 'scatter':        
                plot.plot_data_scatter(args)
        else:
            subprocess.call("gdp data -h", shell=True)
            exit(0)

    elif args.module == 'stats':
        
        if args.submodule == 'min':
            dat.calc_min(args)
            exit(0)
        elif args.submodule == 'max':
            dat.calc_max(args)
            exit(0)
        elif args.submodule == 'sum':
            dat.calc_sum(args)
            exit(0)
        elif args.submodule == 'mean':
            dat.calc_mean(args)
            exit(0)
        elif args.submodule == 'median':
            dat.calc_median(args)
            exit(0)
        elif args.submodule == 'std':
            dat.calc_std(args)
            exit(0)
        elif args.submodule == 'plot':

            if args.subsubmodule == 'hist':
                plot.plot_hist(args)
                exit(0)
        else:
            subprocess.call("gdp stats -h", shell=True)
            exit(0)

    elif args.module == 'raster':
        
        if args.submodule == 'georef':

            from . import georefmaps
            from . import dat
            import tkinter as tk
            epsg = dat.return_epsg_code(args.cs)
            root = tk.Tk()
            app = georefmaps.Application(master=root, epsg=epsg)
            app.mainloop()

        elif args.submodule == 'plot':
            
            if args.subsubmodule == 'geotiff':
                under_dev()
        else:
            subprocess.call("gdp raster -h", shell=True)
            exit(0)

    elif args.module == 'convert':
        
        if args.submodule == '1Dto2D':
            conv.datasets_1Dto2D(args)
            exit(0)
        elif args.submodule == '1Dto3D':
            conv.datasets_1Dto3D(args)
            exit(0)
        elif args.submodule == '2Dto1D':
            conv.datasets_2Dto1D(args)
            exit(0)
        elif args.submodule == '2Dto3D':
            conv.datasets_2Dto3D(args)
            exit(0)
        elif args.submodule == 'anomaly1D':
            dat.anomaly_1D(args)
            exit(0)
        elif args.submodule == 'anomaly2D':
            dat.anomaly_2D(args)
            exit(0)
        elif args.submodule == 'shp2dat':
            if args.point == None and args.polygon == None:
                print("Error! At least one shape file must be given")
                exit(1)
            conv.shp2dat(args)
            exit(0)
        elif args.submodule == 'nc2dat':
            conv.nc2dat(args)
            exit(0)
        elif args.submodule == 'dat2nc':
            conv.dat2nc(args)
            exit(0)
        else:
            subprocess.call("gdp convert -h", shell=True)
            exit(0)

    elif args.module == 'ubc':
        
        if args.submodule == 'mod2xyz':
            ubc.mod2xyz(args)
            exit(0)
        elif args.submodule == 'mvi2xyz':
            ubc.mvi2xyz(args)
            exit(0)
        elif args.submodule == 'plot':

            if args.subsubmodule == 'invcurves':
                ubc.invcurves(args)
                exit(0)
        else:
            subprocess.call("gdp ubc -h", shell=True)
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
            if args.relative == None:
                sacproc.cut(args)
            else:
                sacproc.cut_relative(args)
            exit(0)
        elif args.submodule == 'remchan':
            sacproc.remchan(args)
            exit(0)
        elif args.submodule == 'sws':
            from . import sws
            
            if args.subsubmodule == 'init':
                sws.run_sws_dataset_app(args.input_files, refmodel=args.refmodel,
                    SAC=args.sac, headonly=args.hdronly)
                exit(0)

        elif args.submodule == 'ans':

            if args.subsubmodule == 'init':

                from . import ans_config
                from . import ans_proc
                
                if not os.path.isdir(args.maindir):
                    os.mkdir(args.maindir)
                if not os.path.isdir(os.path.join(args.maindir, '.ans')):
                    os.mkdir(os.path.join(args.maindir, '.ans'))
                defaults = ans_config.Defaults(args.maindir)
                parameters = defaults.parameters()
                ans_config.write_config(args.maindir, parameters)
                print("Project directory was successfully initialized!\n")

            elif args.subsubmodule == 'config':
                from . import ans_gui
                from PyQt5.QtWidgets import QApplication
                app = QApplication(sys.argv)
                win = ans_gui.MainWindow(args.maindir)
                win.show()
                sys.exit(app.exec_())
                app.exec_()

            elif args.subsubmodule == 'download':
                from . import ans_download
                if args.subsubsubmodule == 'stations':
                    ans_download.download_stations(args.maindir)
                elif args.subsubsubmodule == 'metadata':
                    ans_download.download_metadata(args.maindir, args.update_stations)
                elif args.subsubsubmodule == 'mseeds':
                    ans_download.download_mseeds(args.maindir)

            elif args.subsubmodule == 'mseed2sac':
                
                from . import ans_mseed2sac
                ans_mseed2sac.mseed2sac_run_all(args.maindir, args.mseeds_dir, args.sacs_dir, args.all)

            elif args.subsubmodule == 'sac2ncf':

                from . import ans_sac2ncf
                ans_sac2ncf.sac2ncf_run_all(args.maindir, args.sacs_dir, args.ncfs_dir, args.all)

            elif args.subsubmodule == 'ncf2egf':

                from . import ans_ncf2egf
                ans_ncf2egf.ncf2egf_run_all(args.maindir, args.ncfs_dir, args.egfs_dir, args.cmp)

        elif args.submodule == 'plot':

            if args.subsubmodule == 'stations':
                if args.glob:
                    plot.plot_stations_global(args.stalist, labels=args.labels,
                        meridian=args.meridian, boundaries=args.boundaries, GMT=args.gmt)
                else:
                    plot.plot_stations(args.stalist, args.labels, GMT=args.gmt)
                exit(0)
            elif args.subsubmodule == 'events':
                plot.plot_events(args.eventlist, args.lon, args.lat, GMT=args.gmt)
                exit(0)
        else:
            subprocess.call("gdp seismic -h", shell=True)
            exit(0)



if __name__ == "__main__":
    main(*args, **kwargs)
