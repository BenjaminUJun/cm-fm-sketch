class SrcDest(object):

    def __init__(self, srcAddr,DestSet):
        self.DestSet = DestSet
        self.srcAddr = srcAddr
        self.match = self
    def __eq__(self, other):
        result = (self.srcAddr == other.srcAddr)
        if result:
            self.match = other
            other.DestSet = self.DestSet | other.DestSet
            #print "Match: new self length" + str(len(other.DestSet))
            #print "updateSet: new " + str(other.DestSet)
        return result
    def __ne__(self, other):
        return self.srcAddr != other.srcAddr 
    def __hash__(self):
        return hash(self.srcAddr)

from sets import Set
import sys


if __name__ == '__main__':


    entireSet = Set()
    
    f = sys.argv[1]


    with open(f, 'r') as fin:
        counter = 0
        for line in fin:

            counter += 1
            if (counter % 100000) == 0:
                sys.stderr.write(str(counter//100000) + "%\n")

            arr = line.strip().split(',') # [src, dst]
            dest1 = Set([arr[1]])
            sd1 = SrcDest(arr[0],dest1)

            if sd1 in entireSet:
                #print "--------Main Loop--------"
                #print "existing " + str(sd1.DestSet)
                #print "new " + str(dest1)
                #print "Updated length " + str(len(sd1.DestSet))
                #print "------End Main Loop------"
                entireSet.discard(sd1)
                entireSet.add(sd1)
                #print sd1.match.DestSet
            else:
                entireSet.add(sd1)

    k = sys.argv[2]
    printDestNum = sys.argv[3]
    for src in entireSet:
        #print src.srcAddr + " " + str(len(src.DestSet))
        #for dst in src.DestSet:
        #    print dst + ","
        if len(src.DestSet) >= int(k):
            if int(printDestNum) == 1:
                print src.srcAddr + " " + str(len(src.DestSet))
            else:
                print src.srcAddr
