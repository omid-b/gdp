#!/usr/bin/env python3

import os
import gdp


def test_interpolate_2D():
	input_file = os.path.abspath(os.path.join("data", "tpwt_C_p045_UTM16N.dat"))
	input_file_copy = os.path.abspath(os.path.join("data", "tpwt_C_p045_UTM16N_copy.dat"))
	ds = gdp.Dataset()
	ds.append(input_file)
	ds.append(input_file_copy)
	ds.set(x=[1,2], v=[3,4], skipnan=True)

	ds.interpolate_2D(interval=100000)
	


if __name__ == "__main__":
	test_interpolate_2D()

