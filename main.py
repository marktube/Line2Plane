# -*- coding: utf-8 -*-
import sys
sys.path.append('../models')
import LScene


input_file='data/line_segments_3d_clustered_allpics_11_5_18.obj'
output_file=input_file[:-3]+"vg"

test=LScene.LScene()
test.readObjFile(input_file)
test.Cluster(11)
test.drawScene()

print("writing output file")
test.saveSceneAsVG(output_file)
print("done")