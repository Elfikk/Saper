import pyglet
from pyglet.window import key
from GameConstants import SCREEN_WIDTH, SCREEN_HEIGHT, FRAME_RATE
from Grid import SquareGrid
from GridUI import SquareGridUI
from GameLogic import Game
from MetaUI import MetaUI
from MinesweeperSolver import Solver
from AdapterSolver import SolvingAdapter
from time import time

class GameWindow(pyglet.window.Window):

    def __init__(self, grid_ui, game, meta_ui):
        super(GameWindow, self).__init__(width = SCREEN_WIDTH,\
            height = SCREEN_HEIGHT)
        self.__grid_ui = grid_ui
        self.__game_handler = game
        self.__meta_ui = meta_ui
        self.__start_stamp = time()
        self.__timer = 0
        self.__clicks = 0
        self.__game_ended = False
        self.__solver_on = False
        self.__adapter = False
        self.__solver = False
        self.__none_streak = 0

        self.__grid_bounds = self.__grid_ui.get_bounds()
        self.__restard_bounds = self.__meta_ui.get_restart_bounds()
        print(self.__grid_bounds)

    def on_draw(self):
        self.clear()
        self.update("")
        self.__grid_ui.draw()
        self.__meta_ui.draw()

    def on_mouse_press(self, x, y, button, modifiers):

        if not self.__solver_on:

            x_min, x_max, y_min, y_max = self.__grid_bounds["x_min"], \
                self.__grid_bounds["x_max"], self.__grid_bounds["y_min"],\
                self.__grid_bounds["y_max"]

            print(x,y)
            print(int(self.__timer))

            if x_min <= x < x_max and y_min < y <= y_max: #If clicking the grid.
                if not self.__game_ended:
                    # self.__clicks += 1
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

    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            if not self.__game_ended:
                self.__solver_on = True
                self.__adapter = SolvingAdapter(self.__game_handler)
                self.__solver = Solver(self.__adapter)
        if symbol == key.Q:
            self.__solver_on = False
        # if symbol == key.A:
        #     print(self.__grid.)

    def update(self, _):
        changed_tiles = self.__game_handler.get_changes()
        self.__grid_ui.update_tiles(changed_tiles)
        self.__game_ended = self.__game_handler.is_lost() or self.__game_handler.is_won()
        if self.__clicks:
            if not self.__game_ended:
                self.__timer = time() - self.__start_stamp
                if self.__timer > 999:
                    self.__timer = 999
                current_counter = self.__game_handler.get_mine_counter()
                counter = current_counter if current_counter > 0 else 0
                counter_string = (3 - len(str(counter))) * "0" + str(counter)
                self.__meta_ui.update(int(self.__timer), counter_string)
        else:
            self.__start_stamp = time()      

        if self.__solver_on:
            if not self.__game_ended:
                next_move = self.__adapter.next_move()
                print(next_move)
                if next_move != None:
                    self.__none_streak = 0
                    tile_id, move_type = next_move
                    if move_type == 0:
                        if not self.__game_handler.is_marked(tile_id):
                            self.__game_handler.mark(tile_id)
                    elif move_type == 1:
                        tile_status = self.__grid_ui.get_tile_status(tile_id)
                        if tile_status == "?":
                            self.__game_handler.reveal_tile(tile_id)
                    elif move_type == 2:
                        self.__game_handler.reveal_adjacents(tile_id)
                self.__none_streak += 1
                if self.__none_streak == 2:
                    # self.__none_streak = 0
                    self.__adapter.get_moves(self.__solver)
                # if 2 nones in a row, take a guess.
                # taking a guess takes generating all possible 
                # configurations for remaining floor, and finding where
                # mines/safe tiles occur most frequently.
                elif self.__none_streak == 3:
                    self.__adapter.get_guess(self.__solver)

            else:
                self.__solver_on = False


    def reset(self):

        print(self.__clicks, self.__timer)

        self.__timer = 0
        self.__clicks = 0
        self.__game_ended = False
        self.__game_handler.reset()
        self.__grid_ui.reset()
        self.__meta_ui.reset()

        self.__solver_on = False
        self.__adapter = False
        self.__solver = False
        self.__none_streak = 0

if __name__ == "__main__":

    # # Expert Board (31 x 16 with 99 mines)
    # # Solver works on expert board too (but needs guessing badly)

    # factor = SCREEN_WIDTH / 1280

    # x_pad = 144 * factor
    # y_pad = 104 * factor
    # mag = 1 * factor

    # grid = SquareGrid(31, 16, 99, mag)

    # game = Game(grid)

    # grid_ui = SquareGridUI(31, 16, x_pad, x_pad, 1.5 * y_pad, 0.5 * y_pad, mag)

    # meta_ui = MetaUI(y_pad, x_pad, x_pad, 0.5*y_pad, 32 * mag)

    # window = GameWindow(grid_ui, game, meta_ui)

    # Beginner Board (8 x 8 with 10 mines)

    factor = SCREEN_HEIGHT / 1080

    x_pad = 576 * factor
    y_pad = 156 * factor
    mag = 3 * factor

    #Who put the mag factor down as the damn seed. Dum ass.
    grid = SquareGrid(8, 8, 10, mag)

    game = Game(grid)

    grid_ui = SquareGridUI(8, 8, x_pad, x_pad, 1.5 * y_pad, 0.5 * y_pad, mag)
    
    meta_ui = MetaUI(y_pad, x_pad, x_pad, 0.5*y_pad, 32 * mag)

    window = GameWindow(grid_ui, game, meta_ui)

    pyglet.clock.schedule_interval(window.update, 1/FRAME_RATE)
    pyglet.app.run()

    