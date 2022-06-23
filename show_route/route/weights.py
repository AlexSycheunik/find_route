class RoutingWeights:
    def __init__(self):
        self.Weightings = {
            'motorway': {'car': 1},
            'trunk': {'car': 1},
            'primary': {'car': 1},
            'secondary': {'car': 1},
            'tertiary': {'car': 1},
            'unclassified': {'car': 1},
            'minor': {'car': 1},
            'residential': {'car': 1},
            'track': {'car': 1},
            'service': {'car': 1},
        }

    def get(self, transport, wayType):
        try:
            return self.Weightings[wayType][transport]
        except KeyError:
            return 0
