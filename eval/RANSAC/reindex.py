import open3d as o3d
import numpy as np
import colorsys
import matplotlib.pyplot as plt

def readObj(fn):
    vx = []
    lidx = []
    with open(fn, "r") as f:
        for line in f:
            if line.startswith('#'): continue
            elif line.startswith('v'):
                values = line.strip().split(' ')
                v = [float(x) for x in values[1:4]]
                vx.append(v)
            elif line.startswith('f'):
                values = line.split(' ')
                idx = [int(x) for x in values[1:4]]
                if idx[1] == idx[2]:
                    lidx.append([idx[0] - 1, idx[1] - 1])
            elif line.startswith('l'):
                values = line.split(' ')
                idx = [int(x) for x in values[1:]]
                lidx.append([idx[0] - 1, idx[1] - 1])
            #else:
            # add other type for mesh
    return np.array(vx), np.array(lidx)


def readVg(fn, vx):
    xyz = []
    labels = - np.ones(len(vx), dtype=int)
    with open(fn, "r") as fr:
        num_str = fr.readline().strip()
        pcount = int(num_str.split(' ')[1])
        for i in range(pcount):
            line = fr.readline().strip()
            values = line.split(' ')
            v = [float(x) for x in values]
            xyz.append(v)

        line = fr.readline() # color
        line = fr.readline() # normal

        num_str = fr.readline().strip()
        gcount = int(num_str.split(':')[1])

        for i in range(gcount):
            fr.readline()  # group_type: 0
            fr.readline()  # num_group_parameters: 4
            fr.readline()  # group_parameters: xxx xxx xxx xxx
            fr.readline()  # group_label: unknown
            fr.readline()  # group_color

            line = fr.readline().strip()
            gpcount = int(line.split(':')[1])
            line = fr.readline().strip()
            line = line.split(' ')
            for j in range(gpcount):
                it = xyz[int(line[j])]
                dis = vx - it
                dis = np.sum(np.square(dis), axis=-1)
                minid = np.argmin(dis)
                labels[minid] = i
            fr.readline()  # num_children: 0
    return labels

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

def show_ransac_cluster(vertices, lidx, labels):
    llabels = []
    for i in range(len(lidx)):
        l1 = labels[lidx[i][0]]
        l2 = labels[lidx[i][1]]
        if l1 == l2:
            llabels.append(l1)
        else:
            print(f'l1: {l1} l2: {l2}')
            llabels.append(-1)

    max_label = labels.max()
    llabels = np.array(llabels)
    drawRes(vertices, lidx, llabels, max_label)

    return llabels, max_label + 1

def run_reindex(opath, vpath):
    vx, lidx = readObj(opath)
    labels = readVg(vpath, vx)
    pred_labels, pred_num = show_ransac_cluster(vx, lidx, labels)
    save_cluster_vg(opath[:-4] + '_pr_res.vg', vx, lidx, pred_labels, pred_num)
    #np.savetxt(opath[:-4] + '_pr.txt', pred_labels, fmt="%d")


if __name__ == '__main__':
    #print(o3d.__version__)
    #run_reindex('/home/hiko/Downloads/data/dispatch/other_ball1_line.obj', '/home/hiko/Downloads/output/other_ball1_line.vg')
    #run_reindex('/home/hiko/Downloads/data/dispatch/Fig103_line.obj', '/home/hiko/Downloads/output/Fig103_line.vg')
    #run_reindex('/home/hiko/Downloads/data/dispatch/toy_data2_line.obj', '/home/hiko/Downloads/output/toy_data2_line.vg')
    #run_reindex('/home/hiko/Downloads/data/real/Line3D++_office_crop_line.obj','/home/hiko/Downloads/output/Line3D++_office_crop_line.vg')
    run_reindex('/home/hiko/Downloads/data/real/LSD_sixuegongyu_cut_line.obj', '/home/hiko/Downloads/output/LSD_sixuegongyu_cut_line.vg')
