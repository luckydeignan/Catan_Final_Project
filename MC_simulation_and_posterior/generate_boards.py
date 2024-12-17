import random
from catan_game import game_logic

'''
This file randomly generates different boards, first step in generating intermediate game states
'''

def generate_layout():
    hexes = {
        'lumber':3,
        'brick':3,
        'sheep':3,
        'wheat':3,
        'ore':3
    }

    numbers = {i: 2 for i in range(2,13)}

    hex_and_t = []

    while len(hex_and_t) < 10:
        hex = random.choice(list(hexes.keys()))
        if hexes[hex] > 0:
            hexes[hex] -= 1
            while True:
                token = random.choice(list(numbers.keys()))
                if numbers[token]>0 and token!=7:
                    numbers[token] -= 1
                    break
            hex_and_t.append((hex, token))
    
    return hex_and_t

for i in range(10):
    h_and_t = generate_layout()
    game = game_logic.Game()
    
    game.initialize_game(hex_and_tokens=h_and_t, player_count=1)
    print(h_and_t)
    game.visualize_board(block=True)


        