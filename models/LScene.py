# -*- coding: utf-8 -*-
import LGeometry
import LEM
import numpy as np
import open3d as o3d
import colorsys

def get_colors(num_colors):
    colors=[]
    for i in np.arange(0., 360., 360. / num_colors):
        hue = i/360.
        lightness = (50 + np.random.rand() * 10)/100.
        saturation = (90 + np.random.rand() * 10)/100.
        colors.append(colorsys.hls_to_rgb(hue, lightness, saturation))
    return colors

class LScene:
    def __init__(self):
        self.vertices=[]
        self.lines=[]
        self.planes=[]
        self.max_coord=np.zeros(3)
        self.min_coord=np.zeros(3)

    # read lines .obj file
    def readObjFile(self, filePath):
        f=open(filePath, "r")
        for line in f:
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = [float(x) for x in values[1:4]]
                vx = LGeometry.LVertex(v[0],v[1],v[2])
                self.vertices.append(vx)
                #set max and min coord
                if self.max_coord[0]==0:
                    self.max_coord[0] = v[0]
                else:
                    self.max_coord[0] = v[0] if v[0]>self.max_coord[0] else self.max_coord[0]
                if self.min_coord[0]==0:
                    self.min_coord[0] = v[0]
                else:
                    self.min_coord[0] = v[0] if v[0]<self.min_coord[0] else self.min_coord[0]

                if self.max_coord[1]==0:
                    self.max_coord[1] = v[1]
                else:
                    self.max_coord[1] = v[1] if v[1]>self.max_coord[1] else self.max_coord[1]
                if self.min_coord[1]==0:
                    self.min_coord[1] = v[1]
                else:
                    self.min_coord[1] = v[1] if v[1]<self.min_coord[1] else self.min_coord[1]

                if self.max_coord[2]==0:
                    self.max_coord[2] = v[2]
                else:
                    self.max_coord[2] = v[2] if v[2]>self.max_coord[2] else self.max_coord[2]
                if self.min_coord[2]==0:
                    self.min_coord[2] = v[2]
                else:
                    self.min_coord[2] = v[2] if v[2]<self.min_coord[2] else self.min_coord[2]
            elif values[0] == 'f':
                id = [int(x) for x in values[1:4]]
                if id[1]==id[2]:
                    id[0]=id[0]-1
                    id[1]=id[1]-1
                    self.lines.append(LGeometry.LLine(id[0], id[1]))
                #else:
                #todo:add other type for mesh
        f.close()
        return

    # draw points, lines and planes
    def drawScene(self):
        points = []
        for v in self.vertices:
            points.append(v.getCoordinate())
        colors = []
        lines = []
        candicate_colors=get_colors(len(self.planes))
        for j in range(len(candicate_colors)):
            for lid in self.planes[j].members_id:
                lines.append(self.lines[lid].getVidSet())
                colors.append(candicate_colors[j])
        line_set = o3d.geometry.LineSet()
        line_set.points = o3d.utility.Vector3dVector(points)
        line_set.lines = o3d.utility.Vector2iVector(lines)
        line_set.colors = o3d.utility.Vector3dVector(colors)
        o3d.visualization.draw_geometries([line_set])

    def initSet(self):
        #todo init
        pass

    # cluster lines
    def Cluster(self, cluster_count):
        model=LEM.LEM(cluster_count, self.min_coord, self.max_coord)
        model.iter(16,self.lines,self.vertices)
        cluster_count = cluster_count * 3
        for j in range(cluster_count):
            tmp = LGeometry.LPlane(model.f_v[j], model.f_n[j])
            self.planes.append(tmp)
        response=model.expect(self.lines, self.vertices)
        for i in range(len(self.lines)):
            id = np.argmax(response[i])
            self.planes[id].members_id.append(i)
        #drop empty face
        self.planes = [p for p in self.planes if len(p.members_id)!=0]
        print('Filter done')
