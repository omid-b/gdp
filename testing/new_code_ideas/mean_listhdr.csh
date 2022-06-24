#!/bin/csh
#This script is to calculate mean values of sac file headers for each event
#Update: Sep 28, 2017
#------Adjustable Parameters-------#
set mainDir = $PWD #should contain all event directories
set headers = "BAZ GCARC" #All desired sac headers to calculate average; Note: The result will be sorted based on the first specified header. 
#----------------------------------#
#Code block!
clear
cd $mainDir
echo "This script is to calculate mean values of sac file headers for each event."
if (-e events.tmp) rm -f events.tmp
if (-e headers.txt) rm -f headers.txt
if (-e mean_listhdr_results.txt) rm -f mean_listhdr_results.txt
if (-e mean_listhdr_results.tmp) rm -f mean_listhdr_results.tmp
ls -d */|awk -F"/" '{print $1}' > events.tmp

set nEvents = `cat events.tmp|wc|awk '{print $1}'`
echo "\nMain Directory: $mainDir\nNumber of event folders: $nEvents\nSpecified headers: $headers"

echo -n "\nDo you want to continue (y/n)? "
set ansin = $<
if ($ansin == y || $ansin == yes) then
   echo ''
else if ($ansin == n || $ansin == no) then
   echo 'OK, You did not want to continue!\n'
   rm -f events.tmp
   exit
else
   echo 'You entered a wrong input!\n'
   rm -f events.tmp
   exit
endif
@ itrEvt =0
foreach event (`cat events.tmp`)
 @ itrEvt++
 cd $event
 if (-e sacList.tmp) rm -f sacList.tmp
 file *|awk '{print $1,$2}'|cut -d" " -f 1-2|grep -w data|awk -F":" '{print $1}'|sort|uniq > sacList.tmp
 if (-e sacHeaders.tmp) rm -f sacHeaders.tmp
 saclst `echo $headers` f `cat sacList.tmp` > sacHeaders.tmp
 
 set nCol = `awk NR==1 <sacHeaders.tmp|wc| awk '{print $2}'`
 set nHdr = `echo "$nCol-1"|bc` #(Number of columns-1)
 set nLin = `cat sacHeaders.tmp|wc|awk '{print $1}'`
 

 set hdrIndex = `seq 1 1 $nHdr`
 set sum1 = `echo $hdrIndex`

 foreach index ($hdrIndex)
  set sum1[$index] = 0
 end

 @ itr = 1
 while ($itr <= $nLin)
  echo -n " Working on event $itrEvt of $nEvents    \r"
  set hdrData = `awk NR==$itr < sacHeaders.tmp|sed -re 's,\s+, ,g'|cut -d" " -f 2-$nCol`
  @ itr2 = 1
  while ($itr2 <= $nHdr)
   set sum1[$itr2] = `echo "scale=4;$sum1[$itr2]+$hdrData[$itr2]"|bc`
   @ itr2++
  end
  @ itr++
 end

 foreach index ($hdrIndex)
  set sum1[$index] = `echo "scale=4;$sum1[$index]/$nLin"|bc`
 end
 
 cd ..
 cat $event/sacHeaders.tmp|sed -re 's,\s+, ,g'|sed 's/ /   /g'>> headers.txt
 set nSac = `echo "$itr-1"|bc`
 echo $nSac $event $sum1>> mean_listhdr_results.tmp
 rm -f $event/sacHeaders.tmp $event/sacList.tmp
end

cat mean_listhdr_results.tmp|sort -n -k3|sed 's/ / /g'> mean_listhdr_results.txt
rm -f mean_listhdr_results.tmp

echo -n " Working on event $itrEvt of $nEvents...Done!\r"
echo "\n\n Outputs: 1. headers.txt              <SacFile   $headers>"
echo "          2. mean_listhdr_results.txt <#SacFiles EventName $headers>\n"

rm -f events.tmp
