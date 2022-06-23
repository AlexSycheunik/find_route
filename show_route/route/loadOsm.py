import os
import osmapi
import xml.etree.ElementTree as etree
from datetime import datetime
from .dbdata import way_config

from . import tiledata
from . import tilenames
from . import weights


def getElementTags(element):
    result = {}
    for child in element:
        if child.tag == "tag":
            k = child.attrib["k"]
            v = child.attrib["v"]
            result[k] = v
    return result


def _ParseDate(DateString):
    result = DateString
    try:
        result = datetime.strptime(DateString, "%Y-%m-%d %H:%M:%S UTC")
    except:
        try:
            result = datetime.strptime(DateString, "%Y-%m-%dT%H:%M:%SZ")
        except:
            pass
        return result


def equivalent(tag):
    """Simplifies a bunch of tags to nearly-equivalent ones"""
    equivalent = {
        "primary_link": "primary",
        "trunk": "primary",
        "trunk_link": "primary",
        "secondary_link": "secondary",
        "tertiary": "secondary",
        "tertiary_link": "secondary",
        "residential": "unclassified",
        "minor": "unclassified",
        "steps": "footway",
        "driveway": "service",
        "pedestrian": "footway",
        "bridleway": "cycleway",
        "track": "cycleway",
        "arcade": "footway",
        "canal": "river",
        "riverbank": "river",
        "lake": "river",
        "light_rail": "railway"
    }
    try:
        return equivalent[tag]
    except KeyError:
        return tag


class LoadOsm(object):
    """Parse an OSM file looking for routing information, and do routing with it"""

    def __init__(self, transport, machine_weight, machine_height, machine_width):
        """Initialise an OSM-file parser"""
        self.routing = {}
        self.rnodes = {}
        self.transport = transport
        self.tiles = {}
        self.lines = []
        self.machine_weight = machine_weight
        self.machine_height = machine_height
        self.machine_width = machine_width
        self.weights = weights.RoutingWeights()
        self.api = osmapi.OsmApi(api="api.openstreetmap.org")

    def getArea(self, lat, lon):
        """Download data in the vicinity of a lat/long.
    Return filename to existing or newly downloaded .osm file."""

        z = tiledata.DownloadLevel()
        (x, y) = tilenames.tileXY(lat, lon, z)

        tileID = '%d,%d' % (x, y)
        if self.tiles.get(tileID, False):
            return
        self.tiles[tileID] = True

        filename = tiledata.GetOsmTileData(z, x, y)
        # print "Loading %d,%d at z%d from %s" % (x,y,z,filename)
        return self.loadOsm(filename)

    def getElementAttributes(self, element):
        result = {}
        for k, v in element.attrib.items():
            if k == "uid":
                v = int(v)
            elif k == "changeset":
                v = int(v)
            elif k == "version":
                v = int(v)
            elif k == "id":
                v = int(v)
            elif k == "lat":
                v = float(v)
            elif k == "lon":
                v = float(v)
            elif k == "open":
                v = (v == "true")
            elif k == "visible":
                v = (v == "true")
            elif k == "ref":
                v = int(v)
            elif k == "comments_count":
                v = int(v)
            elif k == "timestamp":
                v = _ParseDate(v)
            elif k == "created_at":
                v = _ParseDate(v)
            elif k == "closed_at":
                v = _ParseDate(v)
            elif k == "date":
                v = _ParseDate(v)
            result[k] = v
        return result

    def parseOsmFile(self, filename):
        result = []
        with open(filename, "r", encoding="utf-8") as f:
            for event, elem in etree.iterparse(f):  # events=['end']
                temp_name = ''
                flag = False
                if elem.tag == "node":
                    data = self.getElementAttributes(elem)
                    data["tag"] = getElementTags(elem)
                    result.append({
                        "type": "node",
                        "data": data
                    })
                elif elem.tag == "way":
                    data = self.getElementAttributes(elem)
                    data["tag"] = getElementTags(elem)
                    data["nd"] = []
                    for child in elem:
                        if child.tag == "nd":
                            data["nd"].append(int(child.attrib["ref"]))
                        if child.tag == "tag" and child.attrib["k"] == 'name':
                            temp_name = child.attrib["v"]
                            flag = True
                        if child.tag == "tag" and child.attrib["k"] == 'place':
                            flag = False
                    if flag:
                        self.lines.append({
                            "id": data["id"],
                            "name": temp_name,
                            "data": data["nd"]
                        })
                    result.append({
                        "type": "way",
                        "data": data
                    })
        return result

    def loadOsm(self, filename):
        if not os.path.exists(filename):
            print("No such data file %s" % filename)
            return False

        nodes, ways = {}, {}

        data = self.parseOsmFile(filename)

        for x in data:
            try:
                if x['type'] == 'node':
                    nodes[x['data']['id']] = x['data']
                elif x['type'] == 'way':
                    ways[x['data']['id']] = x['data']
                else:
                    continue
            except KeyError:
                continue

        for way_id, way_data in ways.items():
            flag = False
            for id in way_config:
                if way_id == id['way_id'] and (id['truck_ban'] == True
                                                or id['weight_limit'] < self.machine_weight
                                                or id['way_height'] < self.machine_height
                                                or id['way_width'] < self.machine_width):
                    flag = True
                    break
            if flag:
                continue
            way_nodes = []
            for nd in way_data['nd']:
                if nd not in nodes:
                    continue
                way_nodes.append([nodes[nd]['id'], nodes[nd]['lat'], nodes[nd]['lon']])
            self.storeWay(way_id, way_data['tag'], way_nodes)

        return True

    def storeWay(self, wayID, tags, nodes):
        highway = equivalent(tags.get('highway', ''))
        oneway = tags.get('oneway', '')
        reversible = not oneway in ('yes', 'true', '1')

        # Calculate what vehicles can use this route
        access = {'car': highway in (
            'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'minor', 'residential', 'service')}

        # Store routing information
        last = [None, None, None]
        for node in nodes:
            (node_id, x, y) = node
            if last[0]:
                if access[self.transport]:
                    weight = self.weights.get(self.transport, highway)
                    self.addLink(last[0], node_id, weight)
                    self.makeNodeRouteable(last)
                    if reversible:
                        self.addLink(node_id, last[0], weight)
                        self.makeNodeRouteable(node)
            last = node

    def makeNodeRouteable(self, node):
        self.rnodes[node[0]] = [node[1], node[2]]

    def addLink(self, fr, to, weight=1):
        """Add a routeable edge to the scenario"""

        try:
            if to in list(self.routing[fr].keys()):
                return
            self.routing[fr][to] = weight
        except KeyError:
            self.routing[fr] = {to: weight}

    def findNode(self, lat, lon):
        """Find the nearest node that can be the start of a route"""
        self.getArea(lat, lon)
        maxDist = 1E+20
        nodeFound = None
        for (node_id, pos) in list(self.rnodes.items()):
            dy = pos[0] - lat
            dx = pos[1] - lon
            dist = dx * dx + dy * dy
            if dist < maxDist:
                maxDist = dist
                nodeFound = node_id
        return nodeFound
