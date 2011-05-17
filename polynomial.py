###############################################################################
# Functions related to dealing with polynomials

import os.path
import progress_meter
from sage.all import *

def random_coefficients(n, min=-100, max=100):
    """ 
    random_coefficients(n, min=-100, max=100)
        n - positive integer
        min - integer
        max - integer

    returns [i_1, i_2, ..., i_n] 
        where i_j are random integers between min and max
    """

    return [randint(min,max) for i in range(0,n)]


def make_polynomial(coeffs, ring=QQ):
    """ 
    INPUT:
        `coeffs` -- coefficients, [c_0, c_1, ..., c_n]
        `ring` -- base ring

    OUTPUT:
    returns f
        where f = c_n*x**n + ... + c_1*x + c_0
    """
    R = PolynomialRing(ring, 'x')
    x = R.gen()
    f = x - x # Sort of a trick to make f zero polynomial

    one = ring.gen()
    coeffs = [int(c) * one for c in coeffs]

    for i in range(0, len(coeffs)):
        f = f + coeffs[i] * x ** i

    return f

def random_polynomial(d, min=-100, max=100):
    """ 
    random_polynomial(d)
        d - positive integer
        min - integer
        max - integer

    returns f
        where f is degree d polynomial with random coefficients between min and max
    """

    c = random_coefficients(d+1, min, max)
    f = make_polynomial(c)
    while not f.degree() == d:
        c = random_coefficients(d+1, min, max)
        f = make_polynomial(c)

    return f

def irreducible_polynomial(d, min=-100, max=100):
    """
    irreducible_polynomial(d)
        d - positive integer
        min - integer
        max - integer

    returns f
        where f is degree d, irreducible polynomial with random coefficients between
        min and max
    """

    # constant polynomial
    if d == 0:
        return 0

    f = random_polynomial(d, min, max)
    while not f.is_irreducible():
        f = random_polynomial(d, min, max)

    return f

def integerize_coefficients(f):
    """
    integerize_coefficients(f)
        f - polynomial

    returns None
        multiplies lcm of denominators
    """
        
    d = list()

    # Use f.coefficients() since this omitts zero coefficients
    for c in f.coefficients():
        if c.denominator() != 1:
            d.append(c.denominator())
    
    f = lcm(d)*f

    return None


def name_polynomial(f):
    """Return a string that identifies a polynomial."""
    name = str()
    for c in f.coeffs():
        name += str(c) + "_"

    return name.rstrip("_")


def name_to_polynomial(name):
    """Convert name to Sage polynomial object."""
    coeffs = [int(c) for c in name.split("_")]
    
    return make_polynomial(coeffs)


def roots_mod(f, n):
    """ 
    roots_mod(f,n)
        f - polynomial
        n - integer

    returns [r_1, r_2,...r_n] 
        where f(r_i) === 0 mod n
    """
    var('y') # need to use a variable for solve_mod
    roots = solve_mod(f(y) == 0, n)

    sol = []
    for i in roots:
        sol.append(i[0])

    return sol

def roots_modp(f, p, n=1):
    """
    roots_modp(f, p1, p2)
        f - polynomial
        p - prime number
        n - positive integer

    returns [r_1/p_1, r_2/p_2, ..., r_n/p_n]
        where f(r_i) = 0 mod p_i
        and p1 <= p_i <= p2
    """
    if not is_prime(p):
        p = next_prime(p)

    rootsp = []
    for i in range(0,n):
        roots = roots_mod(f, p)
        for r in roots:
            rootsp.append((r,p))
        p = next_prime(p)

    return rootsp


def solve_mod_even(f, p1, p2, progress=True):
    """
    This does the same as solve_mod_multiple for even functions.
    The purpose is to take advantage of the fact that even functions
    produce symmetric zeros mod p.

    """

    import time
    start = time.time()

    if not is_even(f):
        print f, "is not even!"
        return None

    sol = list()

    # 2 is a special prime...
    if p1 == 2:
        if p1.divides(f(0)):
            sol.append((0,2))
        if p1.divides(f(1)):
            sol.append((1,2))
        if p2 == 2:
            return sol
        p1 = next_prime(2)

    if progress:
        print "Generating output:"
        pbar = progress_meter.ProgressMeter(total=(p2 + 1) / 2)

    output = list()
    for n in range((p2 + 1) / 2):
        output.append((n,f(n)))
        if progress:
            pbar.update(1)


    if progress:
        print "Solving for roots:"
        pbar = progress_meter.ProgressMeter(total=p2-p1)

    p = p1
    degree = f.degree()
    while p <= p2:
        solp = list()
        solp2 = list()
        for fn in output[:(p + 1) / 2]:
            if p.divides(fn[1]):
                solp.append((fn[0], p))
                if fn[0] != 0:
                    solp2.insert(0, (p - fn[0], p))

                if len(solp) == degree:
                    break
                    
        sol += solp + solp2
        p, p0 = next_prime(p), p
        if progress:
            pbar.update(p-p0)

    print time.time() - start

    return sol


def solve_mod_multiple(f, p1, p2, progress=True):
    """
    Solve roots of polynomial modulo p for p in [p1,p2]

    INPUT:
        f -- Polynomial
        p1 -- prime number lowerbound
        p2 -- prime number upperbound

    OUTPUT:
        [(r,p),...] -- tuples of roots and corresponding prime

    """
    import time
    start = time.time()

    if progress:
        print "Generating output:"
        pbar = progress_meter.ProgressMeter(total=p2)

    output = list()
    for n in range(p2):
        output.append((n,f(n)))
        if progress:
            pbar.update(1)

    if progress and p1 != p2:
        print "Solving for roots:"
        pbar = progress_meter.ProgressMeter(total=p2-p1)

    sol = list()
    p = p1
    degree = f.degree()
    while p <= p2:
        solp = list()
        for fn in output[:p]:
            if p.divides(fn[1]):
                solp.append((fn[0], p))

                # Maxmimum number of solutions is the degree
                if len(solp) == degree:
                    break

        sol += solp
        p, p0 = next_prime(p), p
        if progress and p1 != p2:
            pbar.update(p-p0)

    print time.time() - start

    return sol


def is_even(f):
    coeffs = f.coeffs()
    for i,c in enumerate(coeffs):
        if i % 2 == 1 and c != 0:
            return false

    return true


def is_translate(f, g):
    """
    Returns True if f, g are translates of each other (2nd method). It is 
    assumed that f and g are monic.
    """
    x = f.parent().gen()
    f_deg = f.degree()
    g_deg = g.degree()

    if f_deg != g_deg:
       return False

    if f[f_deg] != 1:
        f = f / f[f_deg]

    if g[g_deg] != 1:
        g = g / g[g_deg]



    t = (f[f_deg - 1] - g[g_deg - 1]) / f_deg

    f_trans = f(x - t)

    for i in range(f_deg - 1):
        if f_trans[i] != g[i]:
            return False

    return True


def solve_roots_range(f, p1, p2, progress=True, extra=False):
    if progress:
        print "Calculating roots..."
        pbar = progress_meter.ProgressMeter(total=p2 - p1)

    p1 = Integer(p1)
    if not p1.is_prime():
        p1 = next_prime(p1)

    p = p1
    coeffs = f.coeffs()
    roots = list()
    while p < p2:
        g = make_polynomial(coeffs, Zmod(p))
        rootsp = g.roots(multiplicities=False)
        total = len(rootsp)

        if extra:
            p = int(p)
            for i in range(total):
                r = int(rootsp.pop())
                roots.append((r, p, float(RR(r)/p), i + 1, total))
        else:
            for i in range(total):
                roots.append((rootsp.pop(), p))

        p, p0 = next_prime(p), p
        pbar.update(p - p0)

    return roots
