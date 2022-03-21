from PIL import Image
import os
import colorsys
import numpy as np
from sklearn import metrics

def get_colors(num_colors):
    colors=[]
    for i in np.arange(0., 360., 360. / num_colors):
        hue = i / 360.
        lightness = (50 + np.random.rand() * 10)/100.
        saturation = (90 + np.random.rand() * 10)/100.
        colors.append(colorsys.hls_to_rgb(hue, lightness, saturation))
    return np.array(colors)

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
            line=fr.readline().strip()
            values = line.split()
            pxyz.append([float(values[0]),float(values[1]),float(values[2])])
        #print(pxyz)

        num_str = fr.readline().strip()
        ccount = int(num_str.split(':')[1])
        for i in range(ccount):
            line=fr.readline().strip()
            # color info is not needed
        #print(ccount)

        num_str = fr.readline().strip()
        ncount = int(num_str.split(':')[1])
        for i in range(ncount):
            line=fr.readline().strip()
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
            membid = [int(n) for n in line.split(' ')]
            gmemid.append(membid)
            fr.readline()  # num_children: 0

    return np.array(pxyz), np.array(gpara), gmemid

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
    gt_label = []
    lineCountPerFace = 90
    if mode:
        # random generate
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
                    gt_label.append(i)
    else:
        pass
    # save lines obj
    with open(fpath + str(mode) + '_line.obj', 'w') as fw:
        count = len(vertices)
        for i in range(count):
            fw.write('v %f %f %f\n'%(vertices[i][0],vertices[i][1],vertices[i][2]))
        count = int(count / 2)
        for i in range(count):
            fw.write('l %d %d\n'%(i*2+1,i*2+2))
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
    ours_label = np.loadtxt(fpath[:-6] + 'line_ours.txt', dtype=int)
    print(type(ms_label[0]))
    db_ri = metrics.rand_score(gt_label, db_label)
    db_nmi = metrics.normalized_mutual_info_score(gt_label, db_label)
    ms_ri = metrics.rand_score(gt_label, ms_label)
    ms_nmi = metrics.normalized_mutual_info_score(gt_label, ms_label)

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
        f.write('Ours Prediction Number: %d\n' % (np.max(ours_label) + 1))
        f.write('Ours Rand Index: %f\n' % ours_ri)
        f.write('Ours Normalized Mutual Index: %f\n' % ours_nmi)

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
    #wire2line('/home/hiko/Workspace/line3dpp-vsfm-gta5-16-face-inf-var.obj')
    #wire2line('/home/hiko/Downloads/compare/DJI_modified_line.obj')
    #format2jpg('/home/hiko/Workspace/11_1lines/Andalusian/images')

    '''prefix1 = '/home/hiko/Downloads/data/dispatch/Fig10'
    prefix2 = '/home/hiko/Downloads/data/dispatch/toy_data'
    prefix3 = '/home/hiko/Downloads/data/dispatch/other_ball'
    genLines(1, prefix1)
    genLines(1, prefix2)
    genLines(1, prefix3)'''
    computeClusterIndex('/home/hiko/Downloads/data/dispatch/toy_data1_gt.txt')

