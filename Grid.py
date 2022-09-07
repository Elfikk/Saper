from Tile import Tile
from random import randint
import random

class SquareGrid():

    # Representation of standard Minesweeper grid.

    def __init__(self, width, height, n_mines, seed = None):

        self.__width = width
        self.__height = height
        self.__n_mines = n_mines

        self.__grid = {}

        for x in range(width):
            for y in range(height):
                self.__grid[(x,y)] = Tile()

        self.generate_game(n_mines, seed)

    def generate_game(self, n_mines, seed = None):

        # Method for setting up a standard Minesweeper game. Generates
        # positions of specified number of mines, with possible seed for
        # repeatable results (for testing/debugging).

        if seed is not None:
            random.seed(seed)

        possible_positions = [key for key in self.__grid]
        max_index = len(possible_positions) - 1

        for i in range(n_mines):

            random_index = randint(0, max_index - i)
            random_pos = possible_positions[random_index]
            random_x, random_y = random_pos

            self.__grid[random_pos].set_mined()
            
            neighbours = self.get_neighbours((random_x, random_y))

            for pos in neighbours:
                neighbours[pos].increment_adjacents()

            possible_positions = possible_positions[:random_index] + possible_positions[random_index+1:]

    def reset(self):
        for pos in self.__grid:
            tile = self.__grid[pos]
            tile.reset()

    def regenerate_game(self, n_mines, seed = None):
        self.reset()
        self.generate_game(n_mines, seed)

    def mark(self, pos):
        # Player marking of tile as a mine.
        self.__grid[pos].update_mark() 

    def reveal(self, pos):
        # Sets the visibility of target tile to True, returning the Tile
        # for further inspection by the game logic.

        revealed_tile = self.__grid[pos]
        revealed_tile.set_visible()
        return revealed_tile

    def game_print(self, debug = False):

        # Generates a string of the current grid. In debug mode (debug = True), all
        # the mines and adjacent values are visible. By default, generates a grid 
        # with visibility taken into account.

        if debug:
            print_method = Tile.debug_output
        else:
            print_method = Tile.return_status

        game_grid = [["" for i in range(self.__width)] for j in range(self.__height)]

        for pos in self.__grid:
            tile = self.__grid[pos]
            x, y = pos[0], pos[1]
            game_grid[y][x] = print_method(tile)

        game_string = ""
        for row in game_grid:
            for tile in row:
                game_string = game_string + tile + " "
            game_string = game_string + "\n"

        return game_string

    def __str__(self):
        #For use with print()
        return self.game_print()

    def generate_mineless_tiles(self):

        # Generates the set of all mineless tiles for the objective of the game
        # (uncovering all mineless tiles!)

        to_reveal = []

        for pos in self.__grid:
            tile = self.__grid[pos]
            if not tile.get_mined():
                to_reveal.append(pos)

        return set(to_reveal)

    def get_neighbours(self, pos):

        # Generates a dictionary of all the adjacent tiles of a tile given its 
        # x, y position, with the key being their positions.

        x, y = pos

        neighbours = {}

        for pos_x in range(max(0, x - 1), min(x + 2, self.__width)):
            for pos_y in range(max(0, y - 1), min(y + 2, self.__height)):
                neighbours[(pos_x, pos_y)] = self.__grid[(pos_x, pos_y)]
        
        neighbours.pop((x,y))

        return neighbours

    def get_mines(self):
        return self.__n_mines

    def get_tile(self, pos):
        return self.__grid[pos]

    def is_marked(self, pos):
        return self.__grid[pos].get_marked()

if __name__ == "__main__":


    grid = SquareGrid(5, 5, 5, 2)

    da_brint = grid.game_print(debug=True)

    print(da_brint)

    grid.reveal((4,3))

    da_brint = grid.game_print(debug=False)

    print(da_brint)

    # print(grid.get_neighbours(0, 1))