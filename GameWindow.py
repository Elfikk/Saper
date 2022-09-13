import pyglet
from GameConstants import SCREEN_WIDTH, SCREEN_HEIGHT, FRAME_RATE
from Grid import SquareGrid
from GridUI import SquareGridUI
from GameLogic import Game
from MetaUI import MetaUI

class GameWindow(pyglet.window.Window):

    def __init__(self, grid_ui, game, meta_ui):
        super(GameWindow, self).__init__(width = SCREEN_WIDTH,\
            height = SCREEN_HEIGHT)
        self.__grid_ui = grid_ui
        self.__game_handler = game
        self.__meta_ui = meta_ui
        self.__timer = 0
        self.__clicks = 0
        self.__game_ended = False

        self.__grid_bounds = self.__grid_ui.get_bounds()
        self.__restard_bounds = self.__meta_ui.get_restart_bounds()
        print(self.__restard_bounds)

    def on_draw(self):
        self.clear()
        self.update("")
        self.__grid_ui.draw()
        self.__meta_ui.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        x_min, x_max, y_min, y_max = self.__grid_bounds["x_min"], \
            self.__grid_bounds["x_max"], self.__grid_bounds["y_min"],\
            self.__grid_bounds["y_max"]

        print(x,y)
        print(int(self.__timer))

        if x_min <= x <= x_max and y_min <= y <= y_max: #If clicking the grid.
            if not self.__game_ended:
                self.__clicks += 1
                id = self.__grid_ui.coords_to_id(x,y)
                tile_status = self.__grid_ui.get_tile_status(id)
                print(id)
                if button == pyglet.window.mouse.LEFT:
                    self.__clicks += 1
                    if tile_status == "?":
                        self.__game_handler.reveal_tile(id)
                    else:
                        self.__game_handler.reveal_adjacents(id)
                elif button == pyglet.window.mouse.RIGHT:
                    self.__clicks += 1
                    if tile_status == "?" or tile_status == "X":
                        self.__game_handler.mark(id)
        
        x_min, x_max, y_min, y_max = self.__restard_bounds["x_min"], \
            self.__restard_bounds["x_max"], self.__restard_bounds["y_min"],\
            self.__restard_bounds["y_max"]

        if x_min <= x <= x_max and y_min <= y <= y_max: #If clicking the restart button.
            if button == pyglet.window.mouse.LEFT:
                self.reset()

    def update(self, _):
        changed_tiles = self.__game_handler.get_changes()
        self.__grid_ui.update_tiles(changed_tiles)
        self.__game_ended = self.__game_handler.is_lost() or self.__game_handler.is_won()
        if self.__clicks:
            if not self.__game_ended:
                self.__timer += 1/FRAME_RATE
                self.__meta_ui.update(int(self.__timer), self.__game_handler.get_mine_counter())
                # print(int(self.__timer))

    def reset(self):

        self.__timer = 0
        self.__clicks = 0
        self.__game_ended = False
        self.__game_handler.reset()
        self.__grid_ui.reset()
        self.__meta_ui.reset()

if __name__ == "__main__":

    factor = SCREEN_WIDTH / 1280

    x_pad = 144 * factor
    y_pad = 136 * factor
    mag = 1 * factor

    grid = SquareGrid(31, 16, 99, mag)

    game = Game(grid)

    grid_ui = SquareGridUI(31, 16, x_pad, x_pad, 1.5 * y_pad, 0.5 * y_pad, mag)

    meta_ui = MetaUI(y_pad, x_pad, x_pad, 0.5*y_pad, 32 * mag)

    window = GameWindow(grid_ui, game, meta_ui)

    pyglet.clock.schedule_interval(window.update, 1/FRAME_RATE)
    pyglet.app.run()

    