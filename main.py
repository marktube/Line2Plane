# -*- coding: utf-8 -*-
import sys
sys.path.append('../models')
import LScene


input_file='data/cube.obj'
output_file=input_file[:-3]+"vg"

test=LScene.LScene()
test.readObjFile(input_file)
test.Cluster(2)
test.drawScene()

print("writing output file")
test.saveSceneAsVG(output_file)
print("done")