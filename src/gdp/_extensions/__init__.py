#!/usr/bin/env python3

try:
	from . import _geographic as geographic
except:
	print("hi")
	from . import geographic

try:
	from . import _funcs as funcs
except:
	print("hi")
	from . import funcs
