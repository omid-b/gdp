# ***gdp*: Geophysical Data Processing**

*gdp* provides a set of tools that are available through command-line-interface (CLI) to process and/or convert common geophysical data types.

## Requirements

Ubuntu/Debian:

```bash
sudo apt-get install libbz2-dev
```

Fedora:

```bash
sudo yum install bzip2-devel
```


## Release notes

### Version 0.1.2 (work in progress roadmap)

The following features might not still work. Please download Version 0.1.1 from https://pypi.org/project/gdp/.

**Following changes will be applied**:
- *mseed2sac* and *sac2dat* will be moved into the *seismic* module
- *--lonrange* >> *--xrange* (generalization for utm/cartesian case)
- *--latrange* >> *--yrange* (generalization for utm/cartesian case)

FIX: make sure data is not missing at the beginning or at the end of sac files when using mseed2sac (~ cutter fillz)

The following new tools/modules will be added for this version:

| **Tool/Module** | **Description** |
|----------|-----------------|
|chull     |convex-hull / minimum bounding polygon for a set of points|
|add       |add value columns of two or more ascii data files|
|shp2dat   |convert GIS shape files (point/polygon) to ascii data|
|1Dto2D    |Combine/convert 1D datasets into 2D datasets. Example use cases: (1) building phase velocity map datasets from point/1D dispersion curve datasets, (2) building shear velocity map datasets from 1D shear velocity profiles.|
|2Dto1D    |Extract/convert 2D datasets into 1D datasets. Example use cases: (1) extracting point dispersion curves from phase velocity maps, (2) extracing 1D shear velocity profiles from shear velocity map datasets|
|seismic   |seismic data acquisition and processing module |
|plot      |plot module (requires gmt)|

- *seismic* module will include the following tools:

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



- *plot* module will include the following tools:

  1. *stations*: plot stations list using gmt
  2. *events*: plot events list using gmt
  3. *hist*: plot histogram(s)

### Version 0.1.1

Only README is updated for this version.

### Version 0.1.0

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

## Examples

Some example *gdp* commands are explained below:

```bash
gdp cat file* -x 1 2 -v 5 3 4 --header 2 --footer 4 --fmt .2 .4 --sort --uniq --noextra -o concatenated.txt
```
> **Description:** This command will concatenate files in current directory matching names 'files\*'. While reading, 2 header lines and 4 footer lines will be omitted. Positional columns are the first and second columns (-x 1 2), and value/numerical columns are \[5 3 4\]. Positional columns will be printed in %.2f format, and value columns will be printed in %.4f.	If files have extra (non-numerical) columns other than the first 5 columns,	'--noextra' will cause not printing them. Flag '-o' can be used to set the output file name and if not specified, the results will be printed to standard output.Many of these flags are also common for the following commands.


```bash
gdp union file_1.dat file_2.dat file_3.dat
```
> **Description:** Output union of a set of numerical data files (two or more) while considering positional columns (default=\[1 2\]) and value columns as \[3\] (defaults; these could be modified using '-x' '-v' flags).


```bash
gdp intersect file_1.dat file_2.dat file_3.dat
```
> **Description:** Output intersect of a set of numerical data files (two or more) considering positional columns	(similar positional columns that could be specified using '-x' flag; the value of the first file will be the output). Note that the first value of the flag '--fmt' will be important here.


```bash
gdp difference file_1.dat file_2.dat file_3.dat
```
> **Description:** Output difference of a set of numerical data files (two or more) considering positional columns. In this case, data points that are unique to 'file_1.dat' will be the output results.



```bash
gdp split dataset.dat --method ncol --number 4 --start -2 --name 3 -o outdir
```
> **Description:** This command is useful to split/unmerge a concatenated dataset ('dataset.dat'). Two methods can be choosen: (1) nrow: split based on a fixed number of rows, (2) ncol: split based on a row that has a unique number of columns as an identifier. In case of method 'ncol' above: '--number 4' specifies that the row with unique number of columns has 4 columns (reference row); '--start -2' specifies the start line or row offset relative to the reference line; '--name 3' specifies the row offset relative to 'start line' that will be used for output file names;	'-o outdir' specifies output directory (it can be omitted for printing to the standard output)


```bash
gdp min  *.xyz -v 1 2 3
gdp max  *.xyz -v 1 2 3
gdp sum  *.xyz -v 1 2 3
gdp mean  *.xyz -v 1 2 3
gdp median  *.xyz -v 1 2 3
gdp std  *.xyz -v 1 2 3
```
> **Description:** Output min, max, sum, mean, median, or std of the three first columns in \*.xyz files.


```bash
gdp pip  --point *.xyz  --polygon polygon.dat
gdp pip  --point *.xyz  --polygon polygon.dat -i
```
> **Description:** Only output points inside or outside ('-i') of the given polygon. Alternatively '--lonrange' and '--latrange' flags could be used to define the polygon.


```bash
gdp gridder vs_model/depth* --spacing 0.2 --smoothing 50 --polygon polygon.dat -o outdir
```
> **Description:** This command will perform gridding (2D interpolation) to the input xyz format data files. In case of the above command: '--spacing 0.2' specifies that grid spacing along both longitude and latitude is 0.2 degrees (two values can be given as well; \[lon_spacing, lat_spacing\]); '--smoothing 50' sets a 50 km Gaussian smoothing to the output data; '--polygon polygon.dat' is optional: if given, only points inside the given polygon will be printed out.



```bash
gdp  mseed2sac mseed_dataset/*  --reformat --offset -500 --resample 10 -o sac_dataset 

```
> **Description:** This command will convert mseed files in 'mseed_dataset'  to another directory named 'sac_dataset'. Flag '--reformat' will cause creating of sub-folders in the output directory in 'YYJJJHHMMSS' format, and the sacfiles within these sub-directories will be renamed as 'YYJJJHHMMSS_STA.CHN', where 'STA' is the station code and 'CHN' is the channel code. If reformat is enabled, offset time can be adjusted using '--offset'. Finally, '--resample 10' results in resampling of output timeseries to 10 Hz.


```bash
gdp sac2dat sac_dataset/*  -o timeseries --timerange 0 3600
```
> **Description:** This command will output the first hour (0-3600 s) of the sac data in sac_dataset/\*


```bash
gdp nc2dat model.nc --metadata
gdp nc2dat model.nc -v vs vp --fmt .2 .6 -o model.dat
```
> **Description:** This tool can be used to convert NetCDF files to ascii format. In this example, by running the first command, the program will output meta data information related to 'model.nc'. It's necessary to figure out the data fields that one is interested to extract from the nc file first (in this case, they are 'vp' and 'vs'). The second command will print to file the results in a custom format to 'model.dat'.



