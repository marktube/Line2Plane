import open3d as o3d
import numpy as np
import colorsys
import matplotlib.pyplot as plt

def get_colors(num_colors):
    colors=[]
    if num_colors <= 1:
        return [[1,0,0]]
    for i in np.arange(0., 360., 360. / num_colors):
        hue = i/360.
        lightness = (50 + np.random.rand() * 10)/100.
        saturation = (90 + np.random.rand() * 10)/100.
        colors.append(colorsys.hls_to_rgb(hue, lightness, saturation))
    return colors

def save_cluster_vg(fn, xyz, lidx, labels, max_label):
    colors = plt.get_cmap("tab20")(labels / (max_label if max_label > 0 else 1))
    colors[labels < 0] = 0
    with open(fn, 'w') as fo:
        num_points = len(xyz)
        fo.write(f"num_points: {num_points}\n")
        for i in range(num_points):
            fo.write(f"{xyz[i][0]} {xyz[i][1]} {xyz[i][2]}\n")

        fo.write("num_colors: 0\n")
        fo.write("num_normals: 0\n")

        fo.write(f"num_groups: {max_label+2}\n")
        for i in range(-1, max_label+1):
            fo.write("group_type: 0\n")
            fo.write("num_group_parameters: 4\n")
            fo.write("group_parameters: 0 0 0 0\n")
            fo.write("group_label: unknown\n")
            fo.write(f"group_color: {colors[i][0]} {colors[i][1]} {colors[i][2]}\n")
            members_id = np.where(labels == i)
            members_id = members_id[0]
            fo.write("group_num_points: %d\n" % (2 * len(members_id)))
            for j in members_id:
                fo.write("%d %d " % (lidx[j][0], lidx[j][1]))
            fo.write("\n")
            fo.write("num_children: 0\n")

def readObj(fn):
    vx = []
    lidx = []
    #gt = []
    with open(fn, "r") as f:
        for line in f:
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = [float(x) for x in values[1:4]]
                vx.append(v)
            elif values[0] == 'f':
                idx = [int(x) for x in values[1:4]]
                if idx[1] == idx[2]:
                    lidx.append([idx[0] - 1, idx[1] - 1])
            elif values[0] == 'l':
                idx = [int(x) for x in values[1:]]
                lidx.append([idx[0] - 1, idx[1] - 1])
            #else:
            # add other type for mesh
    return vx,lidx

def drawRes(xyz, lidx, labels, max_label):
    colors = plt.get_cmap("tab20")(labels / (max_label if max_label > 0 else 1))
    colors[labels < 0] = 0
    line_set = o3d.geometry.LineSet()
    line_set.points = o3d.utility.Vector3dVector(xyz)
    line_set.lines = o3d.utility.Vector2iVector(lidx)
    line_set.colors = o3d.utility.Vector3dVector(colors[:, :3])
    o3d.visualization.draw_geometries([line_set])

def show_dbscan_cluster(xyz, lidx):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(xyz)
    with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Debug) as cm:
        labels = np.array(pcd.cluster_dbscan(eps=1.6, min_points=5, print_progress=True))
    max_label = labels.max()
    print(f"point cloud has {max_label + 1} clusters")
    #for i in range(max_label):
    #    print(f"cluster {i} has {np.sum(labels==i)} members")
    llabels = []
    for i in range(len(lidx)):
        l1 = labels[lidx[i][0]]
        l2 = labels[lidx[i][1]]
        if l1 == l2:
            llabels.append(l1)
        else:
            if l1<0 or l2<0:
                if l1<0:
                    llabels.append(l2)
                else:
                    llabels.append(l1)
            else:
                print(f'l1: {l1} l2: {l2}')
                llabels.append(-1)
    llabels = np.array(llabels)
    drawRes(xyz, lidx, llabels, max_label)

    return llabels, max_label+1


def run_test(filepath):
    vertices, lidx = readObj(filepath)
    pred_labels, pred_num = show_dbscan_cluster(vertices, lidx)
    save_cluster_vg(filepath[:-4]+'_db.vg', vertices, lidx, pred_labels, pred_num)
    np.savetxt(filepath[:-4] + '_db.txt', pred_labels, fmt="%d")


if __name__ == '__main__':
    #print(o3d.__version__)
    run_test('/home/hiko/Downloads/data/dispatch/Fig103_line.obj')
