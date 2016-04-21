import cmfm
import sys

f = sys.argv[1]
k = 3 # arbitrary value for superspreader

# initialize CM-FM Sketch
sketch = cmfm.CountMinSketch(1000, 10)

with open(f, 'r') as fin:
    for line in fin:
        arr = line.strip().split(',') # [src, dst]
        sketch.add(arr[0], arr[1])
        count = sketch.query(arr[0])
        if count >= k:
            print "%s is a %d-superspreader with %d distinct destinations" % (arr[0], k, count)

sketch.cleanup()
del sketch
