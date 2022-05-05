# gdp: Geophysical Data Processing

gdp provides a set tools available through command-line-interface (CLI) to process general geophysical data.

## Release notes

### Version 0.0.1:

This version includes a functional module 'data' that can be used to process general geophysical data files. A brief description of example CLI commands is given below:

	- $> gdp data cat file* -x 1 2 -v 5 3 4 --header 2 --footer 4 --fmt .2 .4 --sort --uniq --noextra -o concatenated.txt
	Description: This command will concatenate files in current directory matching names 'files*'.
	While reading, 2 header lines and 4 footer lines will be omitted. Positional columns are the first and second columns (-x 1 2),
	and value columns are [5 3 4]. Positional columns will be printed in %.2f format, and value columns will be printed in %.4f.
	If files have extra (non-numerical) columns other than the first 5 columns, '--noextra' will cause not printing them.
	Flag '-o' can be used to set the output file name and if not specified, the results will be printed to standard output.
	Many of these flags are also common for the following commands.


	- $> gdp data union file_1.dat file_2.dat file_3.dat
	Description: Output union of a set of numerical data files (two or more) while considering positional columns as [1 2] and
	value columns as [3] (default; these could be modified using '-x' '-v' columns).


	- $> gdp data intersect file_1.dat file_2.dat file_3.dat
	Description: Output intersect of a set of numerical data files (two or more) considering positional columns
	(similar positional columns; the value of the first file will be the output). Note that the first value of
	the flag '--fmt' will be important here.


	- $> gdp data difference file_1.dat file_2.dat file_3.dat
	Description: Output difference of a set of numerical data files (two or more) considering positional columns.
	In this case, lines that are unique to 'file_1.dat' will be the output results.


	- $> gdp data unmerge dataset.dat --method ncol --number 4 --start -2 --name 3 -o outdir
	Description: This command is useful to unmerge a concatenated dataset ('dataset.dat').
	Two methods can be choosen: (1) nrow: unmerge based on fixed number of rows, (2) ncol: unmerge based on
	a row that has a unique number of columns as an identifier.
	In case of method 'ncol' above: '--number 4' specifies that the row with unique number of columns has 4 columns (reference row);
	'--start -2' specifies the start line or row offset relative to the reference line;
	'--name 3' specifies the row offset relative to 'start line' that will be used for output file names;
	'-o outdir' specifies output directory (it can be omitted for printing to the standard output)


	- $> gdp data gridder vs_model/depth* --spacing 0.2 --smoothing 50 --pip polygon.dat -o outdir
	Description: This command will perform gridding to the input xyz format data files.
	In case of the above command: '--spacing 0.2' specifies that grid spacing along both
	longitude and latitude is 0.2 degrees (two values can be given as well; [lon_spacing, lat_spacing]);
	'--smoothing 50' sets a 50 km Gaussian smoothing to the output grid;
	'--pip polygon.dat' is optional: if given, only points inside the given polygon will be printed out.


	- $> gdp data pip  *.xyz  polygon.dat
	  $> gdp data pip  *.xyz  polygon.dat -i
	Description: Only output points inside or outside ('-i') a polygon


	- $> gdp data min  *.xyz -v 1 2 3
	  $> gdp data max  *.xyz -v 1 2 3
	  $> gdp data sum  *.xyz -v 1 2 3
	  $> gdp data mean  *.xyz -v 1 2 3
	  $> gdp data median  *.xyz -v 1 2 3
	  $> gdp data std  *.xyz -v 1 2 3
	Description: Output min, max, sum, mean, median, or std of the three first columns in *.xyz files.
	




