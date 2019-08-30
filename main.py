# -*- coding: utf-8 -*-
import sys
sys.path.append(r'E:\Workspace\Line2Plane\models')
import LScene


test=LScene.LScene()
test.readObjFile(r'E:\Workspace\Line2Plane\data\DJI_modified.obj')
test.Cluster(13)
test.drawScene()