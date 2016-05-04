"""
This module implements probabilistic data structure which is able to calculate the cardinality of large multisets in a single pass using little auxiliary memory
"""

import math
from hashlib import sha1
from hashlib import md5
from const import rawEstimateData, biasData, tresholdData
#from .compat import *
#import array

def bit_length(w):
    return w.bit_length()


def bit_length_emu(w):
    return len(bin(w)) - 2 if w > 0 else 0


# Workaround for python < 2.7
if not hasattr(int, 'bit_length'):
    bit_length = bit_length_emu


def get_treshold(p):
    return tresholdData[p - 4]


def estimate_bias(E, p):
    bias_vector = biasData[p - 4]
    nearest_neighbors = get_nearest_neighbors(E, rawEstimateData[p - 4])
    return sum([float(bias_vector[i]) for i in nearest_neighbors]) / len(nearest_neighbors)


def get_nearest_neighbors(E, estimate_vector):
    distance_map = [((E - float(val)) ** 2, idx) for idx, val in enumerate(estimate_vector)]
    distance_map.sort()
    return [idx for dist, idx in distance_map[:6]]


def get_alpha(p):
    if not (4 <= p <= 16):
        raise ValueError("p=%d should be in range [4 : 16]" % p)

    if p == 4:
        return 0.673

    if p == 5:
        return 0.697

    if p == 6:
        return 0.709

    return 0.7213 / (1.0 + 1.079 / (1 << p))


def get_rho(w, max_width):
    rho = max_width - bit_length(w) + 1

    if rho <= 0:
        raise ValueError('w overflow')

    return rho


class HyperLogLog(object):
    """
    HyperLogLog cardinality counter
    """

    __slots__ = ('alpha', 'p', 'm', 'M')

    def __init__(self, error_rate):
        """
        Implementes a HyperLogLog

        error_rate = abs_err / cardinality
        """

        if not (0 < error_rate < 1):
            raise ValueError("Error_Rate must be between 0 and 1.")

        # error_rate = 1.04 / sqrt(m)
        # m = 2 ** p
        # M(1)... M(m) = 0

        p = int(math.ceil(math.log((1.04 / error_rate) ** 2, 2)))

        self.alpha = get_alpha(p)
        self.p = p
        self.m = 1 << p
        self.M = [ 0 for i in range(self.m) ]

    def __getstate__(self):
        return dict([x, getattr(self, x)] for x in self.__slots__)

    def __setstate__(self, d):
        for key in d:
            setattr(self, key, d[key])

    def add(self, value):
        """
        Adds the item to the HyperLogLog
        """
        # h: D -> {0,1} ** 64
        # x = h(v)
        # j = <x_0x_1..x_{p-1}>
        # w = <x_{p}x_{p+1}..>
        # M[j] = max(M[j], rho(w))

        x = long(sha1(bytes(value.encode() if isinstance(value, unicode) else value)).hexdigest()[:16], 16)
        j = x & (self.m - 1)
        w = x >> self.p

        self.M[j] = max(self.M[j], get_rho(w, 64 - self.p))

    def update(self, *others):
        """
        Merge other counters
        """

        for item in others:
            if self.m != item.m:
                raise ValueError('Counters precisions should be equal')

        self.M = [max(*items) for items in zip(*([ item.M for item in others ] + [ self.M ]))]

    def __eq__(self, other):
        if self.m != other.m:
            raise ValueError('Counters precisions should be equal')

        return self.M == other.M

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return round(self.card())

    def _Ep(self):
        E = self.alpha * float(self.m ** 2) / sum(math.pow(2.0, -x) for x in self.M)
        return (E - estimate_bias(E, self.p)) if E <= 5 * self.m else E

    def card(self):
        """
        Returns the estimate of the cardinality
        """

        #count number or registers equal to 0
        V = self.M.count(0)

        if V > 0:
            H = self.m * math.log(self.m / float(V))
            return H if H <= get_treshold(self.p) else self._Ep()
        else:
            return self._Ep()


class CountMinSketch(object):
    def __init__(self, m, d):
        """ `m` is the size of the hash tables, larger implies smaller
            overestimation. `d` the amount of hash tables, larger implies lower
            probability of overestimation.
            """
        if not m or not d:
            raise ValueError("Table size (m) and amount of hash functions (d)"
                             " must be non-zero")
        self.m = m
        self.d = d
        #self.n = 0
        self.tables = []
        for _ in xrange(d):
            #table = array.array("l", (0 for _ in xrange(m)))
            table = [HyperLogLog(0.01) for _ in xrange(m)]
            self.tables.append(table)

    def _hash(self, x):
        mymd5 = md5(str(hash(x)))
        for i in xrange(self.d):
            mymd5.update(str(i))
            yield int(mymd5.hexdigest(), 16) % self.m

    # x is the src, y is the destination
    def add(self, x, y, value=1):
        #self.n += value
        for table, i in zip(self.tables, self._hash(x)):
            table[i].add(y)

    def query(self, x):
        return min(len(table[i]) for table, i in zip(self.tables, self._hash(x)))

    def __getitem__(self, x):
        return self.query(x)

    def cleanup(self):
        for table in self.tables:
            for fm in table:
                del fm
            del table

    # x is another CountMinSketch object of same dimensions
    def combine(self, x):
        for tbl1, tbl2 in zip(self.tables, x.tables):
            for fm1, fm2 in zip(tbl1, tbl2):
                fm1.update(fm2)

    # combine a list of CM sketches
    def combineAll(self, lst):
        for sk in lst:
            self.combine(sk)

    #def __len__(self):
        #return self.n


