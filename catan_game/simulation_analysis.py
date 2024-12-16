import pickle
import os
from player_and_agent import Player, Agent
from game_logic import Game


current_directory = os.getcwd()  # Get current working directory
file_name = 'simulation_data.pkl'
board_intsects_name = 'desired_intersection.pkl'
file_path = os.path.join(current_directory, file_name)
board_intsects_path = os.path.join(current_directory, board_intsects_name)

with open(file_path, 'rb') as file:
    sim_data = pickle.load(file)
    desired_intersections = sim_data['game data'][-1].structures
    with open(board_intsects_path, 'wb') as f:
        pickle.dump(desired_intersections, f)
    import pdb; pdb.set_trace()
    print(sim_data)

with open(board_intsects_path, 'rb') as f:
    board_ints = pickle.load(f)
    import pdb; pdb.set_trace()