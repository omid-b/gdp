from .ascii import io
from .ascii import numerical
from .ascii import non_numerical
from .geographic import epsg
from .geographic import coordinate_systems
from .geographic import polygon_operations
from .discretize import nodes
from .gridder import fixed_gaussian_smoothing

#-------------------------#
def data_concatenate(args):
    out_lines = []
    for inpfile in args.input_files:
        out_lines += io.data_lines(inpfile, args)
    io.output_lines(out_lines, args)

#-------------------------#
def data_union(args):
    if args.nan:
        non_numerical.union(args)
    else:
        numerical.union(args)

#-------------------------#
def data_intersect(args):
    if args.nan:
        non_numerical.intersect(args)
    else:
        numerical.intersect(args)

#-------------------------#
def data_difference(args):
    if args.nan:
        non_numerical.difference(args)
    else:
        numerical.difference(args)

#-------------------------#
def data_add(args):
    numerical.add_intersect_values(args)

#-------------------------#
def data_split(args):
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

            non_numerical.split_data_nrow(args)

        else:

            non_numerical.split_data_ncol(args)

#-------------------------#
def data_cs_info(args):
    epsg.get_csinfo(args)

#-------------------------#
def data_cs_transform(args):
    coordinate_systems.csproj_ascii(args)

#-------------------------#
def data_cs_fix(args):
    if (args.tryall == False and args.trylist==""):
        print("Error: either of these flags must be used: '--tryall' or '--trylist'")
        exit(1)
    coordinate_systems.csproj_fix(args)

#-------------------------#
def data_chull(args):
    polygon_operations.convex_hull_polygon(args)

#-------------------------#
def data_ashape(args):
    polygon_operations.alpha_shape_polygon(args)

#-------------------------#
def data_pip(args):
    polygon_operations.points_in_polygon(args)

#-------------------------#
def data_nodes(args):
    nodes.nodes(args)

def data_gridder(args):
    if args.nodes == None and args.spacing == None:
        print("Either of these arguments is required: 'spacing' or 'nodes'")
        exit(1)
    elif args.nodes != None and args.spacing != None:
        print("Only one of these arguments should be given: 'spacing' or 'nodes'")
        exit(1)
    if args.utm:
        fixed_gaussian_smoothing.gridder_utm(args)
    else:
        fixed_gaussian_smoothing.gridder(args)



