import time as time
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.neighbors import kneighbors_graph
import colorsys
import matplotlib.pyplot as plt
import open3d as o3d
import mpl_toolkits.mplot3d  # noqa: F401

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
    return np.array(vx),lidx

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

def drawRes(xyz, lidx, labels, max_label):
    colors = plt.get_cmap("tab20")(labels / (max_label if max_label > 0 else 1))
    colors[labels < 0] = 0
    line_set = o3d.geometry.LineSet()
    line_set.points = o3d.utility.Vector3dVector(xyz)
    line_set.lines = o3d.utility.Vector2iVector(lidx)
    line_set.colors = o3d.utility.Vector3dVector(colors[:, :3])
    o3d.visualization.draw_geometries([line_set])

def show_hierachy_cluster(X, lidx):
    print("Compute unstructured hierarchical clustering...")
    st = time.time()
    ward = AgglomerativeClustering(n_clusters=6, linkage="ward").fit(X)
    elapsed_time = time.time() - st
    label = ward.labels_
    print(f"Elapsed time: {elapsed_time:.2f}s")
    print(f"Number of points: {label.size}")
    connectivity = kneighbors_graph(X, n_neighbors=10, include_self=False)
    print("Compute structured hierarchical clustering...")
    st = time.time()
    ward = AgglomerativeClustering(
        n_clusters=6, connectivity=connectivity, linkage="ward"
    ).fit(X)
    elapsed_time = time.time() - st
    label = ward.labels_
    print(f"Elapsed time: {elapsed_time:.2f}s")
    print(f"Number of points: {label.size}")
    max_label = label.max()
    print(f"point cloud has {max_label + 1} clusters")

    '''fig2 = plt.figure()
    ax2 = fig2.add_subplot(121, projection="3d", elev=7, azim=-80)
    ax2.set_position([0, 0, 0.95, 1])
    for l in np.unique(label):
        ax2.scatter(
            X[label == l, 0],
            X[label == l, 1],
            X[label == l, 2],
            color=plt.cm.jet(float(l) / np.max(label + 1)),
            s=20,
            edgecolor="k",
        )
    fig2.suptitle(f"With connectivity constraints (time {elapsed_time:.2f}s)")

    plt.show()'''

    llabels = []
    for i in range(len(lidx)):
        l1 = label[lidx[i][0]]
        l2 = label[lidx[i][1]]
        if l1 == l2:
            llabels.append(l1)
        else:
            print(f'l1: {l1} l2: {l2}')
            llabels.append(-1)

    llabels = np.array(llabels)
    drawRes(X, lidx, llabels, max_label)

    return llabels, max_label + 1

def run_test(filepath):
    vertices, lidx = readObj(filepath)
    pred_labels, pred_num = show_hierachy_cluster(vertices, lidx)
    save_cluster_vg(filepath[:-4] + '_hc.vg', vertices, lidx, pred_labels, pred_num)
    #np.savetxt(filepath[:-4] + '_hc.txt', pred_labels, fmt="%d")

if __name__ == '__main__':
    #run_test('/home/hiko/Downloads/data/real/LSD_sixuegongyu_cut.obj')
    #run_test('/home/hiko/Downloads/data/real/Line3D++_office_crop.obj')
    run_test('/home/hiko/Downloads/data/dispatch/Fig103_line.obj')
    #run_test('/home/hiko/Downloads/data/dispatch/other_ball1_line.obj')
    #run_test('/home/hiko/Downloads/data/dispatch/toy_data2_line.obj')