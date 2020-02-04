import os, sys
import subprocess
import shlex
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import argparse
from shlex import quote
import re

# ./stitch -o map_55_12_56_13_z12.png  -- 55 12 56 13  12  http://a.tile.openstreetmap.org/{z}/{x}/{y}.png

parser = argparse.ArgumentParser()
#parser.add_argument( '-a', "--anon", action='store_true', default=False, help='Anonymous axes' )
parser.add_argument( '-E', "--east",  type=int, default=13, help='This many days ago (14)' )
parser.add_argument( '-N', "--north", type=int, default=57, help='This many days ago (14)' )
parser.add_argument( '-S', "--south", type=int, default=56, help='This many days ago (14)' )
parser.add_argument( '-W', "--west",  type=int, default=12, help='This many days ago (14)' )
parser.add_argument( '-t', "--tiles", type=str, default="http://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
                     help='Full date string' )
parser.add_argument( '-z', "--zoom",  type=int, default=8, help='This many days ago (14)' )
parser.add_argument( "--dry", action='store_true', default=False, help='Dry run' )
args = parser.parse_args()

def run_command(command):
    print( command )
    process = subprocess.Popen(command, stderr=subprocess.PIPE)
    while True:
        output = process.stderr.readline().decode()
        if output == '' and process.poll() is not None:
            break
        if "==" in output:
            m = re.search(r'Raster Size: (\d+)x(\d+)', output)
            #print( m )
            if m:
                #print( m )
                png_w = m.group(1)
                png_h = m.group(2)
                #print( png_w, png_h )
        print( output.strip() )
    rc = process.poll()
    return rc, png_w, png_h

now_dt = datetime.now()

map_base = "map_" + str(args.south) + '_' + str(args.west) + '_' +str(args.north) + '_' +str(args.east) + '_z' +str(args.zoom)
map_name = map_base + ".png"
map_map  = map_base + ".map"

invocation = "./stitch -o " + map_name + ' -- ' +\
    str(args.south) + ' ' +\
    str(args.west)  + ' ' +\
    str(args.north) + ' ' +\
    str(args.east)  + ' ' +\
    str(args.zoom)  + ' ' +\
    args.tiles

cmd = shlex.split( invocation )
print( cmd )
res, png_w, png_h = run_command( cmd )
if res != 0:
    print( "ERROR" )
    sys.exit(1)
print( res, png_w, png_h )

# Post process
# convert IMG -colors 16 (-colorspace gray)  -normalize NEWIMG ->does not load.
# for f in '*png'; do echo $f; mogrify -normalize $f;done
'''
BITMAP_NAME     map06z10.png
WIDTH          3787
HEIGHT         3111 
LON_WEST        2.8
LON_EAST        8.0
LAT_SOUTH       51.2
LAT_NORTH       53.8
'''
with open(map_map, "w") as f:
    f.write( "BITMAP_NAME"+map_name+"\n" )
    f.write( "WIDTH      "+png_w+"\n" )
    f.write( "HEIGHT     "+png_h+"\n" )
    f.write( "LON_WEST   "+str(args.west)+"\n" )
    f.write( "LON_EAST   "+str(args.east)+"\n" )
    f.write( "LAT_SOUTH  "+str(args.south)+"\n" )
    f.write( "LAT_NORTH  "+str(args.north)+"\n" )
print( map_name, map_map )



