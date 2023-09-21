# from .io import numerical
import os
from .io import non_numerical
from .io import numerical
# from .geographic import epsg
# from .geographic import coordinate_systems
# from .geographic import polygon_operations
# from .discretize import nodes
# from .gridder import fixed_gaussian_smoothing

#-------------------------#
def data_concatenate(args):
    concatenated = [] 
    if args.nan: # non-numerical
        for input_file in args.input_files:
            concatenated += non_numerical.read_lines(input_file, args.header, args.footer)
    else: # numerical
        concatenated = [] 
        for input_file in args.input_files:
            numerical_data = numerical.read_numerical_dataset(input_file, args.header, args.footer,\
                                                            args.x, args.v, args.skipnan)
            numerical_data_strLines = numerical.numerical_dataset_to_strLines(numerical_data, args.fmt, args.noextra)
            concatenated += numerical_data_strLines

    # output results
    if args.outfile:
        non_numerical.write_to_file(concatenated,\
                                    args.outfile,\
                                    uniq=args.uniq,\
                                    sort=args.sort,\
                                    append=args.append)
    else:
        non_numerical.write_to_stdout(concatenated,\
                                    uniq=args.uniq,\
                                    sort=args.sort)

#-------------------------#
def data_union(args):
    datasets = []
    for input_file in args.input_files:
        if args.nan:
            datasets.append(non_numerical.read_lines(input_file, args.header, args.footer))
        else:
            datasets.append(numerical.read_numerical_dataset(input_file, args.header, args.footer,\
                                                             args.x, args.v, args.skipnan))
    if args.nan:
        union = non_numerical.calc_union(datasets)
    else:
        union = numerical.calc_union(datasets, args.inverse)
        union = numerical.numerical_dataset_to_strLines(union, args.fmt, args.noextra)

    # output results
    if args.outfile:
        non_numerical.write_to_file(union,\
                                    args.outfile,\
                                    uniq=args.uniq,\
                                    sort=args.sort,\
                                    append=args.append)
    else:
        non_numerical.write_to_stdout(union,\
                                    uniq=args.uniq,\
                                    sort=args.sort)

#-------------------------#
def data_intersect(args):
    datasets = []
    for input_file in args.input_files:
        if args.nan:
            datasets.append(non_numerical.read_lines(input_file, args.header, args.footer))
        else:
            datasets.append(numerical.read_numerical_dataset(input_file, args.header, args.footer,\
                                                             args.x, args.v, args.skipnan))
    if args.nan:
        intersect = non_numerical.calc_intersect(datasets)
    else:
        intersect = numerical.calc_intersect(datasets, args.inverse)
        intersect = numerical.numerical_dataset_to_strLines(intersect, args.fmt, args.noextra)
    # output results
    if args.outfile:
        non_numerical.write_to_file(intersect,\
                                    args.outfile,\
                                    uniq=args.uniq,\
                                    sort=args.sort,\
                                    append=args.append)
    else:
        non_numerical.write_to_stdout(intersect,\
                                    uniq=args.uniq,\
                                    sort=args.sort)

#-------------------------#
def data_difference(args):
    datasets = []
    for input_file in args.input_files:
        if args.nan:
            datasets.append(non_numerical.read_lines(input_file, args.header, args.footer))
        else:
            datasets.append(numerical.read_numerical_dataset(input_file, args.header, args.footer,\
                                                             args.x, args.v, args.skipnan))
    if args.nan:
        difference = non_numerical.calc_difference(datasets)
    else:
        difference = numerical.calc_difference(datasets, args.inverse)
        difference = numerical.numerical_dataset_to_strLines(difference, args.fmt, args.noextra)
    # output results
    if args.outfile:
        non_numerical.write_to_file(difference,\
                                    args.outfile,\
                                    uniq=args.uniq,\
                                    sort=args.sort,\
                                    append=args.append)
    else:
        non_numerical.write_to_stdout(difference,\
                                    uniq=args.uniq,\
                                    sort=args.sort)

# #-------------------------#
def data_add(args):
    datasets = []
    for input_file in args.input_files:
        datasets.append(numerical.read_numerical_dataset(input_file, args.header, args.footer,\
                                                             args.x, args.v, args.skipnan))

    add_intersect = numerical.calc_add_intersect(datasets)
    add_intersect = numerical.numerical_dataset_to_strLines(add_intersect, args.fmt, noextra=True)
     # output results
    if args.outfile:
        non_numerical.write_to_file(add_intersect,\
                                    args.outfile,\
                                    uniq=False,\
                                    sort=args.sort,\
                                    append=args.append)
    else:
        non_numerical.write_to_stdout(add_intersect,\
                                    uniq=False,\
                                    sort=args.sort)

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
    # read combined dataset
    combined_dataset = non_numerical.read_lines(args.input_file, args.header, args.footer)
    # start split
    if args.method == 'nrow':
        if args.start:
            print(f"\nError! Argument 'start' is only for method=ncol\n")
            exit(1)

        split_dataset = non_numerical.split_by_nrows(combined_dataset,\
                                                     args.number,\
                                                     name_index_offset=args.name)
    else: # args.method == 'ncol'

        split_dataset = non_numerical.split_by_ncols(combined_dataset,\
                                                     args.number,\
                                                     name_index_offset=args.name,\
                                                     start_index_offset=args.start)
    # output results
    if args.outdir:
        if not os.path.isdir(args.outdir):
            os.mkdir(args.outdir)
        for key in split_dataset.keys():
            fout = os.path.join(args.outdir, f"{key}.{args.ext}")
            non_numerical.write_to_file(split_dataset[f"{key}"], fout)
    else:
        for key in split_dataset.keys():
            print(f'\nFile: "{key}.{args.ext}"')
            non_numerical.write_to_stdout(split_dataset[f"{key}"])

# #-------------------------#
# def data_cs_info(args):
#     epsg.get_csinfo(args)

# #-------------------------#
# def data_cs_transform(args):
#     coordinate_systems.csproj_ascii(args)

# #-------------------------#
# def data_cs_fix(args):
#     if (args.tryall == False and args.trylist==""):
#         print("Error: either of these flags must be used: '--tryall' or '--trylist'")
#         exit(1)
#     coordinate_systems.csproj_fix(args)

# #-------------------------#
# def data_chull(args):
#     polygon_operations.convex_hull_polygon(args)

# #-------------------------#
# def data_ashape(args):
#     polygon_operations.alpha_shape_polygon(args)

# #-------------------------#
# def data_pip(args):
#     polygon_operations.points_in_polygon(args)

# #-------------------------#
# def data_nodes(args):
#     nodes.nodes(args)

# def data_gridder(args):
#     if args.nodes == None and args.spacing == None:
#         print("Either of these arguments is required: 'spacing' or 'nodes'")
#         exit(1)
#     elif args.nodes != None and args.spacing != None:
#         print("Only one of these arguments should be given: 'spacing' or 'nodes'")
#         exit(1)
#     if args.utm:
#         fixed_gaussian_smoothing.gridder_utm(args)
#     else:
#         fixed_gaussian_smoothing.gridder(args)



