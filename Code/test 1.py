import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys

# Simple block world settings
BLOCK_SIZE = 1
WORLD_SIZE = 10

# Block types
BLOCK_TYPES = ['grass', 'stone', 'wood']
BLOCK_COLORS = {
    'grass': (0.3, 0.8, 0.3),
    'stone': (0.5, 0.5, 0.5),
    'wood': (0.6, 0.4, 0.2)
}

class World:
    def __init__(self):
        self.blocks = {}
        for x in range(WORLD_SIZE):
            for z in range(WORLD_SIZE):
                self.blocks[(x, 0, z)] = 'grass'

    def add_block(self, pos, block_type):
        self.blocks[pos] = block_type

    def remove_block(self, pos):
        if pos in self.blocks:
            del self.blocks[pos]

    def draw(self):
        for pos, block_type in self.blocks.items():
            self.draw_block(pos, BLOCK_COLORS[block_type])

    def draw_block(self, pos, color):
        x, y, z = pos
        glColor3fv(color)
        glPushMatrix()
        glTranslatef(x, y, z)
        self.cube()
        glPopMatrix()

    def cube(self):
        glBegin(GL_QUADS)
        for surface in [
            [(0,0,0),(1,0,0),(1,1,0),(0,1,0)], # front
            [(0,0,1),(1,0,1),(1,1,1),(0,1,1)], # back
            [(0,0,0),(0,0,1),(0,1,1),(0,1,0)], # left
            [(1,0,0),(1,0,1),(1,1,1),(1,1,0)], # right
            [(0,1,0),(1,1,0),(1,1,1),(0,1,1)], # top
            [(0,0,0),(1,0,0),(1,0,1),(0,0,1)], # bottom
        ]:
            for vertex in surface:
                glVertex3fv(vertex)
        glEnd()

class Player:
    def __init__(self):
        self.x, self.y, self.z = WORLD_SIZE//2, 1, WORLD_SIZE//2
        self.inventory = {block: 10 for block in BLOCK_TYPES}
        self.selected = 0

    def move(self, dx, dz):
        self.x = max(0, min(WORLD_SIZE-1, self.x + dx))
        self.z = max(0, min(WORLD_SIZE-1, self.z + dz))

    def get_selected_block(self):
        return BLOCK_TYPES[self.selected]

def main():
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(-WORLD_SIZE//2, -2, -WORLD_SIZE*1.5)

    world = World()
    player = Player()

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_w: player.move(0, -1)
                if event.key == K_s: player.move(0, 1)
                if event.key == K_a: player.move(-1, 0)
                if event.key == K_d: player.move(1, 0)
                if event.key == K_1: player.selected = 0
                if event.key == K_2: player.selected = 1
                if event.key == K_3: player.selected = 2
                if event.key == K_SPACE:
                    pos = (player.x, player.y, player.z)
                    block_type = player.get_selected_block()
                    if player.inventory[block_type] > 0:
                        world.add_block(pos, block_type)
                        player.inventory[block_type] -= 1
                if event.key == K_BACKSPACE:
                    pos = (player.x, player.y, player.z)
                    if pos in world.blocks:
                        world.remove_block(pos)

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        world.draw()
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()