for i in {16..20}
do
#  echo $i
    python main.py --volume $i --line_data /home/hiko/Downloads/L3DData/office.obj --gui false
    python main.py --volume $i --line_data /home/hiko/Downloads/L3DData/restaurant.obj --gui false
    python main.py --volume $i --line_data /home/hiko/Downloads/L3DData/sixuegongyu.obj --gui false
done
