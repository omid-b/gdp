#!/bin/csh
#This script checks how close your events are to each other! Usages of this script:
# 1. you can use this script to find out how many of your seismograms can be considered as duplicates of data.
# 2. you can use this script to find out how the seismic phases of different events are interfering each other.
# !!!WARNING!!! This algorithm might not work for events before 2000.
# $mainDir: The main directory which contains the eventList file
# $eventList: Eevnts list in the format of yyjddhhmmss (e.g. 13216071521)
# $interval: Time interval to check interfrences in seconds(e.g. 86400 = A day; 3600 = An hour)
#------Adjustable Parameters---------
set mainDir = $PWD
set eventList = allEvents 
set interval = (1000 5000) #Close events time difference interval to check e.g. (1 10); Should be positive numbers seperated by an space.
#------------------------------------
#Code Block!
clear

cd $mainDir
if (-e eventList.txt)  rm -f eventList.txt
cat $eventList|sort > eventList.txt
set num_evt =  `cat eventList.txt|wc|awk '{print $1}'` #Number of events
echo "\nThis script checks how close your events are to each other!\n\n Event list file: $mainDir/$eventList"
echo " Time difference interval to check interferences: $interval[1]s to $interval[2]s"
echo " Total number of events: $num_evt\n"

echo -n "Calculating time of the events (seconds)"
if (-e time.tmp) rm -f time.tmp
@ itr = 1
while ($itr <= $num_evt)
 set evt = `cat eventList.txt|awk NR==$itr`
 set yy  = `echo $evt|cut -c 1-2`
 set jdd = `echo $evt|cut -c 3-5`
 set hh  = `echo $evt|cut -c 6-7`
 set mm  = `echo $evt|cut -c 8-9`
 set ss  = `echo $evt|cut -c 10-11`
 
 
 set time = `echo "$yy*365.25*86400 + $jdd*86400 + $hh*3600 + $mm*60 + $ss"|bc|awk -F"." '{print $1}'`
 echo $time >> time.tmp
 @ itr++ 
end
echo "...Done!"

if (-e interfered_events.tmp) rm -f interfered_events.tmp
if (-e interfered_events.txt) rm -f interfered_events.txt

echo -n "Searching for interfered events"
@ itr = 1
while ($itr < $num_evt)
 set dataValue  = `cat time.tmp| awk NR==$itr`

 @ dif = $interval[1]
 @ next_itr = `echo "$itr+1"|bc`
 while ($dif <= $interval[2] && $dif >= $interval[1] && $next_itr <= $num_evt)

  set next_dataValue  = `cat time.tmp| awk NR==$next_itr`
  set dif = `echo "$next_dataValue-$dataValue"|bc`
  #echo $itr $next_itr $dif $dataValue $next_dataValue
  if ($dif <= $interval[2] && $dif >= $interval[1]) then
   set e1 = `cat eventList.txt|awk NR==$itr`
   set e2 = `cat eventList.txt|awk NR==$next_itr`
   echo "$itr $e1">> interfered_events.tmp
   echo "$next_itr $e2">> interfered_events.tmp
  endif
  @ next_itr++

 end
 @ itr++
end
echo "............Done!"
rm -f time.tmp

if (-e interfered_events.tmp) then
 sort -k2 interfered_events.tmp|uniq > interfered_events.txt
 rm -f interfered_events.tmp
 echo "\nOutput files: 1. eventList.txt (Sorted eventlist)"
 echo "              2. interfered_events.txt (interfered eventNumber and eventName)\n"
else 
 echo "\nThere is no interference in your events for the specified time interval!\n"
 rm -f interfered_events.txt eventList.txt
endif


