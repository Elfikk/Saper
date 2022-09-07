from GameLogic import Game
from Grid import SquareGrid

#TextGame.py rewritten with 

width, height, mines, seed = 5, 5, 5, 2

grid = SquareGrid(width, height, mines, seed)

game_handler = Game(grid)

game_ended = False

print(game_handler.game_print())

x, y = int(input("Choose x pos to reveal: ")), int(input("Choose y pos to reveal: "))

outcome = game_handler.reveal_tile((x, y))

if outcome is not None:
    print(outcome)
    game_ended = True

while game_ended is False:

    print("")
    print(game_handler.game_print())

    choice = int(input("To mark a tile, input 0. To reveal a tile, input 1. "))

    if choice == 0:
        x, y = int(input("Choose x pos to mark: ")), int(input("Choose y pos to mark: "))
        game_handler.mark((x, y))
    elif choice == 1:
        x, y = int(input("Choose x pos to reveal: ")), int(input("Choose y pos to reveal: "))
        if game_handler.check_visible((x,y)):
            outcome = game_handler.reveal_adjacents((x, y))
        else:
            outcome = game_handler.reveal_tile((x, y))
        if outcome is not None:
            print(outcome)
            game_ended = True
    else:
        print("not a move fam")

    if game_handler.is_won():
        print("")
        print("Victory!")
        game_ended = True

print(game_handler.game_print())