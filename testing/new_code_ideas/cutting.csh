#!/bin/csh
#
# $dataDir: Should contain all the event folders in 'yyjjjhhmmss' format
# $Macro_cutbp: Full path to the 'cut_bp.m' sac macro file
# $Macro_cutbp: Full path to the 'cut_bp.m' sac macro file
#----Adjustable Parameters----
set dataDir = $PWD
set Macro_cutbp = /data/home/bagherpur_o/scripts/2PLANEWV/macros/cut_bp.m
#-----------------------------
clear
cd $dataDir
echo "This script is written to use the windowing information in 'wndbbf' files for cutting the seismograms. Before running this script one should run the windowing script (windowing.csh) to make the 'wndbbf' files for each event.\n" 
if (! -e $Macro_cutbp) then
 echo " Could not find 'cut_bp.m' sac macro file!"
 exit 
endif

echo -n " Gathering some info ...\r"
if (-d cutting) then
 rm -rf cutting
 mkdir cutting
else 
 mkdir cutting
endif

ls -d */| grep -v cutting| awk -F"/" '{print $1}'|sort|uniq> cutting/events.txt
foreach event (`cat cutting/events.txt`)
 cd $event
 if (! -e wndbbf) echo "$event" >> $dataDir/cutting/wndbbfUnvailable.txt
 cd ..
end

set numEvt = `cat cutting/events.txt|wc|awk '{print $1}'`
set numUnav = `cat cutting/wndbbfUnvailable.txt|wc|awk '{print $1}'`
set numWndbbf = `expr $numEvt - $numUnav`

echo -n " Gathering some info ...Done! \n\n"

echo " Number of events: $numEvt\n Number of 'wndbbf' files found: $numWndbbf\n Number of missing 'wndbbf' files: $numUnav\n"

if ($numUnav > 0) then
 echo " Some 'wndbbf' files are missing: "
 cat cutting/wndbbfUnvailable.txt
 exit
endif

echo -n "WARNING! You cand not undo the following procedure!\nDo you want to continue? "
set uans = $<
if ($uans == yes || $uans == YES || $uans == Y || $uans == y) then
 echo ""
else if ($uans == no || $uans == NO || $uans == N || $uans == n) then
 echo "\n OK. You don't want to continue!\n"
 rm -rf cutting
 exit
else
 echo "\n You entered a wrong command!\n"
 rm -rf cutting
 exit
endif

foreach event (`cat cutting/events.txt`)
 cd $event

 foreach sacfile (`file *|awk '{print $1,$2}'|cut -d" " -f 1-2|grep -w data|awk -F":" '{print $1}'|grep -v bbf`)
setenv SAC_DISPLAY_COPYRIGHT 0
sac <<ENDSAC
setbb MacroFile $Macro_cutbp
macro %MacroFile
quit
ENDSAC
 end
 cd ..
end

