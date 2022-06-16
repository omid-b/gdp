
import os
import re

def gen_metadata_list(metadata_dir):
    metadata_list = {}
    regex_pattern = '^.*\..*\..*$'
    regex = re.compile(regex_pattern)
    for x in os.listdir(metadata_dir):
        if regex.match(x) and len(x.split('.')) == 3:
            metadata_list[f'{x}'] = os.path.join(metadata_dir, x)
    return metadata_list

def writehdr(args):
    metadata_dir = os.path.abspath(args.metadata)
    print(f"metadata directory: {metadata_dir}\n")
    print(gen_metadata_list(metadata_dir))
    exit(0)

    
def remresp(args):
    print("Hello from remresp!")
    exit(0)

    
def decimate(args):
    print("Hello from decimate!")
    exit(0)

    
def bandpass(args):
    print("Hello from bandpass!")
    exit(0)

    
def cut(args):
    print("Hello from cut!")
    exit(0)

    
def detrend(args):
    print("Hello from detrend!")
    exit(0)

    
def remchannel(args):
    print("Hello from remchannel!")
    exit(0)

    