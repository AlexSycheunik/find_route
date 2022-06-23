import math


class Router(object):
    def __init__(self, data):
        self.searchEnd = None
        self.queue = None
        self.data = data

    def distance(self, n1, n2):
        lat1 = self.data.rnodes[n1][0]
        lon1 = self.data.rnodes[n1][1]
        lat2 = self.data.rnodes[n2][0]
        lon2 = self.data.rnodes[n2][1]

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        dist2 = dlat * dlat + dlon * dlon
        dist = math.sqrt(dist2)
        return dist

    def doRoute(self, start, end):
        self.searchEnd = end
        closed = [start]
        self.queue = []

        blankQueueItem = {'end': -1, 'distance': 0, 'nodes': str(start)}

        try:
            for i, weight in self.data.routing[start].items():
                self.addToQueue(start, i, blankQueueItem, weight)
        except KeyError:
            return 'no_such_node', []

        count = 0
        while count < 1000000:
            count = count + 1
            try:
                nextItem = self.queue.pop(0)
            except IndexError:
                return 'no_route', []
            x = nextItem['end']
            if x in closed:
                continue
            if x == end:
                routeNodes = [int(i) for i in nextItem['nodes'].split(",")]
                return 'success', routeNodes
            closed.append(x)
            try:
                for i, weight in self.data.routing[x].items():
                    if not i in closed:
                        self.addToQueue(x, i, nextItem, weight)
            except KeyError:
                pass
        else:
            return 'gave_up', []

    def addToQueue(self, start, end, queueSoFar, weight=1):
        end_pos = self.data.rnodes[end]
        self.data.getArea(end_pos[0], end_pos[1])

        for test in self.queue:
            if test['end'] == end:
                return
        distance = self.distance(start, end)
        if weight == 0:
            return
        distance = distance / weight
        distanceSoFar = queueSoFar['distance']
        queueItem = {
            'distance': distanceSoFar + distance,
            'maxdistance': distanceSoFar + self.distance(end, self.searchEnd),
            'nodes': queueSoFar['nodes'] + "," + str(end),
            'end': end}

        count = 0
        for test in self.queue:
            if test['maxdistance'] > queueItem['maxdistance']:
                self.queue.insert(count, queueItem)
                break
            count = count + 1
        else:
            self.queue.append(queueItem)
