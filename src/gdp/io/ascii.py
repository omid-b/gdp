#!/usr/bin/env python3

"""
 Numerical & Non-numerical ascii datasets

"""

import os
import numpy as np

class Dataset:

    def __init__(self, files=[]):
        self.processed = [] # [[pos, val, extra], ..., [pos, val, extra]]
        self.nds = 0 # number of datasets
        self.nx  = 0 # datasets dimension
        self.nv  = 0 # number of value columns
        self.files = []
        self.titles = []
        self.lines = []
        self.header = 0
        self.footer = 0
        self.x = [] # positional columns e.g. x, y, z
        self.v = [] # value columns e.g. velocity, density
        self.nan = True # nan dataset i.e. only has extra
        self.noextra = False # no extra columns
        self.skipnan = False # skip nan data
        self.fmt = [".4", ".4"] # format for positional and value columns
        self.sort = False # sort when output 
        self.uniq = False # uniq when output 
        if len(files):
            self.append(files)


    def append(self, *new_files):
        new_files = new_files[0]
        nof = len(new_files)
        for i in range(nof):
            try:
                fopen = open(new_files[i], 'r')
                lines = fopen.read().splitlines()
                fopen.close()
            except Exception as e:
                print(f"{e}")
                exit(1)
            self.files.append(new_files[i])
            self.lines.append(lines)
            self.nds += 1
        self.update()


    def reset(self):
        while self.nds:
            self.pop()
        self.append(self.files)


    def pop(self):
        if self.nds > 0:
            self.nds -= 1
        self.update()


    def options(self, **kwargs):
        for option in kwargs.keys():
            if option == 'header':
                self.header = kwargs['header']
            elif option == 'footer':
                self.footer = kwargs['footer']
            elif option == 'x':
                self.x = kwargs['x']
            elif option == 'v':
                self.v = kwargs['v']
            elif option == 'noextra':
                self.noextra = kwargs['noextra']
            elif option == 'skipnan':
                self.skipnan = kwargs['skipnan']
            elif option == 'fmt':
                self.fmt = kwargs['fmt']
                if len(kwargs['fmt']) == 1:
                    self.fmt = [kwargs['fmt'][0], kwargs['fmt'][0]]
            elif option == 'sort':
                self.sort = kwargs['sort']
            elif option == 'uniq':
                self.uniq = kwargs['uniq']
        self.update()


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


    def merge(self, inverse=False):
        if self.nds < 2:
            return
        if self.nan:
            self.union()
            merge = self.processed[0]
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

        if inverse:
            self.processed = [calc_complementary_dataset(self.processed, merge)]
            self.titles = ['merge_inv']
        else:
            self.processed = [merge]
            self.titles = ['merge']
        self.nds = 1


    def union(self, inverse=False):
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
        if inverse:
            self.processed = [calc_complementary_dataset(self.processed, union)]
            self.titles = ['union_inv']
        else:
            self.processed = [union]
            self.titles = ['union']
        self.nds = 1



    def intersect(self, inverse=False):
        if self.nds < 2:
            return
        if self.nan:

            intersect = [[], [], []]
            nol = len(self.processed[0][2])
            comparing_extras = []
            for ids in range(1, self.nds):
                comparing_extras.append(self.processed[ids][2])

            print(comparing_extras)
            for iline in range(nol):
                line = self.processed[0][2][iline]
                if all(line in l for l in comparing_extras):
                    intersect[2].append(line)
        else:
            pass

        if inverse:
            self.processed = [calc_complementary_dataset(self.processed, intersect)]
            self.titles = ['intersect_inv']
            print(self.processed)
        else:
            self.processed = [intersect]
            self.titles = ['intersect']
        self.nds = 1



    def difference(self, inverse=False):
        if self.nan:
            pass
        else:
            pass

    def add_intersect(self):
        if self.nan:
            pass
        else:
            pass

    def split(self):
        if self.nan:
            pass
        else:
            pass


    def write(self, path=None):
        output_lines = []
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
                output_lines.append(str_line)
        if self.sort:
            output_lines = sorted(output_lines)
        if self.uniq:
            uniq_lines = []
            for line in output_lines:
                if line not in uniq_lines:
                    uniq_lines.append(line)
            output_lines = uniq_lines

        if path:
            pass
        else:
            for line in output_lines:
                print(line)


    def update(self):
        # check types
        try:
            assert isinstance(self.header, int)
        except AssertionError:
            print("Error: argument 'header' must be an integer")
            exit(1)
        try:
            assert isinstance(self.footer, int)
        except AssertionError:
            print("Error: argument 'footer' must be an integer")
            exit(1)
        try:
            assert isinstance(self.noextra, bool)
        except AssertionError:
            print("Error: argument 'noextra' must be a boolean")
            exit(1)
        try:
            assert isinstance(self.skipnan, bool)
        except AssertionError:
            print("Error: argument 'skipnan' must be a boolean")
            exit(1)
        try:
            assert isinstance(self.sort, bool)
        except AssertionError:
            print("Error: argument 'sort' must be a boolean")
            exit(1)
        try:
            assert isinstance(self.uniq, bool)
        except AssertionError:
            print("Error: argument 'uniq' must be a boolean")
            exit(1)
        try:
            assert isinstance(self.x, list)
        except AssertionError:
            print("Error: argument 'x' must be a list")
            exit(1)
        try:
            assert isinstance(self.v, list)
        except AssertionError:
            print("Error: argument 'v' must be a list")
            exit(1)
        try:
            assert isinstance(self.fmt, list)
        except AssertionError:
            print("Error: argument 'fmt' must be a list")
            exit(1)

        # update self.titles ?
        if len(self.titles) != len(self.processed):
            self.titles = []
            for i in range(self.nds):
                self.titles.append(os.path.split(self.files[i])[1])

        # is it a nan dataset?
        if len(self.x) == 0 and len(self.v) == 0:
            self.noextra = False
            self.skipnan = False
            self.nan = True
        else:
            self.nan = False

        # update/finalize dataset
        self.nx = len(self.x)
        self.nv = len(self.v)

        # truncate (remove header and footer lines): a nan dataset object
        self.processed = self.get_truncated()

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
        line = ' '
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

