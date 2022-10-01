class SolvingAdapter():

    def __init__(self, game):

        visible_tiles = game.get_all_visible_tiles()

        self.__visible = set(visible_tiles.keys())
        self.__redundant = set()
        self.__game = game #Held to be able to reference the game in methods.

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
    