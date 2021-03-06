from math import *


def numTiles(z):
    return pow(2, z)


def sec(x):
    return 1 / cos(x)


def latlon2relativeXY(lat, lon):
    x = (lon + 180) / 360
    y = (1 - log(tan(radians(lat)) + sec(radians(lat))) / pi) / 2
    return x, y


def latlon2xy(lat, lon, z):
    n = numTiles(z)
    x, y = latlon2relativeXY(lat, lon)
    return n * x, n * y


def tileXY(lat, lon, z):
    x, y = latlon2xy(lat, lon, z)
    return int(x), int(y)


def latEdges(y, z):
    n = numTiles(z)
    unit = 1 / n
    relY1 = y * unit
    relY2 = relY1 + unit
    lat1 = mercatorToLat(pi * (1 - 2 * relY1))
    lat2 = mercatorToLat(pi * (1 - 2 * relY2))
    return lat1, lat2


def lonEdges(x, z):
    n = numTiles(z)
    unit = 360 / n
    lon1 = -180 + x * unit
    lon2 = lon1 + unit
    return lon1, lon2


def tileEdges(x, y, z):
    lat1, lat2 = latEdges(y, z)
    lon1, lon2 = lonEdges(x, z)
    return lat2, lon1, lat1, lon2  # S,W,N,E


def mercatorToLat(mercatorY):
    return degrees(atan(sinh(mercatorY)))
