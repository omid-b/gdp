#/bin/csh
#Coded by: omid.bagherpur@gmail.com
#UPDATE: 10 May 2019
#Run the sctipt to see the usage!
#===Adjustable Parameters====#
set output_folder = results-May2019/saito-sm30-AK135-PS2
set data_gridding_interval = 0.05 #in degrees
#============================#
clear
printf "This script generates the data required for plotting cross sections over a tomography model using GMT.\n\n" 
printf "The inputs include:\n 1) scattered datasets at different depths\n 2) A polygon data that defines the region of interest\n 3) Profiles (xy track)\n\n"

#---check input data---#
if ($#argv != 3) then
  printf "Error!\n USAGE: csh crosssection-genData.csh <datalist> <mask polygon> <profiles>\n\nInput data format (columns):\n\n   <datalist>  : 1)Depth,  2)Scattered data location\n <mask polygon>: 1)Lon,    2)Lat\n   <profiles>  : 1)profile (xy track) location \n\n"
  exit
else
  set datalist = $1
  set polygon  = $2
  set profiles = $3
endif

if (! -e $datalist) then
  printf "Error!\n Could not find <datalist>: '$datalist'\n"
else
  set depth_A = `awk '{print $1}' $datalist| sort -n |awk 'NR==1'`
  set depth_Z = `awk '{print $1}' $datalist| sort -nr|awk 'NR==1'`
  set nData = `cat $datalist|wc -l`
  set ncol = `awk '{print NF}' $datalist|sort -n|uniq|awk 'NR==1'`
  if ($ncol != 2) then
    printf " Error in <datalist> format; number of columns should be 2:\n 1)Depth,  2)Scattered data location\n\n"
    exit
  endif
endif

if (! -e $polygon) then
  printf "Error!\n Could not find <mask polygon>: '$polygon'\n"
else
  set ncol = `awk '{print NF}' $polygon|sort -n|uniq|awk 'NR==1'`
  if ($ncol != 2) then
    printf " Error in <mask polygon> format; number of columns should be 2:\n 1)Lon,  2)Lat\n\n"
    exit
  else
  	set polygon_lon1 = `awk '{print $1}' $polygon|sort -n |awk 'NR==1'`
  	set polygon_lon2 = `awk '{print $1}' $polygon|sort -nr|awk 'NR==1'`
  	set polygon_lat1 = `awk '{print $2}' $polygon|sort -n |awk 'NR==1'`
  	set polygon_lat2 = `awk '{print $2}' $polygon|sort -nr|awk 'NR==1'`
  endif
endif

if (! -e $profiles) then
  printf "Error!\n Could not find <profiles>: '$profiles'\n"
else
  set nProfiles = `cat $profiles|wc -l`
  set ncol = `awk '{print NF}' $profiles|sort -n|uniq|awk 'NR==1'`
  if ($ncol < 1) then
    printf " Error! <profiles> should at least have 1 column.\n\n"
    exit
  endif
endif

touch pstart.tmp; rm -f pstart.tmp; touch pstart.tmp
touch pend.tmp  ; rm -f pend.tmp  ; touch pend.tmp

foreach profile (`cat $profiles|awk '{print $1}'`)
  if (! -e $profile) then
    printf "Error! Could not find '$profile' in <profiles>\n\n"
    rm -f pend.tmp pstart.tmp
    exit
  endif

  head -n1 $profile >> pstart.tmp
  tail -n1 $profile >> pend.tmp
end

set profiles_slon1 = `awk '{print $1}' pstart.tmp|sort -n |awk 'NR==1'`
set profiles_slon2 = `awk '{print $1}' pstart.tmp|sort -nr|awk 'NR==1'`
set profiles_slat1 = `awk '{print $2}' pstart.tmp|sort -n |awk 'NR==1'`
set profiles_slat2 = `awk '{print $2}' pstart.tmp|sort -nr|awk 'NR==1'`
set profiles_elon1 = `awk '{print $1}' pend.tmp|sort -n |awk 'NR==1'`
set profiles_elon2 = `awk '{print $1}' pend.tmp|sort -nr|awk 'NR==1'`
set profiles_elat1 = `awk '{print $2}' pend.tmp|sort -n |awk 'NR==1'`
set profiles_elat2 = `awk '{print $2}' pend.tmp|sort -nr|awk 'NR==1'`
rm -f pend.tmp pstart.tmp
#-------------------#
#find profile region
if (`echo "$profiles_slon1 < $profiles_elon1"|bc`) then
  set profiles_lon1 = $profiles_slon1
else
  set profiles_lon1 = $profiles_elon1
endif

if (`echo "$profiles_slon2 > $profiles_elon2"|bc`) then
  set profiles_lon2 = $profiles_slon2
else
  set profiles_lon2 = $profiles_elon2
endif

if (`echo "$profiles_slat1 < $profiles_elat1"|bc`) then
  set profiles_lat1 = $profiles_slat1
else
  set profiles_lat1 = $profiles_elat1
endif

if (`echo "$profiles_slat2 > $profiles_elat2"|bc`) then
  set profiles_lat2 = $profiles_slat2
else
  set profiles_lat2 = $profiles_elat2
endif
#-------------------#
printf "  Number of scattered datasets: $nData\n  Number of profiles: $nProfiles\n  Profiles region:\n    Lon[%10.6f, %10.6f]  Lat[%10.6f, %10.6f]\n  Mask polygon region:\n    Lon[%10.6f, %10.6f]  Lat[%10.6f, %10.6f]\n  Grid spacing: %.2f\n\n Do you want to continue (y/n)? " $profiles_lon1 $profiles_lon2 $profiles_lat1 $profiles_lat2 $polygon_lon1 $polygon_lon2 $polygon_lat1 $polygon_lat2 $data_gridding_interval

set uans = $<
if ($uans != 'y') then
  printf "\nExit program!\n\n"
  exit
else
  printf "\n\n"
endif

foreach data (`cat $datalist|awk '{print $2}'`)
  if (! -e $data) then
    printf "\nError! Could not find '$data'\n\n"
    exit
  endif
end

if (-d $output_folder) then
  rm -rf $output_folder
  mkdir  $output_folder
else 
  mkdir  $output_folder
endif

cat $datalist|sort -nk1|uniq > datalist.tmp
set datalist = datalist.tmp
#-------------------#
#  Main code block!
#-------------------#
#find the map region and projection: 
if (`echo "$profiles_lon1 < $polygon_lon1"|bc`) then
  set map_lon1 = $profiles_lon1
else
  set map_lon1 = $polygon_lon1
endif

if (`echo "$profiles_lon2 > $polygon_lon2"|bc`) then
  set map_lon2 = $profiles_lon2
else
  set map_lon2 = $polygon_lon2
endif

if (`echo "$profiles_lat1 < $polygon_lat1"|bc`) then
  set map_lat1 = $profiles_lat1
else
  set map_lat1 = $polygon_lat1
endif

if (`echo "$profiles_lat2 > $polygon_lat2"|bc`) then
  set map_lat2 = $profiles_lat2
else
  set map_lat2 = $polygon_lat2
endif

set map_lon0 = `echo "$map_lon1 $map_lon2"|awk '{print ($1+$2)/2}'`
set map_lat0 = `echo "$map_lat1 $map_lat2"|awk '{print ($1+$2)/2}'`

set reg = "$map_lon1/$map_lon2/$map_lat1/$map_lat2"
set prj = "L$map_lon0/$map_lat0/$map_lat1/$map_lat2/900p"

#find grid spacing
set first_data = `awk 'NR==1' $datalist|awk '{print $2}'`
set p1x = `awk 'NR==1' $first_data|awk '{print $1}'`
set p1y = `awk 'NR==1' $first_data|awk '{print $2}'`
set p2x = `awk 'NR==2' $first_data|awk '{print $1}'`
set p2y = `awk 'NR==2' $first_data|awk '{print $2}'`

set grdSpacing = `echo "$data_gridding_interval"|awk '{printf "%.4fd",$1}'`

#copy all data to the result folder
@ i=0
while ($i < $nData)
  @ i++
  printf "  Copying data: %d of %d\r" $i $nData

  set depth = `awk "NR==$i" $datalist|awk '{printf "%04d",$1}'`
  set data  = `awk "NR==$i" $datalist|awk '{print $2}'`
  cp $data $output_folder/data_$depth.dat
end

@ i=0
while ($i < $nProfiles)
  @ i++
  set profile = `awk "NR==$i" $profiles|awk '{print $1}'`
  set fn = `echo $i|awk -v out=$output_folder '{printf "%s/profile_%04d.dat",out,$1}'`
  cp $profile $fn
end
cp $polygon $output_folder/polygon.dat
cp $profiles $output_folder/profiles_list.dat
rm -f $datalist
printf "  Copying data ............... Done.          \n"

cd $output_folder

#make mask grid
printf "  Generating mask grid \r"
gmt grdmask polygon.dat -R$reg -I$grdSpacing -NNaN/1/1 -Gmask.nc
printf "  Generating mask grid ....... Done.\n"

#grid data

@ i=0
foreach data (`ls|grep data_`)
  @ i++
  printf "  Gridding data: %d of %d\r" $i $nData
  set depth = `echo $data|awk -F"_" '{print $2}'|awk -F"." '{printf "%04d",$1}'`
  gmt blockmean $data -R$reg -I$grdSpacing > bm.tmp
  gmt surface bm.tmp -I$grdSpacing -R$reg -T0 -Ggrid.tmp
  gmt grdmath mask.nc grid.tmp MUL = grid_$depth.nc
end
rm -f {bm,grid}.tmp mask.nc
printf "  Gridding data .............. Done.\n"


#sample the grids
@ pc=0
foreach profile (`ls|grep profile_`)
  @ pc++
  touch dist.tmp
  rm -f dist.tmp
  set prf_num = `printf "%04d" $pc`
  printf "  Extracting profile data: $pc of $nProfiles                   \r"
  #make dist.tmp
  set nSample = `cat $profile|wc -l`
  set p0x = `awk 'NR==1' $profile|awk '{print $1}'`
  set p0y = `awk 'NR==1' $profile|awk '{print $2}'`
  @ i=0
  while ($i < $nSample)
    @ i++
    set px = `awk "NR==$i" $profile|awk '{print $1}'`
    set py = `awk "NR==$i" $profile|awk '{print $2}'`
    set dist = `echo $p0x $p0y|gmt mapproject -G"$px/$py+uk"|awk '{printf "%.0f",$3}'`
    echo $dist >> dist.tmp
  end
  
  #extract data along the profile track
  @ i=0
  foreach grid (`ls|grep grid_`)
    @ i++
    printf "  Extracting profile data: $pc of $nProfiles (Grid $i of $nData)\r"
    set depth = `echo $grid|awk -F"_" '{print $2}'|awk -F"." '{print $1}'`
    gmt grdtrack $profile -G$grid -N|awk -v dep=$depth '{print dep,$3,$1,$2}' > profileData.tmp
    paste dist.tmp profileData.tmp|awk '{printf "%4d %4d %14s %.8f %.8f\n",$1,$2,$3,$4,$5}' >> crosssection_$prf_num.dat
  end
end
printf "  Extracting profile data .... Done.                      \n"

printf "\n Finished.\n\n"
