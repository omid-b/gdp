#!/usr/bin/env python3

"""
 Numerical & Non-numerical ascii datasets

"""

import os
import numpy as np

class Dataset:

    def __init__(self, files=[]):
        self.nds = 0 # number of datasets
        self.nx = 0 # (datasets dimensions)
        self.nv = 0 # number of dimensions
        self.processed = []
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


    def pop(self):
        if self.nds > 0:
            self.files.pop()
            self.lines.pop()
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
        self.update()


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
                self.titles.append(os.path.split(self.files[i]))

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

        # initially consider the datasets as non-numerical (extra-only)
        for ids in range(self.nds):
            if self.footer != 0:
                extra = self.lines[ids][self.header:-self.footer]
            else:
                extra = self.lines[ids][self.header:]
            self.processed.append(
                [[ ], [ ], extra]
            #   [[x],[v]   extra]
            )

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

                    extra_this_line = ' '.join(extra_line_split).strip()
                    self.processed[ids][2][iline] = extra_this_line
                self.processed[ids][0] = pos
                self.processed[ids][1] = val

