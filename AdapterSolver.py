class SolvingAdapter():

    def __init__(self, game):

        visible_tiles = game.get_all_visible_tiles()

        self.__visible = set(visible_tiles)
        self.__redundant = set()
        self.__game = game #Held to be able to reference the game in methods.

        self.__to_reveal = set()
        self.__to_mark = set()
        self.__moves = {}
        self.__previous_moves = {}

    def check_redundant(self, id):
        if self.__game.is_satisfied(id):
            self.__redundant.add(id)    
            return True
        return False

    def is_redundant(self, id):
        return id in self.__redundant

    def get_visible(self):
        return self.__visible

    def get_useful_neighbours(self, info_set):
        neighbour_ids = set()
        adjacency_dict = {}
        for id in info_set:
            adjacency_dict[id] = []
            neighbours = self.__game.get_neighbours(id)
            for neighbour_id in neighbours:
                if not neighbours[neighbour_id].get_visible():
                    neighbour_ids.add(neighbour_id)
                    adjacency_dict[id].append(neighbour_id)

        return list(neighbour_ids), adjacency_dict

    def get_adjacents(self, id):
        return self.__game.get_adjacents(id)
    
    def get_moves(self, solver):

        visible_tiles = self.__game.get_all_visible_tiles()
        self.__visible = set(visible_tiles)

        print(self.__visible)
        print(len(self.__visible))

        self.__to_reveal, self.__to_mark = solver.solve()
        self.__moves = {**{id: 1 for id in self.__to_reveal},
                        **{id: 0 for id in self.__to_mark}
                        }

        if self.__previous_moves == self.__moves:
            self.__moves = {}
        else:
            self.__previous_moves = {}

    def next_move(self):
        try:
            new_move = self.__moves.popitem()
            self.__previous_moves[new_move[0]] = new_move[1]
            return new_move
        except KeyError:
            return None

    def get_guess(self, solver):
        tile_id, move_type = solver.guess()
        self.__moves = {tile_id: move_type}

    def get_heuristic_guess(self, solver):
        tile_id = solver.heuristic_guess()
        self.__moves = {tile_id: 1}

    def get_tile_identity(self, id):
        tile = self.__game.get_tile(id)
        if tile.get_marked():
            return 1
        if tile.get_visible():
            return 0
        return None

    def partially_satisfied(self, id):
        # Partial satisfaction - if enough flags are marked but some 
        # neighbours are not revealed.
        return self.__game.partially_satisfied(id)

    def is_marked(self, id):
        return self.__game.is_marked(id)

    def get_hidden_tiles(self):
        return self.__game.get_hidden_tiles()

    def remaining_mines(self):
        return self.__game.get_mine_counter()

    