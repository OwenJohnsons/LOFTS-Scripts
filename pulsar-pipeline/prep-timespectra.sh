obs_file=$1

if [[ -z "$obs_file" ]]; then
    echo "Usage: $0 <filterbank file>"
    exit 1
fi
basedir=$(dirname "$obs_file")
cd "$basedir" || exit 1
mkdir -p "$basedir/timeseries"
basename=$(basename "$obs_file" .fil)

prepsubband -nsub 412 "$obs_file" -o "timeseries/${basename}" -lodm 0 -dmstep 0.007 -numdms 92 "$obs_file"
prepsubband -nsub 412 "$obs_file" -o "timeseries/${basename}" -lodm 0.601 -dmstep 0.026 -numdms 69 "$obs_file"
prepsubband -nsub 412 "$obs_file" -o "timeseries/${basename}" -lodm 2.402 -dmstep 0.085 -numdms 64 "$obs_file"
prepsubband -nsub 412 "$obs_file" -o "timeseries/${basename}" -lodm 7.808 -dmstep 0.275 -numdms 64 "$obs_file"
prepsubband -nsub 412 "$obs_file" -o "timeseries/${basename}" -lodm 25.225 -dmstep 0.871 -numdms 63 "$obs_file"
prepsubband -nsub 412 "$obs_file" -o "timeseries/${basename}" -lodm 79.88 -dmstep 1.22 -numdms 427 "$obs_file"