from Grid import SquareGrid

width, height, mines, seed = 5, 5, 5, 2

grid = SquareGrid(width, height, mines, seed)

to_reveal = grid.generate_mineless_tiles()
visited = set()

n_moves = 1

game_ended = False

print(grid)

x, y = int(input("Choose x pos to reveal: ")), int(input("Choose y pos to reveal: "))

revealed_tile = grid.reveal(x, y)

if revealed_tile.get_mined():
    game_ended = True
    print("Hit a mine")
else:
    to_reveal.remove((x,y))
    visited.add((x,y))

while game_ended is False:

    n_moves += 1

    print(grid)
    print("")
    choice = int(input("To mark a tile, input 0. To reveal a tile, input 1. "))

    if choice == 0:
        x, y = int(input("Choose x pos to mark: ")), int(input("Choose y pos to mark: "))
        grid.mark(x, y)
    elif choice == 1:
        x, y = int(input("Choose x pos to reveal: ")), int(input("Choose y pos to reveal: "))
        revealed_tile = grid.reveal(x, y)
        if (x, y) in visited:
            n_adj_mines = revealed_tile.get_adjacents()
            adj_tiles = grid.get_neighbours(x, y)
            number_of_marks = len([adj_tiles[pos] for pos in adj_tiles if adj_tiles[pos].get_marked()])
            if number_of_marks == n_adj_mines:
                reveal_list = [pos for pos in adj_tiles if not adj_tiles[pos].get_marked()]
                for pos in reveal_list:
                    # print(pos, reveal_list)
                    new_revealed_tile = grid.reveal(pos[0], pos[1])
                    visited.add((pos[0],pos[1]))
                    if (pos[0],pos[1]) in to_reveal:
                        to_reveal.remove((pos[0],pos[1]))
                    if new_revealed_tile.get_adjacents() == 0:
                        new_neighbours = grid.get_neighbours(pos[0], pos[1])
                        not_visible_neighbours = {pos: new_neighbours[pos] for pos in new_neighbours if pos not in visited}
                        reveal_list.extend(not_visible_neighbours.keys())
        else:
            if revealed_tile.get_mined():
                print("Hit a mine")
                game_ended = True
            else:
                to_reveal.remove((x, y))
                visited.add((x,y))
    else:
        print("burh thats not an option")

    if len(to_reveal) == 0:
        game_ended = True
        print("Game completed successfully! Congrats. Took ya,", n_moves, "moves. Way to go 8)")

print(grid)