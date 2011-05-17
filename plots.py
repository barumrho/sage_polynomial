###############################################################################
# Code used in producing plots
###############################################################################

from __future__ import division
from sage.all import *
from db import DB

colors = ["#000000", "#FF0000", "#FFFF00", "#0000FF", "#FF00FF",
          "#808080", "#008000", "#00FF00", "#800000", "#000080",
          "#808000", "#800080", "#C0C0C0", "#00FFFF", "#008080"]

class DensityPlot:
    """Density plot object."""

    plotdir = "plots"
    defaults = {"precision": 50,
                "type_": None,
                "limit": None,
                "show_label": True,
                "filename": None
               }

    def __init__(self, f, **kw):
        """Create a density plot.

        Arguments:
        f -- Polynomial in database
        precision -- Number of bins
        type_ -- Type of roots

        Keyword Arguments:
        
        """
        self.f = f
        self.degree = f.degree()
        self.group = f.galois_group()._n
        
        self.precision = kw.get("precision", self.defaults["precision"])
        self.type_ = type_

        db = DB()
        self.count = db.count(f)
        self.last_prime = db.last_prime(f)

    def filename(self):
        """Return appropriate filename for the plot."""
        degree = "d" + str(self.degree)
        group = "g" + str(self.group)
        count = "c" + str(self.count)
        last_prime = "l" + str(self.last_prime)
        precision = "p" + str(precision)

        filename = join([degree, group, count, last_prime, precision],
                        "_")

        if self.type_:
            type_ = "t" + str(type_) + "_"
            filename = join([filename, type_], "_")

        coeffs = [str(c) for c in self.f.coeffs()]
        coeffs = join(coeffs, "_")

        filename += "_" + coeffs
        
        return "density/" + filename + ".png"

    def label(self):
        """Return label."""
        label_opts = {'fontsize': 8,
                      'horizontal_alignment': 'right',
                      'vertical_alignment': 'top'}
        label_text = join([str(self.f), 
                           "Galois Group: " + str(self.group),
                           "Count:" + str(self.count),
                           "Last prime:" + str(self.last_prime)])
        if self.type_ is not None:
            label_text += ", " + str(self.type_) + "-roots only"
        

        return text(label_text, (1, plot_opts['ymax']), **label_opts)

    def plot(self):
        # Keyworded arugments
        start = kw.get('start', 0)
        stop = kw.get('stop')
        showlines = kw.get('showlines', True)
        showlabel = kw.get('showlabel', True)
        traces = kw.get('traces', 0)

        # Plot options
        plot_opts = {'xmin': kw.get('xmin'),
                     'xmax': kw.get('xmax'), 
                     'ymin': kw.get('ymin', 0.75 / precision), 
                     'ymax': kw.get('ymax', 1.25 / precision), 
                     'markersize': kw.get('markersize', 3)}

        db = DB()
        last_prime = db.last_prime(f)
        total = db.count(f, True, type_=type_)
        interval = 1 / precision

        # Calculate points where we take snapshots to show traces
        snapshots = list()
        unit = total // (traces + 1)
        for n in range(traces):
            snapshots.append(unit * (n + 1))

        snapshots.append(total)

        plot = scatter_plot([])
        counts = [0, ] * precision
        n = 0
        for p in db.roots_by_partition(f, precision, type_):
            counts[p] += 1

            if n == snapshots[0]:
                del snapshots[0]
                plot += plot_density([i / n for i in counts], 
                                     alpha=(n/total), **plot_opts)
            n += 1

        plot += plot_density([i / total for i in counts], show_lines=True,  **plot_opts)

        self.plot = plot

    def save(self):
        """Save the plot."""
        plot = density(f, precision=precision, type_=type_, traces=5)
        plot += line([(0,1/precision), (1,1/precision)], alpha=0.3)
        filename = "plots/" + density_filename(f, db.count(f),
                                               db.last_prime(f), precision,
                                               type_)
        save_opts = {'figsize': [10,5],
                     'ymax': 1.25/precision,
                     'ymin': 0.75/precision
                    }
        plot.save(filename, **save_opts)

        return None

    def show(self):
        """Show current configuration."""
        print "f(x) =", self.f
        print "Precision:", self.precision
        print "Root-type:", self.type_
        print "Filename:", self.filename

def sqr_dist_prime(f, precision=50, skip=1000, start=None):
    """Return a plot of square distances from the expected value."""
    db = DB()
    exp = 1 / precision
    points = list()
    for (d, p) in db.densities_by_prime(f, precision, skip, start):
        sqd = sum([(n - exp) ** 2 for n in d])
        points.append((p, sqd))

    plot_opts = {"markersize": 3,
                 "ymin": 0,
                 "ymax": 0.000001}

    return scatter_plot(points, **plot_opts)


def square_distance(f, precision=50, interval=1000, start=0):
    """Return a plot of square distances from the expected value."""
    db = DB()
    exp = 1 / precision
    points = list()
    i = 1
    for d in db.densities(f, precision, interval, start):
        sqd = sum([(n - exp) ** 2 for n in d])
        points.append((i * interval + start, sqd))
        i += 1

    plot_opts = {"markersize": 3}

    return scatter_plot(points, **plot_opts)


def weyl_sum(f,l,stop=None):
    db = DB()
    roots = db.load_roots(f)[:stop]
    sum = 0

    for n in range(len(roots)):
        print sum
        print roots[n]
        sum += 1 / (n + 1) * exp(2*pi.n()*l*roots[n].n()).n()

    return sum


def distance_prime(f):
    db = DB()
    roots = db.load_roots(f, raw=True)
    p = int(roots[0][1])
    lst = list()
    for r in roots:
        p1 = int(r[1])
        if p != p1:
            lst.append((p, p1 - p))
            p = p1

    return lst


def distance_plot(f, limit=None):
    dist = distance_prime(f)[:limit]
    #dist = [(i, dist[i]) for i in range(len(dist))]
  
    return scatter_plot(dist)


def density_interval(f, low, high, limit=None, convergence=False):
    """Return the density for the interval [low, high]."""
    db = DB()
    roots = db.load_roots(f, raw=False)[:limit]
    total = len(roots)
    count = 0
    if convergence:
        lst = list()

    for i in range(len(roots)):
        if low <= roots[i] <= high:
            count += 1
        if convergence:
            lst.append((i + 1, count / (i + 1)))

    if convergence:
        return lst
    else:
        return count / total


def convergence_plots(fs, low, high):
    """
    """
    plots = scatter_plot([])
    for i in range(len(fs)):
        plots += convergence_plot(fs[i], low, high, colors[i])

    return plots


def convergence_plot(f, low, high, color='#000000'):
    """
    Given f, and a subinterval of [0,1], draws convergence plot with data
    available in DB
    """
    points = density_interval(f, low, high, convergence=True)
    conv_line = line([(0, high - low), (len(points), high - low)])

    plot_opts = {'markersize': 1,
                 'marker': 's',
                 'facecolor': color,
                 'edgecolor': color}
    plot = scatter_plot(points, **plot_opts)
    plot += conv_line

    return plot
        

def plot_density(density, show_lines=False, **plot_opts):
    """Return a density plot.

    Arguments:
    density -- a list of length precision containing the density in each
               interval
    plot_opts -- a dictionary of options for plots used by
                 scatter_plot()

    Notes:
    This function returns a plain plot with no labels or scaling. It is
    designed to be used by density()

    """
    points = list()
    precision = len(density)
    interval = 1 / precision
    lines = scatter_plot([])
    for i in range(precision):
        x = (i+0.5) * interval
        y = density[i]
        points.append((x, y))

        if show_lines and i > 0:
            lines += line([points[i], points[i -1]])

    return scatter_plot(points, **plot_opts) + lines


def animate_density_plot(f, frames, precision=50, **kw):
    """
    """
    db = DB()
    total = db.count(f)
    n = int(total // frames)

    lst = list()

    ymax = 0
    for i in range(frames - 1):
        stop = (i + 1) * n
        lst.append(density(f, precision, stop=stop))

        if ymax < lst[-1].get_minmax_data()['ymax']:
            ymax = lst[-1].get_minmax_data()['ymax']

    lst.append(density(f, precision))

    # Plot options
    plot_opts = {'xmin': kw.get('xmin'),
                 'xmax': kw.get('xmax'),
                 'ymin': kw.get('ymin', 0),
                 'ymax': kw.get('ymax', ymax)}

    return animate(lst, **plot_opts)


def animate_flat_plot(f, step=10, limit=None, figsize=None):
    db = DB()

    if type(f) != list:
        f = [f, ]

    # Figure out how many frames we will have
    # ...not very efficient
    max = 1
    for i in range(len(f)):
        n = len(db.load_roots(f[i], raw=False))
        if max < n:
            max = n

    if (limit and max < limit) or not limit:
        limit = max
    frames = ceil(limit / step)

    plots = list()
    for i in range(frames):
        j = (i + 1) * step
        plots.append(flat_plot(f, j, False))

    figsize = (15, len(f))

    return animate(plots, figsize=figsize)


def flat_plot(f, limit=None, legend=False, save=False):
    """
    Produces a plot of normalized roots for given irreducible f

    INPUT:
      `f` -- Either a polynomial or a list of polynomials
      `limit` -- Limit the number of roots used in the plot
      `legend` -- Show lables for polynomials

    OUTPUT:
      Sage graphics object
    """
    db = DB()
    
    if type(f) != list:
        f = [f, ]

    plot = scatter_plot([])
    classes = list() # For color coordination

    for i in range(len(f)):
        # Identify a class of f by (degree, group id) tuple.
        degree = f[i].degree()
        gid = f[i].galois_group()._n
        cid = (degree, gid)
        if classes.count(cid) == 0:
            classes.append(cid)
        color = classes.index(cid)

        # Add plots
        roots = db.load_roots(f[i], raw=False)[:limit]
        points = [(j,i + 1) for j in roots]
        plot_opts = {'edgecolor': colors[0],
                     'facecolor': colors[color], 
                     'markersize': 10}
        plot += scatter_plot(points, **plot_opts)

        # Add labels
        count = len(roots)
        label = str(i + 1) + ": " + "D" + str(degree) + "G" + str(gid)
        # If the database contains more roots than given limit, do not add count
        # on the label, otherwise add count
        if not limit or count != limit:
            label += "(" + str(count) + ")" 

        label_opts = {'fontsize': 8, 
                      'rgbcolor': (20, 20, 20),
                      'horizontal_alignment': 'left'}
        plot += text(label, (1.02, i + 1), **label_opts)

        if legend:
            legend_opts ={'fontsize': 8, 
                          'rgbcolor': (20, 20, 20),
                          'horizontal_alignment': 'left'}
            legend_text = "(" + str(i + 1) + ") " + str(f[i])
            plot += text(legend_text, (0.01, -i-1), **legend_opts)

    if not limit:
        limit = ""

    plot += text(limit, (1,len(f)-0.2), horizontal_alignment='right')
    for i in range(11):
        plot += line([(i * 0.1, -100), (i * 0.1, 100)], alpha = 0.2, rgbcolor = (0, 0, 0))

    plot.axes(False)
    plot.axes_color((0.2, 0.2, 0.2))
    if not legend:
        axes_range = {'xmin': 0, 'xmax': 1.3, 'ymin': 0.5, 'ymax': len(f) + 0.5}
    else:
        axes_range = {'xmin': 0, 'xmax': 1.3, 'ymin': -len(f), 'ymax': len(f)}
      
    plot.set_axes_range(**axes_range)

    return plot
