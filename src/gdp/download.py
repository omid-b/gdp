import os

def read_config(args):
	print(f"Hello from read config!")
	exit(0)


def write_config(args):
	print(f"Hello from write config!")
	maindir = os.path.abspath(args.maindir)
	if not os.path.exists(maindir):
	    os.makedirs(maindir)
	exit(0)


def events(args):
	print(f"Hello from events!")
	exit(0)


def stations(args):
	print(f"Hello from stations!")
	exit(0)


def metadata(args):
	print(f"Hello from metadata!")
	exit(0)


def mseeds(args):
	print(f"Hello from mseeds!")
	exit(0)

