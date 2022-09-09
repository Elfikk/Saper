from pyglet.graphics import Batch
from TileUI import TileUI
from GameConstants import SCREEN_WIDTH, SCREEN_HEIGHT

class SquareGridUI():

    tile_file_names = {
        "?": "SquareHiddenTile.png",
        "X": "SquareMarkedTile.png",
        "M": "SquareMinedTile.png",
        "m": "SquareMinedTriggered.png",
        "0": "SquareEmptyTile.png",
        "1": "SquareAdjacent1.png",
        "2": "SquareAdjacent2.png",
        "3": "SquareAdjacent3.png",
        "4": "SquareAdjacent4.png",
        "5": "SquareAdjacent5.png",
        "6": "SquareAdjacent6.png",
        "7": "SquareAdjacent7.png",
        "8": "SquareAdjacent8.png"
    }

    square_pixels = 32

    def __init__(self, width, height, x_padding, y_padding, mag = 1):

        self.__batch = Batch()
        self.__tiles = {}
        self.__status_to_path = {status: "Sprites/SquareGridTiles/" + \
            SquareGridUI.tile_file_names[status] for status in \
                                            SquareGridUI.tile_file_names}

        self.__square_length = mag * SquareGridUI.square_pixels

        for x in range(width):
            for y in range(height):
                self.__tiles[(x,y)] = TileUI(x * self.__square_length + x_padding, \
                                            SCREEN_HEIGHT - self.__square_length * y - y_padding,\
                                            self.__status_to_path["?"], self.__batch, mag)

        self.__grid_height = height * self.__square_length 
        # print(self.__grid_height)
        self.__x_pad = x_padding
        self.__y_pad = y_padding

    def draw(self):
        self.__batch.draw()

    def coords_to_id(self, x, y):
        x_s, y_s = (x - self.__x_pad, y - self.__grid_height - self.__y_pad)
        return ((x_s + self.__square_length//2) // self.__square_length, \
                (-y_s+self.__square_length//2) // self.__square_length)

    def get_x_pad(self):
        return self.__x_pad

    def get_y_pad(self):
        return self.__y_pad

    def get_tile_status(self, id):
        return self.__tiles[id].get_status()

    def update_tiles(self, changed_tiles):
        for id in changed_tiles:
            tile = self.__tiles[id]
            new_status = changed_tiles[id]
            tile.update(self.__status_to_path[new_status], new_status)