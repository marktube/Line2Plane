for i in {14..32}
do
#  echo $i
    python main.py --volume $i --line_data /home/hiko/Workspace/Line2Plane/data/3dstl/pyramid_box_lid_line.obj --gui false
done
