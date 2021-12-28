for i in {23..61}
do
#  echo $i
    python main.py --volume $i --line_data /home/hiko/Workspace/Line2Plane/data/Barn+haoyu_cut.obj --gui false
done
