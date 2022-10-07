# -*- coding: utf-8 -*-
import sys
import os
import argparse
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'models'))
from models.LScene import LScene

parser = argparse.ArgumentParser()
parser.add_argument('--volume', type=int, default=17, help='Volumes to use [default: volume 2]')
parser.add_argument('--line_data', default='/home/hiko/Workspace/Line2Plane/data/BJ39_500_100048_0045/3dline_uncluster_song_cut.obj', help='Line data input filepath [default: ]')
parser.add_argument('--out', default='', help='Line data output filepath [default: {input filepath_[volume]}.vg]')
parser.add_argument('--gui', default='true', help='true or false for showing graphic result [default: false]')
parser.add_argument('--sr', default=1.0, help='sigma ratio can control the variance [default: 1.0]')
FLAGS = parser.parse_args()

NUM_VOLUMES=FLAGS.volume
LINE_DATA=FLAGS.line_data
OUTPUT=FLAGS.out
IS_GUI=FLAGS.gui
SR=FLAGS.sr

if not os.path.exists(LINE_DATA):
    print('Error: input file not exist')
    exit(0)
if NUM_VOLUMES<2:
    print('Error: volume<2')
    exit(0)
if not OUTPUT:
    OUTPUT=LINE_DATA[:-4]+"_"+str(NUM_VOLUMES)+".vg"
    OUTPUT_ply=LINE_DATA[:-4]+"_"+str(NUM_VOLUMES)+".ply"
if IS_GUI=='true':
    IS_GUI=True
else:
    IS_GUI=False

test=LScene(SR)
test.readObjFile(LINE_DATA)
test.Cluster(NUM_VOLUMES)

if IS_GUI:
    test.drawScene()

print("writing output file")
test.saveSceneAsVG(OUTPUT)
#test.saveClusterAsPly(OUTPUT_ply)
print("done")