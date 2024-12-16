from catan_game import game_logic
import numpy as np
#import pymc as pm
import pickle
import os

current_directory = os.getcwd()  # Get current working directory
file_name = 'simulation_data.pkl'
board_intsects_name = 'desired_intersection.pkl'
file_path = os.path.join(current_directory, file_name)
board_intsects_path = os.path.join(current_directory, board_intsects_name)


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








for i in range(10):
    print(i)
    simulate_game(hex_and_tokens, (4,4))