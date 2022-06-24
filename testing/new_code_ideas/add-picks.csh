#!/bin/csh

# Usage: csh add-picks.csh <PATH> <list> where PATH is the directory containing all
# the station or event directories with SAC data files.
# addpicks is a script that reads the SAC headers gcarc & evdp, sends the information
# to a pair of executables ("ttimes_new" and "findit_fd") which predict the P & S
# arrival times and place the information in the SAC header.

set masterpath=$1
set dlist=$2

foreach evtorstn (`cat $dlist`)
/usr/local/bin/addpicks $masterpath/$evtorstn
end

