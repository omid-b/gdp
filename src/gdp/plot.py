import os
import sys
import numpy as np
import subprocess
import shutil
import re

from . import io
from . import stations
from . import events
from . import dependency

pkg_dir, _ = os.path.split(__file__)

def plot_features(args):
    print("Hello from plot_features!")
    from . import io
    points = []
    polygons = []

    if args.point != None:
        for point in args.point:
            io.read_point_shp(point)

    if args.polygon != None:
        for polygon in args.polygon:
            io.read_polygon_shp(polygon)


def plot_hist(args):
    import random
    import matplotlib.pyplot as plt
    import seaborn as sns
    datasets = []
    datasets_all = []
    for input_file in args.input_files:
        data = io.read_numerical_data(input_file, args.header, args.footer,
                                      args.fmt, [], args.v, skipnan=True)
        for v in data[1]:
            if len(v):
                datasets.append(v)
                datasets_all += v
            else:
                print("Error reading data column!\nHint: check argument 'v'")
                exit(1)
    nod = len(datasets)
    print(f"number of datasets: {nod}\n\n  generating histogram plot ...\n")
    # nbins
    if args.nbins == 999: # auto
        nbins = []
        for dataset in datasets:
            nbins.append(np.sqrt(len(dataset)))
        nbins = int(np.nanmin(nbins))
        if nbins > 20:
            nbins = 20
    else:
        nbins = args.nbins
    # legend
    if len(args.legend) == 0: #auto
        legend = []
        for i in range(nod):
            legend.append(f"data_{i+1}")
    else:
        legend = args.legend
    if len(legend) != nod:
        print(f"Error! Number of 'legend' items does not match the number of datasets.")
        print(f"Hint: Use underline instead of space for each legend item.")
        exit(1)
    # xlabel & ylabel & title
    xlabel = ' '.join(args.xlabel)
    ylabel = ' '.join(args.ylabel)
    title = ' '.join(args.title)
    # start plot
    bins = np.linspace(np.min(datasets_all), np.max(datasets_all), num=nbins+1).tolist()
    sns.set_style("ticks")
    sns.set_context("notebook")
    fig = plt.figure(figsize=(8,6))
    ax = plt.subplot(1,1,1)
    colors = []
    palette = sns.color_palette("Set1", nod)
    for i in range(nod):
        colors.append((palette[i][0],
                      palette[i][1],
                      palette[i][2],
                      0.75))
        ax.hist(datasets[i], label=legend[i].replace('_',' '), color=colors[i], bins=bins)

    max_y = ax.get_ylim()[1]*1.1
    if args.mean:
        for i in range(nod):
            plt.plot((np.nanmean(datasets[i]),np.nanmean(datasets[i])),(0,max_y),ls="dashed",lw=4,color=colors[i][0:3])
    if args.median:
        for i in range(nod):
            plt.plot((np.nanmedian(datasets[i]),np.nanmedian(datasets[i])),(0,max_y),ls="dashed",lw=4,color=colors[i][0:3])
    if len(title):
        plt.title(title)
    if len(xlabel):
        plt.xlabel(xlabel)
    if len(ylabel):
        plt.ylabel(ylabel)
    ax.legend(loc=2)
    plt.ylim((0,max_y))
    # save or show the plot
    if args.o:
        outfile = os.path.abspath(args.o)
        if os.path.splitext(outfile)[1] != '.pdf':
            outfile = f"{outfile}.pdf"
        plt.savefig(outfile, format="PDF", transparent=True)
        plt.close()
        print(f"output: {outfile}\n\nDone!\n")
    else:
        plt.show()





def plot_stations(input_stalist, labels=False, GMT='auto'):
    # GMT
    if GMT == 'auto':
        GMT = dependency.find_gmt_path()
    if len(GMT) == 0 or not os.path.isfile(GMT):
        print(f"Error! Could not find GMT executable:\nGMT: '{GMT}'\n")
        exit(1)

    tempdir = os.path.abspath('./.gmt')
    if not os.path.isdir(tempdir):
        os.mkdir(tempdir)

    padding_fac = 0.10
    input_stalist = os.path.abspath(input_stalist)
    maindir, fname = os.path.split(input_stalist)
    fname, _ = os.path.splitext(fname)

    stations_obj = stations.STATIONS(input_stalist, stalist_input=True)
    stalist = stations_obj.read_stalist()
    if len(stalist['lon']) == 0:
        print(f"\nError! No station is listed in the station file!\n")
        exit(1)

    print(f"station list: {input_stalist}\n")

    stalist['lon'] = np.array(stalist['lon'], dtype=float)
    stalist['lat'] = np.array(stalist['lat'], dtype=float)

    region_centre = [np.mean(stalist['lon']), np.mean(stalist['lat'])]
    prj = f"L{region_centre[0]}/{region_centre[1]}/{np.nanmin(stalist['lat'])}/{np.nanmax(stalist['lat'])}/800p"

    lat_fac = np.cos(np.deg2rad(region_centre[1]))
    if lat_fac < 0.3:
        lat_fac = 0.3
    lon_pad = (np.nanmax(stalist['lon']) - np.nanmin(stalist['lon'])) * padding_fac
    lat_pad = (np.nanmax(stalist['lat']) - np.nanmin(stalist['lat'])) * padding_fac * lat_fac
    reg = "%.2f/%.2f/%.2f/%.2f" \
    %(np.nanmin(stalist['lon'])-lon_pad, np.nanmax(stalist['lon'])+lon_pad,\
      np.nanmin(stalist['lat'])-lat_pad, np.nanmax(stalist['lat'])+lat_pad)

    # bulid plot script and run
    print(f"  generating plot ...\n")
    remove_gmt_temp(tempdir, fname)
    os.chdir(tempdir)
    gmt_script = [\
    f"{GMT} set PS_MEDIA 2000px2000p",
    f"{GMT} set GMT_VERBOSE q",
    f"{GMT} set MAP_FRAME_PEN thin,black",
    f"{GMT} set MAP_GRID_CROSS_SIZE_PRIMARY 0",
    f"{GMT} set MAP_FRAME_TYPE plain",
    f"{GMT} set MAP_FRAME_PEN 2p,black",
    f"{GMT} set FONT_ANNOT_PRIMARY 18p,Helvetica,black",
    f"{GMT} pscoast -R{reg} -J{prj} -K -P -Dh -Ba -A1000 -Givory3 -Slightcyan > {fname}.ps"]
    fopen = open(f"{fname}.dat",'w')
    for i in range(len(stalist['lon'])):
        fopen.write(f"{stalist['lon'][i]} {stalist['lat'][i]}\n")
    fopen.close()
    fopen = open(f"{fname}.tmp",'w')
    for i in range(len(stalist['lon'])):
        fopen.write(f"{stalist['lon'][i]} {stalist['lat'][i]} {stalist['net'][i]}.{stalist['sta'][i]}\n")
    fopen.close()
    if labels:
        gmt_script += [f"cat {fname}.tmp| gmt pstext -D0/-0.27i -F+f11p,Helvetica-Bold,black -R -J -P -K -O >> {fname}.ps"]
    gmt_script += [f"cat {fname}.dat | gmt psxy -R -J -K -O -P -Si15p -Groyalblue4 -Wthin,black >> {fname}.ps",
    f"echo 0 0|gmt psxy -R -J -P -O -Sc0.001p -Gblack -Wthin,black >> {fname}.ps"]
    subprocess.call("\n".join(gmt_script), shell=True)
    outfile = ps2pdf(f"{fname}.ps", maindir)
    remove_gmt_temp(tempdir, fname)
    shutil.rmtree(tempdir)
    print(f"output: '{os.path.join(maindir,outfile)}'\n\nDone!\n")



def plot_events(input_eventlist, region_lon, region_lat, GMT='auto'):
    import matplotlib.pyplot as plt
    import seaborn as sns
    # adjustable parameters
    baz_bin_size = 15

    input_eventlist = os.path.abspath(input_eventlist)
    print(f"Event list: {input_eventlist}\n")
    # GMT
    if GMT == 'auto':
        GMT = dependency.find_gmt_path()
    GMT = dependency.find_gmt_path()
    if len(GMT) == 0 or not os.path.isfile(GMT):
        print(f"Error! Could not find GMT executable:\nGMT: '{GMT}'\n")
        exit(1)

    tempdir = os.path.abspath('./.gmt')
    if not os.path.isdir(tempdir):
        os.mkdir(tempdir)

    maindir, fname = os.path.split(input_eventlist)

    fname, _ = os.path.splitext(fname)
    events_obj = events.EVENTS(input_eventlist, eventlist_input=True)
    events_list = events_obj.read_events()

    events_list['lat'] = np.array(events_list['lat'], dtype=float)
    events_list['lon'] = np.array(events_list['lon'], dtype=float)
    events_list['baz'] = np.array(events_list['baz'], dtype=float)
    events_list['gcarc'] = np.array(events_list['gcarc'], dtype=float)

    outfiles = []
    if len(events_list['lon']) == 0:
        print(f"\nError! No event is listed in the events file!\n")
        exit(1)

    # PLOT 1 of 2: event locations
    print(f"  generating plot 1 of 2 ...")
    remove_gmt_temp(tempdir, fname)
    os.chdir(tempdir)
    gmt_script = [\
    f"{GMT} set PS_MEDIA 600x600",
    f"{GMT} set GMT_VERBOSE q",
    f"{GMT} set MAP_FRAME_PEN thin,black",
    f"{GMT} set MAP_GRID_CROSS_SIZE_PRIMARY 0",
    f"{GMT} pscoast -Rg -JE{region_lon}/{region_lat}/6.5i -K -P -Di -B5555 -A5000 -Givory3 -Vq > {fname}.ps"]
    # tectonic boundaries
    for x in os.listdir(os.path.join(pkg_dir,'data','tectonics')):
        if re.search('dat$',x):
            gmt_script += [f"cat {os.path.join(pkg_dir,'data','tectonics',x)}|gmt psxy -R -J -O -P -K -Wthick,azure3 >> {fname}.ps"]
    gmt_script += [\
    f"{GMT} grdmath -Vq -Rg -I120m {region_lon} {region_lat} SDIST KM2DEG = {fname}.tmp",
    f"{GMT} grdcontour {fname}.tmp -A60 -L0/170 -C20 -J -P -O -K >> {fname}.ps"]
    # tectonics
    fopen = open(f"{fname}.dat",'w')
    for i in range(len(events_list['lon'])):
        fopen.write(f"{events_list['lon'][i]} {events_list['lat'][i]}\n")
    fopen.close()
    gmt_script += [f"cat {fname}.dat | gmt psxy -R -J -K -O -P -Sc6p -Gblack -Wthin,black >> {fname}.ps",
    f"echo {region_lon} {region_lat}|gmt psxy -R -J -O -P -Sa16p -Gred -Wthin,darkred >> {fname}.ps"]
    subprocess.call("\n".join(gmt_script), shell=True)
    outfiles.append( ps2pdf(f"{fname}.ps", maindir) )
    remove_gmt_temp(tempdir, fname)
    # PLOT 2 of 2: event stats
    print(f"  generating plot 2 of 2 ...\n")
    plt.figure(figsize=(10,5))
    ax1=plt.subplot2grid((5, 11), (0, 0),rowspan=5, colspan=5)
    plt.hist(events_list['gcarc'],edgecolor="#0072BB", color="#1183CC")
    plt.xlabel('GCArc distance (degrees)')
    ax2=plt.subplot2grid((5, 11),(0, 6),rowspan=5,colspan=5,projection='polar')
    ax2.set_theta_zero_location("N")
    ax2.set_theta_direction(-1)
    degrees=np.asarray(events_list['baz'])
    radians=np.asarray(np.deg2rad(events_list['baz']))
    a, b=np.histogram(degrees, bins=np.arange(0, 360+baz_bin_size, baz_bin_size))
    centres=np.deg2rad(np.ediff1d(b)//2 + b[:-1])
    bars=ax2.bar(centres, a, bottom=0,width=np.deg2rad(baz_bin_size), edgecolor="#0072BB", color="#1183CC")
    plt.xlabel('Backazimuths (degrees)')
    plt.tight_layout()
    plt.savefig(os.path.join(maindir,f"{fname}-histograms.pdf"),dpi=300)
    outfiles.append(f"{fname}-histograms.pdf")
    shutil.rmtree(tempdir)
    print(f"outputs: {', '.join(outfiles)}\n\nDone!\n")


def remove_gmt_temp(fdir, fname):
    flist = [f"{fname}.tmp",
    f"{fname}.eps",f"{fname}.epsi",
    "gmt.conf","gmt.history"]
    for f in flist:
        if os.path.isfile(os.path.join(fdir,f)):
            os.remove(os.path.join(fdir,f))


def ps2pdf(input_ps, outdir):
    fname, _ = os.path.splitext(os.path.split(input_ps)[1])
    fname_ext_out = f"{fname}.pdf"
    if sys.platform in ["linux","linux2","darwin"]:
        # method 1: works on MacOS and Ubuntu
        if subprocess.call('ps2eps --version',shell=True,
        stderr=subprocess.STDOUT,
        stdout=subprocess.DEVNULL) == 0:
            script = [f"ps2eps {fname}.ps --quiet -f",
            f"epstopdf {fname}.eps --outfile={os.path.join(outdir,fname)}.pdf --quiet"]
            subprocess.call('\n'.join(script), shell=True)
        # method 2: works on CentOS
        if subprocess.call('ps2epsi --version',shell=True,
        stderr=subprocess.STDOUT,
        stdout=subprocess.DEVNULL) == 0\
        and not os.path.isfile(f"{fname}.eps"):
            script = [f"ps2epsi {fname}.ps {fname}.epsi",
            f"epstopdf {fname}.epsi --outfile={os.path.join(outdir,fname)}.pdf"]
            subprocess.call('\n'.join(script), shell=True)
    if not os.path.isfile(os.path.join(outdir,f'{fname}.pdf')):
        shutil.copyfile(input_ps,os.path.join(outdir,fname_ext_out))
        fname_ext_out = f"{fname}.ps"
    return fname_ext_out

