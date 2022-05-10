# gdp: Geophysical Data Processing

gdp provides a set of tools that are available through command-line-interface (CLI) to process common geophysical data types.

## Release notes

### Version 0.0.5:

This version adds a new module named 'convert' that can be used to convert common geophysical file types or data formats to one another. A brief description of example CLI commands is given below:

	- $> gdp convert mseed2sac mseed_dataset/*  --reformat --offset -500 --resample 10 -o sac_dataset
	This command will convert mseed files in 'mseed_dataset' to another directory named 'sac_dataset'.
	Flag '--reformat' will cause creating of sub-folders in the output directory in 'YYJJJHHMMSS' format,
	and the sacfiles within these sub-directories will be renamed as 'YYJJJHHMMSS_STA.CHN', where 'STA' is the 
	station code and 'CHN' is the channel code. If reformat is enabled, offset time can be adjusted using 
	'--offset'. Finally, '--resample 10' results in resampling of output timeseries to 10 Hz.

	- $> gdp convert sac2dat sac_dataset/*  -o timeseries --timerange 0 3600
	This command will output the first hour (0-3600 s) of the sac data in sac_dataset/* .

	- $> gdp convert nc2dat model.nc --metadata
	     gdp convert nc2dat model.nc -v vs vp --fmt .2 .6 -o model.dat
	This tool can be used to convert NetCDF files to ascii format. In this example, by running the first command,
	the program will output meta data information related to 'model.nc'. It's necessary to figure out the data fields
	that one is interested to extract from the nc file first (in this case, they are 'vp' and 'vs').
	The second command will print to file the results in a custom format to 'model.dat'.

### Version 0.0.1:

This version includes a module named 'data' that can be used to process general geophysical data files. A brief description of example CLI commands is given below:

	- $> gdp data cat file* -x 1 2 -v 5 3 4 --header 2 --footer 4 --fmt .2 .4 --sort --uniq --noextra -o concatenated.txt
	Description: This command will concatenate files in current directory matching names 'files*'.
	While reading, 2 header lines and 4 footer lines will be omitted. Positional columns are the 
	first and second columns (-x 1 2), and value/numerical columns are [5 3 4]. Positional columns 
	will be printed in %.2f format, and value columns will be printed in %.4f.
	If files have extra (non-numerical) columns other than the first 5 columns,	'--noextra' will
	cause not printing them. Flag '-o' can be used to set the output file name and if not specified,
	the results will be printed to standard output.
	Many of these flags are also common for the following commands.


	- $> gdp data union file_1.dat file_2.dat file_3.dat
	Description: Output union of a set of numerical data files (two or more) while considering
	positional columns (default=[1 2]) and value columns as [3] (default; these could be modified
	using '-x' '-v' columns).


	- $> gdp data intersect file_1.dat file_2.dat file_3.dat
	Description: Output intersect of a set of numerical data files (two or more) considering positional columns
	(similar positional columns that could be specified using '-x' flag; the value of the first file 
	will be the output). Note that the first value of the flag '--fmt' will be important here.


	- $> gdp data difference file_1.dat file_2.dat file_3.dat
	Description: Output difference of a set of numerical data files (two or more) considering positional columns.
	In this case, data points that are unique to 'file_1.dat' will be the output results.


	- $> gdp data split dataset.dat --method ncol --number 4 --start -2 --name 3 -o outdir
	Description: This command is useful to split/unmerge a concatenated dataset ('dataset.dat').
	Two methods can be choosen: (1) nrow: split based on a fixed number of rows, (2) ncol: split based on
	a row that has a unique number of columns as an identifier.
	In case of method 'ncol' above: '--number 4' specifies that the row with unique number of columns has 
	4 columns (reference row); '--start -2' specifies the start line or row offset relative to the reference line;
	'--name 3' specifies the row offset relative to 'start line' that will be used for output file names;
	'-o outdir' specifies output directory (it can be omitted for printing to the standard output)


	- $> gdp data min  *.xyz -v 1 2 3
	  $> gdp data max  *.xyz -v 1 2 3
	  $> gdp data sum  *.xyz -v 1 2 3
	  $> gdp data mean  *.xyz -v 1 2 3
	  $> gdp data median  *.xyz -v 1 2 3
	  $> gdp data std  *.xyz -v 1 2 3
	Description: Output min, max, sum, mean, median, or std of the three first columns in *.xyz files.
	

	- $> gdp data pip  *.xyz  --polygon polygon.dat
	  $> gdp data pip  *.xyz  --polygon polygon.dat -i
	Description: Only output points inside or outside ('-i') a polygon


	- $> gdp data gridder vs_model/depth* --spacing 0.2 --smoothing 50 --polygon polygon.dat -o outdir
	Description: This command will perform gridding (2D interpolation) to the input xyz format data files.
	In case of the above command: '--spacing 0.2' specifies that grid spacing along both
	longitude and latitude is 0.2 degrees (two values can be given as well; [lon_spacing, lat_spacing]);
	'--smoothing 50' sets a 50 km Gaussian smoothing to the output grid;
	'--polygon polygon.dat' is optional: if given, only points inside the given polygon will be printed out.

	
