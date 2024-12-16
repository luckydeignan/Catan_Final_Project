import random
from catan_game import game_logic

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

# for i in range(10):
#     h_and_t = generate_layout()
#     game = game_logic.Game()
    
#     game.initialize_game(hex_and_tokens=h_and_t, player_count=1)
#     print(h_and_t)
#     game.visualize_board(block=True)

middle_to_upward_fork = [('ore', 4), ('wheat', 6), ('lumber', 3), ('lumber', 8), ('lumber', 10), ('ore', 9), ('sheep', 8), ('ore', 5), ('wheat', 11), ('brick', 12)]
traverse_across = [('sheep', 3), ('wheat', 11), ('brick', 12), ('ore', 9), ('ore', 10), ('brick', 10), ('sheep', 2), ('brick', 9), ('wheat', 11), ('lumber', 8)]
b2sloc= (4,6)
obvious_city_ending = [('wheat', 6), ('ore', 9), ('ore', 3), ('ore', 12), ('brick', 9), ('lumber', 12), ('sheep', 4), ('lumber', 10), ('wheat', 11), ('brick', 2)]
well_rounded_board = [('lumber', 5), ('brick', 5), ('wheat', 8), ('ore', 3), ('brick', 12), ('sheep', 11), ('sheep', 2), ('brick', 6), ('sheep', 9), ('wheat', 6)]
symmetrical_board = [('wheat', 10), ('lumber', 6), ('ore', 4), ('brick', 8), ('sheep', 11), ('sheep', 10), ('brick', 5), ('ore', 4), ('lumber', 6), ('wheat', 3)]

boards = [middle_to_upward_fork, traverse_across, obvious_city_ending, well_rounded_board, symmetrical_board]

for b in boards:
    if b == traverse_across:
        game = game_logic.Game(starting_loc=(4,6))
    else:
        game = game_logic.Game()
    game.initialize_game(hex_and_tokens=b, player_count=1)
    game.visualize_board(block=True)
        