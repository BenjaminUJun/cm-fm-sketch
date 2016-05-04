import cmfm
import sys

f1 = sys.argv[1]
f2 = sys.argv[2]
k = 10
if len(sys.argv) > 3:
    k = int(sys.argv[3])

fwrite = "dist-%d-superspreader.txt" % k

# initialize CM-FM Sketch
sketch1 = cmfm.CountMinSketch(1000, 10)

with open(f1, 'r') as fin: #, open(f2, 'w+') as fout:
    # skip the header line
    fin.readline()
    # read line by line
    for line in fin:
        arr = line.strip().split(',')
        src = arr[2] # src ip
        dst = arr[3] # dst ip
        sketch1.add(src, dst)
        #count = sketch.query(src)
        #if count >= k:
            #print "%s is a %d-superspreader with %d distinct destinations" % (src, k, count)
            #fout.write(src + '\n')

sketch2 = cmfm.CountMinSketch(1000, 10)

with open(f2, 'r') as fin:
    for line in fin:
        arr = line.strip().split(',')
        src = arr[2] # src ip
        dst = arr[3] # dst ip
        sketch2.add(src, dst)

sketch1.combine(sketch2)

print "done"

sketch2.cleanup()
del sketch2

with open(f1, 'r') as fin, open(fwrite, 'w+') as fout:
    fin.readline()
    # read line by line
    for line in fin:
        arr = line.strip().split(',')
        src = arr[2] # src ip
        count = sketch1.query(src)
        if count >= k:
            fout.write(src + '\n')

with open(f2, 'r') as fin, open(fwrite, 'a') as fout:
    for line in fin:
        arr = line.strip().split(',')
        src = arr[2] # src ip
        count = sketch1.query(src)
        if count >= k:
            fout.write(src + '\n')

sketch1.cleanup()
del sketch1

