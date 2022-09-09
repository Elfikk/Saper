from pyglet.sprite import Sprite
from pyglet.gl import *
from pyglet.image import load

class TileUI(Sprite):

    def __init__(self, x, y, default_texture, batch, mag = 1, status = "?"):

        image_base = load(default_texture)
        image_texture = image_base.get_texture()
        self.__mag = 1
        self.__status = status

        if self.__mag != 1:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST) 
            image_texture.width = image_texture.width * mag
            image_texture.height = image_texture.height * mag
        
        Sprite.__init__(self, image_texture, x - image_texture.width//2, \
                        y - image_texture.height//2, batch = batch)

    def update(self, texture, status):
        image_base = load(texture)
        image_texture = image_base.get_texture()

        if self.__mag != 1:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST) 
            texture.width = image_texture.width * self.__mag
            image_texture.height = image_texture.height * self.__mag
        
        self.image = image_texture
        self.__status = status

    def get_status(self):
        return self.__status

if __name__ == "__main__":

    tile = TileUI(0, 0, "Sprites/SquareGridTiles/SquareEmptyTile.png")
    tile2 = TileUI(0, 0, "Sprites/SquareGridTiles/SquareEmptyTile.png", 2)

    tile.update("Sprites/SquareGridTiles/SquareMined.png")
    tile2.update("Sprites/SquareGridTiles/SquareMined.png")

    print("SHEESH")