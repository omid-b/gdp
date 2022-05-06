
# from libcpp cimport bool

class Point:
    def __init__(self, double lon, double lat):
        self.lon = lon
        self.lat = lat


class Line:
    def __init__(self, object point1, object point2):
        self.point1 = point1
        self.point2 = point2

    def calc_gcarc(self):
        from math import sin, cos, atan2, radians, degrees, sqrt
        cpdef double lon1
        cpdef double lon2
        cpdef double lat1
        cpdef double lat2
        cpdef double delta_lon
        cpdef double delta_lat
        cpdef double a
        cpdef double gcarc
        lon1, lat1 = radians(self.point1.lon), radians(self.point1.lat)
        lon2, lat2 = radians(self.point2.lon), radians(self.point2.lat)
        delta_lon = lon2 - lon1
        delta_lat = lat2 - lat1
        a = (sin(delta_lat / 2))**2 + cos(lat1) * cos(lat2) * (sin(delta_lon / 2))**2
        gcarc = 2 * atan2(sqrt(a), sqrt(1 - a))
        return degrees(gcarc)

    def calc_dist(self):
        # calculate earth radius at mid_latitude first
        # formula from https://rechneronline.de/earth-radius/
        from math import sin, cos, radians, sqrt
        cpdef double mid_lat
        cpdef double r1
        cpdef double r2
        cpdef double a1
        cpdef double a2
        cpdef double b1
        cpdef double b2
        cpdef double earth_radius
        cpdef double dist
        mid_lat = radians((self.point1.lat + self.point2.lat) / 2)
        r1 = 6378. # radius at equator
        r2 = 6356. # radius at pole
        a1 = r1**2 * cos(mid_lat)
        a2 = r2**2 * sin(mid_lat)
        b1 = r1 * cos(mid_lat)
        b2 = r2 * sin(mid_lat)
        earth_radius = sqrt((a1**2 + a2**2) / (b1**2 + b2**2))
        # now calculate dist
        dist = earth_radius * radians(self.calc_gcarc())
        return dist

    def calc_az(self):
        from math import sin, cos, atan2, radians, degrees
        cpdef double lon1
        cpdef double lon2
        cpdef double lat1
        cpdef double lat2
        cpdef double delta_lon
        cpdef double az
        lon1, lat1 = radians(self.point1.lon), radians(self.point1.lat)
        lon2, lat2 = radians(self.point2.lon), radians(self.point2.lat)
        delta_lon = lon2 - lon1
        az = atan2(sin(delta_lon) * cos(lat2),
                     cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(delta_lon))
        az = degrees(az)
        if az < 0:
            az += 360
        return az

    def calc_baz(self):
        from math import sin, cos, atan2, radians, degrees
        cpdef double lon1
        cpdef double lon2
        cpdef double lat1
        cpdef double lat2
        cpdef double delta_lon
        cpdef double baz
        lon1, lat1 = radians(self.point2.lon), radians(self.point2.lat)
        lon2, lat2 = radians(self.point1.lon), radians(self.point1.lat)
        delta_lon = lon2 - lon1
        baz = atan2(sin(delta_lon) * cos(lat2),
                     cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(delta_lon))
        baz = degrees(baz)
        if baz < 0:
            baz += 360
        return baz

    def is_intersect_line(self, object line):
        cpdef object point3
        cpdef object point4
        cpdef bint ccw_123
        cpdef bint ccw_124
        cpdef bint ccw_134
        cpdef bint ccw_234
        point3 = line.point1
        point4 = line.point2
        ccw_123 = ((point3.lat-self.point1.lat)*(self.point2.lon-self.point1.lon) > (self.point2.lat-self.point1.lat)*(point3.lon-self.point1.lon))
        ccw_124 = ((point4.lat-self.point1.lat)*(self.point2.lon-self.point1.lon) > (self.point2.lat-self.point1.lat)*(point4.lon-self.point1.lon))
        ccw_134 = ((point4.lat-self.point1.lat)*(point3.lon-self.point1.lon) > (point3.lat-self.point1.lat)*(point4.lon-self.point1.lon))
        ccw_234 = ((point4.lat-self.point2.lat)*(point3.lon-self.point2.lon) > (point3.lat-self.point2.lat)*(point4.lon-self.point2.lon))
        return ccw_134 != ccw_234 and ccw_123 != ccw_124


class Polygon:
    def __init__(self, list polygon_lon, list polygon_lat):
        self.lon = polygon_lon
        self.lat = polygon_lat
        if polygon_lon[0] != polygon_lon[-1] or polygon_lat[0] != polygon_lat[-1]:
            print(f"Error in class Polygon! The first and last points must be the same (closed polygon).\n")
            exit(1)

    def get_lines(self):
        cpdef int i
        cpdef int nlines
        cpdef list lines
        cpdef object point1
        cpdef object point2
        nlines = len(self.lon) -1
        lines = []
        for i in range(nlines):
            point1 = Point(self.lon[i], self.lat[i])
            point2 = Point(self.lon[i+1], self.lat[i+1])
            lines.append(Line(point1, point2))
        return lines

    def is_point_in(self, object point, bint inverse=False):
        cpdef list lon_range
        cpdef list lat_range
        cpdef double dlon
        cpdef double dlat
        cpdef object point_north
        cpdef object point_south
        cpdef object point_east
        cpdef object point_west
        cpdef list test_lines
        cpdef object test_line
        cpdef object line
        cpdef int num_intersects
        

        cpdef bint true = True
        cpdef bint false = False
        lon_range = [min(self.lon), max(self.lon)]
        lat_range = [min(self.lat), max(self.lat)]
        if point.lon < lon_range[0] or point.lon > lon_range[1] or point.lat < lat_range[0] or point.lat > lat_range[1]:
            if inverse:
                return true
            else:
                return false
        else:
            dlon = (lon_range[1] - lon_range[0]) / 10
            dlat = (lat_range[1] - lat_range[0]) / 10
            point_north = Point(point.lon, lat_range[1]+dlat)
            point_south = Point(point.lon, lat_range[0]-dlat)
            point_east = Point(lon_range[1]+dlon, point.lat)
            point_west = Point(lon_range[0]-dlon, point.lat)
            test_lines = [Line(point, point_north),
                          Line(point, point_south),
                          Line(point, point_east),
                          Line(point, point_west)] # four crossing lines
            for test_line in test_lines:
                num_intersects = 0
                for line in self.get_lines():
                    if line.is_intersect_line(test_line):
                        num_intersects += 1
                if num_intersects: # no need to test other crossing lines
                    break
            if inverse:
                if num_intersects % 2:
                    return false
                else:
                    return true
            else:
                if num_intersects % 2:
                    return true
                else:
                    return false


cpdef double calc_earth_radius(double lat):
    from math import cos, sin, sqrt
    cpdef double r1
    cpdef double r2
    cpdef double a1
    cpdef double a2
    cpdef double b1
    cpdef double b2
    cpdef double earth_radius
    r1 = 6378 # radius at equator
    r2 = 6356 # radius at pole
    a1 = r1**2 * cos(lat)
    a2 = r2**2 * sin(lat)
    b1 = r1 * cos(lat)
    b2 = r2 * sin(lat)
    earth_radius = sqrt((a1**2 + a2**2) / (b1**2 + b2**2))
    return earth_radius

