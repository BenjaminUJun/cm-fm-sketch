import cmfm
import sys

import threading
from threading import Thread
from multiprocessing import Queue
import time

#f = sys.argv[1]
k = int(sys.argv[1]) # arbitrary value for superspreader
h_size = int(sys.argv[2]) # size of each hash table
h_num = int(sys.argv[3]) # number of hash tables

def cmfmFunction( threadName, fileName, q):
	# initialize CM-FM Sketch
	sketch = cmfm.CountMinSketch(h_size, h_num)

	with open(fileName, 'r') as fin:
	    for line in fin:
	        arr = line.strip().split(',') # [src, dst]
	        #print arr
	        #print arr[0], arr[1]
	        src = arr[0] # src ip
	        dst = arr[1] # dst ip
	        sketch.add(src, dst)
	        #count = sketch.query(arr[0])
	        #if count >= k:
	        #    print "%s is a %d-superspreader with %d distinct destinations" % (arr[0], k, count)
	q.put(sketch)
	#sketch.cleanup()
	#del sketch



print "Starting CM-FM"
print "k = " + str(sys.argv[1])
print "hash table size = " + str(sys.argv[2])
print "hash table number = " + str(sys.argv[3])
print "files: " + str(sys.argv[4:])

threadList = []
results = []
i = 0
for fileName in sys.argv[4:]:
	i += 1
	try:
		threadName = "Thread" + str(i)
		print threadName
		q = Queue()
		t = Thread(target=cmfmFunction, name=(threadName), args=("One!", fileName, q ) )
		t.start()
		threadList.append(t)
		results.append(q)
	except Exception as e:
	   print "Error: unable to start thread! " + str(e)

for thread in threadList:
	thread.join()
	print thread.name + " ended"



print "Combining sketches"
primarySketch=None
i = 0
for result in results:
	i += 1
	print "Combining sketch " + str(i)
	if primarySketch is None:
		primarySketch = result.get()
	else:
		primarySketch.combine(result.get())



print "Final processing"

fwrite = "dist-%d-superspreader-%d-%d.txt" % (k, h_size, h_num)

i = 0
with open(fwrite, 'w+') as fout:
	for fileName in sys.argv[4:]:
		with open(fileName, 'r') as fin:
		    fin.readline()
		    #print "processing" + fileName
		    # read line by line
		    for line in fin:
		        arr = line.strip().split(',')
		        src = arr[0] # src ip
		        #print (src)
		        count = primarySketch.query(src)
		        if count >= k:
		            fout.write(src + '\n')
		        #fout.write(src + " " + str(count) + '\n')
		i += 1
print "Done processing!!"

#print "Cleaning up!!"
#for result in results:
#	result.get().cleanup()


print "Done!!"

