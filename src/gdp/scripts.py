
import os

import numpy as np

from .io import non_numerical
from .io import numerical
from .spatial import coordinate_systems
from .spatial import polygon_operations

from .io.ascii import Dataset

# from .geographic import epsg
# from .discretize import nodes
# from .gridder import fixed_gaussian_smoothing

#-------------------------#
def test(args):
    if args.nan:
        args.x = args.v = []
    
    dataset = Dataset(args.input_files)
    dataset.options(**vars(args))
    dataset.write()

    print()
    print("intersect")
    dataset.intersect()
    dataset.write()

    print()
    print("intersect_inv")
    dataset.intersect(inverse=True)
    dataset.write()
    print(dataset.titles)




#-------------------------#
def data_concatenate(args):
    concatenated = [] 
    if args.nan: # non-numerical
        for input_file in args.input_files:
            concatenated += non_numerical.read_dataset(input_file, args.header, args.footer)
    else: # numerical
        concatenated = [] 
        for input_file in args.input_files:
            numerical_data = numerical.read_dataset(input_file, args.header, args.footer,\
                                                            args.x, args.v, args.skipnan)
            numerical_data_strLines = numerical.convert_to_non_numerical(numerical_data, args.fmt, args.noextra)
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
            datasets.append(non_numerical.read_dataset(input_file, args.header, args.footer))
        else:
            datasets.append(numerical.read_dataset(input_file, args.header, args.footer,\
                                                             args.x, args.v, args.skipnan))
    if args.nan:
        union = non_numerical.calc_union(datasets)
    else:
        union = numerical.calc_union(datasets, args.inverse)
        union = numerical.convert_to_non_numerical(union, args.fmt, args.noextra)

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
            datasets.append(non_numerical.read_dataset(input_file, args.header, args.footer))
        else:
            datasets.append(numerical.read_dataset(input_file, args.header, args.footer,\
                                                             args.x, args.v, args.skipnan))
    if args.nan:
        intersect = non_numerical.calc_intersect(datasets, inverse=args.inverse)
    else:
        intersect = numerical.calc_intersect(datasets, inverse=args.inverse)
        intersect = numerical.convert_to_non_numerical(intersect, args.fmt, args.noextra)
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
            datasets.append(non_numerical.read_dataset(input_file, args.header, args.footer))
        else:
            datasets.append(numerical.read_dataset(input_file, args.header, args.footer,\
                                                             args.x, args.v, args.skipnan))
    if args.nan:
        difference = non_numerical.calc_difference(datasets)
    else:
        difference = numerical.calc_difference(datasets, args.inverse)
        difference = numerical.convert_to_non_numerical(difference, args.fmt, args.noextra)
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
        datasets.append(numerical.read_dataset(input_file, args.header, args.footer,\
                                                             args.x, args.v, args.skipnan))

    add_intersect = numerical.calc_add_intersect(datasets)
    add_intersect = numerical.convert_to_non_numerical(add_intersect, args.fmt, noextra=True)
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
        print(f"\nError: argument 'number' should be a positive integer\n")
        exit(1)
    if args.header < 0 :
        print(f"\nError: argument 'header' should be a positive integer\n")
        exit(1)
    if args.footer < 0 :
        print(f"\nError: argument 'footer' should be a positive integer\n")
        exit(1)
    if args.name < 1 :
        print(f"\nError: argument 'name' should be a positive integer (> 0) for method=nrow\n")
        exit(1)
    if args.name > args.number:
        print(f"\nError: argument 'name' should be less than or equal argument 'number' for method=nrow\n")
        exit(1)
    # read combined dataset
    combined_dataset = non_numerical.read_dataset(args.input_file, args.header, args.footer)
    # start split
    if args.method == 'nrow':
        if args.start:
            print(f"\nError: argument 'start' is only for method=ncol\n")
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
def data_cs_info(args):
    coordinate_systems.get_csinfo(args.keywords)


# #-------------------------#
def data_cs_transform(args):
    if (args.data and args.xy) or (not args.data and not args.xy):
        print("Error: either of these options must be used:'data' or 'xy'")
        exit(1)

    elif args.data and not args.xy:

        if not args.x:
            print("Error: positional columns i.e. option 'x' not specified")
            exit(1)

        transformed = [[],[]] # [[x], [y]]
        numerical_data = numerical.read_dataset(\
                         args.data, args.header, args.footer,\
                         pos_indx=args.x, val_indx=[], skipnan=False)
        nol = len(numerical_data[2])
        for iline in range(nol):
            x0 = numerical_data[0][0][iline]
            y0 = numerical_data[0][1][iline]
            xt, yt = coordinate_systems.transform(x0, y0, args.cs[0], args.cs[1])
            transformed[0].append(xt)
            transformed[1].append(yt)

        if args.skiporig:
            numerical_data[0] = []
            numerical_data[1] = transformed
        else:
            numerical_data[1] = transformed
    
    elif args.xy and not args.data:

        x0, y0 = args.xy
        xt, yt = coordinate_systems.transform(x0, y0, args.cs[0], args.cs[1])
        numerical_data = [[[x0], [y0]], [[xt], [yt]], ['']]
        if args.skiporig:
            numerical_data[0] = []


    numerical_data_strLines = numerical.convert_to_non_numerical(numerical_data, args.fmt, noextra=False)
    # output results
    if args.outfile:
        non_numerical.write_to_file(numerical_data_strLines,\
                                    args.outfile,\
                                    uniq=False,\
                                    sort=False,\
                                    append=args.append)
    else:
        non_numerical.write_to_stdout(numerical_data_strLines,\
                                    uniq=False,\
                                    sort=False)


#-------------------------#
def data_cs_mismatch(args):
    if (args.tryall == False and args.trylist==""):
        print("Error: either of these flags must be used: '--tryall' or '--trylist'")
        exit(1)

    known_xy, _, _ = numerical.read_dataset(\
                               args.known, 0, 0,\
                               pos_indx=args.x, val_indx=[], skipnan=True)
    unknown_xy, _, _ = numerical.read_dataset(\
                                 args.unknown, 0, 0,\
                                 pos_indx=args.x, val_indx=[], skipnan=True)
    
    trylist = []
    if args.trylist:
        trylist = non_numerical.read_dataset(args.trylist)

    best_mismatch_mean_dist = coordinate_systems.find_smallest_mismatch(\
                                        known_xy, unknown_xy, args.cs,\
                                        trylist, args.n)
    
    output_lines = []
    for key in best_mismatch_mean_dist.keys():
        output_lines.append(f"%s  %.2f" %(key, best_mismatch_mean_dist[key]))

    # output results
    if args.outfile:
        non_numerical.write_to_file(output_lines,\
                                    args.outfile,\
                                    uniq=False,\
                                    sort=False,\
                                    append=args.append)
    else:
        non_numerical.write_to_stdout(output_lines,\
                                    uniq=False,\
                                    sort=False)


#-------------------------#
def data_chull(args):
    [points_x, points_y], _, _ = numerical.read_dataset(\
                               args.points_file, 0, 0,\
                               pos_indx=args.x, val_indx=[], skipnan=True)

    chull_x, chull_y = polygon_operations.convex_hull(points_x, points_y)
    numerical_chull = [[chull_x, chull_y],[],['' for i in range(len(chull_x))]]

    # output results
    if args.outfile:
        numerical.write_to_file(numerical_chull,\
                                args.outfile,\
                                uniq=False,\
                                sort=False,\
                                append=False,\
                                fmt=args.fmt,
                                noextra=True)
    else:
        numerical.write_to_stdout(numerical_chull,\
                                  uniq=False,\
                                  sort=False,
                                  fmt=args.fmt,
                                  noextra=True)


#-------------------------#
def data_ashape(args):
    [points_x, points_y], _, _ = numerical.read_dataset(\
                               args.points_file, 0, 0,\
                               pos_indx=args.x, val_indx=[], skipnan=True)

    ashape_x, ashape_y = polygon_operations.alpha_shape(points_x, points_y, alpha=args.alpha)
    numerical_ashape = [[ashape_x, ashape_y],[],['' for i in range(len(ashape_x))]]

    # output results
    if args.outfile:
        numerical.write_to_file(numerical_ashape,\
                                args.outfile,\
                                uniq=False,\
                                sort=False,\
                                append=False,\
                                fmt=args.fmt,\
                                noextra=True)
    else:
        numerical.write_to_stdout(numerical_ashape,\
                                 uniq=False,\
                                 sort=False,
                                 fmt=args.fmt,
                                 noextra=True)


#-------------------------#
def data_pip(args):
    points_dataset = numerical.read_dataset(\
                               args.points_file, 0, 0,\
                               pos_indx=args.x, val_indx=[], skipnan=True)
    [polygon_x, polygon_y], _, _ = numerical.read_dataset(\
                                   args.points_file, 0, 0,\
                                   pos_indx=[1,2], val_indx=[], skipnan=True)
    # make it a closed polygon if necessary
    if polygon_x[0] != polygon_x[-1] and polygon_y[0] != polygon_y[-1]:
        polygon_x.append(polygon_x[0])
        polygon_y.append(polygon_y[0])

    results_numerical = polygon_operations.dataset_in_polygon(\
                        points_dataset, polygon_x, polygon_y,\
                        inverse=args.inverse)
    numerical.write_to_stdout(results_numerical)

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

