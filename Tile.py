class Tile(object):

    #Object representation of a single MineSweeper tile.
    #Attributes:
    # mined - whether the tile has a mine on it.
    # marked - whether the player has marked the tile as a mine.
    # visible - whether the player can see the number of mined adjacent tiles 
    # adjacents - number of neighbour tiles that have a mine on them.

    def __init__(self, mine = False, marked = False, visible = False):

        self.__mined = mine
        self.__marked = marked
        self.__visible = visible
        self.__adjacents = 0

    def set_mined(self):
        self.__mined = True

    def update_mark(self):
        if not self.__visible:
            self.__marked = not self.__marked

    def set_visible(self):
        self.__visible = True

    def set_adjacents(self, number):
        self.__adjacents = number

    def increment_adjacents(self):
        self.__adjacents += 1

    def deincrement_adjacents(self):
        self.__adjacents -= 1

    def get_mined(self):
        return self.__mined

    def get_marked(self):
        return self.__marked

    def get_visible(self):
        return self.__visible

    def get_adjacents(self):
        return self.__adjacents

    def reset(self):

        self.__mined = False
        self.__marked = False
        self.__visible = False
        self.__adjacents = 0

    def return_status(self):
        if self.__visible:
            if self.__mined:
                return "M"
            return str(self.__adjacents)
        else:
            if self.__marked:
                return "X"
            return "?"

    def debug_output(self):
        if self.__mined:
            return "M"
        return str(self.__adjacents)