from core_classes import Board, Hex
import random
import numpy as np



class Player:
    def __init__(self, player_color):
        #basics
        self.color = player_color
        self.resources = {'lumber': 0, 'brick': 0, 'ore': 0, 'wheat': 0, 'sheep': 0}
        self.settlements_remaining = 5
        self.cities_remaining = 5
        self.roads_remaining = 15
        self.settlements = set() # intersections of settlements
        self.roads = set() # edges of roads
        self.cities = set() # upgraded settlements
        self.score = 0

        #helper pointers
        self.available_intersections = set() # available spots to settle
        self.available_edges = set() # available spots to build road
        self.gained_resource = [] # indicates what was received on a roll; used for visualization
        self.closest_intersections = set() # spots that we can build a road off of (used for shortest_path)
        self.traded = False # indicates whether they made trade // used for strategy consistency
        self.last_target = None, None # if traded, updates these to ensure consistency within a single turn
    
    def collect_resources(self, board_state, roll):
        '''
        roll = int
        board_state = instance of Board
        '''
        self.gained_resource = []
        for id, hex_info in board_state.hexes.items():
            if hex_info['hex_type'].number_token == roll:
                if not hex_info['hex_type'].robber_blocking:
                    for int in hex_info['intersections']:
                        if int in self.settlements:
                            r = hex_info['hex_type'].resource_type
                            self.resources[r] += 1
                            self.gained_resource.append(r)
                        if int in self.cities:
                            r = hex_info['hex_type'].resource_type
                            self.resources[r] += 2
                            self.gained_resource.append(f'two {r}')
    
    def build_settlement(self, board_state, intersection):
        '''
        If valid placement, 
            a. update personal and board tracking of settlements
            b. update score
            c. update new open edges for road placements
        '''
        row, col = intersection

        self.settlements.add(intersection)
        self.settlements_remaining -= 1
        board_state.intersections[row, col]['item'] = (self.color, 'settlement')
        board_state.intersections[row, col]['settleable'] = False
        self.score += 1

        for r in ['lumber', 'brick', 'wheat', 'sheep']: # pay for settleent
            self.resources[r] -= 1

        self.available_intersections.remove(intersection) # no longer can build settlement in place we just built
        neighbors = board_state.graph[intersection] # enfore neighbor rule; can't build 1 edge distance away 
        for neigh in neighbors:
            if neigh != (9,9):
                board_state.intersections[neigh]['settleable'] = False
                if neigh in self.available_intersections:
                    self.available_intersections.remove(neigh)


        adjacent_edges = board_state.intersections[intersection]['adjacent_edges']
        for edge in adjacent_edges:
            if board_state.edges[edge] == 'open':
                self.available_edges.add(edge)

        board_state.graph[(9, 9)].add(intersection)
        board_state.graph[intersection].add((9, 9))

        
    def build_road(self, board_state, edge):
        """
        If valid placement,
            a. add to self and board's marking of roads
            b. remove from potential new road locations
            c. update new open intersections locations
            d. update new open edge locations
        """
        
 
        self.roads.add(edge)
        board_state.edges[edge] = self.color
        self.available_edges.remove(edge)
        self.roads_remaining -= 1
        self.resources['lumber'] -= 1
        self.resources['brick'] -= 1

        #update new open intersections
        for intsect in edge:
            if self.is_valid(board_state, 'settlement', intsect):
                self.available_intersections.add(intsect)

        #update new open edges
        int1, int2 = edge
        adjacent_edges = set(board_state.intersections[int1]['adjacent_edges'] + board_state.intersections[int2]['adjacent_edges'])
        for e in adjacent_edges:
            if board_state.edges[e] == 'open':
                self.available_edges.add(e)
        
        #update closest_intersections, used for BFS
        self.closest_intersections.add(int1)
        self.closest_intersections.add(int2)
        board_state.graph[(9, 9)].add(int1)
        board_state.graph[(9, 9)].add(int2)
        board_state.graph[int1].add((9, 9))
        board_state.graph[int2].add((9, 9))

    
    def build_city(self, board_state, intersection):
        self.settlements_remaining += 1
        self.settlements.remove(intersection)
        self.cities_remaining -= 1
        self.cities.add(intersection)
        self.score += 1
        self.resources['ore'] -= 3
        self.resources['wheat'] -= 2
        board_state.intersections[intersection]['item'] = (self.color, 'city')

    
    
    def shortest_path(self, graph, start, end):
        """
        Finds the shortest path between two nodes in an unweighted graph.

        :param graph: Dictionary where keys are nodes and values are lists of neighboring nodes.
        :param start: Starting node (int).
        :param end: Ending node (int).
        :return: List of nodes representing the shortest path, or None if no path exists.
        """
        if start == end:
            return [start]
        
        # Queue for BFS, storing (current_node, path_to_current_node)
        queue = [(start, [start])]
        
        # Visited set to avoid reprocessing nodes
        visited = set()
        visited.add(start)
        
        while queue:
            # Remove the first element from the queue (FIFO)
            current_node, path = queue.pop(0)
            
            # Explore neighbors
            for neighbor in graph[current_node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    
                    # Check if we've reached the end
                    if neighbor == end:
                        return new_path
                    
                    # Add to queue for further exploration
                    queue.append((neighbor, new_path))
        
        # If we exhaust the queue without finding the end, no path exists
        return None
            


    
class Agent(Player):
    def __init__(self, player_color):
        super().__init__(player_color)
    
    def choose_action(self, game_state):
        '''
        Here is the bread and butter

        Primary function relevant to 9.66 Final Project

        Calculates intersection scores, then (probabilistically) obtains target product & intersection from those scores

        executes actions towards buying that product @ that intersections 
        '''

        actions = [] # logging purposes
        targets = []
        board_state = game_state.board

        
        if self.traded: # ensure, if we traded, we maintain current "strategy"
            target_product, target_intsect = self.last_target
            
        else:
            intsect_scores = self.evaluate_intersection_value(board_state) # collect intersection evaluations
            target_product, target_intsect = self.choose_priority(intsect_scores, game_state) # choose intersection & product probabilistically

            game_state.game_data['intsect scores'].append(intsect_scores) # debugging data

        game_state.game_data['targets'].append((target_product, target_intsect)) # debugging data


        self.four_to_one_trades(target_product, target_intsect, game_state) # execute 4:1 trade if possible
        

        if target_product == 'city': 
            if self.can_build('city'):
                self.build_city(board_state, target_intsect)
                actions.append('city')
                targets.append(target_intsect)
            return actions, targets
        
        if target_product == 'settlement':
            # if no roads necessary, buy the settlement
            if target_intsect in self.available_intersections and self.can_build('settlement'):
                self.build_settlement(board_state, target_intsect)
                actions.append('settlement')
                targets.append(target_intsect)
                return actions, targets
            
            # else, calculate desired route to intersection       
            temp = self.shortest_path(board_state.graph, (9,9), target_intsect)
            path_intsects = temp[1:]
            

            target_path = []
            for i in range(len(path_intsects) - 1):
                edge = tuple(sorted((path_intsects[i], path_intsects[i+1])))
                target_path.append(edge)
            #import pdb; pdb.set_trace()

            # build AMAP roads in desired route to intersection
            for edge in target_path: 
                if self.can_build('road'):
                    self.build_road(board_state, edge)
                    actions.append('road')
                    targets.append(edge)
                else:
                    return actions, targets
            
            # after building roads, check if we can buy settlement now
            if target_intsect in self.available_intersections and self.can_build('settlement'):
                self.build_settlement(board_state, target_intsect)
                actions.append('settlement')
                targets.append(target_intsect)
                
            
            return actions, targets
            
    def four_to_one_trades(self, target_product, target_intsect, game_state):
        board_state = game_state.board
        if target_product == 'city':
            req = {'lumber': 0,
                        'brick': 0,
                        'sheep': 0,
                        'wheat': 2,
                        'ore': 3}
        elif target_intsect in self.available_intersections: # then it would be a settlement
            req = {'lumber': 1 ,
                            'brick': 1 ,
                            'sheep': 1,
                            'wheat': 1,
                            'ore': 0}
        else:
            req = {'lumber': 1 , # then target is a road
                            'brick': 1 ,
                            'sheep': 0,
                            'wheat': 0,
                            'ore': 0}
        
        resources_needed = self.calculate_deficits(req) # dict of 'resource' --> int(amt needed)

        surplus_resources = {}

        for r in resources_needed.keys():
            surplus_resources[r] = max(self.resources[r] - req[r], 0)
        
        while any(amt >= 4 for r, amt in surplus_resources.items()): # while we have >=4 surplus resources, execute trades
            for r, amt in surplus_resources.items():
                if amt >= 4:
                    desired_r = max(resources_needed.keys(), key=lambda r: (resources_needed[r], self.tiebreaker(r, board_state))) # desired_resource is one with most deficits
                    self.resources[r] -= 4
                    surplus_resources[r] -= 4
                    self.resources[desired_r] += 1
                    resources_needed[desired_r] -= 1
                    game_state.last_action.append(f"{self.color} traded 4 {r} for 1 {desired_r} with bank") 
        
            
                





    def evaluate_intersection_value(self, board_state):
        '''
        Outlined in paper how intersections are evaluated

        value = (sum of dots in adjacent hexes) / (resources needed to build there, assuming optimal route)

        only valid intersections are considered (invalid if affected by neighbor rule or existing city on intersection)
        
        returns dictionary of {every valid intersection : intersections scores}
        '''
        intsect_scores = {}

        for(row, col), value in np.ndenumerate(board_state.intersections):
            if isinstance(value, dict):
                if value['settleable']: # valid settleable intersection
                    path = self.shortest_path(board_state.graph, (row, col), (9, 9))
                    roads_needed = len(path) - 2 # optimal path
                    req = {'lumber': 1 + roads_needed,
                            'brick': 1 + roads_needed,
                            'sheep': 1,
                            'wheat': 1,
                            'ore': 0}
                        
                elif (row, col) in self.settlements: # settlement intersection; ugradable to city
                    req = {'lumber': 0,
                        'brick': 0,
                        'sheep': 0,
                        'wheat': 2,
                        'ore': 3}
                else: # city intersection, don't do anything
                    continue
                
                missing_resources = self.calculate_deficits(req)
                num_missing = sum(missing_resources.values())
                dots = board_state.intersections[row, col]['adjacent_dots_sum']
                if num_missing:
                    intsect_scores[(row, col)] = dots/num_missing
                else:
                    intsect_scores[(row, col)] = dots/.1 # ensures extremely high value for intersection that can be built upon this very turn
                
        return intsect_scores
    
    
    def softmax_with_temperature(self, scores, T=1.0):
        """
        Apply softmax with temperature to a list of scores.
        
        Parameters:
            scores (list or np.array): List of input scores.
            T (float): Temperature parameter.
            
        Returns:
            np.array: Probability distribution.
        """
        scores = np.array(scores)
        exp_values = np.exp(scores / T)
        probabilities = exp_values / np.sum(exp_values)
        return probabilities

        
    
    def can_build(self, product):
        '''
        return True if player can build product, else False
        solely based on # of resoruces
        '''
        if product == 'road':
            necessary_resources = [('lumber', 1), ('brick', 1)]
        elif product == 'settlement':
            necessary_resources = [('lumber', 1), ('brick', 1), ('wheat', 1), ('sheep', 1)]
        elif product == 'city':
            necessary_resources = [('ore', 3), ('wheat', 2)]
        
        for resource, quantity in necessary_resources:
            if self.resources[resource] < quantity:
                return False
        return True
    
    def trade_for(self, game_state):
        '''
        Considers most desired_product and the resources needed to get there
        Returns the resource most needed to complete these products
        Tie breaker is determined by lack of abundance in accessible economy
        '''
        board_state = game_state.board
        intsect_scores = self.evaluate_intersection_value(board_state)
        game_state.game_data['intsect scores'].append(intsect_scores) # used for debugging data
        target_product, target_intsect = self.choose_priority(intsect_scores, game_state) # probabilistically choose strategy
        self.last_target = target_product, target_intsect # update pointer to ensure consistency in strategy for this turn



        if target_product == 'city':
            req = {
            'lumber': 0,
            'brick': 0,
            'sheep': 0,
            'wheat': 2,
            'ore': 3
        }
        
        if target_product == 'settlement':
            initial_path = self.shortest_path(board_state.graph, target_intsect, (9, 9))
            path = initial_path[:-1]
            roads_needed = len(path) - 1
            req = {'lumber': 1 + roads_needed,
                        'brick': 1 + roads_needed,
                        'sheep': 1,
                        'wheat': 1,
                        'ore': 0}


        missing_resources = self.calculate_deficits(req)
        desired_r = max(missing_resources.keys(), key=lambda r: (missing_resources[r], self.tiebreaker(r, board_state)))
        return desired_r

            
    
    def tiebreaker(self, resource, board_state):
        '''
        Used as a tie breaker for choosing a resource
        Occurs in circumstances when equal # of resources necessary for product
        The resource that is less abundant in economy is chosen
        Need to return the negative value so that the max function works out correctly
        '''
        num_dots = 0
        for s in self.settlements:
            for h in board_state.intersections[s]['adjacent_hexes']:
                if h.resource_type == resource:
                    num_dots += h.dots
        
        return -num_dots
            
    
    def calculate_deficits(self, requirements):
        '''
        Calculate quantitity of missing resources in order to achieve target

        Requirements (dict): key --> value // str(resource) --> # necessary for product
        '''
        missing_resources = {}
        for resource, required_amount in requirements.items():
            current_amount = self.resources.get(resource, 0)
            deficit = max(0, required_amount - current_amount)
            missing_resources[resource] = deficit
        return missing_resources
    
    def choose_priority(self, intsect_scores, game_state):
        '''
        Given intsect scores, we want to return -- probabilistically -- intersection we desire to build towards AND product we want to buy
        utilizes softmax to perform probabilistic decision
        '''
        # sort intersection scores
        sorted_scores = sorted(intsect_scores.values(), reverse=True) 
        sorted_keys = sorted(intsect_scores.keys(), key= lambda x: intsect_scores[x], reverse=True)


        first_four = sorted_scores[:4] # only considers top 4 options as realistic

        # randomly choose intersection from top 4
        probabilities = self.softmax_with_temperature(first_four, T=game_state.softmax_temp)
        index = (random.choices(range(len(probabilities)), weights=probabilities))[0]
        chosen_intsect = sorted_keys[index]
        
        if chosen_intsect in self.settlements:
            return ('city', chosen_intsect)
        
        return ('settlement', chosen_intsect)



    