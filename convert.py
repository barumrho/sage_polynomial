from sage.all import *
import db_old
import db


old = db_old.DB()
new = db.DB()

for f in old.list():
    print f
    new.add(f)

    p = 1
    rootsp = []
    fconn = new.connect(f)
    for r in old.roots(f):
        if p != r[1]:
            if rootsp:
                total = len(rootsp)
                for i in range(total):
                    fconn.execute("insert into roots values(?,?,?,?,?)",
                                  (rootsp[i], p, float(RR(rootsp[i]) / p), i + 1, total))
            p = r[1]
            rootsp = [r[0], ]
        else:
            rootsp.append(r[0])
    
    fconn.commit()
