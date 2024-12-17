import pickle
import os



current_directory = os.getcwd()  # Get current working directory
file_name = 'simulation_data.pkl'
file_path = os.path.join(current_directory, file_name) # analyzing 

with open(file_path, 'rb') as file:
    sim_data = pickle.load(file)
    import pdb; pdb.set_trace() # debugging file; sim_data contains all information of last-run simulation

