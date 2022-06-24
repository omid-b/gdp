#!/usr/bin/env python

#====Adjustable Parameters=====#
#The followings are only used for plotting
mapSize = 8
padding_coe= 0.5 #between 0 and 1; related to map_region for plotting
#==============================#

import os, sys
os.system('clear')
print("This script generates coordinates of parallel profiles (start and end points) perpendicular to a specific track.\n")
about = f'''
  Error!
  USAGE: {sys.argv[0]} <polygon> <#profiles> <len(km)> <sampling(km)>
  Note: <polygon> also defines the study region
'''

if len(sys.argv)!=5:
	print(about)
	exit()

num_profiles = int(sys.argv[2]) #number of profiles
len_profiles = int(sys.argv[3]) #length of profiles
sample_interval = int(sys.argv[4]) #profiles' sampling interval

if not len_profiles > 2*sample_interval:
  print(about)
  print('Error! <sampling(km)> is too large!\n')
  exit()

try:
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.basemap import Basemap
    #conda install basemap 
    #conda install basemap-data-hires
    import shutil
    from geographiclib.geodesic import Geodesic # pip install geographiclib
    from math import degrees, radians, sin, cos, asin, atan, sqrt
except ImportError:
	print("Error loading required modules! Check the followings:")
	print("matplotlib.pyplot, shutil, mpl_toolkits.basemap, geographiclib, numpy, math\n")
	exit()

#-----------profile class-----------#
class profile:
	def __init__(self,lon1,lat1,lon2,lat2):
	    self.lon1=float(lon1)
	    self.lat1=float(lat1)
	    self.lon2=float(lon2)
	    self.lat2=float(lat2)

	def dlon(self):
		dlon=self.lon2-self.lon1
		return dlon

	def dlat(self):
		dlat=self.lat2-self.lat1
		return dlat

	def centre(self):
		x,y= map.gcpoints(self.lon1,self.lat1,self.lon2,self.lat2,3)
		midPoint=map(x[1],y[1],inverse=True)
		return midPoint

	def length(self):
		length=Geodesic.WGS84.Inverse(self.lat1,self.lon1,self.lat2,self.lon2)['s12']
		return length/1000

	def azim(self):
		azim=Geodesic.WGS84.Inverse(self.lat1,self.lon1,self.lat2,self.lon2)['azi1']
		return azim

	def points(self,np):
		x,y= map.gcpoints(self.lon1,self.lat1,self.lon2,self.lat2,np)
		return map(x,y,inverse=True)
#----
class LineDrawer(object):
    lines = []
    def draw_line(self):
        ax = plt.gca()
        xy = plt.ginput(2)

        x = [p[0] for p in xy]
        y = [p[1] for p in xy]
        line = plt.plot(x,y)
        ax.figure.canvas.draw()
        self.lines.append(line)
        return x,y

#----
def make_profile(centre_lon, centre_lat, azimuth, length):
	p1x=Geodesic.WGS84.Direct(centre_lat,centre_lon,azimuth+180,length*500)['lon2']
	p1y=Geodesic.WGS84.Direct(centre_lat,centre_lon,azimuth+180,length*500)['lat2']
	p2x=Geodesic.WGS84.Direct(centre_lat,centre_lon,azimuth,length*500)['lon2']
	p2y=Geodesic.WGS84.Direct(centre_lat,centre_lon,azimuth,length*500)['lat2']
	return [p1x, p1y, p2x, p2y]

#-----------------------------------#

#finding map_region
poly_lon, poly_lat=np.loadtxt(sys.argv[1],dtype=float,unpack=True)
poly_size=[abs(np.max(poly_lon)-np.min(poly_lon)), abs(np.max(poly_lat)-np.min(poly_lat))]
map_padding= [abs(padding_coe*poly_size[0]*cos(degrees(np.mean(poly_lon)))),  padding_coe*poly_size[1]]
map_region = [np.min(poly_lon)-map_padding[0],\
              np.min(poly_lat)-map_padding[1],\
              np.max(poly_lon)+(1+padding_coe)*map_padding[0],\
              np.max(poly_lat)+map_padding[1]]


print(np.min(poly_lon),np.max(poly_lon),np.min(poly_lat),np.max(poly_lat))
print(poly_size)
print(map_region[0],map_region[1],map_region[2],map_region[3])

happy='n'
while (happy != 'y'):
  #plotting section
  fig, ax = plt.subplots(figsize=(mapSize, mapSize))
  map = Basemap(llcrnrlon=map_region[0],llcrnrlat=map_region[1],
  	          urcrnrlon=map_region[2],urcrnrlat=map_region[3],
                projection='lcc',lat_1=map_region[1],lat_2=map_region[3],
                lon_0=(np.min(poly_lon)+np.max(poly_lon))/2,lat_0=(np.min(poly_lat)+np.max(poly_lat))/2, resolution ='i',
                area_thresh=1000., ax=ax)
  
  map.drawmeridians(np.arange(-180,180,int(poly_size[0]/3)),labels=[0,0,1,1], dashes=[1,1], color='w')
  map.drawparallels(np.arange(-90,90,int(poly_size[1]/3)),labels=[1,1,0,0], dashes=[1,1], color='w')
  
  map.fillcontinents(color='0.8')
  map.drawcountries(linewidth=0.4)
  map.drawcoastlines(linewidth=0.25)
  
  x, y=map(poly_lon, poly_lat)
  map.plot(x,y,linewidth=2,color='darkblue')
  
  print('\nChoose the starting and the ending points interactively, then close the plot window to create the outputs.\n')
  
  ld = LineDrawer()
  mainPx,mainPy=ld.draw_line()
  mainPx,mainPy=map(mainPx,mainPy,inverse=True)
  
  main_profile=profile(mainPx[0],mainPy[0],mainPx[1],mainPy[1])
  main_profile_azim=main_profile.azim()
  profiles_centre_X, profiles_centre_Y = main_profile.points(num_profiles)
  
  #make and draw parallell profiles
  profiles_start_X = [];
  profiles_start_Y = [];
  profiles_end_X   = [];
  profiles_end_Y   = [];
  for i in range(num_profiles):
  	#make profile i:
  	profiles_start_X.append(make_profile\
  		(profiles_centre_X[i], profiles_centre_Y[i],\
  		 main_profile_azim-90,len_profiles)[0])
  	profiles_start_Y.append(make_profile\
  		(profiles_centre_X[i], profiles_centre_Y[i],\
  		 main_profile_azim-90,len_profiles)[1])
  	profiles_end_X.append(make_profile\
  		(profiles_centre_X[i], profiles_centre_Y[i],\
  		 main_profile_azim-90,len_profiles)[2])
  	profiles_end_Y.append(make_profile\
  		(profiles_centre_X[i], profiles_centre_Y[i],\
  		 main_profile_azim-90,len_profiles)[3])
  	#draw profile i:
  	x, y=map([profiles_start_X[i],profiles_end_X[i]],\
  	 [profiles_start_Y[i],profiles_end_Y[i]])
  	map.plot(x,y,linewidth=2,color='black')
  
  ax.figure.canvas.draw()
  plt.savefig('profiles.pdf',dpi=300)
  plt.show()
  plt.close()
  happy=input('Are you happy with the results (y/n)? ')

if os.path.isdir('profiles'):
    shutil.rmtree('profiles')

os.mkdir('profiles')
shutil.move('profiles.pdf', 'profiles/profiles.pdf')
#make the output
fn1=open('profiles/profiles_all.dat', mode='w')
for i in range(num_profiles):
	fn1_data = f'%.8f %.8f %.8f %.8f\n' % (profiles_start_X[i], profiles_start_Y[i], profiles_end_X[i], profiles_end_Y[i])
	fn1.write(str(fn1_data))
	fn2= open(f'profiles/profile_%03d.dat' % (i+1), mode='w')
	x,y= map.gcpoints(profiles_start_X[i],profiles_start_Y[i], profiles_end_X[i], profiles_end_Y[i],int(len_profiles/sample_interval)+1)
	x,y= map(x,y,inverse=True)
	for j in range(len(x)):
		fn2_data = f'%.8f %.8f\n' % (x[j], y[j])
		fn2.write(fn2_data)
	fn2.close()

fn1.close()
print('\n  Outputs are created.\n')
