# ***gdp*: Geophysical Data Processing**

*gdp* provides a set of tools that are available through command-line-interface (CLI) to process and/or convert common geophysical data types. 

:heavy_check_mark: *gdp* is here to stay and get better. Please share your thoughts and ideas.

:heavy_check_mark: Feel free to share and modify the source codes.

:heavy_check_mark: *gdp* has been successfully tested on Python 3.x versions.

# Requirements (installation prerequisites)

*gdp* uses GMT (generic mapping tools ) and SAC (seismic analysis codes) in some of the tools. Hence, these software must be already installed if one wish to use such tools. Os-specific prerequisites are described below.

Ubuntu/Debian:

Note that the version of binary bindings for GDAL (could be installed using pip) and libgdal-dev must match.

```bash
$ sudo apt-get install libbz2-dev
$ sudo apt-get install python3-tk
$ sudo apt install libgdal-dev
$ pip install gdal
```

Fedora:

```bash
$ sudo yum install bzip2-devel
$ sudo yum install python3-tkinter
$ pip install gdal
```

MacOS:

Note that installing requirements for tkinter on MacOS is python version specific.

```bash
$ brew install python-tk@3.10
$ brew install gdal
$ pip install gdal
```

# Installation

In order to install the latest (under development) version:

```bash
$ pip install git+https://github.com/omid-b/gdp.git
```

To install the last stable version from PyPI:

```bash
$ pip install gdp
```

# Currently available modules

| **Tool/Module** | **Description** |
|----------|-----------------|
|cat       |concatenate/reformat numerical or non-numerical data|
|union     |generate the union of input data files|
|intersect |generate the intersect of input data files|
|difference|generate the difference of input data files|
|split     |split a concatenated dataset into multiple data files|
|min       |calculate minimum of values in numerical column(s)|
|max       |calculate maximum of values in numerical column(s)|
|sum       |calculate summation of values in numerical column(s)|
|mean      |calculate mean of values in numerical column(s)|
|median    |calculate median of values in numerical column(s)|
|std       |calculate standard deviation of values in numerical column(s)|
|add       |add value columns of two or more ascii data files|
|pip       |output points inside/outside a polygon (ray tracing method)|
|gridder   |gridding/interpolation of 2D/map data with Gaussian smoothing applied|
|chull     |convex-hull / minimum bounding polygon for a set of points|
|shp2dat   |convert GIS shape files (point/polygon) to ascii data|
|nc2dat    |convert nc data to dat/ascii|
|dat2nc    |convert gridded ascii data to nc format|
|1Dto2D    |Combine/convert 1D datasets into 2D datasets. Example use cases: (1) building phase velocity map datasets from point/1D dispersion curve datasets, (2) building shear velocity map datasets from 1D shear velocity profiles.|
|2Dto1D    |Extract/convert 2D datasets into 1D datasets. Example use cases: (1) extracting point dispersion curves from phase velocity maps, (2) extracing 1D shear velocity profiles from shear velocity map datasets|
|georef    | image georeferencing module |
|seismic   |seismic data acquisition and processing module set (see below)|
|plot      |plot module set (requires gmt; see below)|

- *seismic* module set includes the following tools:

  1. *download init*: initialize current directory for seismic data acquisition. It outputs a config file (i.e. 'download.config') that is used by the 4 following tools.
  2. *download events*: download list of events according to the list of datacenters (specified in download.config)
  3. *download stations*: download list of stations according to the list of datacenters (specified in download.config)
  4. *download metadata*: download station metadata (xml) according to stations.dat
  5. *download mseeds*: download mseed datafiles based
  6. *writehdr*: update sac headers using xml metadata (obspy method)
  7. *remresp*: remove sac file instrument response using xml metadata (obspy method)
  8. *resample*: resample sac timeseries using obspy method
  9. *bandpass*: apply bandpass filter to sac files (sac method)
  10. *cut*: cut sac timeseries (sac method)
  11. *remchannel*: remove extra channels
  12. *sws init*: initialize shear-wave-splitting project by writing arrivals info into sac headers and making copies

- *plot* module set includes the following tools:

  1. *plot station*: plot station map from previously downloaded station list
  2. *plot events*: plot event distribution map and related statistics
  3. *plot hist*: generate combined histogram plots (customizable)
  4. *plot features*: quickly visualize geographical features on a map. Accepted input data types include points and polygons (both ascii and shape files), and GeoTiff


# Example commands

Some example *gdp* commands are explained below:

```bash
$ gdp cat file* -x 1 2 -v 5 3 4 --header 2 --footer 4 --fmt .2 .4 --sort --uniq --noextra -o concatenated.txt
```
> **Description:** This command will concatenate files in current directory matching names 'files\*'. While reading, 2 header lines and 4 footer lines will be omitted. Positional columns are the first and second columns (-x 1 2), and value/numerical columns are \[5 3 4\]. Positional columns will be printed in %.2f format, and value columns will be printed in %.4f.	If files have extra (non-numerical) columns other than the first 5 columns,	'--noextra' will cause not printing them. Flag '-o' can be used to set the output file name and if not specified, the results will be printed to standard output.Many of these flags are also common for the following commands.


```bash
$ gdp union file_1.dat file_2.dat file_3.dat
```
> **Description:** Output union of a set of numerical data files (two or more) while considering positional columns (default=\[1 2\]) and value columns as \[3\] (defaults; these could be modified using '-x' '-v' flags).


```bash
$ gdp intersect file_1.dat file_2.dat file_3.dat
```
> **Description:** Output intersect of a set of numerical data files (two or more) considering positional columns	(similar positional columns that could be specified using '-x' flag; the value of the first file will be the output). Note that the first value of the flag '--fmt' will be important here.


```bash
$ gdp difference file_1.dat file_2.dat file_3.dat
```
> **Description:** Output difference of a set of numerical data files (two or more) considering positional columns. In this case, data points that are unique to 'file_1.dat' will be the output results.



```bash
$ gdp split dataset.dat --method ncol --number 4 --start -2 --name 3 -o outdir
```
> **Description:** This command is useful to split/unmerge a concatenated dataset ('dataset.dat'). Either of two methods can be selected: (1) nrow: split based on a fixed number of rows, (2) ncol: split based on a row that has a unique number of columns as an identifier. In case of method 'ncol' above: '--number 4' specifies that the row with unique number of columns has 4 columns (reference row); '--start -2' specifies the start line or row offset relative to the reference line; '--name 3' specifies the row offset relative to 'start line' that will be used for output file names;	'-o outdir' specifies output directory (it can be omitted for printing to the standard output)


```bash
$ gdp min  *.xyz -v 1 2 3
$ gdp max  *.xyz -v 1 2 3
$ gdp sum  *.xyz -v 1 2 3
$ gdp mean  *.xyz -v 1 2 3
$ gdp median  *.xyz -v 1 2 3
$ gdp std  *.xyz -v 1 2 3
```
> **Description:** Output min, max, sum, mean, median, or std of the three first columns in \*.xyz files.


```bash
$ gdp pip  --point *.xyz  --polygon polygon.dat
$ gdp pip  --point *.xyz  --polygon polygon.dat -i
```
> **Description:** Only output points inside or outside ('-i') of the given polygon. Alternatively '--xrange' and '--yrange' flags could be used to define the polygon.


```bash
$ gdp gridder vs_model/depth* --spacing 0.2 --smoothing 50 --polygon polygon.dat -o outdir
```
> **Description:** This command will perform gridding (2D interpolation) to the input xyz format data files. In case of the above command: '--spacing 0.2' specifies that grid spacing along both longitude and latitude is 0.2 degrees (two values can be given as well; \[lon_spacing, lat_spacing\]); '--smoothing 50' sets a 50 km Gaussian smoothing to the output data; '--polygon polygon.dat' is optional: if given, only points inside the given polygon will be printed out.


```bash
$ gdp chull points.xy -x 2 1 --smooth 10 -o polygon.dat 
```
> **Description:**  This command will output the polygon enclosing the points in 'points.xy' (convex-hull problem). Flag -x specifies the column numbers for longitude and latitude information respectively. Flag '--smooth 10' specifies that the output polygon will be smoothed using 10 Bezier points between each output point pairs. Using flag '-o', the output results will be written into 'polygon.dat'.

```bash
$ gdp shp2dat --point points.shp --polygon polygons.shp -o ./
```
> **Description:**  Convert GIS shape files (point/polygon) to ascii format. This command will output the results into the following directory.

```bash
$ gdp nc2dat model.nc --metadata
$ gdp nc2dat model.nc -v vs vp --fmt .2 .6 -o model.dat
```
> **Description:** This tool can be used to convert NetCDF files to ascii format. In this example, by running the first command, the program will output meta data information related to 'model.nc'. It's necessary to figure out the data fields that one is interested to extract from the nc file first (in this case, they are 'vp' and 'vs'). The second command will print to file the results in a custom format to 'model.dat'.


```bash
$ gdp dat2nc vs_10km_gridded.dat  vs_10km_gridded.nc  --xrange -75 -60 --yrange 44 48 -x 1 2 -v 3
```
> **Description:** Convert gridded ascii data (column format is specified using '-x' and '-v' flags: lon, lat, value) to NetCDF ('\*.nc') format. Using '--xrange' and '--yrange' flags, the output is restricted to a polygon area.



```bash
$ gdp 1Dto2D datalist_1D.dat -x 4 -v 5 6 --header 1 --footer 1 -o phvel_maps_data
```
> **Description:**   Combine/convert 1D datasets into 2D datasets. In this example command, a list of 1D dispersion data in 'datalist_1D.dat' are combined into 2D phase velocity map data at different periods. Column format for 'datalist_1D.dat' MUST be (1) longitude, (2) latitude, (3) data path. While reading the dispersion datasets, the first and last lines are ignored ('--header' and '--footer' flags). In this example, position column is the 'period' column and value columns are 'phase velocity' and 'measurement error', and these are specified using '-x' and '-v' flags.

```bash
$ gdp 2Dto1D datalist_2D.dat -x 1 2 -v 3 4 -o dispersion_curves
```
> **Description:**  Extract/convert 2D datasets into 1D datasets. In this example command, a list of 2D data files in 'datalist_2D.dat' are read and 1D profiles are extracted. Column format for 'datalist_2D.dat' MUST be (1) identifier e.g. depth, period etc., (2) data path. While reading the phase velocity map data in this example, longitude and latitude columns are considered as the first and the second column (specified using '-x' flag) and phase velocity values and measurement errors are 3rd and 4th columns respectively (specified using '-v' flag).


```bash
$ gdp georef --epsg 4326
```
> **Description:**  Open georeferencing module window. This module reads in an image (supports bmp, png, jpg, tiff) and outputs the GeoTiff referenced map. Flag '--epsg' sets EPSG coordinate system and transformation codes (EPSG=4326 corresponds to WGS84; visit epsg.io for more information). Georeferencing procedure: (1) 'file > open image' or 'ctrl + o', (2) zoom-in (mouse wheel or square bracket buttons on the keyboard) and pan image (left mouse button drag) to points on map where coordinates are known, and open new warp point dialog using right mouse click or 'p' and enter the coordinates. (3) repeat step 2 for at least 4 points. (4) To save the GeoTiff, 'file > save GeoTiff' or 'ctrl + s'. The resulting georeference image could be plotted using the 'plot feature' module (e.g., '$ gdp plot features --geotiff georeferenced.tiff').


```bash
$ gdp seismic download init --maindir ./myproject
```
> **Description:**  initialize seismic download project and create 'download.config' file in './myproject'. Once the config file was created, open it in a text editor and modify the parameters as desired. Some example important parameters to be adjusted include 'startdate', 'enddate', 'station_channels', 'station_location_codes', 'station_minlon', 'station_maxlon', 'station_minlat', 'station_maxlat' etc. Once all parameters were set, one can start downloading events list ($ gdp seismic download events), stations list ($ gdp seismic download stations), station meta data XML files ($ gdp seismic download metadata), and mseed data files ($ gdp seismic download mseeds).


```bash
$ gdp gdp seismic download mseeds --maindir ./myproject --mseeds ./myproject/mseeds --duration 3000 --offset -500 
```
> **Description:**  This command will start downloading mseed files based on previously set parameters in 'download.config' into './myproject/mseeds' directory. The timeseries duration will be 3000 seconds and the begin time will be 500 seconds earlier than the event origin time.


```bash
$ gdp gdp seismic download mseeds --maindir ./myproject --mseeds ./myproject/mseeds --duration 86400 --ant
```
> **Description:**  This command is similar to the example above, except that by using the flag '--ant', the code will not read event list and the entire time span between 'startdate' and 'enddate' will be considered for downloading.


```bash
$ gdp seismic mseed2sac ./myproject/mseeds/\*/\*.mseed -o ./myproject/sacs --offset -500 --resample 10 --reformat
```
> **Description:**  This command will convert previously downloaded mseed files in './myproject/mseeds/\*/\*.mseed' into sacfiles and the output results will be stored in './myproject/sacs'. Flag '--reformat' specifies that the output sac files should be renamed/reformatted to './myproject/sacs/YYJJJHHMMSS/YYJJJHHMMSS_STA.CHN' file naming convention. Note that parameter '--offset -500' will be important here and it has to be set the same as the data download time ($ gdp seismic download mseeds). Setting the flag '--resample 10' results in resampling of the output sacfiles to 10 hertz sampling rate after the conversion process.


```bash
$ gdp seismic sac2dat ./myproject/sacs/*/* -o ./myproject/sacs_ascii --timerange 1000 2000
```
> **Description:**  Extract sac file data in time, value format and output in ascii format. In this example, only date between 1000 and 2000 seconds will be extracted.


```bash
$ gdp seismic sac2dat ./myproject/sacs/*/* -o ./myproject/sacs_ascii --timerange 1000 2000
```
> **Description:**  Extract sac file data in time, value format and output the results in ascii format. In this example, only data between 1000 and 2000 seconds will be extracted.



```bash
$ gdp seismic writehdr sacs/*/* --metadata ./metadata --maindir ./
```
> **Description:** Write/update sac file headers from station meta files (metadata directory is specified using flag '--metadata ./metadata'), and event list (path to event list file is specified in '$maindir/download.config'; if this is an ambient noise tomography project, append '--ant' flag to the command above and it will ignore '--maindir').


```bash
$ gdp seismic remresp sacs/*/* --metadata ./metadata --unit VEL --pre_filt 0.005 0.006 30.0 35.0 --water_level 60

```
> **Description:** Remove instrument response of sacfiles using station XML metadata information and the ObsPy remove\_response() method (see related ObsPy documentation for more information).


```bash
$ gdp seismic resample sacs/*/* --sf 5 

```
> **Description:** In this example, the input sac file timeseries will be decimated to a sampling frequency of 5 Hz.


```bash
$ gdp seismic bandpass sacs/*/* --cp1 3 --cp2 300 -n 3 -p 2

```
> **Description:** This command will apply bandpass filtering to the input sac files using corner periods of 3 and 300 seconds, number-of-poles of 3, and a number of passes of 2. See SAC documentation for more information.


```bash
$ gdp seismic cut sacs/*/* --begin 1000 --end 2000

```
> **Description:** This command will cut the input sac file timeseries from 1000 s to 2000 s, and zero values will replace missing data (i.e. applies 'cutter fillz'; see SAC documentation for more information).


```bash
$ gdp seismic remchan sacs/*/* --channels BHZ HHZ --onlykeep BHZ

```
> **Description:** This command is useful to remove extra channels from datasets. In the above example, if both BHZ and HHZ channels of the same stations and events are present, the extra HHZ channel will be removed.


```bash
$ gdp seismic sws init sacs/*/* --refmodel iasp91 --hdronly

```
> **Description:** Initialize the input sac dataset for shear-wave-splitting measurement. This command writes arrival header information using reference model iasp91 (to see other reference models: $ gdp seismic sws init -h). T1-T2: first P arrivals, T3-T4: first S arrivals, T5-T6: SKSS and PKS arrivals, T7-T9: other arrivals.


```bash
$ gdp gdp seismic sws init sacs/*/* --refmodel iasp91

```
> **Description:** Similar to the previous example, this command will update sac headers with important arrival information for the purpose of shear wave splitting measurements. In addition (because '--hdronly' is not appended), it opens a GUI for QC of timeseries and selecting appropriate arrivals to generate specific copies in the dataset (e.g., 13240081122_SHEY_SKKS.{BHE,BHN,BHZ}).


```bash
$ gdp plot stations ./stations.dat --labels

```
> **Description:** This command uses GMT to generate a station map from './stations.dat' that was previously downloaded using command '$ gdp seismic download stations'. By appending '--labels', station names will also be shown on the output map. The output file will be either './stations.pdf' or './stations.ps' (depends on if 'ghostscript' is installed on the current terminal environment)


```bash
$ gdp plot events ./events.dat --lon -66 --lat 45 

```
> **Description:** This command uses GMT (and python matplotlib library) to generate an event distribution map and related statistics figures from './events.dat' that was previously downloaded using command '$ gdp seismic download events'. Flags '--lon -66' and '--lat 45' set the study region center coordinates that are used to calculate BAZ and GCARC distribution (for illustration only). The output files will be './events.pdf' (or './events.ps') and './events-histograms.pdf'.


```bash
$ gdp plot hist model_1.dat model_2.dat -v 3 -n 10 --legend model_1 model_2 --xlabel Velocity \(km/s\) --ylabel Number --title Model 1 versus Model 2 --mean --transparency 0.6
```
> **Description:** Generate combine histogram plots (number of input data fields can vary). In this command, column 3 of 'model_1.dat' and 'model_2.dat' are read as data fields ('-v 3'), number of histogram bins is set to 10 ('-n 10'), legends are set to 'model 1' and 'model 2' ('--legend model_1 model_2'; note that underlines are considered as spaces as the number of items must match with the number of data fields), x-axis label is set to 'Velocity (km/s)' and 'Number' using flags '--xlabel' and '--ylabel' respectively (note that parenthesis must be entered using the escape character '\\' in a bash command), title of the plot is set using '--title Model 1 versus Model 2', the distribution means will be denoted by dashed lines as the flag '--mean' is appended, and the transparency of the histograms are set to 0.6 (must be >0 and <=1).

```bash
$ gdp plot features --point points_set1.shp  points_set2.dat --polygon polygons.shp --geotiff georeferenced.tiff

```
> **Description:** Using this module, one can quickly visualize geographical data files including points, polygons (both ascii and shape files are accepted), as well as the GeoTiff format. Other optional arguments are available to customize the plot regarding the level of details (e.g., minimum area to be plotted using flag '--area') and aesthetics (e.g., '--landcolor', '--pointsize', '--ticks' etc.). Coordinate system and projection could also be set using '--epsg' flag. Enter command '$ gdp plot features -h' for more information.



# Release notes


## Version 0.1.2


**Following changes will be applied**:
- *mseed2sac* and *sac2dat* will be moved into the *seismic* module
- *--lonrange* >> *--xrange* (generalization for utm/cartesian case)
- *--latrange* >> *--yrange* (generalization for utm/cartesian case)

FIX: make sure data is not missing at the beginning or at the end of sac files when using mseed2sac (~ cutter fillz)

The following new tools/modules are added for this version:

| **Tool/Module** | **Description** |
|----------|-----------------|
|chull     |convex-hull / minimum bounding polygon for a set of points|
|add       |add value columns of two or more ascii data files|
|shp2dat   |convert GIS shape files (point/polygon) to ascii data|
|1Dto2D    |Combine/convert 1D datasets into 2D datasets. Example use cases: (1) building phase velocity map datasets from point/1D dispersion curve datasets, (2) building shear velocity map datasets from 1D shear velocity profiles.|
|2Dto1D    |Extract/convert 2D datasets into 1D datasets. Example use cases: (1) extracting point dispersion curves from phase velocity maps, (2) extracing 1D shear velocity profiles from shear velocity map datasets|
|seismic   |seismic data acquisition and processing module |
|plot      |plot module (requires gmt)|

- *seismic* module includes the following tools:

  1. *download init*: initialize current directory for seismic data acquisition. It outputs a config file (i.e. 'download.config') that is used by the 4 following tools.
  2. *download events*: download list of events according to the list of datacenters (specified in download.config)
  3. *download stations*: download list of stations according to the list of datacenters (specified in download.config)
  4. *download metadata*: download station metadata (xml) according to stations.dat
  5. *download mseeds*: download mseed datafiles based
  6. *writehdr*: update sac headers using xml metadata (obspy method)
  7. *remresp*: remove sac file instrument response using xml metadata (obspy method)
  8. *resample*: resample sac timeseries using obspy method
  9. *bandpass*: apply bandpass filter to sac files (sac method)
  10. *cut*: cut sac timeseries (sac method)
  11. *remchannel*: remove extra channels
  12. *sws init*: initialize shear-wave-splitting project by writing arrivals info into sac headers and making copies


- *plot* module includes the following tools:

  1. *stations*: plot stations list using gmt
  2. *events*: plot events list using gmt
  3. *hist*: plot histogram(s)

## Version 0.1.1

Only README is updated for this version.

## Version 0.1.0

This version is the first version that is published on *PyPI* and it includes the following tools:


| **Tool/Module** | **Description** |
|----------|-----------------|
|cat       |concatenate/reformat numerical or non-numerical data|
|union     |generate the union of input data files|
|intersect |generate the intersect of input data files|
|difference|generate the difference of input data files|
|split     |split a concatenated dataset into multiple data files|
|min       |calculate minimum of values in numerical column(s)|
|max       |calculate maximum of values in numerical column(s)|
|sum       |calculate summation of values in numerical column(s)|
|mean      |calculate mean of values in numerical column(s)|
|median    |calculate median of values in numerical column(s)|
|std       |calculate standard deviation of values in numerical column(s)|
|pip       |output points inside/outside a polygon (ray tracing method)|
|gridder   |gridding/interpolation of 2D/map data with Gaussian smoothing applied|
|mseed2sac |convert mseed to sac. this script also handles data fragmentation issue.|
|sac2dat   |convert sac to dat (ascii); output format: time, amplitude|
|nc2dat    |convert nc data to dat/ascii|


# License

*gdp* is presented under GPL 3 which is a **strong copyleft** license!

# Contact us

* **[Omid Bagherpur](mailto:omid.bagherpur@gmail.com)**: Geophysicist - Structural Seismologist, PhD.
* **[Fiona Darbyshire](mailto:darbyshire.fiona_ann@uqam.ca)**: Geophysicist - Structural Seismologist, PhD, University Professor at UQAM.
