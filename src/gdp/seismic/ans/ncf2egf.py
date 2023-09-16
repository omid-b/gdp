import os
import sys
import re
import shutil
import subprocess
import obspy

from . import config as ans_config
from . import proc as ans_proc

regex_events = re.compile('^[1-2][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$')


def ncf2egf_run_all(maindir, ncfs_dir, egfs_dir, components):
    cfg = ans_config.read_config(maindir)
    SAC = cfg['setting']['le_sac']
    symmetrize = is_true(cfg['ncf2egf']['chb_ncf2egf_symmetrize'])
    cut = is_true(cfg['ncf2egf']['chb_ncf2egf_cut'])
    cut_begin = float(cfg['ncf2egf']['le_ncf2egf_cut_begin'])
    cut_end = float(cfg['ncf2egf']['le_ncf2egf_cut_end'])

    bp = is_true(cfg['ncf2egf']['chb_ncf2egf_bp'])
    bp_cp1 = float(cfg['ncf2egf']['le_ncf2egf_bp_cp1'])
    bp_cp2 = float(cfg['ncf2egf']['le_ncf2egf_bp_cp2'])
    bp_poles = int(cfg['ncf2egf']['sb_ncf2egf_bp_poles'])
    bp_passes = int(cfg['ncf2egf']['sb_ncf2egf_bp_passes'])

    ncfs_dir = os.path.abspath(ncfs_dir)
    egfs_dir = os.path.abspath(egfs_dir)
    if not os.path.isdir(ncfs_dir):
        print(f"Error! 'ncfs_dir' does not exist!\nncfs_dir: {ncfs_dir}\n")
        exit(1)
    for component in components:
        uniq_xcorr_cmp = get_uniq_xcorr_cmp(ncfs_dir, component)
        print(f"  NCF2EGF: Component: {component}; #cross-correlations: {len(uniq_xcorr_cmp)}\n")

        for xcorr in uniq_xcorr_cmp:
            stacking(ncfs_dir, egfs_dir, xcorr, SAC=SAC)

            if symmetrize:
                symmetrize_sac(egfs_dir,egfs_dir,xcorr, SAC=SAC)

            if cut:
                sacfile = os.path.join(egfs_dir,xcorr)
                ans_proc.sac_cut_fillz(sacfile, sacfile, cut_begin, cut_end, SAC=SAC)

            if bp:
                sacfile = os.path.join(egfs_dir,xcorr)
                ans_proc.sac_bandpass_filter(sacfile, sacfile,
                                         bp_cp1, bp_cp2,
                                         n=bp_poles, p=bp_passes,
                                         SAC=SAC)


#################################################

def symmetrize_sac(inputDataset,outputDataset,sacfile, SAC):
    input_fn=os.path.join(inputDataset,sacfile)
    output_fn=os.path.join(outputDataset,sacfile)
    shell_cmd=["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
    shell_cmd.append(f"r {input_fn}")
    shell_cmd.append("reverse")
    shell_cmd.append(f"addf {input_fn}")
    shell_cmd.append("div 2")
    shell_cmd.append(f"w {output_fn}")
    shell_cmd.append(f"r {output_fn}")
    shell_cmd.append("w over")
    shell_cmd.append('quit')
    shell_cmd.append('EOF')
    shell_cmd = '\n'.join(shell_cmd)
    subprocess.call(shell_cmd,shell=True)


def get_uniq_xcorr_cmp(ncfs_dir, component):
    regex_xcorr = re.compile(f'^.*\_.*\.({component})$')
    uniq_xcorr_cmp = []
    for d in os.listdir(ncfs_dir):
        if regex_events.match(d) and os.path.isdir(os.path.join(ncfs_dir,d)):
            for x in os.listdir(os.path.join(ncfs_dir, d)):
                if regex_xcorr.match(x) and x not in uniq_xcorr_cmp:
                    uniq_xcorr_cmp.append(x)
    return uniq_xcorr_cmp

def get_stack_headers(ncfs_dir, xcorr):
    stack_headers = {}
    for d in os.listdir(ncfs_dir):
        if regex_events.match(d) and os.path.isdir(os.path.join(ncfs_dir,d)):
            if os.path.isfile(os.path.join(ncfs_dir, d, xcorr)):
                st = obspy.read(os.path.join(ncfs_dir, d, xcorr), format="SAC", headonly=True)
                stack_headers['delta'] = float(st[0].stats.sac.delta)
                stack_headers['npts'] = float(st[0].stats.sac.npts)
                stack_headers['b'] = float(st[0].stats.sac.b)
                stack_headers['kstnm'] = str(st[0].stats.sac.kstnm)
                stack_headers['stla'] = float(st[0].stats.sac.stla)
                stack_headers['stlo'] = float(st[0].stats.sac.stlo)
                stack_headers['stel'] = float(st[0].stats.sac.stel)
                stack_headers['evla'] = float(st[0].stats.sac.evla)
                stack_headers['evlo'] = float(st[0].stats.sac.evlo)
                stack_headers['evel'] = float(st[0].stats.sac.evel)
                stack_headers['kcmpnm'] = str(st[0].stats.sac.kcmpnm)
                stack_headers['knetwk'] = str(st[0].stats.sac.knetwk)
                return stack_headers
    return stack_headers



def stacking(ncfs_dir, egfs_dir, xcorr, SAC='/usr/local/sac/bin/sac'):
    if not os.path.isdir(egfs_dir):
        os.mkdir(egfs_dir)
    xcorrFolders = []
    for d in os.listdir(ncfs_dir):
        if regex_events.match(d) and os.path.isdir(os.path.join(ncfs_dir,d)):
            xcorrFolders.append(d)
    stack_headers = get_stack_headers(ncfs_dir, xcorr)

    nStacked = 0
    shell_cmd = ["export SAC_DISPLAY_COPYRIGHT=0", f"{SAC}<<EOF"]
    shell_cmd.append(f"fg line 0 0 delta 1 npts {stack_headers['npts']} begin {stack_headers['b']}")
    for xcorrFolder in xcorrFolders:
        if xcorr in os.listdir(os.path.join(ncfs_dir, xcorrFolder)):
            nStacked += 1
            fn = os.path.join(ncfs_dir, xcorrFolder, xcorr)
            shell_cmd.append(f"addf {fn}")
    shell_cmd.append(f'w {os.path.join(egfs_dir,xcorr)}')
    shell_cmd.append(f"q")
    shell_cmd.append('EOF')
    shell_cmd = '\n'.join(shell_cmd)
    subprocess.call(shell_cmd, shell=True)
    # write headers
    xcorrnm = int(nStacked)
    stack_headers['kevnm'] = xcorrnm
    del stack_headers['npts']
    # write sac headers
    ans_proc.write_sac_headers(os.path.join(egfs_dir,xcorr), stack_headers, SAC=SAC)
    return nStacked


def is_true(value):
    value = int(value)
    if value < 1:
        return False
    else:
        return True
