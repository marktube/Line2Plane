# -*- coding: utf-8 -*-
import sys
sys.path.append(r'E:\Workspace\Line2Plane\models')
import LScene


test=LScene.LScene()
test.readObjFile(r'E:\Workspace\Line2Plane\data\DJI_cut.obj')
test.Cluster(19)
test.drawScene()