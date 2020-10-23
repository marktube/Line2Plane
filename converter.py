from PIL import Image
import os

path_prefix = 'E:\\Workspace\\3DVC\\3DLine\\data\\building_blocks\\complete_sequence\\images'
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