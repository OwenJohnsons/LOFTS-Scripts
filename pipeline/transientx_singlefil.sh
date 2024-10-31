filterbank=$1
# grab target from filterbank filename
target=$(basename $filterbank | cut -d'.' -f1)

echo "Running transientX on $target"

# make output directory
mkdir -p $target.singlepulse

transientx_fil -f $filterbank -t 8 --dms 0 --ddm 1 --ndm 500 --td 2 --fd 2 \
 --threMask 10 --threKadaneT 7 --minw 0.0001 --maxw 0.02 --thre 7 --seglen 30 \
-r 5 -k 3 --maxncand 500 --rootname "$target.singlepulse/$target"  --saveimage