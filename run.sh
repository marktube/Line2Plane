for i in {20..61}
do
#  echo $i
    python main.py --volume $i --line_data /home/hiko/Downloads/LineData/LSD_sixuegongyu_cut.obj --gui false
done
