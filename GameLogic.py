class Game():

# Class for handling the game logic (no matter the type of grid).
# Attributes:
# __grid: Grid instance (like SquareGrid) used by Game().
# __to_reveal: Set of tile ids that must be uncovered by the player to win.
# __n_moves: Number of moves taken by the player. Unused currently.
# __mines_counter: Number of mines - Number of tiles marked by the player.
# __changed_tiles: Dictionary of keys with Tile ids, whose values are the 
#                  new status of the corresponding Tile.

    def __init__(self, grid):
        self.__grid = grid
        self.setup()

    def setup(self):
        #Base setup.
        self.__to_reveal = self.__grid.generate_mineless_tiles()
        self.__visited = set()
        self.__n_moves = 0
        self.__mines_counter = self.__grid.get_mines()
        self.__changed_tiles = {}
        self.__tripped_mines = {}

    def reset(self):
        self.__grid.regenerate_game()
        self.setup()

    def increment_moves(self):
        self.__n_moves += 1

    def mark(self, id): 
        # Marks a tile as a mine, and updates the marked tiles counter
        # for the player accordingly.
        self.__grid.mark(id)
        tile = self.__grid.get_tile(id)
        if tile.get_marked():
            self.__mines_counter -= 1
            self.__changed_tiles[id] = "X"
        else:
            self.__mines_counter += 1
            self.__changed_tiles[id] = "?"

    def reveal_tile(self, id):
        # For clicking on a tile that has not been made visible yet. If a tile
        # with 0 mine neighbours is hit, all its adjacent tiles are revealed 
        # (and beyond, recursively).

        # If the tile is marked as a mine, the player shouldn't be able to 
        # reveal it (without unmarking it)
        if self.__grid.is_marked(id):
            return None

        revealed_tile = self.__grid.reveal(id)
        # If the revealed tile has a mine on it, the game ends.
        if revealed_tile.get_mined():
            self.__changed_tiles[id] = "m"
            self.__tripped_mines[id] = "m"
            return "Game Over. Hit a mine."
        
        self.__changed_tiles[id] = str(revealed_tile.get_adjacents())

        self.__to_reveal.remove(id)
        self.__visited.add(id)

        if not revealed_tile.get_adjacents(): #Tile has no mined neighbours.
            neighbours = self.__grid.get_neighbours(id)
            # unrevealed_neighbours = [id for id in neighbours if id not in self.__visited]
            for neighbour_id in neighbours:
                if neighbour_id not in self.__visited:
                    self.reveal_tile(neighbour_id)

    def reveal_adjacents(self, id):
        # For clicking on a tile that has enough marked neighbours to 
        # reveal all unmarked neighbour tiles.

        clicked_tile = self.__grid.get_tile(id)
        adjacent_tiles = self.__grid.get_neighbours(id)

        n_adj_mines = clicked_tile.get_adjacents()
        marked_tiles = [id for id in adjacent_tiles if adjacent_tiles[id].get_marked()]
        
        #If the number of mines surrounding the tile is the same as the number of marks, 
        #reveal all the unmarked tiles around it.
        if n_adj_mines == len(marked_tiles):
            for id in adjacent_tiles:
                if id not in marked_tiles and id not in self.__visited:
                    self.reveal_tile(id)

    def game_print(self, debug = False):
        #Status of game for text version.
        return "Mines left: " + str(self.__mines_counter) + "\n" + \
            self.__grid.game_print(debug)

    def check_visible(self, id):
        # I dont like this, feels wrong.
        tile = self.__grid.get_tile(id)
        return bool(tile.get_visible())

    def is_won(self):
        # The win condition is all mineless tiles being revealed, corresponding
        # to the list of all tiles left to reveal being empty.
        if len(self.__to_reveal) == 0:
            mines = self.__grid.generate_mined_tiles()
            for pos in mines:
                self.__changed_tiles[pos] = "X"
            return True
        return False

    def is_lost(self):
        return bool(len(self.__tripped_mines))

    def get_mine_counter(self):
        return self.__mines_counter

    def get_changes(self):
        changes_copy = self.__changed_tiles.copy()
        self.__changed_tiles = {}
        return changes_copy

    def get_to_reveal(self):
        return self.__to_reveal

    def get_neighbours(self, id):
        return self.__grid.get_neighbours(id)

    def get_all_visible_tiles(self):
        return self.__grid.get_all_visible_tiles()

    def is_satisfied(self, id):
        # A tile is satisfied if its neighbours are all marked/revealed 
        # whilst respecting the adjacency requirement.
        return self.__grid.is_satisfied(id)

    def partially_satisfied(self, id):
        return self.__grid.partially_satisfied(id)

    def get_adjacents(self, id):
        return self.__grid.get_adjacents(id)

    def is_marked(self, id):
        return self.__grid.is_marked(id)

    def get_tile(self, id):
        return self.__grid.get_tile(id)

if __name__ == "__main__":
    print(help(Game))