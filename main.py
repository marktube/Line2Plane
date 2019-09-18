# -*- coding: utf-8 -*-
import sys
sys.path.append(r'E:\Workspace\Line2Plane\models')
import LScene


input_file=r'E:\Workspace\Line2Plane\data\DJI_modified.obj'
output_file=input_file[:-3]+"vg"

test=LScene.LScene()
test.readObjFile(input_file)
test.Cluster(41)
test.drawScene()

print("writing output file")
test.saveSceneAsVG(output_file)
print("done")