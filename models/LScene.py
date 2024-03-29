# -*- coding: utf-8 -*-
import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
import numpy as np
import open3d as o3d
import colorsys
import LEM

def get_colors(num_colors):
    colors=[]
    for i in np.arange(0., 360., 360. / num_colors):
        hue = i / 360.
        lightness = (50 + np.random.rand() * 10)/100.
        saturation = (90 + np.random.rand() * 10)/100.
        colors.append(colorsys.hls_to_rgb(hue, lightness, saturation))
    return np.array(colors)

class LScene:
    def __init__(self, sr):
        self.vertices=None
        self.lines=None
        self.planes=None
        self.cluster_id=None
        self.max_coord=None
        self.min_coord=None
        self.sigma_ration=sr

    # read lines .obj file
    def readObjFile(self, filePath):
        vx = []
        lidx = []
        with open(filePath, "r") as f:
            for line in f:
                if line.startswith('#'): continue
                values = line.split()
                if not values: continue
                if values[0] == 'v':
                    v = [float(x) for x in values[1:4]]
                    vx.append(v)
                elif values[0] == 'f':
                    idx = [int(x) for x in values[1:4]]
                    if idx[1]==idx[2]:
                        lidx.append([idx[0]-1, idx[1]-1])
                elif values[0] == 'l':
                    idx = [int(x) for x in values[1:]]
                    lidx.append([idx[0]-1, idx[1]-1])
                #else:
                #todo:add other type for mesh
        self.vertices = np.array(vx,dtype=float)
        self.lines = np.array(lidx,dtype=int)
        self.min_coord = np.min(self.vertices, axis=0)
        self.max_coord = np.max(self.vertices, axis=0)
        return

    def drawPoints(self,xyz):
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(xyz)
        o3d.visualization.draw_geometries([pcd])

    # draw points, lines and planes
    def drawScene(self):
        '''colors = []
        lines = []
        candicate_colors=get_colors(len(self.planes))
        np.random.seed(7)
        shuffled_id = np.random.permutation(len(self.planes))
        for j in range(len(candicate_colors)):
            for lid in self.planes[j].members_id:
                colors.append(candicate_colors[shuffled_id[j]])'''
        candicate_colors=get_colors(np.max(self.cluster_id)+1)
        colors = candicate_colors[self.cluster_id]
        line_set = o3d.geometry.LineSet()
        line_set.points = o3d.utility.Vector3dVector(self.vertices)
        line_set.lines = o3d.utility.Vector2iVector(self.lines)
        line_set.colors = o3d.utility.Vector3dVector(colors)
        o3d.visualization.draw_geometries([line_set])

    # cluster lines
    def Cluster(self, volume):
        model = LEM.LEM(volume, self.min_coord, self.max_coord, self.sigma_ration)
        p1xyz = self.vertices[self.lines[:, 0]]
        p2xyz = self.vertices[self.lines[:, 1]]
        self.planes, self.cluster_id = model.iter(180, p1xyz, p2xyz)
        print('Filter done')

    def saveClusterAsPly(self, filePath):
        with open(filePath, "w") as fo:
            fo.write('ply\n')
            fo.write("format ascii 1.0\n")
            fo.write("comment generated by chao\n")
            fo.write("element vertex {}\n".format(self.vertices.shape[0]))
            fo.write("property float x\n")
            fo.write("property float y\n")
            fo.write("property float z\n")
            fo.write("property uchar red\n")
            fo.write("property uchar green\n")
            fo.write("property uchar blue\n")
            fo.write("element edge {}\n".format(len(self.lines)))
            fo.write("property int vertex1\n")
            fo.write("property int vertex2\n")
            fo.write("end_header\n")

            candicate_colors = get_colors(np.max(self.cluster_id) + 1)
            cluster = np.zeros(len(self.vertices), dtype=int)
            cluster[self.lines[:, 0]] = self.cluster_id
            cluster[self.lines[:, 1]] = self.cluster_id
            for i in range(len(self.vertices)):
                fo.write("%f %f %f %d %d %d\n"%(self.vertices[i][0], self.vertices[i][1], self.vertices[i][2],
                                                candicate_colors[cluster[i]][0]*255,candicate_colors[cluster[i]][1]*255,
                                                candicate_colors[cluster[i]][2]*255))
            for i in range(len(self.lines)):
                fo.write("{} {}\n".format(self.lines[i][0], self.lines[i][1]))


    def saveSceneAsVG(self, filePath):
        #np.savetxt(filePath[:-5] + 'ours.txt', self.cluster_id, fmt="%d") # use for comparing with GT
        with open(filePath, "w") as fo:
            fo.write("num_points: %d\n"%len(self.vertices))
            for i in range(self.vertices.shape[0]):
                fo.write("%f %f %f\n"%(self.vertices[i][0], self.vertices[i][1], self.vertices[i][2]))

            candicate_colors = get_colors(np.max(self.cluster_id)+1)

            fo.write("num_colors: 0\n")

            fo.write("num_normals: 0\n")

            fo.write("num_groups: %d\n" % len(self.planes))
            for i in range(len(self.planes)):
                fo.write("group_type: 0\n")
                fo.write("num_group_parameters: 4\n")
                fo.write("group_parameters: %f %f %f %f\n"%(self.planes[i][0], self.planes[i][1],
                                                        self.planes[i][2], self.planes[i][3]))
                fo.write("group_label: unknown\n")
                fo.write("group_color: %f %f %f\n"%(candicate_colors[self.cluster_id[i]][0],
                                                    candicate_colors[self.cluster_id[i]][1],
                                                    candicate_colors[self.cluster_id[i]][2]))
                members_id = np.where(self.cluster_id==i)
                members_id = members_id[0]
                fo.write("group_num_points: %d\n"%(2*len(members_id)))
                for j in members_id:
                    fo.write("%d %d "%(self.lines[j][0],self.lines[j][1]))
                fo.write("\n")
                fo.write("num_children: 0\n")
