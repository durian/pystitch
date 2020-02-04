import os, sys
import subprocess
import shlex
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import argparse
from shlex import quote
import re

# Needs https://github.com/ericfischer/tile-stitch installed.
# ./stitch -o map_55_12_56_13_z12.png  -- 55 12 56 13  12  http://a.tile.openstreetmap.org/{z}/{x}/{y}.png

# Example:
#   python pystitch.py -z 6 -S 50 -N 60 -W 0 -E 15 -t 'https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png'

# Shading:
#   python pystitch.py  -t 'https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png'

parser = argparse.ArgumentParser()
parser.add_argument( '-E', "--east",  type=float, default=13, help='East coordinate.' )
parser.add_argument( '-N', "--north", type=float, default=57, help='North coordinate.' )
parser.add_argument( '-S', "--south", type=float, default=56, help='South coordinate.' )
parser.add_argument( '-W', "--west",  type=float, default=12, help='West coordinate.' )
parser.add_argument( '-x', "--extra",  type=str, default=None, help='Extra string for map name.' )
parser.add_argument( '-t', "--tiles", type=str, default="http://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
                     help='URL of tile server.' )
parser.add_argument( '-z', "--zoom",  type=int, default=8, help='Map zoom level.' )
parser.add_argument( '-d', "--dryrun", action='store_true', default=False, help='Dry run.' )
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

if args.extra:
    map_base = "map_" + args.extra + "_"
else:
    map_base = "map_" 
map_base = map_base + str(args.south) + '_' + str(args.west) + '_' +str(args.north) + '_' +str(args.east) + '_z' +str(args.zoom)
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

if args.dryrun:
    print( invocation )
    sys.exit(0)

if not os.path.exists( map_name ):
    res, png_w, png_h = run_command( cmd )
    if res != 0:
        print( "ERROR" )
        sys.exit(1)
    print( res, png_w, png_h )
else:
    print( "Exists, not downloading" )
    sys.exit(2)
    
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
    f.write( "BITMAP_NAME "+map_name+"\n" )
    f.write( "WIDTH       "+png_w+"\n" )
    f.write( "HEIGHT      "+png_h+"\n" )
    f.write( "LON_WEST    "+str(args.west)+"\n" )
    f.write( "LON_EAST    "+str(args.east)+"\n" )
    f.write( "LAT_SOUTH   "+str(args.south)+"\n" )
    f.write( "LAT_NORTH   "+str(args.north)+"\n" )
print( map_name, map_map )

'''
https://mc.bbbike.org/mc/?num=2&mt0=mapnik&mt1=mapnik-bw

python pystitch.py -S 53 -N 54 -W 11 -E 12  -t 'https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png' -z10 -x BW
python pystitch.py -S 53 -N 54 -W 12 -E 13  -t 'https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png' -z10 -x BW
python pystitch.py -S 53 -N 54 -W 13 -E 14  -t 'https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png' -z10 -x BW

python pystitch.py -S 54 -N 55 -W 11 -E 12  -t 'https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png' -z10 -x BW
python pystitch.py -S 54 -N 55 -W 12 -E 13  -t 'https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png' -z10 -x BW
python pystitch.py -S 54 -N 55 -W 13 -E 14  -t 'https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png' -z10 -x BW

python pystitch.py -S 55 -N 56 -W 11 -E 12  -t 'https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png' -z10 -x BW
python pystitch.py -S 55 -N 56 -W 12 -E 13  -t 'https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png' -z10 -x BW
python pystitch.py -S 55 -N 56 -W 13 -E 14  -t 'https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png' -z10 -x BW
'''
