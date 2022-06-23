import os
from urllib.request import urlretrieve
from .tilenames import tileEdges


def DownloadLevel():
    return 15


def GetOsmTileData(z, x, y):
    if x < 0 or y < 0 or z < 0 or z > 25:
        print("Disallowed (%d,%d) at zoom level %d" % (x, y, z))
        return

    directory = 'cache/%d/%d/%d' % (z, x, y)
    filename = '%s/data.osm.pkl' % directory
    if not os.path.exists(directory):
        os.makedirs(directory)

    if z == 15:
        s, w, n, e = tileEdges(x, y, z)
        URL = 'http://api.openstreetmap.org/api/0.6/map?bbox={},{},{},{}'.format(w, s, e, n)

        if not os.path.exists(filename):
            urlretrieve(URL, filename)
        return filename

    elif z > 15:
        while z > 15:
            z = z - 1
            x = int(x / 2)
            y = int(y / 2)
        return GetOsmTileData(z, x, y)
    return None
