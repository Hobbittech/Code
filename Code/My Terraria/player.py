import pygame
import math
from settings import TILE
import tiles

GRAVITY = 0.55
MAX_FALL_SPEED = 14

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 24
        self.h = 40
        self.vx = 0
        self.vy = 0
        self.speed = 4.2
        self.on_ground = False
        self.facing = 1
        self.mining = False
        self.mine_target = None
        self.mine_progress = 0.0
        self.tool_power = 1.0
        self.attacking = False
        self.attack_cool = 0.0
        self.frames = None
        self.anim_frame = 0
        self.anim_timer = 0.0

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, keys, world, dt):
        ax = 0
        # Movement
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            ax -= self.speed
            self.facing = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            ax += self.speed
            self.facing = 1
        self.x += ax

        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vy = -11
            self.on_ground = False

        # Gravity
        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED
        self.y += self.vy

        # Collisions
        self._resolve_collisions(world)

        # Attack cooldown
        if self.attack_cool > 0:
            self.attack_cool -= dt
        else:
            self.attacking = False

        # Animation
        if self.frames:
            self.anim_timer += dt * (12 if abs(ax) > 0.1 else 4)
            if self.anim_timer > 0.1:
                self.anim_frame = (self.anim_frame + 1) % len(self.frames)
                self.anim_timer = 0.0

    def _resolve_collisions(self, world):
        rect = self.rect()
        left = int(math.floor(rect.left / TILE))
        right = int(math.floor((rect.right - 1) / TILE))
        top = int(math.floor(rect.top / TILE))
        bottom = int(math.floor((rect.bottom - 1) / TILE))
        self.on_ground = False
        for ty in range(top, bottom + 1):
            for tx in range(left, right + 1):
                tid = world.get_tile(tx, ty)
                if tid != tiles.AIR and tiles.TILE_SOLID.get(tid, False):
                    trect = pygame.Rect(tx * TILE, ty * TILE, TILE, TILE)
                    if rect.colliderect(trect):
                        ol = rect.right - trect.left
                        orr = trect.right - rect.left
                        ot = rect.bottom - trect.top
                        ob = trect.bottom - rect.top
                        m = min(ol, orr, ot, ob)
                        if m == ol:
                            rect.right = trect.left
                            self.x = rect.left
                        elif m == orr:
                            rect.left = trect.right
                            self.x = rect.left
                        elif m == ot:
                            rect.bottom = trect.top
                            self.y = rect.top
                            self.vy = 0
                            self.on_ground = True
                        else:
                            rect.top = trect.bottom
                            self.y = rect.top
                            self.vy = 0

    def start_attack(self):
        if self.attack_cool <= 0:
            self.attacking = True
            self.attack_cool = 0.45

    def draw(self, surf, camx, camy):
        if self.frames:
            frame = self.frames[self.anim_frame]
            if self.facing == -1:
                frame = pygame.transform.flip(frame, True, False)
            surf.blit(frame, (int(self.x - camx), int(self.y - camy)))
        else:
            pygame.draw.rect(surf, (200, 200, 255), (int(self.x - camx), int(self.y - camy), self.w, self.h))