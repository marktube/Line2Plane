import bpy
import os
import sys
import numpy as np

def loadClusterPly(fn):
    pointset = []
    colors = []
    cidx = []
    lidx = []

    with open(fn, "r") as freader:
        header = True
        vertices_count = 0
        colors_count = 0
        edges_count = 0
        while header:
            line = freader.readline()
            str = line.strip().split(' ')
            if str[0] == 'element':
                if str[1] == 'vertex':
                    vertices_count = int(str[2])
                elif str[1] == 'color':
                    colors_count = int(str[2])
                elif str[1] == 'edge':
                    edges_count = int(str[2])
            elif str[0] == 'end_header':
                header = False
            # otherwise continue
        for i in range(vertices_count):
            line = freader.readline()
            numbers = line.strip().split(' ')
            pt = []
            pt.append(float(numbers[0]))
            pt.append(float(numbers[1]))
            pt.append(float(numbers[2]))
            pointset.append(pt)

        for i in range(colors_count):
            line = freader.readline()
            numbers = line.strip().split(' ')
            col = []
            col.append(int(numbers[0]))
            col.append(int(numbers[1]))
            col.append(int(numbers[2]))
            colors.append(col)

        for i in range(edges_count):
            line = freader.readline()
            numbers = line.strip().split(' ')
            lid = []
            lid.append(int(numbers[0]))
            lid.append(int(numbers[1]))
            lidx.append(lid)
            cidx.append(int(numbers[2]))

    return np.array(pointset),np.array(colors),np.array(lidx),np.array(cidx)


def createLS(pointset, colors, lidx, cidx):
    mats = []
    #print(colors)
    for i in range(len(colors)):
        mat = bpy.data.materials.new(name='Material for cluster ({0:0>2d})'.format(i))
        mat.diffuse_color = (float(colors[i][0])/255, float(colors[i][1])/255, float(colors[i][2])/255, 1.0)
        mats.append(mat)

    for i in range(len(lidx)):
        # add a curve to link them together
        bpy.ops.curve.primitive_bezier_curve_add()
        obj = bpy.context.object
        obj.data.dimensions = '3D'
        obj.data.fill_mode = 'FULL'
        obj.data.bevel_depth = 0.005
        obj.data.bevel_resolution = 4
        obj.data.resolution_u = 1
        # set first point to centre of sphere1
        obj.data.splines[0].bezier_points[0].co = (
        pointset[lidx[i][0]][0], pointset[lidx[i][0]][1], pointset[lidx[i][0]][2])  # (-1,-1,0)
        obj.data.splines[0].bezier_points[0].handle_left_type = 'VECTOR'
        # set second point to centre of sphere2
        obj.data.splines[0].bezier_points[1].co = (
        pointset[lidx[i][1]][0], pointset[lidx[i][1]][1], pointset[lidx[i][1]][2])  # (1,1,0)
        obj.data.splines[0].bezier_points[1].handle_left_type = 'VECTOR'
        obj.data.materials.append(mats[cidx[i]])
        bpy.ops.object.convert(target='MESH')
        
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.join()



if __name__ == '__main__':
    # Set render engine
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.view_settings.view_transform = 'Standard'
    pointset,colors,lidx,cidx=loadClusterPly('/home/hiko/Workspace/Line2Plane/data/DJI_test_res.ply')
    createLS(pointset,colors,lidx,cidx)

