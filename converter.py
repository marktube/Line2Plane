from PIL import Image
import os
import colorsys
import numpy as np
from sklearn import metrics
from scipy.spatial import Delaunay
from matplotlib import pyplot as plt
import math
from database import COLMAPDatabase
'''
Unless you pass in the Qhull option “QJ”, 
Qhull does not guarantee that each input point appears as 
a vertex in the Delaunay triangulation. 
Omitted points are listed in the coplanar attribute.
https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Delaunay.html
'''


def get_colors(num_colors):
    colors=[]
    for i in np.arange(0., 360., 360. / num_colors):
        hue = i / 360.
        lightness = (50 + np.random.rand() * 10)/100.
        saturation = (90 + np.random.rand() * 10)/100.
        colors.append(colorsys.hls_to_rgb(hue, lightness, saturation))
    return np.array(colors)

def png2jpg(path_prefix):
    filenames = os.listdir(path_prefix)
    print(len(filenames))
    for pngi in filenames:
        infile = os.path.join(path_prefix, pngi)
        outfile = infile[:-3] + 'jpg'
        im = Image.open(infile)
        im = im.convert('RGB')
        im.save(outfile, quality=95)

def format2jpg(path_prefix):
    filenames = os.listdir(path_prefix)
    print(len(filenames))
    for tgai in filenames:
        infile = os.path.join(path_prefix,tgai)
        outfile = infile[:-3]+'jpg'
        try:
            Image.open(infile).save(outfile)
            print(outfile)
        except IOError:
            print("cannot convert", infile)

def wire2line(fpath):
    pxyz = []
    lidx = []
    with open(fpath, 'r') as fr:
        for line in fr:
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = [float(x) for x in values[1:4]]
                pxyz.append(v)
            elif values[0] == 'f':
                lidx.append([int(values[1]),int(values[2])])
    with open(fpath[:-4] + '_line.obj', 'w') as fw:
        for i in range(len(pxyz)):
            fw.write('v %f %f %f\n'%(pxyz[i][0],pxyz[i][1],pxyz[i][2]))
        for i in range(len(lidx)):
            if lidx[i][0] > lidx[i][1]:
                fw.write('l %d %d\n' % (lidx[i][1], lidx[i][0]))
            elif lidx[i][0] == lidx[i][1]:
                continue
            else:
                fw.write('l %d %d\n'%(lidx[i][0],lidx[i][1]))

def line2wire(fpath):
    pxyz = []
    lidx = []
    with open(fpath, 'r') as fr:
        for line in fr:
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = [float(x) for x in values[1:4]]
                pxyz.append(v)
            elif values[0] == 'l':
                idx = [int(x) for x in values[1:]]
                lidx.append(idx)
    with open(fpath[:-4]+'_wire.obj','w') as fw:
        for i in range(len(pxyz)):
            fw.write('v %f %f %f\n'%(pxyz[i][0],pxyz[i][1],pxyz[i][2]))
        for i in range(len(lidx)):
            fw.write('f %d %d %d\n'%(lidx[i][0],lidx[i][1],lidx[i][1]))

def readVg(fn):
    pxyz = []
    gpara = []
    gmemid = []
    with open(fn, "r") as fr:
        num_str = fr.readline().strip()
        pcount = int(num_str.split(':')[1])
        #print(pcount)
        for i in range(pcount):
            line = fr.readline().strip()
            values = line.split(' ')
            pxyz.append([float(values[0]),float(values[1]),float(values[2])])
        #print(pxyz)

        num_str = fr.readline().strip()
        ccount = int(num_str.split(':')[1])
        #for i in range(ccount):
            #line=fr.readline().strip()
            # color info is not needed
        #print(ccount)

        num_str = fr.readline().strip()
        ncount = int(num_str.split(':')[1])
        #for i in range(ncount):
            #line=fr.readline().strip()
            # normal info is not needed
        #print(ncount)

        num_str = fr.readline().strip()
        gcount = int(num_str.split(':')[1])
        print(gcount)

        for i in range(gcount):
            fr.readline() # group_type: 0
            fr.readline()  # num_group_parameters: 4

            line = fr.readline().strip()
            values = line.split()
            gpara.append([float(values[1]), float(values[2]), float(values[3]),float(values[4])])

            fr.readline()  # group_label: unknown
            fr.readline()  # group_color

            line = fr.readline().strip()
            gpcount = int(line.split(':')[1])
            print(gpcount)
            line = fr.readline().strip()
            if gpcount == 0:
                gmemid.append([])
            else:
                membid = [int(n) for n in line.split(' ')]
                gmemid.append(membid)
            fr.readline()  # num_children: 0

    return np.array(pxyz), np.array(gpara), gmemid

def readGlobfit(fn):
    pxyz = []
    gpara = []
    gmemid = []
    with open(fn, "r") as fr:
        line = fr.readline()
        while line[0]=='#' or len(line)==0:
            line = fr.readline()
        numPoints = int(line.strip())
        print(f'num p: {numPoints}')
        while(numPoints>0):
            line = fr.readline()
            if line[0] == '#' or line[0]=='\n':
                continue
            numPoints -= 1
            values = line.strip().split(' ')
            pxyz.append([float(values[0]),float(values[1]),float(values[2])])

        line = fr.readline()
        while line[0]=='#' or line[0]=='\n':
            line = fr.readline()
        numPrimitives = int(line.strip())
        print(f'num pr: {numPrimitives}')
        for i in range(numPrimitives):
            line =  fr.readline().strip()
            while len(line)==0 or line[0] == '#':
                line = fr.readline()
            line = line
            values = line.split(' ')
            gpara.append([float(values[1]),float(values[2]),float(values[3]),float(values[4])])
            line =fr.readline()
            while line[0] == '#' or len(line)==0:
                line = fr.readline()
            line = line.strip()
            values = line.split(' ')
            tmp_mem = []
            for j in range(1,len(values)):
                tmp_mem.append(int(values[j]))
            gmemid.append(tmp_mem)
        return pxyz, gpara, gmemid

def readObj(fn):
    vertices = []
    faces = []
    with open(fn, 'r') as fr:
        for line in fr:
            if line.startswith('#'):
                continue
            elif line.startswith('v '):
                values = line.split()
                vertices.append([float(x) for x in values[1:4]])
            elif line.startswith('vt'):
                continue
            elif line.startswith('f'):
                values = line.strip().split(' ')
                faces.append([int(x.split('/')[0])-1 for x in values[1:]])
            else:
                pass

    return {'v':np.array(vertices), 'f':faces}

def genLines(mode,fpath):
    # list items in directories
    clusters = []
    fitems = os.listdir(fpath)
    print(fitems)
    # read files
    for i in range(len(fitems)):
        full_path = os.path.join(fpath, fitems[i])
        planes = readObj(full_path)
        clusters.append(planes)
    # generate lines
    vertices = []
    lidx = []
    gt_label = []
    lineCountPerFace = 3
    if mode==1:
        # random generate
        count = 1
        for i in range(len(clusters)):
            xyz = clusters[i]['v']
            faces = clusters[i]['f']
            for j in range(len(faces)):
                vt = np.array(faces[j],dtype=int)
                vt = xyz[vt]
                #print(vt)
                for k in range(lineCountPerFace):
                    weight1 = np.random.random(len(vt))
                    weight1 = weight1 / np.sum(weight1)
                    weight2 = np.random.random(len(vt))
                    weight2 = weight2 / np.sum(weight2)
                    vertices.append(weight1.dot(vt))
                    vertices.append(weight2.dot(vt))
                    lidx.append([count, count+1])
                    gt_label.append(i)
                    count += 2
    elif mode==2:
        # delaunay triangulation
        for i in range(len(clusters)):
            xyz = clusters[i]['v']
            faces = clusters[i]['f']
            random_xyz = []
            count = len(vertices)
            for j in range(len(faces)):
                vt = np.array(faces[j],dtype=int)
                vt = xyz[vt]
                #print(vt)
                '''for k in range(len(vt)):
                    random_xyz.append(vt[k])
                    vertices.append(vt[k])'''
                for k in range(lineCountPerFace):
                    weight = np.random.random(len(vt))
                    weight = weight / np.sum(weight)
                    pp = weight.dot(vt)
                    random_xyz.append(pp)
                    vertices.append(pp)
            random_xyz = np.array(random_xyz)
            tri = Delaunay(random_xyz)#, qhull_options='QJ')
            for j in range(len(tri.simplices)):
                tmp = tri.simplices[j]
                lidx.append([count + tmp[0]+1, count + tmp[1]+1])
                gt_label.append(i)
                lidx.append([count + tmp[1]+1, count + tmp[2]+1])
                gt_label.append(i)
                lidx.append([count + tmp[2]+1, count + tmp[0]+1])
                gt_label.append(i)
    elif mode==3:
        # contour
        for i in range(len(clusters)):
            xyz = clusters[i]['v']
            faces = clusters[i]['f']
            count = len(vertices)
            for j in range(len(faces)):
                vt = np.array(faces[j], dtype=int)
                vt = xyz[vt]
                cen = np.ones(len(vt)) / len(vt)
                cen = cen.dot(vt)
                dis = cen - vt
                for k in range(1, lineCountPerFace):
                    weight = k / lineCountPerFace
                    new_xyz = vt + (dis * weight)
                    vertices.extend(new_xyz.tolist())
                    for c in range(len(new_xyz)):
                        lid1 = c + count + 1
                        lid2 = (c+1) % len(new_xyz) + count + 1
                        lidx.append([lid1, lid2])
                        gt_label.append(i)
                    count += len(new_xyz)

    # save lines obj
    with open(fpath + str(mode) + '_line.obj', 'w') as fw:
        count = len(vertices)
        for i in range(count):
            fw.write('v %f %f %f\n'%(vertices[i][0],vertices[i][1],vertices[i][2]))
        count = len(lidx)
        for i in range(count):
            fw.write('l %d %d\n'%(lidx[i][0],lidx[i][1]))
    # save gt labels
    gt_label = np.array(gt_label)
    np.savetxt(fpath + str(mode) + '_gt.txt', gt_label, fmt="%d")

def vg2ply(fn, outfn):
    pxyz, gpara, gmemid = readVg(fn)
    num_l = 0
    for i in range(len(gmemid)):
        num_l = num_l + len(gmemid[i])
    num_l = num_l/2
    colors = get_colors(len(gpara))
    with open(outfn,'w') as fo:
        fo.write("ply\n")
        fo.write("format ascii 1.0\n")
        fo.write("element vertex {}\n".format(len(pxyz)))
        fo.write('property float x\n')
        fo.write('property float y\n')
        fo.write('property float z\n')
        fo.write("element color {}\n".format(len(gpara)))
        fo.write('property uchar red\n')
        fo.write('property uchar green\n')
        fo.write('property uchar blue\n')
        fo.write('element edge %d\n'%(num_l))
        fo.write('property int vertex1\n')
        fo.write('property int vertex2\n')
        fo.write('property int cid\n')
        fo.write('end_header\n')

        for i in range(len(pxyz)):
            fo.write('{} {} {}\n'.format(pxyz[i][0],pxyz[i][1],pxyz[i][2]))

        for i in range(len(gpara)):
            fo.write('%d %d %d\n'%(colors[i][0]*255, colors[i][1]*255, colors[i][2]*255))

        for j in range(len(gmemid)):
            for i in range(len(gmemid[j])):
                if i%2==0:
                    fo.write('{} '.format(gmemid[j][i]))
                else:
                    fo.write('%d %d\n'%(gmemid[j][i],j))

def combineVg(fn1,fn2,outfn):
    pxyz1, gpara1, gmemid1 = readVg(fn1)
    pxyz2, gpara2, gmemid2 = readVg(fn2)
    with open(outfn, 'w') as fo:
        fo.write("num_points: %d\n" % (len(pxyz1)+len(pxyz2)))
        for i in range(len(pxyz1)):
            fo.write("%f %f %f\n" % (pxyz1[i][0], pxyz1[i][1], pxyz1[i][2]))
        for i in range(len(pxyz2)):
            fo.write("%f %f %f\n" % (pxyz2[i][0], pxyz2[i][1], pxyz2[i][2]))

        fo.write("num_colors: 0\n")
        fo.write("num_normals: 0\n")

        fo.write("num_groups: %d\n" % (len(gpara1)+len(gpara2)))
        for i in range(len(gpara1)):
            fo.write("group_type: 0\n")
            fo.write("num_group_parameters: 4\n")
            fo.write("group_parameters: %f %f %f %f\n" % (gpara1[i][0], gpara1[i][1],
                                                          gpara1[i][2], gpara1[i][3]))
            fo.write("group_label: unknown\n")
            fo.write("group_color: %f %f %f\n" % (0,0,0))
            fo.write("group_num_points: %d\n" % len(gmemid1[i]))
            for j in gmemid1[i]:
                fo.write(str(j)+' ')
            fo.write("\n")
            fo.write("num_children: 0\n")

        idshift = len(pxyz1)
        for i in range(len(gpara2)):
            fo.write("group_type: 0\n")
            fo.write("num_group_parameters: 4\n")
            fo.write("group_parameters: %f %f %f %f\n" % (gpara2[i][0], gpara2[i][1],
                                                          gpara2[i][2], gpara2[i][3]))
            fo.write("group_label: unknown\n")
            fo.write("group_color: %f %f %f\n" % (0,0,0))
            fo.write("group_num_points: %d\n" % len(gmemid2[i]))
            for j in gmemid2[i]:
                fo.write(str(j+idshift)+' ')
            fo.write("\n")
            fo.write("num_children: 0\n")

def computeClusterIndex(fpath):
    gt_label = np.loadtxt(fpath, dtype=int)
    db_label = np.loadtxt(fpath[:-6]+'line_db.txt', dtype=int)
    ms_label = np.loadtxt(fpath[:-6]+'line_ms.txt', dtype=int)
    ransac_label = np.loadtxt(fpath[:-6]+'line_ransac.txt', dtype=int)
    hc_label = np.loadtxt(fpath[:-6]+'line_hc.txt', dtype=int)
    glob_label = np.loadtxt(fpath[:-6]+'line_glob.txt', dtype=int)
    pr_label = np.loadtxt(fpath[:-6]+'line_pr.txt', dtype=int)
    ours_label = np.loadtxt(fpath[:-6] + 'line_ours.txt', dtype=int)
    print(type(ms_label[0]))
    db_ri = metrics.rand_score(gt_label, db_label)
    db_nmi = metrics.normalized_mutual_info_score(gt_label, db_label)
    ms_ri = metrics.rand_score(gt_label, ms_label)
    ms_nmi = metrics.normalized_mutual_info_score(gt_label, ms_label)
    ransac_ri = metrics.rand_score(gt_label, ransac_label)
    ransac_nmi = metrics.normalized_mutual_info_score(gt_label, ransac_label)
    hc_ri = metrics.rand_score(gt_label, hc_label)
    hc_nmi = metrics.normalized_mutual_info_score(gt_label, hc_label)
    glob_ri = metrics.rand_score(gt_label, glob_label)
    glob_nmi = metrics.normalized_mutual_info_score(gt_label, glob_label)
    pr_ri = metrics.rand_score(gt_label, pr_label)
    pr_nmi = metrics.normalized_mutual_info_score(gt_label, pr_label)
    ours_ri = metrics.rand_score(gt_label, ours_label)
    ours_nmi = metrics.normalized_mutual_info_score(gt_label, ours_label)

    with open(fpath[:-6]+'cluster_index.txt', 'w') as f:
        f.write('Ground Truth Number: %d\n' % (np.max(gt_label)+1))
        f.write('DBSCAN Prediction Number: %d\n' % (np.max(db_label)+2))
        f.write('DBSCAN Rand Index: %f\n' % db_ri)
        f.write('DBSCAN Normalized Mutual Index: %f\n' % db_nmi)
        f.write('Mean shift Prediction Number: %d\n' % (np.max(ms_label) + 2))
        f.write('Mean shift Rand Index: %f\n' % ms_ri)
        f.write('Mean shift Normalized Mutual Index: %f\n' % ms_nmi)
        f.write('RANSAC Prediction Number: %d\n' % (np.max(ransac_label) + 2))
        f.write('RANSAC Rand Index: %f\n' % ransac_ri)
        f.write('RANSAC Normalized Mutual Index: %f\n' % ransac_nmi)
        f.write('Hierarchical Clustering Prediction Number: %d\n' % (np.max(hc_label) + 2))
        f.write('Hierarchical Clustering Rand Index: %f\n' % hc_ri)
        f.write('Hierarchical Clustering Normalized Mutual Index: %f\n' % hc_nmi)
        f.write('Globfit Prediction Number: %d\n' % (np.max(glob_label) + 2))
        f.write('Globfit Rand Index: %f\n' % glob_ri)
        f.write('Globfit Normalized Mutual Index: %f\n' % glob_nmi)
        f.write('PR15\' Prediction Number: %d\n' % (np.max(pr_label) + 2))
        f.write('PR15\' Rand Index: %f\n' % pr_ri)
        f.write('PR15\' Normalized Mutual Index: %f\n' % pr_nmi)
        f.write('Ours Prediction Number: %d\n' % (np.max(ours_label) + 1))
        f.write('Ours Rand Index: %f\n' % ours_ri)
        f.write('Ours Normalized Mutual Index: %f\n' % ours_nmi)

def vg2globfit(fpath):
    pxyz, gpara, gmemid = readVg(fpath)
    with open(fpath[:-3] + '.globfit', 'w') as fw:
        count = 0
        sbuff = ""
        for i in range(len(gmemid)):
            for j in gmemid[i]:
                count += 1
                sbuff += f'\n{pxyz[j][0]} {pxyz[j][1]} {pxyz[j][2]} {gpara[i][0]} {gpara[i][1]} {gpara[i][2]} 0.99999'
        fw.write('# Number of Points\n')
        fw.write(f'{count}\n')
        fw.write(f'# Here comes the {count} Points\n')
        fw.write('# point_x point_y point_z normal_x normal_y normal_z confidence\n')
        fw.write(sbuff)
        fw.write('\n# End of Points\n\n')
        fw.write('# Number of Primitives\n')
        fw.write(f'{len(gpara)}\n\n')
        fw.write(f'# Here comes the {len(gpara)} Primitives\n')
        count = 0
        for i in range(len(gpara)):
            fw.write(f'# Primitive {i}\n')
            fw.write('# plane normal_x normal_y normal_z d\n')
            fw.write(f'plane {gpara[i][0]} {gpara[i][1]} {gpara[i][2]} {gpara[i][3]}\n')
            fw.write('# points idx_1 idx_2 idx_3 ... \n')
            fw.write('points')
            for j in range(len(gmemid[i])):
                fw.write(f' {count+j}')
            count += len(gmemid[i])
            fw.write('\n\n')
        fw.write('# End of Primitives')

def globfit2vg(fpath):
    pxyz, gpara, gmemid = readGlobfit(fpath)
    with open(fpath[:-8]+'_t.vg','w') as fo:
        fo.write(f"num_points: {len(pxyz)}\n")
        for i in range(len(pxyz)):
            fo.write("%f %f %f\n" % (pxyz[i][0], pxyz[i][1], pxyz[i][2]))
        fo.write("num_colors: 0\n")
        fo.write("num_normals: 0\n")
        fo.write("num_groups: %d\n" % len(gpara))
        for i in range(len(gpara)):
            fo.write("group_type: 0\n")
            fo.write("num_group_parameters: 4\n")
            fo.write("group_parameters: %f %f %f %f\n" % (gpara[i][0], gpara[i][1],
                                                          gpara[i][2], gpara[i][3]))
            fo.write("group_label: unknown\n")
            fo.write("group_color: %f %f %f\n" % (0,0,0))
            fo.write("group_num_points: %d\n" % len(gmemid[i]))
            for j in gmemid[i]:
                fo.write(str(j)+' ')
            fo.write("\n")
            fo.write("num_children: 0\n")

def mat2q(R):
    q0 = 0.5 * math.sqrt(1 + R[0, 0] + R[1, 1] + R[2, 2])
    q1 = (R[2, 1] - R[1, 2]) / (4 * q0)
    q2 = (R[0, 2] - R[2, 0]) / (4 * q0)
    q3 = (R[1, 0] - R[0, 1]) / (4 * q0)
    return np.array([q0,q1,q2,q3])


def npz2Text(fpath):
    npz_path = os.path.join(fpath, 'npz')
    npz_items = os.listdir(npz_path)
    npz_items.sort()
    print(npz_items)

    #image_path = os.path.join(fpath, 'images')
    quaternions = []
    translations = []
    intrinsicses = []

    #test = []

    for i in npz_items:
        '''
                K:  3x3 camera intrinsics
                P: 3x4 K @ Rt
                Rt: 3x4 , 3x3: rotation matrix, 3x1: transform matrix
                junc2D: N x 2 , 2D junctions in images
                junc3D_cam: N x 3, 3D junctions in camera coord system
                junc3D_world: N x 3, 3D junctions in world coord system
                edge: Nx3, (idx1,idx2,if_vis) , idx1/idx2: index of junction, if_vis(bool): if this edge is visible or not
                edgeWireframeIdx: edge corresponding to the gt wireframe edge index
        '''
        '''data = np.load(os.path.join(npz_path, i))
        for k in data.keys():
            print(k,data[k].shape)
            print(data[k])
        junc2D = data['junc2D']
        plt.figure()
        im = plt.imread(os.path.join(image_path,i[:-3]+'png'))
        #plt.imshow(im)
        plt.scatter(junc2D[:,0],junc2D[:,1])
        plt.show()'''

        '''junc3D_world = data['junc3D_world']
        np.savetxt(os.path.join(fpath, i[:-3]+'xyz'), junc3D_world)'''

        data = np.load(os.path.join(npz_path,i))
        intrinsics = data['K']
        # format H W fx fy cx cy
        intrinsicses.append(np.array([intrinsics[0][2]*2, intrinsics[1][2]*2, intrinsics[0][0],intrinsics[1][1],intrinsics[0][2], intrinsics[1][2]]))
        print(f'K {intrinsics.shape}\n{intrinsics}')


        #R_bcam2cv = np.diag([1,-1,-1])
        Rt = data['Rt']
        print(f'Rt {Rt.shape}\n{Rt}')
        #test.append(Rt[:,3])
        i_R = Rt[:,:3]
        i_T = Rt[:, 3]
        print(f'R {i_R.shape}\n{i_R}')
        print(f'T {i_T.shape}\n{i_T}')
        qua = mat2q(i_R)
        #test = R.from_quat(qua).as_matrix()
        #print(f'quaternion {qua.shape}\n{qua}')
        #print(f'inverse matrix {test.shape}\n{test}')
        quaternions.append(qua)
        translations.append(i_T)

    sparse_path = os.path.join(fpath, 'sparse')
    #np.savetxt(os.path.join(fpath,'cam_pos.xyz'),test)

    # connect db
    colmap_db = COLMAPDatabase.connect(os.path.join(fpath, 'database.db'))

    # write cameras.txt
    with open(os.path.join(sparse_path, 'cameras.txt'), 'w') as f:
        f.write('# Camera list with one line of data per camera:\n')
        f.write('#   CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]\n')
        f.write(f'# Number of cameras: {1}\n')
        for i in range(len(npz_items)):
            f.write(
                f'{i+1} PINHOLE {int(intrinsicses[i][0])} {int(intrinsicses[i][1])} {intrinsicses[i][2]} {intrinsicses[i][3]} {intrinsicses[i][4]} {intrinsicses[i][5]}\n')

    # write image.txt
    with open(os.path.join(sparse_path, 'images.txt'), 'w') as f:
        f.write('# Image list with two lines of data per image:\n')
        f.write('#   IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME\n')
        f.write(f'# Number of images: {len(npz_items)}\n')
        for i in range(len(npz_items)):
            colmap_db.update_camera(1, int(intrinsicses[i][0]), int(intrinsicses[i][1]),
                                                np.array((intrinsicses[i][2], intrinsicses[i][3],
                                                          intrinsicses[i][4], intrinsicses[i][5])), i + 1)
            f.write(
                f'{i + 1} {quaternions[i][0]} {quaternions[i][1]} {quaternions[i][2]} {quaternions[i][3]} {translations[i][0]} {translations[i][1]} {translations[i][2]} {i+1} {npz_items[i][:-3] + "jpg"}\n\n')
            #colmap_db.add_image(npz_items[i][:-3] + "png", camera_id, quaternions[i], translations[i])

    colmap_db.commit()
    colmap_db.close()

if __name__ == '__main__':
    '''combineVg('/home/hiko/Workspace/Line2Plane/data/Barn+haoyu_cut6_7.vg',
              '/home/hiko/Workspace/Line2Plane/data/Barn+haoyu_res.vg',
              '/home/hiko/Workspace/Line2Plane/data/Barn+haoyu_res.vg')'''
    #vg2ply('/home/hiko/Workspace/Line2Plane/data/Barn+haoyu_res.vg','/home/hiko/Workspace/Line2Plane/data/Barn+haoyu_res.ply')
    #line2wire('/home/hiko/Workspace/11_1lines/20_sub/cmvs/Line3D++__W_FULL__N_10__sigmaP_2.5__sigmaA_10__epiOverlap_0.25__kNN_10__OPTIMIZED__vis_3.obj')
    #line2wire('/home/hiko/Downloads/LineData/Line3D++__office_c.obj')
    #line2wire('/home/hiko/Downloads/LineData/Line3D++__restaurant.obj')
    #line2wire('/home/hiko/Downloads/LineData/Line3D++_sixuegongyu.obj')
    #line2wire('/home/hiko/Downloads/LineData/Line3D++__thu_ocean.obj')
    #wire2line('/home/hiko/Downloads/LineData/LSD_office.obj')
    #wire2line('/home/hiko/Downloads/data/real/LSD_sixuegongyu_cut.obj')
    #wire2line('/home/hiko/Downloads/data/real/Line3D++_office_crop.obj')
    #format2jpg('/home/hiko/Workspace/Line2Plane/data/BK39_500_002053_0011/images')

    '''prefix1 = '/home/hiko/Downloads/data/dispatch/Fig10'
    prefix2 = '/home/hiko/Downloads/data/dispatch/toy_data'
    prefix3 = '/home/hiko/Downloads/data/dispatch/other_ball'
    genLines(1, prefix1)
    genLines(1, prefix2)
    genLines(1, prefix3)'''
    #computeClusterIndex('/home/hiko/Downloads/data/dispatch/toy_data2_gt.txt')
    '''prefix1 = '/home/hiko/Downloads/data/dispatch/Fig10'
    genLines(3, prefix1)'''
    #vg2globfit('/home/hiko/Downloads/data/real/LSD_sixuegongyu_cut_glob.vg')
    #vg2globfit('/home/hiko/Downloads/data/real/Line3D++_office_crop_glob.vg')
    #vg2globfit('/home/hiko/Downloads/data/dispatch/Fig103_line_glob.vg')
    #vg2globfit('/home/hiko/Downloads/data/dispatch/other_ball1_line_glob.vg')
    #vg2globfit('/home/hiko/Downloads/data/dispatch/toy_data2_line_glob.vg')
    #globfit2vg('/home/hiko/Downloads/data/real/LSD_sixuegongyu_cut_glob_ea.globfit')
    #globfit2vg('/home/hiko/Downloads/data/real/Line3D++_office_crop_glob_ea.globfit')
    #globfit2vg('/home/hiko/Downloads/data/dispatch/Fig103_line_glob_ea.globfit')
    #globfit2vg('/home/hiko/Downloads/data/dispatch/other_ball1_line_glob_ea.globfit')
    #globfit2vg('/home/hiko/Downloads/data/dispatch/toy_data2_line_glob_ea.globfit')
    #png2jpg('/home/hiko/Workspace/Line2Plane/data/BJ39_500_098050_0009/images')
    npz2Text('/home/hiko/Workspace/Line2Plane/data/BJ39_500_098050_0009')