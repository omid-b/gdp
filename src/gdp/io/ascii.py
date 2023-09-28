#!/usr/bin/env python3

"""
 Numerical & Non-numerical ascii Dataset class

 List of possible processes:
    - merge
    - union
    - intersect
    - difference
    - add intersect values
    - split by row
    - split by column
    - ...

"""

import os
import numpy as np
from argparse import Namespace

class Dataset:

    def __init__(self, files=[], datasets=[]):
        self.nds = 0 # number of datasets
        self.files = [] # list of files
        self.datasets = [] # list of datasets
        self.lines = [] # list of file lines
        self.titles = [] # list of processed datset titles
        self.processed = [] # list of processed datsets
        self.last_process = None
        self.default_parameters = Namespace(
            header = 0,
            footer = 0,
            x = [], # positional columns e.g. x, y, z
            v = [], # value columns e.g. velocity, density
            noextra = False, # no extra columns
            skipnan = False, # skip nan data
            fmt = [".4", ".4"], # format for positional and value columns
            sort = False, # sort when output 
            uniq = False, # uniq when output
        )
        self.parameters = self.default_parameters
        self.set(**vars(self.default_parameters))
        self.append(files, datasets) # must be after self.set()


    def __str__(self):
        return '\n'.join(self.get_lines(merge=True))


    def __repr__(self):
        return '\n'.join(self.get_lines(merge=True))


    def set(self, **parameters):
        for param in parameters.keys():
            if param == 'header':
                self.header = parameters['header']
                self.parameters.header = parameters['header']
            elif param == 'footer':
                self.footer = parameters['footer']
                self.parameters.footer = parameters['footer']
            elif param == 'x':
                self.x = parameters['x']
                self.parameters.x = parameters['x']
            elif param == 'v':
                self.v = parameters['v']
                self.parameters.v = parameters['v']
            elif param == 'noextra':
                self.noextra = parameters['noextra']
                self.parameters.noextra = parameters['noextra']
            elif param == 'skipnan':
                self.skipnan = parameters['skipnan']
                self.parameters.skipnan = parameters['skipnan']
            elif param == 'fmt':
                self.fmt = parameters['fmt']
                if len(self.fmt) == 1:
                    self.fmt = [parameters['fmt'][0], parameters['fmt'][0]]
                self.parameters.fmt = parameters['fmt']
            elif param == 'sort':
                self.sort = parameters['sort']
                self.parameters.sort = parameters['sort']
            elif param == 'uniq':
                self.uniq = parameters['uniq']
                self.parameters.uniq = parameters['uniq']
        self.update()


    def append(self, new_files=[], new_datasets=[]):
        # append new_files
        try:
            assert isinstance(new_files, list)
        except AssertionError:
            new_files = [new_files]
        nof = len(new_files)
        for i in range(nof):
            if new_files[i] in self.files:
                continue
            try:
                fopen = open(new_files[i], 'r')
                lines = fopen.read().splitlines()
                fopen.close()
            except FileNotFoundError:
                raise Exception(f"Error: could not read file: {new_files[i]}")

            self.files.append(new_files[i])
            self.lines.append(lines)

        # append new_datasets
        try:
            assert isinstance(new_datasets, list)
        except AssertionError:
            raise AssertionError("appended dataset is not a list")
        nod = len(new_datasets)
        # loop through datasets and check data format
        for i in range(nod): 
            if len(new_datasets[i]) != 3: # [[pos], [val], [extra]]
                raise Exception(f"Error: input dataset format is not correct:\ndatasets[{i}]={new_datasets[i]}")
            nol = len(new_datasets[i][2])
            nx = len(new_datasets[i][0])
            nv = len(new_datasets[i][1])
            # check extra for this dataset
            for iline in range(nol):
                assert type(new_datasets[i][2][iline]) is str
            # check positional for this dataset
            if nx and nx != nol:
                raise Exception(f"Error: input dataset format is not correct for the positional list.\ndatasets[{i}]={new_datasets[i]}")
            for ix in range(nx):
                for iline in range(nol):
                    assert type(new_datasets[i][0][ix][iline]) is float
            # check value list for this dataset
            if nv and nv != nol:
                raise Exception(f"Error: input dataset format is not correct for the values list.\ndatasets[{i}]={new_datasets[i]}")
            for iv in range(nv):
                for iline in range(nol):
                    assert type(new_datasets[i][1][iv][iline]) is float
        # if we reach this line, datasets format was OK!
        for i in range(nod):
            lines = []
            for iline in range(nol):
                nx = len(new_datasets[i][0])
                nv = len(new_datasets[i][1])
                pos = []
                val = []
                extra = new_datasets[i][2]
                for ix in range(nx):
                    pos.append(new_datasets[i][0][ix])
                for iv in range(nv):
                    val.append(new_datasets[i][1][iv])
                line = ' '.join(pos + val + extra)
                lines.append(line)

            self.datasets.append(f"dataset_%02.0f" %(float(i)))
            self.lines.append(lines)

        self.nds = len(self.files) + len(self.datasets)
        self.update()


    def merge(self, inverse=False):
        self.reset()
        if self.nds < 2:
            return
        if self.nan:
            merge = [[], [], []]
            for ids in range(self.nds):
                for line in self.processed[ids][2]:
                    merge[2].append(line)
        else:
            merge = [ [[] for ix in range(self.nx)], [[] for ival in range(self.nv)], [] ]
            for ids in range(self.nds):
                nol = len(self.processed[ids][2])
                for iline in range(nol):
                    for ix in range(self.nx):
                        merge[0][ix].append(self.processed[ids][0][ix][iline])
                    for iv in range(self.nv):
                        merge[1][iv].append(self.processed[ids][1][iv][iline])
                    merge[2].append(self.processed[ids][2][iline])
        # finalize self.processed
        if inverse:
            self.processed = [calc_complementary_dataset(self.processed, merge)]
            self.titles = ['merge_inv']
        else:
            self.processed = [merge]
            self.titles = ['merge']
        self.last_process = 'merge'
        self.nds = 1


    def union(self, inverse=False):
        self.reset()
        if self.nds < 2:
            return
        if self.nan:
            union = [[], [], []]
            for ids in range(self.nds):
                for line in self.processed[ids][2]:
                    if line not in union[2]:
                        union[2].append(line)
        else:
            union = [ [[] for ix in range(self.nx)], [[] for iv in range(self.nv)], [] ]
            pos_data_uniq = []
            for ids in range(self.nds):
                nol = len(self.processed[ids][2]) # number of lines for this dataset
                for iline in range(nol):
                    pos_data = [self.processed[ids][0][k][iline] for k in range(self.nx)]
                    val_data = [self.processed[ids][1][k][iline] for k in range(self.nv)]
                    ext_data = self.processed[ids][2][iline]
                    if pos_data not in pos_data_uniq:
                        pos_data_uniq.append(pos_data)
                        for ix in range(self.nx):
                            union[0][ix].append(pos_data[ix])
                        for iv in range(self.nv):
                            union[1][iv].append(val_data[iv])
                        union[2].append(ext_data)
        # finalize self.processed
        if inverse:
            self.processed = [calc_complementary_dataset(self.processed, union)]
            self.titles = ['union_inv']
        else:
            self.processed = [union]
            self.titles = ['union']
        self.last_process = 'union'
        self.nds = 1


    def intersect(self, inverse=False):
        self.reset()
        if self.nds < 2:
            return
        if self.nan:

            intersect = [[], [], []]
            nol = len(self.processed[0][2])
            comparing_extras = []
            for ids in range(1, self.nds):
                comparing_extras.append(self.processed[ids][2])

            for iline in range(nol):
                line = self.processed[0][2][iline]
                if all(line in l for l in comparing_extras):
                    intersect[2].append(line)
        else:
            intersect = [ [[] for ix in range(self.nx)], [[] for iv in range(self.nv)], [] ]
            pos_data_datasets = [[] for ids in range(self.nds)]
            for ids in range(self.nds):
                nol = len(self.processed[ids][2]) # number of lines for this dataset
                for iline in range(nol):
                    pos_data = [self.processed[ids][0][ix][iline] for ix in range(self.nx)]
                    pos_data_datasets[ids].append(pos_data)

            first_ds_nol = len(self.processed[0][2]) # first dataset number of lines
            for iline in range(first_ds_nol):
                first_ds_pos_data = [self.processed[0][0][ix][iline] for ix in range(self.nx)]
                first_ds_val_data = [self.processed[0][1][iv][iline] for iv in range(self.nv)]
                first_ds_ext_data = self.processed[0][2][iline]
                if all(first_ds_pos_data in l for l in pos_data_datasets[1:]):
                    for ipos in range(self.nx):
                        intersect[0][ipos].append(first_ds_pos_data[ipos])
                    for ival in range(self.nv):
                        intersect[1][ival].append(first_ds_val_data[ival])
                    intersect[2].append(first_ds_ext_data)
        # finalize self.processed
        if inverse:
            self.processed = [calc_complementary_dataset(self.processed, intersect)]
            self.titles = ['intersect_inv']
        else:
            self.processed = [intersect]
            self.titles = ['intersect']
        self.last_process = 'intersect'
        self.nds = 1



    def difference(self, inverse=False):
        self.reset()
        if self.nds < 2:
            return
        if self.nan:
            difference = [[], [], []]
            comparing_extras = []
            for ids in range(1, self.nds):
                comparing_extras.append(self.processed[ids][2])
            nol = len(self.processed[0][2])
            for iline in range(nol):
                line = self.processed[0][2][iline]
                if all(line not in l for l in comparing_extras):
                    difference[2].append(line)
        else:
            difference = [[[] for ix in range(self.nx)],[[] for iv in range(self.nv)],[]]
            pos_data_datasets = [[] for ids in range(self.nds)]
            for ids in range(self.nds):
                nol = len(self.processed[ids][2]) # number of lines for this dataset
                for iline in range(nol):
                    pos_data = [self.processed[ids][0][ix][iline] for ix in range(self.nx)]
                    pos_data_datasets[ids].append(pos_data)

            first_ds_nol = len(self.processed[0][2]) # first dataset number of lines
            for iline in range(first_ds_nol):
                first_ds_pos_data = [self.processed[0][0][ix][iline] for ix in range(self.nx)]
                first_ds_val_data = [self.processed[0][1][iv][iline] for iv in range(self.nv)]
                first_ds_ext_data = self.processed[0][2][iline]
                if all(first_ds_pos_data not in l for l in pos_data_datasets[1:]):
                    for ix in range(self.nx):
                        difference[0][ix].append(first_ds_pos_data[ix])
                    for iv in range(self.nv):
                        difference[1][iv].append(first_ds_val_data[iv])
                    difference[2].append(first_ds_ext_data)
        # finalize self.processed
        if inverse:
            self.processed = [calc_complementary_dataset(self.processed, difference)]
            self.titles = ['difference_inv']
        else:
            self.processed = [difference]
            self.titles = ['difference']
        self.last_process = 'difference'
        self.nds = 1


    def add_intersect(self):
        self.reset()
        if self.nan:
            raise Exception("Error: add_intersect operation is only allowed for numerical datasets.")
        if self.nds < 2:
            return
        # store intersect dataset first
        self.intersect()
        intersect_ds = self.processed[0]
        num_intersects = len(intersect_ds[2])
        if not num_intersects:
            raise Exception("Error: found no intersect dataset to calculate 'add_intersect'.")
        self.reset()
        # lines for intersect_ds positional data
        intersect_pos_data = [[] for ii in range(num_intersects)]
        for ii in range(num_intersects):
            for ix in range(self.nx):
                intersect_pos_data[ii].append(intersect_ds[0][ix][ii])
        # initialize with zeros
        added_values = [[] for iv in range(self.nv)]
        for iv in range(self.nv):
            for ii in range(num_intersects):
                added_values[iv].append(0)
        # calculate add_intersect values
        for ii in range(num_intersects):
            candidate_intersect_pos_data = intersect_pos_data[ii]
            for ids in range(self.nds):
                nol = len(self.processed[ids][2]) # number of lines for this dataset
                for iline in range(nol):
                    pos_data = []
                    for ix in range(self.nx):
                        pos_data.append(self.processed[ids][0][ix][iline])
                    if pos_data == candidate_intersect_pos_data:
                        for iv in range(self.nv):
                            added_values[iv][ii] += self.processed[ids][1][iv][iline]
        # finalize self.processed
        self.processed = [intersect_ds]
        self.processed[0][1] = added_values
        self.titles = ['add_intersect']
        self.last_process = 'add_intersect'
        self.nds = 1


    def split_by_row(self, number, name_index_offset=0):
        self.reset()
        if self.nds != 1:
            raise Exception("Error: split dataset operation is only allowed for single file input.")
        if not self.nan:
            raise Exception("Error: split dataset operation is only allowed for NaN dataset.")
        combined_dataset = self.get_truncated()[0][2]
        split_dataset = {}
        split_indices = [x for x in range(0, len(combined_dataset), number)]
        if split_indices[-1] < len(combined_dataset):
            split_indices.append(len(combined_dataset))
        num_split_datasets = len(split_indices) - 1 # number of split datasets

        # start split_by_row
        self.titles = []
        self.processed = [[[], [], []] for ids in range(num_split_datasets)]
        for ids in range(num_split_datasets):
            split_data_lines = combined_dataset[split_indices[ids]:split_indices[ids + 1]]
            split_data_name = f"{'_'.join(split_data_lines[name_index_offset].split())}"
            self.processed[ids][2] = split_data_lines
            self.titles.append(split_data_name)
        # finalize self.processed
        self.sort = self.uniq = self.skipnan =  False
        self.nds = num_split_datasets
        self.last_process = 'split_by_row'


    def split_by_column(self, number, start_index_offset=0, name_index_offset=0):
        self.reset()
        if self.nds != 1:
            raise Exception("Error: split dataset operation is only allowed for single file input.")
        if not self.nan:
            raise Exception("Error: split dataset operation is only allowed for NaN dataset.")

        combined_dataset = self.get_truncated()[0][2]
        split_dataset = {}
        split_indices = []
        for i, line in enumerate(combined_dataset):
            if len(line.split()) == number:
                split_indices.append(i + start_index_offset)
                if split_indices[-1] < 0:
                    err = ["Error: split_by_column(): 'split_index' cannot be negative!",
                           "       (check argument 'start_index_offset')"]
                    raise Exception('\n'.join(err))

        if split_indices[-1] < len(combined_dataset):
            split_indices.append(len(combined_dataset))
        num_split_datasets = len(split_indices) - 1 # number of split datasets

        # start split_by_column
        self.titles = []
        self.processed = [[[], [], []] for ids in range(num_split_datasets)]
        for ids in range(num_split_datasets):
            split_data_lines = combined_dataset[split_indices[ids]:split_indices[ids+1]]
            split_data_name = f"{'_'.join(split_data_lines[name_index_offset].split())}"
            # self.processed[ids][2] = split_data_lines
            self.processed[ids][2] = ["", "", f"'{split_data_name}'"] + split_data_lines
            self.titles.append(split_data_name)
        # finalize self.processed
        self.sort = self.uniq = self.skipnan =  False
        self.nds = num_split_datasets
        self.last_process = 'split_by_column'


    def get_lines(self, merge=False):
        output_lines = [[] for ids in range(self.nds)]
        for ids in range(self.nds):
            nol = len(self.processed[ids][2])
            for iline in range(nol):
                pos_str = []
                for ix in range(len(self.processed[ids][0])):
                    pos_str.append( f"%{self.fmt[0]}f" %(self.processed[ids][0][ix][iline]) )
                str_line = ' '.join(pos_str)
                for iv in range(len(self.processed[ids][1])):
                    if self.processed[ids][1][iv][iline] != np.nan:
                        str_line = f"%s %{self.fmt[1]}f" %(str_line, self.processed[ids][1][iv][iline])
                    else:
                        str_line = f"{str_line} {np.nan}"
                if len(self.processed[ids][2][iline]) and not self.noextra:
                    str_line = "%s %s" %(str_line, self.processed[ids][2][iline])
                if self.nan:
                    str_line = str_line.strip()
                output_lines[ids].append(str_line)

        if merge:
            output_lines_merged = []
            for ids in range(len(output_lines)):
                output_lines_merged += output_lines[ids]
            output_lines = output_lines_merged
        
        for ids in range(len(output_lines)):
            if self.sort:
                output_lines[ids] = sorted(output_lines[ids])
            if self.uniq:
                uniq_lines = []
                for line in output_lines[ids]:
                    if line not in uniq_lines:
                        uniq_lines.append(line)
                output_lines[ids] = uniq_lines
        
        return output_lines


    def get_numericals(self, merge=False):
        if self.nan:
            raise Exception("Error: get_numericals operation is only allowed for numerical datasets")
        num_numericals = self.nx + self.nv
        numericals = []
        if self.nds == 1:
            for ix in range(self.nx):
                numericals.append(self.processed[0][0][ix])
            for iv in range(self.nv):
                numericals.append(self.processed[0][1][iv])
        else:
            for ids in range(self.nds):
                numericals.append([])
                for ix in range(self.nx):
                    numericals[ids].append(self.processed[ids][0][ix])
                for iv in range(self.nv):
                    numericals[ids].append(self.processed[ids][1][iv])
            if merge:
                numericals_merged = numericals[0]
                for ids in range(1, self.nds):
                    for inum in range(num_numericals):
                        numericals_merged[inum] += numericals[ids][inum]
                numericals = numericals_merged

        return numericals


    def get_dataset(self):
        return self.processed


    def get_truncated(self):
        # outputs a nan dataset object with header and footer lines removed
        truncated = []
        for ids in range(self.nds):
            if self.footer != 0:
                extra = self.lines[ids][self.header:-self.footer]
            else:
                extra = self.lines[ids][self.header:]
            truncated.append(
                [[ ], [ ], extra]
            #   [pos, val, extra]
            )
        return truncated


    # def anomaly(self, refmodel_dataset, calc_percent=True):
    #     # assert if self is 1D/2D/3D
    #     if len(self.x) not in [1, 2, 3]:
    #         raise Exception("Error: dataset must be either 1D/2D/3D")
    #         return
    #     # check if the input refmodel is a type Dataset
    #     try:
    #         assert isinstance(refmodel_dataset, Dataset)
    #     except AssertionError:
    #         raise Exception("Error: input reference model dataset must be a type 'gdp.io.ascii.Dataset'")
    #         return

    #     # XXX


    def update(self):
        # check types
        try:
            assert isinstance(self.files, list)
        except AssertionError:
            raise Exception("Error: argument 'files' must be a list")
        try:
            assert isinstance(self.datasets, list)
        except AssertionError:
            raise Exception("Error: argument 'datasets' must be a list")
        try:
            assert isinstance(self.header, int)
        except AssertionError:
            raise Exception("Error: argument 'header' must be an integer")
        try:
            assert isinstance(self.footer, int)
        except AssertionError:
            raise Exception("Error: argument 'footer' must be an integer")
        try:
            assert isinstance(self.x, list)
        except AssertionError:
            raise Exception("Error: argument 'x' must be a list")
        try:
            assert isinstance(self.v, list)
        except AssertionError:
            raise Exception("Error: argument 'v' must be a list")
        try:
            assert isinstance(self.skipnan, bool)
        except AssertionError:
            raise Exception("Error: argument 'skipnan' must be a boolean")
        try:
            assert isinstance(self.noextra, bool)
        except AssertionError:
            raise Exception("Error: argument 'noextra' must be a boolean")
        try:
            assert isinstance(self.fmt, list)
        except AssertionError:
            raise Exception("Error: argument 'fmt' must be a list")
        try:
            assert isinstance(self.sort, bool)
        except AssertionError:
            raise Exception("Error: argument 'sort' must be a boolean")
        try:
            assert isinstance(self.uniq, bool)
        except AssertionError:
            raise Exception("Error: argument 'uniq' must be a boolean")

        # truncate (remove header and footer lines): a nan dataset object
        self.processed = self.get_truncated()

        # update self.titles ?
        if len(self.titles) != len(self.processed):
            self.titles = []
            for i in range(len(self.files)):
                self.titles.append(os.path.split(self.files[i])[1])
            for i in range(len(self.datasets)):
                self.titles.append("dataset_%02.0f" %(float(i)))

        # is it a nan dataset?
        if len(self.x) == 0 and len(self.v) == 0:
            self.nan = True
            self.noextra = False
            self.skipnan = False
        else:
            self.nan = False

        # update/finalize dataset
        self.nx = len(self.x)
        self.nv = len(self.v)

        # initial processing of numerical datasets:
        if not self.nan:
            for ids in range(self.nds):
                pos = [[] for ix in range(self.nx)] # list of positional values
                val = [[] for iv in range(self.nv)] # list of values/data
                extra = self.processed[ids][2]
                nol = len(extra)
                for iline in range(nol):
                    extra_line_split = extra[iline].split()
                    remove_from_extra = []
                    ncol = len(extra_line_split)

                    # positional columns
                    for ix in range(self.nx):
                        pos_col = self.x[ix] - 1
                        if pos_col < 0 or pos_col >= ncol:
                            pos[ix].append(np.nan)
                            continue
                        pos_data_str = extra_line_split[pos_col]
                        try:
                            pos[ix].append(float(pos_data_str))
                        except ValueError:
                            pos[ix].append(np.nan)
                        # update remove_from_extra
                        if pos_data_str in extra_line_split:
                            remove_from_extra.append(pos_data_str)

                    # value columns
                    for iv in range(self.nv):
                        val_col = self.v[iv] - 1
                        if val_col < 0 or val_col >= ncol:
                            val[iv].append(np.nan)
                            continue
                        val_data_str = extra_line_split[val_col]
                        try:
                            val[iv].append(float(val_data_str))
                        except ValueError:
                            val[iv].append(np.nan)
                        # update remove_from_extra
                        if val_data_str in extra_line_split:
                            remove_from_extra.append(val_data_str)

                    # finalize extra for this line
                    for x in remove_from_extra:
                        if x in extra_line_split:
                            extra_line_split.remove(x)

                    extra_line = ' '.join(extra_line_split).strip()
                    self.processed[ids][2][iline] = extra_line
                self.processed[ids][0] = pos
                self.processed[ids][1] = val

            # skipnan process
            if self.skipnan:
                for ids in range(self.nds):
                    pos_skipnan = [[] for ix in range(self.nx)]
                    val_skipnan = [[] for iv in range(self.nx)]
                    extra_skipnan = []
                    nol = len(self.processed[ids][2])
                    for iline in range(nol):
                        temp = []
                        for ix in range(self.nx):
                            temp.append(self.processed[ids][0][ix][iline])
                        for iv in range(self.nv):
                            temp.append(self.processed[ids][1][iv][iline])
                        
                        if np.nan not in temp:
                            for ix in range(self.nx):
                                pos_skipnan[ix].append(self.processed[ids][0][ix][iline])
                            for iv in range(self.nv):
                                val_skipnan[iv].append(self.processed[ids][1][iv][iline])
                            extra_skipnan.append(self.processed[ids][2][iline])
                    self.processed[ids] = [pos_skipnan, val_skipnan, extra_skipnan]


    def write(self, path=None):
        if path:
            pass
        else:
            output_lines = self.get_lines(merge=True)
            for line in output_lines:
                print(line)


    def reset(self):
        current_parameters = self.parameters
        self.__init__(self.files)
        self.set(**vars(current_parameters))

###################################

#------------FUNCTIONS------------#

def calc_complementary_dataset(datasets, sub_dataset):
    # both datasets and sub_dataset must have the same number of
    # positional and value columns
    nds = len(datasets) # number of datasets
    nx = len(datasets[0][0]) # number of positional columns
    nv = len(datasets[0][1]) # number of velue columns
    complementary_dataset = [[[] for ix in range(nx)],\
                            [[] for iv in range(nv)],\
                             []]
    fmt = [".10",".10"]
    # collect sub_dataset lines
    sub_dataset_lines = []
    nol = len(sub_dataset[2]) # number of lines
    for iline in range(nol):
        line = ''
        for ix in range(nx):
            line = f"%s %{fmt[0]}f" %(line, sub_dataset[0][ix][iline])
        for iv in range(nv):
            line = f"%s %{fmt[1]}f" %(line, sub_dataset[1][iv][iline])
        line = f"%s %s" %(line, sub_dataset[2][iline])
        sub_dataset_lines.append(line.strip())

    # compare sub_dataset lines with all lines in datasets
    # and store the complementary ones
    found_complementary_lines = []
    for ids in range(nds):
        nol = len(datasets[ids][2]) # number of lines
        for iline in range(nol):
            line = ''
            for ix in range(nx):
                line = f"%s %{fmt[0]}f" %(line, datasets[ids][0][ix][iline])
            for iv in range(nv):
                line = f"%s %{fmt[1]}f" %(line, datasets[ids][1][iv][iline])
            line = f"%s %s" %(line, datasets[ids][2][iline])
            line = line.strip()
            if (line not in sub_dataset_lines) and (line not in found_complementary_lines):
                found_complementary_lines.append(line)
                for ix in range(nx):
                    complementary_dataset[0][ix].append(datasets[ids][0][ix][iline])
                for iv in range(nv):
                    complementary_dataset[1][iv].append(datasets[ids][1][iv][iline])
                complementary_dataset[2].append(datasets[ids][2][iline])

    return complementary_dataset


#########################################################

#------------REDUNDANT/NOT-USED/OLD FUNCTIONS (NUMERICAL)------------#


# def numerical_union(datasets, inverse=False):
#     # all datasets must have the same number of positional and value columns
#     nod = len(datasets) # number of numerical datasets
#     if nod < 2:
#         raise Exception("Error: Number of datasets must be larger than 2 for union operation.")
#     num_pos = len(datasets[0][0]) # number of positional columns
#     num_val = len(datasets[0][1]) # number of value columns
    
#     union = [[[] for ipos in range(num_pos)],[[] for ival in range(num_val)],[]]
    
#     pos_data_uniq = []
#     for ids in range(nod):
#         num_lines = len(datasets[ids][2]) # number of lines for this dataset
#         for iline in range(num_lines):
#             pos_data = [datasets[ids][0][k][iline] for k in range(num_pos)]
#             val_data = [datasets[ids][1][k][iline] for k in range(num_val)]
#             ext_data = datasets[ids][2][iline]
#             if pos_data not in pos_data_uniq:
#                 pos_data_uniq.append(pos_data)
#                 for ipos in range(num_pos):
#                     union[0][ipos].append(pos_data[ipos])
#                 for ival in range(num_val):
#                     union[1][ival].append(val_data[ival])
#                 union[2].append(ext_data)

#     if inverse:
#         union_inv = calc_complementary_dataset(datasets, union)
#         return union_inv
#     else:
#         return union

# #######################################

# def numerical_intersect(datasets, inverse=False):
#     # all datasets must have the same number of positional and value columns
#     nod = len(datasets) # number of numerical datasets
#     if nod < 2:
#         raise Exception("Error: Number of datasets must be larger than 2 for intersect operation.")
#     num_pos = len(datasets[0][0]) # number of positional columns
#     num_val = len(datasets[0][1]) # number of value columns

#     intersect = [[[] for ipos in range(num_pos)], [[] for ival in range(num_val)], []]

#     pos_data_datasets = [[] for i in range(nod)]
#     for ids in range(nod):
#         num_lines = len(datasets[ids][2]) # number of lines for this dataset
#         for iline in range(num_lines):
#             pos_data = [datasets[ids][0][k][iline] for k in range(num_pos)]
#             pos_data_datasets[ids].append(pos_data)

#     first_ds_nol = len(datasets[0][2]) # first dataset number of lines
#     for iline in range(first_ds_nol):
#         first_ds_pos_data = [datasets[0][0][k][iline] for k in range(num_pos)]
#         first_ds_val_data = [datasets[0][1][k][iline] for k in range(num_val)]
#         first_ds_ext_data = datasets[0][2][iline]
#         if all(first_ds_pos_data in l for l in pos_data_datasets[1:]):
#             for ipos in range(num_pos):
#                 intersect[0][ipos].append(first_ds_pos_data[ipos])
#             for ival in range(num_val):
#                 intersect[1][ival].append(first_ds_val_data[ival])
#             intersect[2].append(first_ds_ext_data)

#     if inverse:
#         intersect_inv = calc_complementary_dataset(datasets, intersect)
#         return intersect_inv
#     else:
#         return intersect

# #######################################

# def numerical_difference(datasets, inverse=False):
#     # all datasets must have the same number of positional and value columns
#     nod = len(datasets) # number of numerical datasets
#     if nod < 2:
#         raise Exception("Error: Number of datasets must be larger than 2 for difference operation.")
#     num_pos = len(datasets[0][0]) # number of positional columns
#     num_val = len(datasets[0][1]) # number of value columns

#     difference = [[[] for ipos in range(num_pos)],[[] for ival in range(num_val)],[]]

#     pos_data_datasets = [[] for i in range(nod)]
#     for ids in range(nod):
#         num_lines = len(datasets[ids][2]) # number of lines for this dataset
#         for iline in range(num_lines):
#             pos_data = [datasets[ids][0][k][iline] for k in range(num_pos)]
#             pos_data_datasets[ids].append(pos_data)

#     first_ds_nol = len(datasets[0][2]) # first dataset number of lines
#     for iline in range(first_ds_nol):
#         first_ds_pos_data = [datasets[0][0][k][iline] for k in range(num_pos)]
#         first_ds_val_data = [datasets[0][1][k][iline] for k in range(num_val)]
#         first_ds_ext_data = datasets[0][2][iline]
#         if all(first_ds_pos_data not in l for l in pos_data_datasets[1:]):
#             for ipos in range(num_pos):
#                 difference[0][ipos].append(first_ds_pos_data[ipos])
#             for ival in range(num_val):
#                 difference[1][ival].append(first_ds_val_data[ival])
#             difference[2].append(first_ds_ext_data)

#     if inverse:
#         difference_inv = calc_complementary_dataset(datasets, difference)
#         return difference_inv
#     else:
#         return difference

# #######################################

# def numerical_add_intersect(datasets):
#     # all datasets must have the same number of positional and value columns
#     nod = len(datasets) # number of numerical datasets
#     if nod < 2:
#         raise Exception("Error: Number of datasets must be larger than 2 for 'add intersect' operation.")
#     num_pos = len(datasets[0][0]) # number of positional columns
#     num_val = len(datasets[0][1]) # number of value columns

#     intersect = calc_intersect(datasets)
#     num_intersects = len(intersect[2])
#     if not num_intersects:
#         raise Exception("Error: found no intersect to calculate 'add_intersect'.")

#     # lines for intersect positional data
#     intersect_pos_data = [[] for ii in range(num_intersects)]
#     for ii in range(num_intersects):
#         for ipos in range(num_pos):
#             intersect_pos_data[ii].append(intersect[0][ipos][ii])
    
#     # initialize with zeros
#     added_values = [[] for ival in range(num_val)]
#     for ival in range(num_val):
#         for ii in range(num_intersects):
#             added_values[ival].append(0)
#             intersect_pos_data
    
#     for ii in range(num_intersects):
#         candidate_intersect_pos_data = intersect_pos_data[ii]
#         for ids in range(nod):
#             # number of lines for current datset
#             num_lines = len(datasets[ids][2]) 
#             for iline in range(num_lines):
#                 pos_data = []
#                 for ipos in range(num_pos):
#                     pos_data.append(datasets[ids][0][ipos][iline])
#                 if pos_data == candidate_intersect_pos_data:
#                     for ival in range(num_val):
#                         added_values[ival][ii] += datasets[ids][1][ival][iline]

#     add_intersect = intersect.copy()
#     add_intersect[1] = added_values

#     return add_intersect


#######################################

# ANOMALY 1D and 2D codes/operations to be implemented in class Dataset

# def read_1D_datalist(input_datalist, fmt):
#     datalist = {}
#     try:
#         fopen = open(input_datalist, 'r')
#         flines = fopen.read().splitlines()
#         fopen.close()
#     except Exception as e:
#         print(f"{e}\nError: Could not read/find input datalist: '{input_datalist}'")
#         exit(1)
#     for i, line in enumerate(flines):
#         if len(line.split()) == 3:
#             try:
#                 x = float(line.split()[0])
#                 y = float(line.split()[1])
#                 data = line.split()[2]
#             except Exception as e:
#                 print(f"{e}\nDatalist format error at line {i+1}!")
#                 print("All lines must have 3 columns: (1) lon/X, (2) lat/Y, (3) path to 1D data")
#                 exit(1)

#             if not os.path.isfile(data):
#                 raise Exception(f"Error: Could not find data at line {i+1}: '{data}'")
#                 exit(1)
#             else:
#                 key = f"%{fmt}f %{fmt}f" %(x, y)
#                 datalist[key] = data
#         else:
#             print(f"Datalist format error at line {i+1}!")
#             print("All lines must have 3 columns: (1) lon/X, (2) lat/Y, (3) path to 1D data")
#             exit(1)

#     return datalist

# #######################################

# def anomaly_1D(args):

#     outfile_orig = args.outfile
#     # read models
#     [absmodel_x], [absmodel_v], _ = read_numerical_lines(args.absmodel, args.header, args.footer,  [".10", ".10"], args.x, args.value, skipnan=True)
#     [refmodel_x], [refmodel_v], _ = read_numerical_lines(args.refmodel, 0, 0,  [".10", ".10"], [1], [2], skipnan=True)
#     # check if reference model covers the abs model positional data range
#     if min(absmodel_x) < min(refmodel_x) or max(absmodel_x) > max(refmodel_x):
#         raise Exception("Error: reference model does not fully cover the absolute model positional range:\n")
#         print(f"  absmodel range (positional column): {min(absmodel_x)} to {max(absmodel_x)}")
#         print(f"  refmodel range (positional column): {min(refmodel_x)} to {max(refmodel_x)}\n")
#         exit(1)
#     # linear interpolation and convert python lists to numpy arrays for easier processing
#     refmodel_x_interp = np.array(absmodel_x, dtype=float)
#     refmodel_v_interp = np.interp(refmodel_x_interp, refmodel_x, refmodel_v)
#     absmodel_x = np.array(absmodel_x, dtype=float)
#     absmodel_v = np.array(absmodel_v, dtype=float)
#     refmodel_x = np.array(refmodel_x, dtype=float)
#     refmodel_v = np.array(refmodel_v, dtype=float)

#     anomaly_model_x = absmodel_x
#     anomaly_model_v = absmodel_v - refmodel_v_interp # args.type == 'difference'
#     if args.type == 'percentage':
#         anomaly_model_v = (anomaly_model_v / refmodel_v_interp) * 100

#     # Calculate markers
#     markers = {}
#     if args.markers_depths == None:
#         args.markers_depths = [min(absmodel_x), max(absmodel_x)]
#     elif args.markers_depths[0] > args.markers_depths[1]:
#         args.markers_depths = args.markers_depths[::-1]

#     for mv in args.markers: # mv: marker value
#         markers[f"{mv}"] = []
#         for idep, dep in enumerate(anomaly_model_x[1:len(anomaly_model_x)+1], start=1):
#             if dep < args.markers_depths[0] or dep > args.markers_depths[1]:
#                 continue
            
#             if args.markers_case == 'both':
#                 if (anomaly_model_v[idep] <= mv and anomaly_model_v[idep-1] >= mv) \
#                 or (anomaly_model_v[idep] >= mv and anomaly_model_v[idep-1] <= mv):
#                     markers[f"{mv}"].append((anomaly_model_x[idep-1] + anomaly_model_x[idep]) / 2)
#             else:
#                 if args.markers_case == 'increase' \
#                 and anomaly_model_v[idep] >= mv and anomaly_model_v[idep-1] <= mv:
#                     markers[f"{mv}"].append((anomaly_model_x[idep-1] + anomaly_model_x[idep]) / 2)
#                 elif args.markers_case == 'decrease' \
#                 and anomaly_model_v[idep] <= mv and anomaly_model_v[idep-1] >= mv:
#                     markers[f"{mv}"].append((anomaly_model_x[idep-1] + anomaly_model_x[idep]) / 2)

#     # Generate Plot
#     fig = plt.figure(figsize=(6,7))

#     # subplot 1: absolute model and reference model profiles
#     ax1 = fig.add_subplot(121)
#     if args.invert_yaxis == 'True':
#         ax1.invert_yaxis()
#     ax1.plot(refmodel_v, refmodel_x, color='#D2691E', label="ref model")
#     ax1.scatter(refmodel_v, refmodel_x, c='#D2691E', s=5)
#     ax1.plot(absmodel_v, absmodel_x, color='#4169E1', label="abs model")
#     ax1.scatter(absmodel_v, absmodel_x, c='#4169E1', s=5)
#     ax1.legend(loc=f"{args.legend_loc}")
#     ax1.set_xlabel(' '.join(args.vlabel))
#     ax1.set_ylabel(' '.join(args.depthlabel))

#     # subplot 2: anomaly model profile and markers
#     ax2 = fig.add_subplot(122)
#     if args.invert_yaxis == 'True':
#         ax2.invert_yaxis()
#     if args.type == 'percentage':
#         anomaly_vlabel = f"{args.vlabel[0]} anomaly (%)"
#     else:
#         anomaly_vlabel = f"{args.vlabel[0]} anomaly (abs diff)"
#     ax2.plot(anomaly_model_v, anomaly_model_x, color='#4169E1')
#     ax2.scatter(anomaly_model_v, anomaly_model_x, c='#4169E1', s=5)
#     ax2.set_xlabel(anomaly_vlabel)
#     ax2.plot([0,0], ax1.get_ylim(), color='#555', linewidth=0.5, linestyle='--')
#     ax2.set_ylim(ax1.get_ylim())
#     ax2.set_yticks([])

#     # subplot 2: add markers
#     any_marker_found = False
#     for mv in markers.keys(): # marker value
#         for md in  markers[f"{mv}"]: # marker depth
#             any_marker_found = True
#             if args.type == 'percentage':
#                 marker_label = f"{mv}%"
#             else:
#                 marker_label = f"{mv} (abs diff)"
#             ax2.plot([min(anomaly_model_v), max(anomaly_model_v)], 2*[md], linestyle='--', label=marker_label)

#     if any_marker_found:
#         ax2.legend(loc=f"{args.legend_loc}")

#     plt.suptitle(f"{os.path.split(args.absmodel)[1]}")
#     plt.tight_layout()

#     # output to stdout/screen or to files

#     args.append = False
#     args.sort = False
#     args.uniq = False
#     if any_marker_found:
#         outlines_markers = ["value depth"]
#         for mv in markers.keys(): # marker value
#             for md in  markers[f"{mv}"]: # marker depth
#                 outlines_markers.append(f"{mv} {md}")
#         if outfile_orig == None:
#             args.outfile = None
#             outlines_markers.insert(0,f"Markers found for '{os.path.split(args.absmodel)[1]}'")
#             outlines_markers.append("")
#         else:
#             args.outfile = f"{os.path.splitext(outfile_orig)[0]}_markers{os.path.splitext(outfile_orig)[1]}"
#         if len(outlines_markers) == 0:
#             raise Exception("Error: Number of outputs is zero!")
#             exit(1)
#         # write_ascii_lines(outlines_markers, args)

#     outline_anomaly = [f"depth abs_model ref_model anomaly_model"]
#     for idep, dep in enumerate(anomaly_model_x):
#         outline_anomaly.append(\
#         f"%{args.fmt[0]}f %{args.fmt[1]}f %{args.fmt[1]}f %{args.fmt[1]}f" %(dep, absmodel_v[idep], refmodel_v_interp[idep], anomaly_model_v[idep]))
#     if outfile_orig == None: # output anomaly data and plot to stdout and screen
#         # anomaly data
#         args.outfile = None
#         outline_anomaly.insert(0,f"Anomaly data for '{os.path.split(args.absmodel)[1]}'")
#         if len(outline_anomaly) == 0:
#             raise Exception("Error: Number of outputs is zero!")
#             exit(1)
#         # write_ascii_lines(outline_anomaly, args)
#         # plot
#         plt.show()
#     else: # output anomaly data and plot to files
#         # anomaly data
#         args.outfile = outfile_orig
#         if len(outline_anomaly) == 0:
#             raise Exception("Error: Number of outputs is zero!")
#             exit(1)
#         # write_ascii_lines(outline_anomaly, args)
#         # plot
#         outplot = os.path.abspath(f"{os.path.splitext(outfile_orig)[0]}.{args.ext}")
#         plt.savefig(outplot, dpi=args.dpi, format=args.ext)
#     plt.close()


# #######################################

# def read_2D_datalist(input_datalist, fmt):
#     datalist = {}
#     try:
#         fopen = open(input_datalist, 'r')
#         flines = fopen.read().splitlines()
#         fopen.close()
#     except Exception as e:
#         print(f"{e}\nError: Could not read/find input datalist: '{input_datalist}'")
#         exit(1)
#     for i, line in enumerate(flines):
#         if len(line.split()) == 2:
#             try:
#                 fid = float(line.split()[0])
#                 data = line.split()[1]
#             except Exception as e:
#                 print(f"{e}\nDatalist format error at line {i+1}!")
#                 print("All lines must have 2 columns: (1) data identifier e.g. period, depth etc., (2) path to 2D data")
#                 exit(1)
            
#             if not os.path.isfile(data):
#                 raise Exception(f"Error: Could not find data at line {i+1}: '{data}'")
#                 exit(1)
#             else:
#                 key = f"%{fmt}f" %(fid)
#                 datalist[key] = data

#         else:
#             print(f"Datalist format error at line {i+1}!")
#             print("All lines must have 2 columns: (1) data identifier e.g. period, depth etc., (2) path to 2D data")
#             exit(1)

#     return datalist

# #######################################

# def anomaly_2D(args):
#     # read models
#     absmodel_x, [absmodel_v], _ = read_numerical_lines(args.absmodel, args.header, args.footer,  [".10", ".10"], args.x, args.value, skipnan=True)
#     [refmodel_x], [refmodel_v], _ = read_numerical_lines(args.refmodel, 0, 0,  [".10", ".10"], [1], [2], skipnan=True)
#     nop = len(absmodel_v)
#     if nop == 0:
#         raise Exception(f"Error: Number of points read from the absmodel is zero! Check absmodel: '{args.absmodel}'")
#         exit(1)
#     # check if reference model covers the abs model positional data range
#     if args.depth < min(refmodel_x) or args.depth > max(refmodel_x):
#         raise Exception(f"Error: reference model does not cover the absolute model depth={args.depth}\n")
#         exit(1)
#     # linear interpolation and find rederence model value at the given depth
#     refmodel_depth_interp = np.array([args.depth], dtype=float)
#     refmodel_value_interp = np.interp(refmodel_depth_interp, refmodel_x, refmodel_v)
#     # calculate anomaly model
#     if args.outfile == None:
#         output_lines = ["X/Lon  Y/Lat  Anomaly_value"]
#     else:
#         output_lines = []
#     for i in range(nop):
#         xy = f"%{args.fmt[0]}f %{args.fmt[0]}f" %(absmodel_x[0][i], absmodel_x[1][i])
#         if args.type == 'difference':
#             anom_val = f"%{args.fmt[1]}f" %(absmodel_v[i] - refmodel_value_interp[0])
#         elif args.type == 'percentage':
#             anom_val = f"%{args.fmt[1]}f" %((absmodel_v[i] - refmodel_value_interp[0]) * 100 / refmodel_value_interp[0])
#         output_lines.append(f"{xy} {anom_val}")
#     # output lines to std or file
#     args.append = False
#     args.sort = False
#     args.uniq = False
#     # write_ascii_lines(output_lines, args)

#     # print reference model value into stdout
#     if args.outfile == None:
#         print(f"\nCalculated reference model value at depth={args.depth} is {refmodel_value_interp[0]}\n")
#     else:
#         print(f"Calculated reference model value at depth={args.depth} is {refmodel_value_interp[0]}")


#------------REDUNDANT/NOT-USED/OLD FUNCTIONS (NON-NUMERICAL)------------#


# def read_dataset(non_numerical_file, header=0, footer=0):
#     try:
#         fopen = open(non_numerical_file, 'r')
#         if footer != 0:
#             lines = fopen.read().splitlines()[header:-footer]
#         else:
#             lines = fopen.read().splitlines()[header:]
#         fopen.close()
#     except Exception as e:
#         print(f"{e}")
#         exit(1)
#     for i, x in enumerate(lines):
#         lines[i] = x.strip()
#     return lines

# #######################################

# def write_to_stdout(lines,\
#                     uniq=False, sort=False):
#     len_line = []
#     lines_strip = []
#     for x in lines:
#         len_line.append(len(x))
#         lines_strip.append(x.strip())
#     lines_out = lines_strip
#     if sort:
#         lines_out, len_line = zip(*sorted(zip(lines_out, len_line)))
#         lines_out = list(lines_out)
#         len_line = list(len_line)

#     # undo strip
#     for i, x in enumerate(lines_out):
#         lines_out[i] = f"%{len_line[i]}s" %(x)

#     if uniq:
#         lines_out = uniq_lines(lines_out)
#     # write to stdout
#     for x in lines_out:
#         print(f"{x}")

# #######################################            

# def write_to_file(lines, outfile,\
#                   uniq=False, sort=False, append=False):
#     len_line = []
#     lines_strip = []
#     for x in lines:
#         len_line.append(len(x))
#         lines_strip.append(x.strip())
#     lines_out = []
#     if uniq:
#         for x in lines_strip:
#             if x not in lines_out:
#                 lines_out.append(x)
#     else:
#         lines_out = lines_strip
#     if sort:
#         lines_out, len_line = zip(*sorted(zip(lines_out, len_line)))
#         lines_out = list(lines_out)
#         len_line = list(len_line)
#     # undo strip
#     for i,x in enumerate(lines_out):
#         lines_out[i] = f"%{len_line[i]}s" %(x)
#     # write to file
#     if append:
#         fopen = open(outfile,'a')
#     else:
#         fopen = open(outfile,'w')
#     for x in lines_out:
#         fopen.write(f"{x}\n")
#     fopen.close()


# #######################################

# def calc_union(datasets):
#     nod = len(datasets) # number of datasets
#     if nod < 2:
#         print("Error! Number of datasets must be larger than 2 for union operation.")
#         exit(1)
#     union = []
#     for i in range(nod):
#         for line in datasets[i]:
#             if line not in union:
#                 union.append(line)
#     return union

# #######################################

# def calc_intersect(datasets, inverse=False):
#     nod = len(datasets) # number of datasets
#     if nod < 2:
#         print("Error! Number of datasets must be larger than 2 for intersect operation.")
#         exit(1)
#     intersect = []
#     num_lines = len(datasets[0])
#     for j in range(num_lines):
#         if all(datasets[0][j] in l for l in datasets[1:]):
#             intersect.append(datasets[0][j])

#     if inverse:
#         intersect_inv = []
#         for i in range(nod):
#             num_lines = len(datasets[i])
#             for j in range(num_lines):
#                 if datasets[i][j] not in intersect:
#                     intersect_inv.append(datasets[i][j])
#         return intersect_inv
#     else:
#         return intersect


# #######################################

# def calc_difference(datasets, inverse=False):
#     nod = len(datasets) # number of datasets
#     if nod < 2:
#         print("Error! Number of datasets must be larger than 2 for difference operation.")
#         exit(1)
#     difference = []
#     num_lines = len(datasets[0])
#     for j in range(num_lines):
#         if all(datasets[0][j] not in l for l in datasets[1:]):
#             difference.append(datasets[0][j])

#     if inverse:
#         difference_inv = []
#         for i in range(nod):
#             num_lines = len(datasets[i])
#             for j in range(num_lines):
#                 if datasets[i][j] not in difference:
#                     difference_inv.append(datasets[i][j])
#         return difference_inv
#     else:
#         return difference

# #######################################

# def split_by_nrows(combined_dataset, number, name_index_offset=0):
#     split_dataset = {}
#     split_indices = [x for x in range(0, len(combined_dataset), number)]
#     if split_indices[-1] < len(combined_dataset):
#         split_indices.append(len(combined_dataset))
#     num_split_datasets = len(split_indices) - 1 # number of split datasets
#     for i in range(num_split_datasets):
#         split_data_lines = combined_dataset[split_indices[i]:split_indices[i+1]]
#         split_data_name = f"{'_'.join(split_data_lines[name_index_offset-1].split())}"
#         split_dataset[f"{split_data_name}"] = split_data_lines
#     return split_dataset

# #######################################

# def split_by_ncols(combined_dataset, number, \
#                    name_index_offset=0,\
#                    start_index_offset=0):
#     split_dataset = {}
#     split_indices = []
#     for i, line in enumerate(combined_dataset):
#         if len(line.split()) == number:
#             split_indices.append(i + start_index_offset)
#             if split_indices[-1] < 0:
#                 print("Error: split_by_num_cols(): 'split_index' cannot be negative!")
#                 print("       (check argument 'start_index_offset')")
#                 exit(1)
#     if split_indices[-1] < len(combined_dataset):
#         split_indices.append(len(combined_dataset))
#     num_split_datasets = len(split_indices) - 1 # number of split datasets
#     for i in range(num_split_datasets):
#         split_data_lines = combined_dataset[split_indices[i]:split_indices[i+1]]
#         split_data_name = f"{'_'.join(split_data_lines[name_index_offset-1].split())}"
#         split_dataset[f"{split_data_name}"] = split_data_lines
#     return split_dataset
