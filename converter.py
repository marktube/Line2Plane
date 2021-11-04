from PIL import Image
import os

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
            fw.write('l %d %d %d\n'%(lidx[i][0],lidx[i][1],lidx[i][1]))

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

if __name__ == '__main__':
    #line2wire('/home/hiko/Downloads/LineData/Line3D++__largeCity.obj')
    #line2wire('/home/hiko/Downloads/LineData/Line3D++__office_c.obj')
    #line2wire('/home/hiko/Downloads/LineData/Line3D++__restaurant.obj')
    #line2wire('/home/hiko/Downloads/LineData/Line3D++_sixuegongyu.obj')
    #line2wire('/home/hiko/Downloads/LineData/Line3D++__thu_ocean.obj')
    #wire2line('/home/hiko/Downloads/LineData/LSD_office.obj')
    #wire2line('/home/hiko/Downloads/LineData/LSD_thu_ocean.obj')
    #wire2line('/home/hiko/Downloads/LineData/LSD_sixuegongyu.obj')
    format2jpg('/home/hiko/Workspace/11_1lines/Andalusian/images')
