import numpy as np

class Hex:
    def __init__(self, resource_type, number_token):
        self.resource_type = resource_type
        self.number_token = number_token
        self.dots = 0
        self.robber_blocking = False
        self.getdots()
    
    def __repr__(self):
        return f"Hex(resource_type='{self.resource_type}', number_token={self.number_token})"
    
    def getdots(self):
        ref = {0:0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}
        self.dots = ref[self.number_token]
    

class Board:
    def __init__(self):
        # Maps a hex (e.g., 'A') -> List of surrounding intersection coordinates
        # A to J is top to bottom, left to right hexes
        self.hexes = {
            "A": {"intersections": [(1, 1), (0, 2), (1, 3), (2, 3), (3, 2), (2, 1)],
                  "hex_type": None},
            "B": {"intersections": [(1, 3), (0, 4), (1, 5), (2, 5), (3, 4), (2, 3)],
                  "hex_type": None},
            "C": {"intersections": [(1, 5), (0, 6), (1, 7), (2, 7), (3, 6), (2, 5)],
                  "hex_type": None},
            "D": {"intersections": [(3, 0), (2, 1), (3, 2), (4, 2), (5, 1), (4, 0)],
                  "hex_type": None},
            "E": {"intersections": [(3, 2), (2, 3), (3, 4), (4, 4), (5, 3), (4, 2)],
                  "hex_type": None},
            "F": {"intersections": [(3, 4), (2, 5), (3, 6), (4, 6), (5, 5), (4, 4)],
                  "hex_type": None},
            "G": {"intersections": [(3, 6), (2, 7), (3, 8), (4, 8), (5, 7), (4, 6)],
                  "hex_type": None},
            "H": {"intersections": [(5, 1), (4, 2), (5, 3), (6, 3), (7, 2), (6, 1)],
                  "hex_type": None},
            "I": {"intersections": [(5, 3), (4, 4), (5, 5), (6, 5), (7, 4), (6, 3)],
                  "hex_type": None},
            "J": {"intersections": [(5, 5), (4, 6), (5, 7), (6, 7), (7, 6), (6, 5)],
                  "hex_type": None}
        }
        
        self.intersections = np.zeros((8,9), dtype = object)  # each valid intersection will have dict of (cont)
        # keys --> value
        # item --> (player.color, str(product))
        # 'adjacent hexes' --> list(hexes)
        # 'adjacent edges' --> list(edges), 
        # 'adjacent_dots_sum' --> int
        # 'settleable' --> boolean
        self.edges = {}  # dict of edges as keys --> 'open' or 'player.color' as value
        self.graph = {} # represent board (for bFS) as a graoh with int as keys --> set neighbor ints as values



    def generate_board(self, hex_and_tokens):
        """Generate a reduced-size board with labeled hexes."""
        # hex_and_tokens is list from left-to-right-top-to-bottom each resource type and number token
        # list of tuples ('hex type', int(number_token))


        identifiers = [letter for letter, _ in self.hexes.items()]
        for i, h in enumerate(hex_and_tokens):
            try:
                add_hex = Hex(h[0], h[1])
            except:
                import pdb; pdb.set_trace()
            self.hexes[identifiers[i]]['hex_type'] = add_hex
            for intsect in self.hexes[identifiers[i]]['intersections']:
                #import pdb; pdb.set_trace()
                row, col = intsect
                if self.intersections[row, col] == 0:
                    #import pdb; pdb.set_trace()
                    self.intersections[row, col] = {'item': None, 'adjacent_hexes':[], 'adjacent_edges': [], 
                                                    'adjacent_dots_sum': 0, 'settleable': True}
                self.intersections[row, col]['adjacent_hexes'].append(add_hex)
                self.intersections[row, col]['adjacent_dots_sum'] += add_hex.dots

        self._generate_edges()

    def _generate_edges(self):
        """Generate edges between intersections based on adjacency."""
        for id, hex_info in self.hexes.items():
            for i in range(6):
                if i == 5:
                    edge = tuple(sorted((hex_info['intersections'][i], hex_info['intersections'][0])))
                else:
                    edge = tuple(sorted((hex_info['intersections'][i], hex_info['intersections'][i+1])))
                if edge not in self.edges:
                    self.edges[edge] = 'open'
                    for intsect in edge:
                        row, col = intsect
                        self.intersections[row, col]['adjacent_edges'].append(edge)
        self.generate_graph_dict()
    
    def generate_graph_dict(self):
        for edge in self.edges:
            int1, int2 = edge
            if int1 in self.graph:
                self.graph[int1].add(int2)
            else:
                self.graph[int1] = set()
                self.graph[int1].add(int2)
            if int2 in self.graph:
                self.graph[int2].add(int1)
            else:
                self.graph[int2] = set()
                self.graph[int2].add(int1)
        self.graph[(9, 9)] = set() # communal point, used to optimize




    def get_intersecting_hexes(self, intersection):
        """Return the hexes that touch a given intersection."""
        row, col = intersection
        if self.intersections[row, col] == 0:
            return None
        return self.intersections[row, col]['adjacent_hexes']



    
