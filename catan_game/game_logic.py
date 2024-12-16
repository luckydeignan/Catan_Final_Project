import random
from core_classes import Board, Hex
from player_and_agent import Player, Agent
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
import matplotlib.lines as mlines
import numpy as np
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
import threading
import os
import pickle

class Game:
    def __init__(self, victory_points_to_win=5, starting_loc=(4,4), robber_prob = .25, trading_prob = .5, softmax_temp = 1):
        self.board = Board()
        self.players = []
        self.current_turn = 0
        self.round_number = 0
        self.victory_points_to_win = victory_points_to_win
        self.starting_loc = starting_loc
        self.last_action = []
        self.last_dice_roll = None
        self.robber_loc = None
        self.first_time = True # used as a marker to reset resources when player hits 4 VP // for experimental purposes
        self.robber_prob = robber_prob
        self.trading_prob = trading_prob
        self.softmax_temp = softmax_temp
        self.game_log = []
        self.structures = set()
        self.game_data = {
    "game data": [],
    "board layout": [],  # Corresponds to board state instance
    "player info": [], # corresponds to instance of player for each round
    "number of rounds": 0,  # int()
    "actions": [],  # list(self.last_action for each round)
    "targets": [], # list(tuples(target_product, target_intsect))
    "intsect scores": [],  # intsect_scores
    "hyperparameters": {
        "robber prob": robber_prob,  # float(robber_prob)
        "trading prob": trading_prob,  # float(trading_prob)
        "softmax temperature": softmax_temp,  # float(soft_max_temperature)
    },
}
        self.pickle_path = str()


        # Ensure file is created in the current working directory
        current_directory = os.getcwd()  # Get current working directory
        file_name = 'simulation_data.pkl'
        file_path = os.path.join(current_directory, file_name)
        self.pickle_path = file_path

        


    def initialize_game(self, hex_and_tokens, player_count):
        """Set up the board and players.
        
        Hex and tokens example (from left to right top to bottom):
        [
        ('sheep', 3), ('desert', 0), ('wheat', 6), 
        ('lumber', 9), ('lumber', 4), ('sheep', 5), 
        ('sheep', 12), ('sheep', 8), ('ore', 11), ('lumber', 9)
        ]
        """
        self.board.generate_board(hex_and_tokens)
        colors = ['orange', 'white', 'red', 'blue']
        for i in range(player_count):
            player = Agent(player_color=colors[i])
            self.players.append(player)
        
        for p in self.players:
            for r in ['lumber', 'brick', 'wheat', 'sheep']:
                p.resources[r] += 1
            p.available_intersections.add(self.starting_loc)
            p.build_settlement(self.board, self.starting_loc)
            

    def play_turn(self):
        """Handle the sequence of actions for a player's turn."""
        current_player = self.players[self.current_turn]
        self.last_action = []
        
        # Step 1: Roll dice
        dice_roll = self.roll_dice()
        self.last_dice_roll = dice_roll
        #print(f"{current_player.color} rolled a {dice_roll}.")
        
        # Step 2: Distribute resources
        self.distribute_resources(dice_roll)
        
        # Step 3: execute probabilistic trade mechanism and update last_action what resources were received
        for p in self.players:
            p.traded = False
            if not p.gained_resource:
                if self.last_dice_roll != 7:
                    if random.random() < self.trading_prob:
                        resource = p.trade_for(self)
                        p.resources[resource] += 1
                        p.traded = True
                        self.last_action.append(f"{p.color} received {resource} from bank")
                    else:
                        self.last_action.append(f"{p.color} received nothing")
                
            else:
                for r in p.gained_resource:
                    self.last_action.append(f"{p.color} received {r}")



        # Step 4: Let the player decide and execute an action
        if isinstance(current_player, Agent):
            actions, targets = current_player.choose_action(self)
        else:
            action, target = self.prompt_player_action(current_player)
        
        if actions:
            for i in range(len(actions)):
                self.last_action.append(f"{current_player.color} did a {actions[i]} at {targets[i]}")
                self.game_log.append((actions[i], targets[i]))
                self.structures.add((actions[i], targets[i]))
        else:
            self.last_action.append(f"{current_player.color} did nothing")
        
        self.game_data['actions'].append(self.last_action)
        self.game_data['board layout'].append(self.board)
        self.game_data['player info'].append(current_player)
        self.game_data['game data'].append(self)
        self.game_data['number of rounds'] += 1
        # dump Pickle data
        with open(self.pickle_path, 'wb') as file:
            pickle.dump(self.game_data, file)
        
        # Step 5: Check win condition
        if self.check_winner(current_player):
            #print(f"{current_player.color} wins with {current_player.score} points!")
            return True  # Game over
        
        # Step 6: reset resources if just got to 4 vps // part of the experiment
        if current_player.score == 4 and self.first_time:
            self.first_time = False
            for r in current_player.resources.keys():
                current_player.resources[r] = 0

        # Advance to the next turn
        self.current_turn = (self.current_turn + 1) % len(self.players)
        self.round_number += 1
        

       


        return False  # Game continues

    def roll_dice(self):
        """Roll two six-sided dice."""
        return random.randint(1, 6) + random.randint(1, 6)

    def distribute_resources(self, dice_roll):
        """Distribute resources based on the dice roll."""
        board_state = self.board
        for p in self.players:
            p.collect_resources(board_state, dice_roll)
            #handle robber events
            if dice_roll == 7:
                if random.random() < self.robber_prob:
                    # place robber on 1 random hex
                    eligible_hexes = set()
                    for intsect in p.settlements:
                        eligible_hexes.update(set(board_state.intersections[intsect]['adjacent_hexes']))
                    for intsect in p.cities:
                        eligible_hexes.update(set(board_state.intersections[intsect]['adjacent_hexes']))
                    while True:
                        if not eligible_hexes:
                            import pdb; pdb.set_trace()
                        random_hex = random.choice(list(eligible_hexes))
                        if random_hex.robber_blocking == False:
                            random_hex.robber_blocking = True
                            if isinstance(self.robber_loc, Hex):
                                self.robber_loc.robber_blocking = False
                            self.robber_loc = random_hex
                            break
                    # steal 1 random resource
                    resources = ['lumber', 'brick', 'sheep', 'wheat', 'ore']
                    while resources:
                        random_resource = random.choice(resources)
                        resources.remove(random_resource)
                        if p.resources[random_resource]:
                            p.resources[random_resource] -= 1
                            self.last_action.append(f'Robber stole {random_resource} from {p.color}')
                            break
                else:
                    if isinstance(self.robber_loc, Hex):
                        self.robber_loc.robber_blocking = False
                    self.robber_loc = None
                    self.last_action.append("Robber blocked")
                    break

        


    def prompt_player_action(self, player):
        """Prompt a human player for an action."""
        # Example: Ask for input (this could be replaced with a UI in a full implementation)
        print(f"{player.color}, what would you like to do?")
        return "wait", None  # Placeholder for user input

    def check_winner(self, player):
        """Check if a player has won the game."""
        return player.score >= self.victory_points_to_win
    

    def visualize_board(self, block=True):
        """Generate a matplotlib visualization of the game board with custom hexagon vertices and a legend."""
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_aspect('equal')

        # Define colors for resources
        resource_colors = {
            'sheep': 'lightgreen',
            'lumber': 'forestgreen',
            'ore': 'gray',
            'wheat': 'gold',
            'brick': 'brown',
            'desert': 'tan',
            None: 'white'
        }

        # Max rows to calculate inverted y-coordinates
        max_rows = 8

        # Draw each hex based on its vertices
        for hex_id, hex_data in self.board.hexes.items():
            hex_type = hex_data['hex_type']
            intersections = hex_data['intersections']
            color = resource_colors.get(hex_type.resource_type if hex_type else None, 'white')

            # Extract vertex positions from intersections
            vertices = [(col, max_rows - row) for row, col in intersections]  # Subtract y-coordinate from max_rows

            # Draw the hexagon
            hex_polygon = Polygon(vertices, closed=True, color=color, edgecolor='black')
            ax.add_patch(hex_polygon)

            # Add text for the number token
            if hex_type and hex_type.number_token:
                # Calculate center as the average of the vertices
                x_center = sum(v[0] for v in vertices) / len(vertices)
                y_center = sum(v[1] for v in vertices) / len(vertices)
                if not hex_type.robber_blocking:
                    ax.text(x_center, y_center, str(hex_type.number_token),
                        ha='center', va='center', fontsize=10, color='black')
                else:
                    ax.text(x_center, y_center, str('robber'),
                        ha='center', va='center', fontsize=10, color='black')

        # Draw intersections
        for (row, col), data in np.ndenumerate(self.board.intersections):
            if data != 0:
                x, y = col, max_rows - row  # Subtract row index from max_rows
                player_item = data['item']
                if player_item:
                    player_color, structure = player_item
                    shape = 'o' if structure == 'settlement' else 's'
                    ax.scatter(x, y, color=player_color, marker=shape, s=100, edgecolor='black')

        # Draw roads
        for edge, status in self.board.edges.items():
            if status != 'open':
                (row1, col1), (row2, col2) = edge
                x1, y1 = col1, max_rows - row1  # Subtract row index from max_rows
                x2, y2 = col2, max_rows - row2  # Subtract row index from max_rows
                line = plt.Line2D([x1, x2], [y1, y2], color=status, linewidth=3)
                ax.add_line(line)

        # Add legend with current player's resources, last action, and last die roll
        current_player = self.players[self.current_turn]
        resources_text = '\n'.join([f"{resource}: {amount}" for resource, amount in current_player.resources.items()])
        legend_text = f"Round number: {self.round_number}\nLast Action: {self.last_action}\nLast Roll: {self.last_dice_roll}\n\nResources:\n{resources_text}"

        ax.text(8, 7, legend_text, fontsize=12, ha='left', va='top', wrap=True, bbox=dict(facecolor='white', alpha=0.7))

        # Customize plot appearance
        ax.set_xlim(-1, 10)  # Adjust limits as needed
        ax.set_ylim(-1, max_rows + 1)  # Ensure space for flipped grid
        # Ensure the window opens at a specific position (e.g., 100 pixels from the top-left corner)
        manager = plt.get_current_fig_manager()
        manager.window.wm_geometry("+100+100")  # Change the "+100+100" to your desired position
        ax.axis('off')  # Turn off the axes
        plt.title("Catan Board State with Custom Hexagons", fontsize=16)
        plt.show(block=block)  # Non-blocking display
        #plt.pause(3.5)  # Display for 3.5 seconds
        #plt.close()  # Close after the delay








    

if __name__ == "__main__":
    hex_and_tokens = [
        ('sheep', 3), ('desert', 0), ('wheat', 6), 
        ('lumber', 9), ('lumber', 4), ('sheep', 5), 
        ('sheep', 12), ('sheep', 8), ('ore', 11), ('lumber', 9)
    ]
    
    game = Game(robber_prob=.5)
    game.initialize_game(hex_and_tokens, player_count=1)
    lucky = game.players[0]
    lucky.resources = {
        'lumber': 3,
        'brick': 3,
        'sheep': 1,
        'wheat': 1,
        'ore': 0
    }

    
    game_over = False
    while not game_over:
        
        
        ## testing code to test evaluation metric and different softmax performance
        # evaluations = game.players[0].evaluate_intersection_value(game.board)
        # print(sorted(evaluations.keys(), key = lambda x: evaluations[x], reverse= True))
        # scores = sorted(evaluations.values(), reverse= True)
        # first_four = scores[:4]
        # fourprobabilities = game.players[0].softmax_with_temperature(first_four, T=.25)
        # probabilities = game.players[0].softmax_with_temperature(scores, T=.5)
        # print(fourprobabilities)
        # print(probabilities)


        game.visualize_board()
        #import pdb; pdb.set_trace()
        game_over = game.play_turn()
        

