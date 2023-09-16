
import os
import sys

def ans_initialize(maindir="./"):
    import config as ans_config
    import proc as ans_proc

    if not os.path.isdir(maindir):
        os.mkdir(maindir)

    if not os.path.isdir(os.path.join(maindir, '.ans')):
        os.mkdir(os.path.join(maindir, '.ans'))

    defaults = ans_config.Defaults(maindir)
    parameters = defaults.parameters()
    ans_config.write_config(maindir, parameters)
    print("Project directory was successfully initialized!\n")


def ans_configure(maindir="./"):
    from PyQt5.QtWidgets import QApplication
    import gui as ans_gui
    app = QApplication(sys.argv)
    win = ans_gui.MainWindow(maindir)
    win.show()
    sys.exit(app.exec_())
    app.exec_()


def ans_download_stations(maindir="./"):
    import download as ans_download
    ans_download.download_stations(maindir)


def ans_download_stations(maindir="./"):
    import download as ans_download
    ans_download.download_stations(maindir)


def ans_download_metadata(maindir="./"):
    import download as ans_download
    ans_download.download_metadata(maindir)


def ans_mseed2sac(mseeds_dir, sacs_dir, maindir="./"):
    import mseed2sac
    mseed2sac.mseed2sac_run_all(maindir, mseeds_dir, sacs_dir)


def ans_sac2ncf(sacs_dir, ncfs_dir, maindir="./"):
    import sac2ncf
    sac2ncf.sac2ncf_run_all(maindir, sacs_dir, ncfs_dir)

def ans_ncf2egf(ncfs_dir, egfs_dir, maindir="./"):
    import ncf2egf
    ncf2egf.ncf2egf_run_all(maindir, ncfs_dir, egfs_dir, components=['ZZ','TT','RR'])


if __name__ == "__main__":
    usage = f"Usage: python {sys.argv[0]} [init|config|download|mseed2sac|sac2ncf|ncf2egf] [*args] [maindir]"
    if len(sys.argv) == 1:
        print(usage)
        exit(0)
    elif len(sys.argv) > 2 and sys.argv[1] == 'init':
        ans_initialize(sys.argv[2])
    elif len(sys.argv) > 2 and sys.argv[1] == 'config':
        ans_configure(sys.argv[2])
    elif len(sys.argv) > 3 and sys.argv[1] == 'download' and sys.argv[2] == 'stations':
        ans_download_stations(sys.argv[3])
    elif len(sys.argv) > 3 and sys.argv[1] == 'download' and sys.argv[2] == 'metadata':
        ans_download_metadata(sys.argv[3])
    elif len(sys.argv) > 3 and sys.argv[1] == 'download' and sys.argv[2] == 'mseeds':
        ans_download_mseeds(sys.argv[3])
    elif len(sys.argv) > 4 and sys.argv[1] == 'mseed2sac':
        ans_mseed2sac(sys.argv[2], sys.argv[3], sys.argv[4])
    elif len(sys.argv) > 4 and sys.argv[1] == 'sac2ncf':
        ans_sac2ncf(sys.argv[2], sys.argv[3], sys.argv[4])
    elif len(sys.argv) > 4 and sys.argv[1] == 'ncf2egf':
        ans_ncf2egf(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(usage)
        exit(1)
