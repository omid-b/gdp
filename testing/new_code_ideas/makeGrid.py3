#This program gets user inputs to design the grid nodes for SW studies (e.g. TPW tomography).
#Note: This script should run using python 3 interpreter (e.g python3.6 creatgridnode.py3).
#======Adjustable Parameters======#
n = 2 #Number of outer grid nodes for each side (rows/columns)
fac = 2 #Spacing factor in outer region (if it is set to 1, the spacing would be the same as the region of interest)
#=================================#

import os,math
os.system('clear')
print('This program designs the grid nodes for Surface wave studies.\n(e.g. TPW tomography).\n')
outName = input('Enter the output file name?\n')
latmin, dlat, latmax = [float(x) for x in input('Enter MinLatitude, LatitudeSpacing, MaxLatitude?\n').split()]
lonmin, dlon, lonmax = [float(x) for x in input('Enter MinLongitude, LongitudeSpacing, MaxLongitude?\n').split()]

#===functions===#
def earthRad(phi):
	#(phi in degrees) This function calculates Earth's radius at a given latitude
	a = float(6378.137) #Earth's radius at equator in km
	b = float(6356.752) #Earth's radius at poles in km
	a2 = a**2
	b2 = b**2
	sinPhi = math.sin(math.radians(phi))
	cosPhi = math.cos(math.radians(phi))
	earthRad = math.sqrt( ((a2*cosPhi)**2 + (b2*sinPhi)**2) / ((a*cosPhi)**2+(b*sinPhi)**2) )
	return earthRad

def hav(theta):
	 #Haversine function(theta in radians)
	 haversine = (1-math.cos(theta))/2
	 return haversine 

	
def gcDist(lon1,lat1,lon2,lat2):
	#This function calculates great circle distance between two points (All in degrees). 
	r = earthRad((lat1+lat2)/2)
	lon1,lat1,lon2,lat2 = [math.radians(x) for x in [lon1,lat1,lon2,lat2]]
	hca =  hav(lat2-lat1)+math.cos(lat1)*math.cos(lat2)*hav(lon2-lon1) #The haversine of the central angle
	gcDist = 2*r*math.asin(math.sqrt(hca))
	return gcDist
	

def frange(start,end,step):
	#This function is like range() for float numbers!
	lst = [start]
	while start != end :
		start = round(start+step,3)
		lst.append(start)
	return lst

#===============#
#-----Latitude and Longitude nodes-----#
latNodes = frange(latmax,latmin,-dlat)
lonNodes = frange(lonmin,lonmax,dlon)
#Adding n row/column to outer region

for i in range(n):
 latNodes.insert(0,latNodes[0]+fac*dlat)
 latNodes.append(latNodes[-1]-fac*dlat)
 lonNodes.insert(0,lonNodes[0]-fac*dlon)
 lonNodes.append(lonNodes[-1]+fac*dlon)

#--------------------------------------#

outFile = open(outName,'w')
str1 = 'Grid%dx%d\n' %(len(latNodes),len(lonNodes))
outFile.write(str1)
str1 = '%6d\n' %(len(latNodes)*len(lonNodes))
outFile.write(str1)

for j in range(len(lonNodes)):
	for i in range(len(latNodes)):
		str1 = '%8.2f%8.2f\n' %(latNodes[i],lonNodes[j])
		outFile.write(str1)

#region box; The four last coordinates in the output that define inner region boundary
str1 = '%8.2f%8.2f\n%8.2f%8.2f\n%8.2f%8.2f\n%8.2f%8.2f\n' %(latNodes[0+n],lonNodes[0+n],latNodes[0+n],lonNodes[-1-n],latNodes[-1-n],lonNodes[0+n],latNodes[-1-n],lonNodes[-1-n])
outFile.write(str1)
#The last two lines in the output
lon_mid = (lonNodes[-1]+lonNodes[0])/2
lat_mid = (latNodes[-1]+latNodes[0])/2
str1 = '%5d\n%8.2f%8.2f' %(len(lonNodes), gcDist(lon_mid-(0.5*dlon),lat_mid,lon_mid+(0.5*dlon) ,lat_mid), gcDist(lon_mid, lat_mid-(0.5*dlat),lon_mid ,lat_mid+(0.5*dlat)) )
outFile.write(str1)

outFile.close()
