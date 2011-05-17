from __future__ import division
import os
import sqlite3
from sage.all import *
import polynomial


class DB:
    # Some constants for format of roots
    ALL = 0 # (n, p, r)
    TUPLE = 1 # (n, p) where f(n) = 0 mod p
    REAL = 2 # r/p in decimal approx.
    REAL_TUPLE = 3 # (r, p) like TUPLE but r real


    
    def __init__(self, dir_=None):
        """Initialize RootsDB."""
        if dir_ is None:
            dir_ = "data/roots"

        if not os.path.exists(dir_):
            os.makedirs(dir_)

        self.dir_ = dir_
        self.index = dir_ + "/index.db"
        self.connect()

        return None

    def __del__(self):
        """Close database."""
        self.conn.close()
        
        return None

    def _filename(self, f):
        return polynomial.name_polynomial(f)

    def add(self, f):
        """Add a polynomial to the database."""
        coeffs = polynomial.name_polynomial(f)
        degree = int(f.degree())
        group = int(f.galois_group()._n)

        c = self.conn.execute("SELECT count(*) FROM polynomials \
                              WHERE coefficients=?", (coeffs, ))
        if c.fetchone()[0] > 0:
            print f, "is already in the database."
            return None

        fconn = self.connect(f)
        fconn.execute("""CREATE TABLE IF NOT EXISTS roots
                      (root integer,
                      prime integer,
                      normalized real,
                      th integer,
                      total integer)""")
        fconn.commit()
        self.conn.execute("INSERT INTO \
                          polynomials(coefficients, degree, \
                          galois_group, roots, last_prime) \
                          VALUES (?,?,?,?,?)",
                          (coeffs, degree, group, 0, 0))
        self.conn.commit()

        return None

    def check_missing_roots(self, f):
        """Check all primes upto last_prime for missing roots.
        THIS DOESN'T WORK IN REASONABLE TIME!
        """
        last_prime = self.last_prime(f, True)
        p = 1
        missing = list()
        for r in self.roots(f):
            if r[1] > next_prime(p):
                gap_roots = polynomial.solve_roots_range(f,
                        next_prime(p), r[1])
                missing += (gap_roots)
                if gap_roots:
                    print "Missing:", gap_roots
            p = r[1]

        return missing

    def close(self):
        """Close connection to DB."""
        self.conn.close()

        return None

    def connect(self, f=None):
        """Connect to db.

        If f is not given, it connects to the index.

        Arguments:
        f -- Polynomial
        """
        if f is None:
            if os.path.exists(self.index):
                self.conn = sqlite3.connect(self.index)
            else:
                self.conn = sqlite3.connect(self.index)
                self.create()

            return None
        else:
            return sqlite3.connect(self.dir_ + "/" + self._filename(f))

    def count(self, f, force=False, type_=None):
        """Return count of roots for f."""
        if force:
            if type_:
                where = " WHERE total=" + str(type_)
            else:
                where = ""
            fconn = self.connect(f)
            c = fconn.execute("SELECT COUNT(*) FROM roots" + where)

        else:
            c = self.conn.execute("SELECT roots FROM polynomials \
                                  WHERE coefficients=?",
                                  (polynomial.name_polynomial(f),))

        return c.fetchone()[0]

    def create(self):
        """Create tables."""
        self.conn.execute("""CREATE TABLE polynomials
                          (id INTEGER PRIMARY KEY,
                          coefficients TEXT,
                          degree INTEGER,
                          galois_group INTEGER,
                          roots INTEGER,
                          last_prime INTEGER)""")
        return None

    def density(self, f, precision=50):
        """Return a dictionary with density."""
        density = [0, ] * precision
        for p in self.roots_by_partition(f, precision):
            density[p] += 1

        total = sum(density)
        density = [x / total for x in density]

        return density

    def densities(self, f, precision, interval, start=None):
        """Return an iterator of densities.
        
        Arguments:
        f -- A polynomial in the database
        precision -- Number of bins to produce density
        interval -- Number of roots between each density
        start -- Start calculating density after this many roots
        """
        density = [0, ] * precision
        rootsbp = self.roots_by_partition(f, precision)
        count = 0
        n = 0
        if start:
            for p in rootsbp:
                density[p] += 1
                n += 1
                if n == start:
                    break

            count = n
            yield [d / count for d in density]

        n = 0
        for p in rootsbp:
            density[p] += 1
            n += 1
            
            if n == interval:
                count += n
                n = 0
                yield [d / count for d in density]

        if n != 0:
            count += n
            yield [d / count for d in density]

    def densities_by_prime(self, f, precision=50, skip=1, start=None):
        """Return an iterator of (density, prime) at primes.

        Arguments:
        f -- A polynomial in the database
        precision -- Number of bins to produce density
        skip -- Number of primes between each density
        start -- Prime number to calculate densities from
        """
        density = [0, ] * precision
        rootsbp = self.roots_by_partition(f, precision,
                                          format_="realtuple")
        count = 0
        if start:
            for (b, p) in rootsbp:
                density[b] += 1
                count += 1
                if p >= start:
                    break

            yield ([d / count for d in density], p)

        cprime = 0
        skipped = 0
        for (b, p) in rootsbp:
            density[b] += 1
            count += 1
            
            if cprime != p:
                if skipped < skip:
                    cprime = p
                    skipped += 1
                else:
                    yield ([d / count for d in density], p)
                    cprime = p
                    skipped = 0


    def grouped_roots(self, f, format_="roots", type_=None):
        """Return a iterator for list of roots by prime."""
        roots = list()
        p = 0
        for r in self.roots(f, "all", type_):
            if p != r[1]:
                if p != 0:
                    yield roots
                p = r[1]
                roots = list()

            if format_ == "normalized":
                roots.append(r[2])
            elif format_ == "tuple":
                roots.append((r[0], r[1]))
            else:
                roots.append(r[0])

    def last_prime(self, f, force=False):
        """Return the last prime in DB."""
        if force:
            fconn = self.connect(f)
            c = fconn.execute("SELECT MAX(PRIME) FROM roots")
        else:
            c = self.conn.execute("SELECT last_prime FROM polynomials \
                                  WHERE coefficients=?",
                                  (polynomial.name_polynomial(f), ))

        return c.fetchone()[0]

    def list(self, degree=None, group=None, info=False):
        """List polynomials in database."""
        if degree is not None and group is not None:
            degree = int(degree)
            group = int(group)
            c = self.conn.execute("SELECT * FROM polynomials \
                                  WHERE degree=? AND galois_group=? \
                                  ORDER BY coefficients",
                                  (degree, group))
        elif degree is not None and group is None:
            degree = int(degree)
            c = self.conn.execute("SELECT * FROM polynomials \
                                  WHERE degree=? \
                                  ORDER BY galois_group, coefficients",
                                  (degree, ))
        else:
            c = self.conn.execute("SELECT * FROM polynomials \
                                  ORDER BY degree, galois_group, \
                                  coefficients")


        fs = list()
        if info:
            for row in c:
                fs.append(row)
        else:
            for row in c:
                fs.append(polynomial.name_to_polynomial(row[1]))

        return fs

    def load_roots(self, f, format="tuple"):
        """Load roots.
        
        Arguments:
        f -- polynomial
        format -- One of tuple, real, quotient, all
        """
        if format == "all":
            select = "*"
        elif format == "real":
            select = "normalized"
        else:
            select = "root, prime"

        fconn = self.connect(f)
        c = fconn.execute("SELECT " + select + " FROM roots \
                          ORDER BY prime, root")

        roots = list()
        if format == "real":
            for row in c:
                roots.append(row[0])
        else:
            for row in c:
                roots.append(row)

        return roots

    def load(self, id_):
        """Return a Sage polynomial object.

        Arguments:
        id -- number assigned by the database, shows up when DB.show()
              is called
        """
        c = self.conn.execute("SELECT coefficients FROM polynomials \
                              WHERE id=?", (int(id_), ))
        return polynomial.name_to_polynomial(c.fetchone()[0])

    def query(self, f, query):
        """Execute a query for specific polynomial."""
        fconn = self.connect(f)
        return fconn.execute(query)


    def roots(self, f, format_="tuple", type_=None, limit=None):
        """Return iterator over roots."""
        if format_ == "all":
            select = "*"
        elif format_ == "real":
            select = "normalized"
        elif format_ == "realtuple":
            select = "normalized, prime"
        else:
            select = "root, prime"

        if type_:
            where = " WHERE total=" + str(type_)
        else:
            where = ""

        if limit:
            query_limit = " LIMIT " + str(limit)
        else:
            query_limit = ""

        fconn = self.connect(f)
        c = fconn.execute("SELECT " + select + " FROM roots" + where +
                          query_limit)

        print "Query:", "SELECT " + select + " FROM roots" + where + query_limit
        
        if format_ == "real":
            for row in c:
                yield row[0]
        else:
            for row in c:
                yield row

    def roots_by_partition(self, f, precision=50, type_=None,
                           format_=None):
        """Return an iterator of roots by parition."""
        if format_ == "realtuple":
            for (r, p) in self.roots(f, "realtuple", type_):
                yield (RR(r * precision).floor(), p)
        else:
            for r in self.roots(f, "real", type_):
                yield RR(r * precision).floor()

    def save_roots(self, f, p2):
        """Save roots between last prime upto p2."""
        p = next_prime(self.last_prime(f))

        if p > p2:
            print "Already calculated upto", p
            return None

        roots = polynomial.solve_roots_range(f, p, p2, extra=True)
        fconn = self.connect(f)
        for r in roots:
            fconn.execute("INSERT INTO roots VALUES(?,?,?,?,?)", r)
        fconn.commit()

        count = len(roots) + self.count(f)
        last_prime = r[1]

        self.conn.execute("UPDATE polynomials \
                          SET roots=?, last_prime=? \
                          WHERE coefficients=?",
                          (count, last_prime,
                           polynomial.name_polynomial(f)))
        self.conn.commit()

        return None

    def show(self, degree=None, group=None):
        """Show database contents."""
        data = self.list(degree, group, info=True)
        current_degree = str(0)
        current_group = str(0)
        for row in data:
            id = "(" + str(row[0]) + ")"
            id = id.ljust(6)
            f = polynomial.name_to_polynomial(row[1])
            degree = str(row[2])
            group = str(row[3])
            count = str(row[4]).center(10)
            last_prime = str(row[5]).center(10)

            if current_degree != degree:
                current_degree = degree
                print
                print "Degree", degree
            if current_group != group:
                current_group = group
                print
                print "Galois Group", group

            print id, count, last_prime, f

        return None

    def update_index(self, rebuild=False):
        """Update index.

        Arguments:
        rebuild -- Rebuild the index from scratch

        Otherwise, it only updates count and last_prime
        """
        if rebuild:
            os.remove(self.index)
            self.connect()

            files = os.listdir(self.dir_)
            for f in files:
                if f == "index.db":
                    continue
                print "Adding", f
                self.add(polynomial.name_to_polynomial(f))

            self.update_index()
        else:
            for f in self.list():
                count = self.count(f, True)
                last_prime = self.last_prime(f, True)
                if count != self.count(f) or \
                last_prime != self.last_prime(f):
                    print "Updating", f
                    self.conn.execute("UPDATE polynomials \
                                      SET roots=?, last_prime=? \
                                      WHERE coefficients=?",
                                      (count, last_prime,
                                       polynomial.name_polynomial(f)))
            self.conn.commit()

        return None
