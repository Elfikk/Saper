#Adapter class to allow a tensorflow environment and GameLogic to interact.

from numpy import array, int32

class Adapter():

    def __init__(self, width, height):

        #Its important for its name to exist, otherwise it might rebel 
        #(introducing an AIs right to a name - its only humane)
        self.name = "Bob" 
        self.__width = width
        self.__height = height
        self.__step_reward = 0.0

    def map_to_observation(self, game):

        game_state = []

        game_string = game.game_print()
        split_string = game_string.split("\n")[1:-1]

        for row in split_string:
            for i in range(0, len(row), 2):
                tile = row[i]
                if tile == "?":
                    game_state += 0, 0, 0
                elif tile == "m" or tile == "M":
                    game_state += 0, 0, 1
                else:
                    game_state += int32(tile), 1, 0
        
        returnee = array(game_state, dtype = int32)
        # print(returnee.shape)

        return returnee

    def map_to_observation_legacy(self, game):

        game_state = []

        game_string = game.game_print()
        split_string = game_string.split("\n")[1:-1]

        for row in split_string:
            for i in range(0, len(row), 2):
                tile = row[i]
                if tile == "?":
                    game_state.append(-1)
                elif tile == "m" or tile == "M":
                    game_state.append(-2)
                else:
                    game_state.append(int32(tile))
        
        returnee = array(game_state, dtype = int32)
        # print(returnee.shape)

        return returnee

    def reveal_starting_tile(self, game, index):

        to_reveal = list(game.get_to_reveal())
        pos = to_reveal[index]

        game.reveal_tile(pos)

    def reveal_with_action(self, game, action):

        #This way of generating the id is specific to the rectangular grid.
        #This is fine, for now.
        id = (action % self.__width, action // self.__width)
        
        if not game.check_visible(id):
            neighbours = game.get_neighbours(id)
            wild_guess = True
            for neighbour_id in neighbours:
                if game.check_visible(neighbour_id):
                    wild_guess = False
            game.reveal_tile(id)
            if wild_guess:
                self.__step_reward = -0.3
            else:
                self.__step_reward = 0.9
        else:
            self.__step_reward = -0.9

    def game_is_won(self, game):
        return game.is_won()

    def game_is_lost(self, game):
        return game.is_lost()

    def get_reward(self):
        return self.__step_reward