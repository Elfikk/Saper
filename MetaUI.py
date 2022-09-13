from pyglet.graphics import Batch
from pyglet.sprite import Sprite
from pyglet.shapes import Rectangle
from GameConstants import SCREEN_WIDTH, SCREEN_HEIGHT
from TileUI import TileUI

class MetaUI():

#I hate writing UIs so much.

    sprites_names = {
        "0": "0.png",
        "1": "1.png",
        "2": "2.png",
        "3": "3.png",
        "4": "4.png",
        "5": "5.png",
        "6": "6.png",
        "7": "7.png",
        "8": "8.png",
        "9": "9.png",
        "R": "RestartButton.png"
    }

    def __init__(self, height, x_pad_left, x_pad_right, y_pad_bottom, grid_width):

        self.__status_to_path = {status: "Sprites/StandardUI/" + \
            MetaUI.sprites_names[status] for status in MetaUI.sprites_names}

        self.__mag = height / 32

        self.__batch = Batch()
        self.__bounding_box = Rectangle(x_pad_left - 0.5 * grid_width, \
            y_pad_bottom - height // 2 + 0.5 * grid_width, \
            SCREEN_WIDTH - x_pad_left - x_pad_right, height)

        self.__mine_digits = [TileUI(x_pad_left + i * 1/3 * height + 0.5 * grid_width,\
            y_pad_bottom + height // 8, self.__status_to_path["0"], self.__batch, \
            self.__mag, "0") for i in range(3)]
        self.__mine_digits_status = ["0", "0", "0"]

        self.__timer_digits = [TileUI(SCREEN_WIDTH - x_pad_right - i * 1/3 * height - 1.5 * grid_width,\
            y_pad_bottom + height // 8, self.__status_to_path["0"], self.__batch, \
            self.__mag, "0") for i in range(2, -1, -1)]
        self.__timer_digits_status = ["0", "0", "0"]

        ui_centre = (0.5 * (SCREEN_WIDTH + x_pad_left - x_pad_right), y_pad_bottom + height // 8)
        self.__restart_button = TileUI(ui_centre[0], ui_centre[1], self.__status_to_path["R"], \
            self.__batch, self.__mag, "R")
        self.__restart_bounds = {"x_min": ui_centre[0] - self.__mag * 16,\
                                 "x_max": ui_centre[0] + self.__mag * 16,\
                                 "y_min": ui_centre[1] - self.__mag * 16,\
                                 "y_max": ui_centre[1] + self.__mag * 16}

    def update(self, timer, mines):
        timer_string = str(timer)
        for i in range(len(timer_string)):
            current_status = timer_string[-i-1]
            if current_status != self.__timer_digits_status[-i-1]:
                self.__timer_digits[-i-1].update(self.__status_to_path[current_status], \
                    current_status)
                self.__timer_digits_status[-i-1] = current_status

        mine_string = str(mines)
        for i in range(len(mine_string)):
            current_status = mine_string[-i-1]
            if current_status != self.__mine_digits_status[-i-1]:
                self.__mine_digits[-i-1].update(self.__status_to_path[current_status], \
                    current_status)
                self.__mine_digits_status[-i-1] = current_status

    def draw(self):
        self.__bounding_box.draw()
        self.__batch.draw()

    def get_restart_bounds(self):
        return self.__restart_bounds

    def reset(self):
        self.__timer_digits_status = ["0", "0", "0"]
        for digit in self.__timer_digits:
            digit.update(self.__status_to_path["0"], "0")