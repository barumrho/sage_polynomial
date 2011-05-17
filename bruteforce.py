import os.path
from db import DB
from polynomial import *

def test_discriminant(f):
    return f.discriminant().is_square()

def bruteforce_random(d, limit=1, record=False, min=-100, max=100):
    db = DB()

    tried = 0
    tried_hundred = 0
    found = 0

    while found < limit:
        f = irreducible_polynomial(d)
        if test_discriminant(f):
            print
            print "Tried:", tried, "polynomials"
            print "f(x) =", f
            if record:
                db.add(f)
      
            found += 1
    
        tried += 1
        if tried_hundred != int(tried / 100):
            print >> sys.stderr, tried, 
            tried_hundred = int(tried / 100)

    return f


def all_coeffs(n, min=0, max=5, feed=None):
    """
    Returns a iterator of all permutations of a list of integers with
    length n.  If feed is not given, it uses all the numbers between 
    min and max to produce permutations.  If feed, a list of integers, 
    is given, then it will use those numbers to generate the permutations.

    """
    
    if n == 1:
        if feed:
            for i in feed:
                yield [i, ]
        else:
            for i in range(min, max + 1):
                yield [i, ]
    else:
        for c1 in all_coeffs(n - 1, min, max, feed):
            for c2 in all_coeffs(1, min, max, feed):
                yield c2 + c1
    

def bruteforce_order(d, limit=5, min=0, max=3, feed=None):
    """
    Considers monic polynomials with the rest coefficients between min and max
    adds to the database upto limit (counting already existing ones)
    
    """

    db = DB()

    for c in all_coeffs(d, min, max, feed):
        c.append(1)  # Monic polynomials
        f = make_polynomial(c)

        if f.is_irreducible():
            g = f.galois_group()
            print f, "(", g._n, ")"

            if len(db.list(d, g._n)) < limit:
                print "Added", f, "(", g._n, ")"
                db.add(f)

    return None
