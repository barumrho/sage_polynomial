import sys
import db
import plots

num_args = len(sys.argv)
if num_args == 2:
    print "Please specify an action."

if sys.argv[2] == "save":
    if num_args >= 4:
        degree = int(sys.argv[3])
    else:
        degree = None

    if num_args >= 5:
        group = int(sys.argv[4])
    else:
        group = None

    if num_args >= 6:
        index = int(sys.argv[5])
    else:
        index = None

    db_ = db.DB(sys.argv[1])
    print "Using DB: " + sys.argv[1]
    if index != None:
        try:
            f = db_.list(degree, group)[index]
        except IndexError:
            print "Index is out of range."
            print "You have", len(db_.list(degree, group)), \
                    "polynomials in the specified group."
	    sys.exit(1)

        p2 = db_.last_prime(f) + 1000000
        print "Saving upto primes around", p2, "for", f
        db_.save_roots(f, p2)
    else:
        polynomials = db_.list(degree, group)
        p2 = db_.last_prime(polynomials[0]) + 100000
        for f in polynomials:
            print f
            db_.save_roots(f, p2)
