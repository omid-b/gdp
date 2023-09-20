
import os
import shutil
import subprocess

from ..ascii_procs import io
from .. import programs

     

def shp_to_ascii(args):
    if not os.path.isdir(args.outdir):
        os.mkdir(args.outdir)

    if args.point != None:
        for ptfile in args.point:
            points = io.read_point_shp(ptfile)
            nop = len(points[0])
            points_lines = []
            for ip in range(nop):
                points_lines.append(f"%{args.fmt[0]}f %{args.fmt[0]}f" %(points[0][ip], points[1][ip]))

            args.outfile = os.path.join(args.outdir, f"{os.path.splitext(os.path.split(ptfile)[1])[0]}.dat")
            args.sort = False
            args.uniq = False
            args.append = False
            io.output_lines(points_lines, args)
            print(f"shp2dat: '{ptfile}' >> '{args.outfile}'")

    if args.polygon != None:
        for plyfile in args.polygon:
            polygons = io.read_polygon_shp(plyfile)
            nply = len(polygons)
            for iply in range(nply):
                polygon = polygons[iply]
                nop = len(polygon[0])
                polygon_lines = []
                for ip in range(nop):
                    polygon_lines.append(f"%{args.fmt[0]}f %{args.fmt[0]}f" %(polygon[0][ip], polygon[1][ip]))
                
                if nply == 1:
                    args.outfile = os.path.join(args.outdir, f"{os.path.splitext(os.path.split(plyfile)[1])[0]}.dat")
                else:
                    args.outfile = os.path.join(args.outdir, f"{os.path.splitext(os.path.split(plyfile)[1])[0]}_{iply+1}.dat")
                args.sort = False
                args.uniq = False
                args.append = False
                io.output_lines(polygon_lines, args)
                print(f"shp2dat: '{plyfile}' >> '{args.outfile}'")









