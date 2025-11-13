directory=$1
station=$2

for fil in $(ls $directory/*.fil); do
    plot-bandpass.py -f $fil -s $station
done

slack-bandpass.py $directory 