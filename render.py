import bpy
import os
import sys
import numpy as np
import colorsys


def get_colors(num_colors):
    colors = []
    for i in np.arange(0., 360., 360. / num_colors):
        hue = i / 360.
        lightness = (50 + np.random.rand() * 10) / 100.
        saturation = (90 + np.random.rand() * 10) / 100.
        colors.append(colorsys.hls_to_rgb(hue, lightness, saturation))
    return np.array(colors)


def loadClusterVg(fn):
    pxyz = []
    colors = []
    lidx = []
    cidx = []
    with open(fn, "r") as fr:
        num_str = fr.readline().strip()
        pcount = int(num_str.split(':')[1])
        line = fr.readline().strip()
        line = line.split(' ')
        for i in range(pcount):
            pxyz.append([float(line[3 * i]), -float(line[3 * i + 2]), float(line[3 * i + 1])])
            '''line=fr.readline().strip()
            values = line.split()
            pxyz.append([float(values[0]),-float(values[2]),float(values[1])])'''

        num_str = fr.readline().strip()
        ccount = int(num_str.split(':')[1])
        line = fr.readline()
        # for i in range(ccount):
        #    line=fr.readline().strip()
        # color info is not needed

        num_str = fr.readline().strip()
        ncount = int(num_str.split(':')[1])
        line = fr.readline()
        # for i in range(ncount):
        #    line=fr.readline().strip()
        # normal info is not needed

        num_str = fr.readline().strip()
        gcount = int(num_str.split(':')[1])
        colors = get_colors(gcount)

        for i in range(gcount):
            fr.readline()  # group_type: 0
            fr.readline()  # num_group_parameters: 4

            fr.readline()  # group_parameters: xxx xxx xxx xxx

            fr.readline()  # group_label: unknown
            line = fr.readline().strip()  # group_color
            # c_str = line.split(' ')
            # colors.append([float(c_str[1]),float(c_str[2]),float(c_str[3])])

            line = fr.readline().strip()
            gpcount = int(line.split(':')[1])
            # print(gpcount)
            gpcount = int(gpcount / 2)
            line = fr.readline().strip()
            line = line.split(' ')
            for j in range(gpcount):
                lidx.append([int(line[j * 2]), int(line[j * 2 + 1])])
                cidx.append(i)
            fr.readline()  # num_children: 0

    return np.array(pxyz), np.array(colors, dtype='float'), np.array(lidx), np.array(cidx)


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

    return np.array(pointset), np.array(colors, dtype='float') / 255, np.array(lidx), np.array(cidx)


def createLS(pointset, colors, lidx, cidx):
    mats = []
    # print(colors)
    for i in range(len(colors)):
        mat = bpy.data.materials.new(name='Material for cluster ({0:0>2d})'.format(i))
        # mat.diffuse_color = (float(colors[i][0])/255, float(colors[i][1])/255, float(colors[i][2])/255, 1.0)
        # get the nodes
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        # clear all nodes to start clean
        nodes.clear()
        # create emission node
        node_emission = nodes.new(type='ShaderNodeEmission')
        node_emission.inputs[0].default_value = (*colors[i], 1)  # RGBA
        # node_emission.inputs[1].default_value = 1.0 # strength
        # create output node
        node_output = nodes.new(type='ShaderNodeOutputMaterial')
        # link nodes
        links = mat.node_tree.links
        link = links.new(node_emission.outputs[0], node_output.inputs[0])
        mats.append(mat)

    bpy.ops.curve.primitive_bezier_curve_add()
    bcobj = bpy.context.object
    for i in range(len(lidx)):
        print(i)
        # add a curve to link them together
        bcurve = bcobj.copy()
        bcurve.data = bcobj.data.copy()

        bcurve.data.dimensions = '3D'
        bcurve.data.fill_mode = 'FULL'
        bcurve.data.bevel_depth = 0.002
        bcurve.data.bevel_resolution = 4
        bcurve.data.resolution_u = 1
        # set first point to centre of sphere1
        bcurve.data.splines[0].bezier_points[0].co = (
            pointset[lidx[i][0]][0], pointset[lidx[i][0]][1], pointset[lidx[i][0]][2])  # (-1,-1,0)
        bcurve.data.splines[0].bezier_points[0].handle_left_type = 'VECTOR'
        # set second point to centre of sphere2
        bcurve.data.splines[0].bezier_points[1].co = (
            pointset[lidx[i][1]][0], pointset[lidx[i][1]][1], pointset[lidx[i][1]][2])  # (1,1,0)
        bcurve.data.splines[0].bezier_points[1].handle_left_type = 'VECTOR'
        bcurve.data.materials.append(mats[(cidx[i] + 11) % len(colors)])
        # bpy.ops.object.convert(target='MESH')

        bpy.context.collection.objects.link(bcurve)

    # bpy.context.scene.update() error in 2.9?
    bpy.context.view_layer.update()  # only once

    # remove initial
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['BezierCurve'].select_set(True)
    bpy.ops.object.delete()

    # convert to mesh and combine
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='CURVE')
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.join()


if __name__ == '__main__':
    # Set render engine
    '''bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.view_settings.view_transform = 'Standard' '''
    # pointset,colors,lidx,cidx=loadClusterPly(r'D:\Cha0s\Workspace\Blender_rendering\Line2Plane\data\DJI_cluster.ply')
    pointset, colors, lidx, cidx = loadClusterVg(
        r'D:\Cha0s\Workspace\Blender_rendering\Line2Plane\data\vg\timber_house_cut.vg')
    createLS(pointset, colors, lidx, cidx)

