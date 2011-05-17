######################################################################
# DB class for saving roots of polynomials mod p
######################################################################

import os
from sage.all import *
from polynomial import *

class DB():
    """File database for polynomials and its normalized roots."""

    def __init__(self, db_dir="data", degree_prefix="degree",
                 gid_prefix="id", load=True):
        self.db_dir = db_dir
        self.degree_prefix = degree_prefix
        self.gid_prefix = gid_prefix
        if load:
            self.load()

    def add(self, f):
        """
        Adds a polynomial to the database by creating a file

        INPUT:

        - ``f`` -- Irreducible polynomial over rationals

        EXAMPLES::

            sage: db = DB()
            sage: R.<x> = PolynomialRing(QQ)
            sage: f = x^4 - 16*x^3 - 2*x + 1
            sage: db.add(f)
        """
        if not f.is_irreducible():
            print f, "is not irreducible."
            return None

        fname = self.path_to(f)

        if os.path.isfile(fname):
            print f, "is already in the database."

        else:
            fdb = open(fname, 'w')
            fdb.close()
            self.load()

        return None

    def check(self):
        """
        """

        n = len(self.data)
        for i in range(n - 1):
            for j in range(i + 1,n):
                f = self.data[i][2]
                g = self.data[j][2]
                linef = self.data[i]
                lineg = self.data[j]

                if not (linef[0] == lineg[0]) or not (linef[1] == lineg[1]):
                    break

                if is_translate(f, g):
                    count_f = self.count(f)
                    count_g = self.count(g)
                    print "(1) " + str(f) + " Roots in data: " + str(count_f)
                    print "(2) " + str(g) + " Roots in data: " + str(count_g)
                    print "seem to be translates of each other. "
                    print "Following are real parts of the roots: "
                    roots_f = f.complex_roots()
                    roots_g = g.complex_roots()
                    print roots_f
                    print roots_g

                    try:
                        delete = int(raw_input(
                                "Which one would you like to delete? (1,2) "))
                    except ValueError:
                        print "Input 1 or 2. Continuing without deleting."
                    except:
                        raise
                    else:
                        if delete == 1:
                            self.delete(f)
                        elif delete == 2:
                            self.delete(g)

        return None

    def delete(self, f):
        """
        Moves data file of f into db.dir/trash

        """
        if not os.path.exists(self.db_dir + "/trash"):
            os.mkdir(self.db_dir + "/trash")

        confirm = raw_input("Do you want to delete " + str(f) + 
                            " from DB? (y/n) ")

        if confirm == "y":
            fname = self.filename(f)
            os.rename(self.db_dir + "/" + fname, self.db_dir + "/trash/" + fname)
            self.load()

        return None

    def files(self):
        """
        Lists files in data directory
        """
        files = os.listdir(self.db_dir)
        files = filter(lambda name: name[:len(self.degree_prefix)] == \
                                    self.degree_prefix, files)
        return files

    def list(self, degree=None, gid=None, info=False, filter_func=None):
        """
        Lists polynomials in the database
        
        INPUT:

        - ``degree`` -- integer (default: None); list only the polynomials of
          degree
        - ``gid`` -- integer (default: None); list only the polynomials with
          Galois
                     group gid, requires degree
        - ``info`` -- Returns a list of tuple: (degree, gid, f, filename)
        """

        lst = list()

        for item in self.data:
            if ((not degree) or (degree == item[0])) and \
               ((not gid) or (gid == item[1])):
                if info:
                    lst.append(item)
                else:
                    lst.append(item[2])

        if filter_func:
            lst = filter(filter_func, lst)

        return lst

    def degrees(self):
        """Return a list of degrees of polynomials in database."""
        
        degrees = list()
        degrees.append(self.data[0][0])
        
        for entry in self.data:
            if entry[0] != degrees[-1]:
                degrees.append(entry[0])

        return degrees

    def galois_groups(self, n):
        """Return a list of Galois groups for degree n.

        Arguments:
        n -- degree of polynomial

        """
        data = self.list(n, info=True)
        groups = list()
        groups.append(data[0][1])
        
        for entry in data:
            if entry[1] != groups[-1]:
                groups.append(entry[1])

        return groups

    def load(self):
        """Load db, stores data in self.data."""
        files = self.files()
        self.data = list()

        for path in files:
            f = self.fname_to_poly(path)
            fname = path.split("/")[-1]
            d = int(fname.split("_")[0][len(self.degree_prefix):])
            g = int(fname.split("_")[1][len(self.gid_prefix):])
            self.data.append((d, g, f, fname))

        self.data.sort()

        return None

    def show(self, degree=None, gid=None, filter_func=None):
        """Show the summary of the database.

        Arguments:
        degree -- integer (default: None); list only the polynomials of
                  degree
        gid -- integer (default: None); list only the polynomials with
               Galois group gid (requires degree)
          
        """
        lst = self.list(degree, gid, info=True, filter_func=filter_func)
        current_degree = 0
        current_group = 0
        for i in range(len(lst)):
            if current_degree != lst[i][0]:
                current_degree = lst[i][0]
                current_group = 0
                print ""
                print ""
                print "Degree ", current_degree

            if current_group != lst[i][1]:
                current_group = lst[i][1]
                print ""
                print "Galois Group:", current_group

            print " ("+str(i)+") ", lst[i][2], " ["+str(self.count(lst[i][2]))+"]"

    def loadf(self, i):
        """
        Loads a polynomial available in db

        INPUT:

        - ``i`` -- integer; number shown when self.show() is called

        OUPTUT
          f -- An element of polynomial ring over rationals
        """
        return self.data[i][2]

    def filename(self, f):
        """Return a filename for given polynomial."""

        # Read coefficients
        c = str()
        for i in f.coeffs():
            c += "_" + str(i)

        degree = str(f.degree())
        
        # Find out Galois group id
        gid = str(f.galois_group()._n)

        fname = self.degree_prefix + degree + "_" + self.gid_prefix + gid + c

        return fname

    def path_to(self, f):
        """Return relative path to data file for a polynomial.

        INPUT:
        f -- a polynomial
        """

        return self.db_dir + "/" + self.filename(f)

    def fname_to_poly(self, fname):
        """Return polynomial from filename.
        
        Arguments:
        fname -- file name

        """
        name = fname.split("_")
        c = list()
        for i in name[2:]:
            try:
                i = QQ(i)
            except:
                print "Error reading file name of: ", fname

            c.append(i)

        # Make polynomial, check galois group
        f = make_polynomial(c)

        return f

    def _degree(self, fname):
        return int(fname.split("/")[-1].split("_")[0][len(self.degree_prefix):])

    def _gid(self, f):
        return int(f.split("/")[-1].split("_")[1][len(self.gid_prefix):])

    def count(self, f):
        """Return the count of roots in database."""
        path = self.path_to(f)
        if not os.path.isfile(path):
            print "File does not exist"
            return None

        i = -1
        with open(path) as file_:
            for i, l in enumerate(file_):
                pass

        return i + 1

    def load_roots(self, f, raw=True):
        """Return a list of roots for f."""
        path = self.path_to(f)

        output = list()
        with open(path) as fdb:
          for i, l in enumerate(fdb):
              [num, denom] = l.split()
              if raw:
                  output.append((int(num), int(denom)))
              else:
                  output.append(QQ(num) / QQ(denom))

        return output

    def roots(self, f):
        path = self.path_to(f)

        with open(path) as rootsdb:
            for l in rootsdb:
                [num, denom] = l.split()
                yield (int(num), int(denom))

    def roots_by_partition(self, f, precision=50):
        """Return a list of roots by partition."""
        roots = self.load_roots(f)

        return [(r[0] * precision / QQ(r[1])).floor() for r in roots]

    def density(self, f, precision=50):
        """Return a dictionary with density."""
        roots_by_partition = self.roots_by_partition(f, precision)
        total = len(roots_by_partition)
        density = dict([(i,0) for i in range(precision)])
        for p in roots_by_partition:
            density[p] += 1

        for k in density.keys():
            density[k] = density[k] / QQ(total)

        return density

    def save_roots(self, f, p2, verbose=True, even=False):
        """Save roots in db for polynomial f.
        
        Arguments:
        f -- Irreducible polynomial

        """
        p1 = next_prime(self.last_prime(f))
        if p1 > p2:
            print "No roots to calculate."
            return None

        fname = self.path_to(f)
        fdb = open(fname, 'a')
        r = roots_sage(f, p1, p2)

        for q in r:
            fdb.write(str(q[0]) + " " + str(q[1]) + "\n")

        fdb.close()
        
        return None
      
    def last_prime(self, f):
        """Return the last prime number recorded in DB

        Arguments:
        f -- Polynomial in database

        OUTPUT:
          integer -- the last prime in DB
        """
        fname = self.path_to(f)
        if os.path.getsize(fname) == 0:
            p = 0
        else:
            for line in open(fname):
                pass
            p = QQ(line.split()[1])

        return p
