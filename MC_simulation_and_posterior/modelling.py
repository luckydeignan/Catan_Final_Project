from catan_game import game_logic 
import numpy as np
import pickle
import os
from datetime import datetime

'''
This file includes: 

First, info needed to execute each of the 5 experiments is saved as variables (exp1, ... , exp5)

Second, function for simulating game in a way that conditions it to pass through an intermediate game state

Third, a model that runs Monte Carlo simulation until there are an arbitrary # of conditioned samples 

'''
### BELOW I WILL STORE THE HEX_AND_TOKEN AND FROZEN_GAME.STRUCTURES FOR EACH EXPERIMENT

## EXPERIMENT 1: INITIAL TOY EXAMPLE

hex_and_tokens1 = [
        ('sheep', 3), ('desert', 0), ('wheat', 6), 
        ('lumber', 9), ('lumber', 4), ('sheep', 5), ('sheep', 12), 
        ('sheep', 8), ('ore', 11), ('lumber', 9)
    ]

hex_loc = (4,4)

d_structures1 = {('road', ((2, 5), (3, 4))), ('settlement', (2, 5)), ('settlement', (4, 2)), 
                 ('road', ((3, 4), (4, 4))), ('road', ((4, 2), (5, 3))), ('city', (4, 4)), ('road', ((4, 4), (5, 3)))}

exp1 = (1, hex_and_tokens1, hex_loc, d_structures1)

## EXPERIMENT 2: 

upper_left_split = [
    ('brick', 4), ('wheat', 11), ('wheat', 3), 
    ('lumber', 3), ('lumber', 10), ('ore', 4), ('sheep', 8), 
    ('ore', 11), ('lumber', 8), ('brick', 9)
        ]
up_loc = (2,3)

d_structures2 = {('road', ((4, 6), (5, 5))), ('settlement', (4, 6)), ('road', ((2, 3), (3, 4))), ('settlement', (4, 4)),
                  ('road', ((3, 4), (4, 4))), ('road', ((4, 4), (5, 5))), ('city', (4, 4))}

exp2 = (2, upper_left_split, up_loc, d_structures2)

## EXPERIMENT 3:

fat_city_upp_left = [
    ('wheat', 6), ('ore', 9), ('ore', 3), 
    ('ore', 12), ('brick', 9), ('lumber', 12), ('sheep', 4), 
    ('lumber', 10), ('wheat', 11), ('brick', 2)
    ]

fat_loc = (4,4)

d_structures3 = {('settlement', (2, 5)), ('settlement', (2, 3)), ('road', ((2, 5), (3, 4))), 
                 ('road', ((2, 3), (3, 4))), ('road', ((3, 4), (4, 4))), ('city', (2, 3))}

exp3 = (3, fat_city_upp_left, fat_loc, d_structures3)

## EXPERIMENT 4:

well_rounded = [
    ('lumber', 2), ('brick', 5), ('wheat', 8), 
    ('ore', 9), ('brick', 12), ('sheep', 11), ('sheep', 3), 
    ('brick', 6), ('sheep', 9), ('wheat', 6)
    ]

well_loc = (4,4)

d_structures4 = {('settlement', (2, 5)), ('road', ((3, 4), (4, 4))), ('road', ((4, 2), (5, 3))), 
                 ('road', ((4, 4), (5, 3))), ('city', (2, 5)), ('road', ((2, 5), (3, 4))), ('settlement', (4, 2))}

exp4 = (4, well_rounded, well_loc, d_structures4)

## EXPERIMENT 5:


symmetric_scenario = [
    ('wheat', 10), ('lumber', 6), ('ore', 4), 
    ('brick', 8), ('sheep', 11), ('sheep', 10), ('brick', 5), 
    ('ore', 4), ('lumber', 6), ('wheat', 3)
                  ]

sym_loc = (2,3)

d_structures5 = {('settlement', (4, 4)), ('settlement', (2, 5)), ('road', ((2, 5), (3, 4))), ('city', (2, 3)), 
                 ('road', ((2, 3), (3, 4))), ('road', ((3, 4), (4, 4)))}

exp5 = (5, symmetric_scenario, sym_loc, d_structures5)


def simulate_game(hex_and_tokens, desired_structures, loc):
    '''
    Simulates game
    Returns none if simulation didn't pass through desired state
    Else, return the game itself
    '''
    game = game_logic.Game(starting_loc=loc)
    game.initialize_game(hex_and_tokens, player_count=1)
    game_over = False
    hit_4 = False 
    while not game_over:
        game_over = game.play_turn()
        current_score = game.players[game.current_turn].score
        if not hit_4 and not game.structures <= desired_structures: # ensuring simulation is only returned if the beginning portion led to intermediate state
            return None
        if current_score == 4 and not hit_4:
            hit_4 = True
    # print(game.game_log)
    return game

def model(exp, num_simulations):
    '''
    Dumps raw data from simulations as to where final VP was achieved
    Given a experiment and num_simulations (int)
    Inputs:
    - exp (tuple) containing three items:
        - number (int) indicating which experiment it is [1-5]
        - hex_and_tokens (list of tuples) which indicates board layout
        - desired_structures (set) indicating how first four VPs are achieved
        - starting_loc (tuple) indicating where player starts
    - num_simulations: number of samples needed before stopping
    Outputs:
        - none
        - dumps vp data into pickle file. data takes the form of dict:
            - hypothesis (final vp product & location) --> frequency
            - total # of samples in posterior is sum of frequencies
    '''
    
    final_vps = {}
    num_samples = 0
    trials = 0
    num, h_and_t, starting_loc, desired_structures = exp 
    print(f"Experiment {num}")
    print(datetime.now().time())
    while num_samples < num_simulations:
        trials += 1
        if trials % 500 == 0:
            print(num_samples) # track progress


        end_game = simulate_game(h_and_t, desired_structures, starting_loc)
        if end_game is not None:
            #below is for final vp given first 4
            vp = end_game.game_log[-1]
            if vp not in final_vps:
                final_vps[vp] = 0
            final_vps[vp] += 1
            num_samples += 1
    print(datetime.now().time())


    final_vps_path = r'C:\Users\ljdde\Downloads\9.66\Catan_Final_Project\data\newsm_raw_experiment_data\experiment_0{num}_raw_vp_data.pkl'
    with open(final_vps_path, 'wb') as file:
        pickle.dump(final_vps, file)


# if __name__ == '__main__':
#     '''
#     running this code runs Monte Carlo sample for each experiment (100 samples each experiment)
#     '''
#     experiments = [exp1, exp2, exp3, exp4, exp5]

#     for e in experiments:
#         model(e, 100)