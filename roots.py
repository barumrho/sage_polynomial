# Collection of functions to analyze roots

from __future__ import division
from sage.all import *
import db
import polynomial

def count_roots(f, limit=None):
    db_ = db.DB(load=False)
    
    p = 0
    tally = dict()
    for r in db_.roots(f):
        if r[1] != p:
            p = r[1]
            if limit is not None and p > limit:
                break
            tally[p] = 1
        else:
            tally[p] += 1

    return tally


def count_primes_by_roots(f, ratio=True):
    """Return a tally of number of primes by number of roots.
    
    Arguments:
    f -- polynomial
    ratio -- return ratio instead of actual counts (Default: True)
    """
    db_ = db.DB(load=False)

    p = 0
    count_p = 0
    tally = dict([(i,0) for i in range(f.degree() + 1)])
    tally[0] = -1 # Trick to offset first increment of tally[0]

    for r in db_.roots(f):
        if r[1] > p:
            tally[count_p] += 1
            count_p = 1
            
            p = next_prime(p)
            while p < r[1]:
                tally[0] += 1
                p = next_prime(p)
        else:
            count_p += 1

    total = sum(tally.values())
    for i in tally:
        tally[i] /= total

    return tally


def roots_by_prime(f):
    db_ = db.DB(load=False)

    p = 0
    roots = dict()
    for r in db_.roots(f):
        if p != r[1]:
            p = r[1]
            roots[p] = [r[0],]
        else:
            roots[p].append(r[0])
    return roots


def find_max(f, type=None, range=(0, 1), limit=None):
    roots = roots_by_prime(f)

    max = QQ(0) 
    for p in roots.keys():
        if type != None and len(roots[p]) != type:
            continue

        if range == (0, 1):
            if QQ(roots[p][-1]) / QQ(p) > max:
                max = QQ(roots[p][-1]) / QQ(p)
        else:
            for n in roots[p]:
                q = QQ(n) / QQ(p)
                if q <= range[1] and q >= range[0]:
                    max_p = q
            if max_p > max:
                max = max_p

    return max
