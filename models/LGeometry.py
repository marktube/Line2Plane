# -*- coding: utf-8 -*-
import numpy as np

class LVertex:
    def __init__(self, x=0, y=0, z=0):
        self.x=x
        self.y=y
        self.z=z

    def getCoordinate(self):
        return [self.x,self.y,self.z]

class LLine:
    def __init__(self, id1=0, id2=0):
        self.id1=id1
        self.id2=id2

    def getDirection(self, vertices):
        d=np.array([vertices[self.id1].x-vertices[self.id2].x,vertices[self.id1].y-vertices[self.id2].y,vertices[self.id1].z-vertices[self.id2].z])
        return d

    def getVertexCoordinateStart(self, vertices):
        return vertices[self.id1].getCoordinate()

    def getVertexCoordinateEnd(self, vertices):
        return vertices[self.id2].getCoordinate()

    def getVidSet(self):
        return [self.id1, self.id2]

class LPlane:
    def __init__(self, point, normal, corr=np.zeros([3,3])):
        self.point=point
        self.normal=normal
        self.members_id=[]
        self.corr=corr

    def add_support_line(self, line_id):
        self.members_id.append(line_id)