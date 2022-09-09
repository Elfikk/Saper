import pyglet
from GameConstants import SCREEN_WIDTH, SCREEN_HEIGHT, FRAME_RATE
from Grid import SquareGrid
from GridUI import SquareGridUI
from GameLogic import Game

class GameWindow(pyglet.window.Window):

    def __init__(self, grid_ui, game):
        super(GameWindow, self).__init__(width = SCREEN_WIDTH,\
            height = SCREEN_HEIGHT)
        self.__grid_ui = grid_ui
        self.__game_handler = game
        self.__timer = 0
        self.__clicks = 0

        self.__grid_bounds = {"x_min": grid_ui.get_x_pad() - 16, 
                              "x_max": SCREEN_WIDTH - grid_ui.get_x_pad() + 16,
                              "y_min": grid_ui.get_y_pad() - 16,
                              "y_max": SCREEN_HEIGHT - grid_ui.get_y_pad() + 16}

    def on_draw(self):
        self.clear()
        self.update("ya boi skinny penis")
        self.__grid_ui.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        x_min, x_max, y_min, y_max = self.__grid_bounds["x_min"], \
            self.__grid_bounds["x_max"], self.__grid_bounds["y_min"],\
            self.__grid_bounds["y_max"]

        if x_min <= x <= x_max and y_min <= y <= y_max: #If clicking the grid.
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
        
        print(x,y)
        print(int(self.__timer))

    def update(self, _):
        changed_tiles = self.__game_handler.get_changes()
        # print(changed_tiles)
        self.__grid_ui.update_tiles(changed_tiles)
        if self.__clicks:
            self.__timer += 1/FRAME_RATE

if __name__ == "__main__":

    grid = SquareGrid(30, 16, 99)

    game = Game(grid)

    grid_ui = SquareGridUI(30, 16, 160, 104, 1)

    window = GameWindow(grid_ui, game)

    pyglet.clock.schedule_interval(window.update, 1/FRAME_RATE)
    pyglet.app.run()

    