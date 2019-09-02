# -*- coding: utf-8 -*-
import sys
sys.path.append(r'E:\Workspace\Line2Plane\models')
import LScene


test=LScene.LScene()
test.readObjFile(r'E:\Workspace\Line2Plane\data\line_segments_3d_clustered_allpics_11_5_18.obj')
test.initPlaneSet()
test.drawScene()