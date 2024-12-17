from catan_game import game_logic
import numpy as np
import pickle
import os

'''
this file was used to create different intermediate game states used in experiment
this was done by changing hex_and_tokens variable (indicating different boards)
different boards were obtained by generate_boards.py
'''

current_directory = os.getcwd()  # Get current working directory
file_name = 'simulation_data.pkl'
file_path = os.path.join(current_directory, file_name)


hex_and_tokens = [
    ('ore', 4), ('wheat', 6), ('lumber', 3), 
    ('lumber', 8), ('lumber', 10), ('ore', 9), ('sheep', 8), 
    ('ore', 5), ('wheat', 11), ('brick', 12)
        ]



def simulate_game(hex_and_tokens, loc):
    game = game_logic.Game(victory_points_to_win=4, starting_loc=loc)
    game.initialize_game(hex_and_tokens, player_count=1)
    game_over = False
    while not game_over:
        game_over = game.play_turn()
    print(game.structures)
    game.visualize_board()


# can play with different hex_and_token combinations to create different possible intermediate states
for i in range(10):
    print(i)
    simulate_game(hex_and_tokens, (4,4))