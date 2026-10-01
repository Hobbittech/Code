import pygame, random
from settings import TILE
import tiles
from pathlib import Path
class Gel:
    def __init__(self,x,y):
        self.x=x; self.y=y; self.w=28; self.h=20; self.vx=random.choice([-1,1])*1.2; self.vy=0
        self.hp=6; self.dead=False
        self.sprite=pygame.image.load(str(Path(__file__).parent/'assets'/'enemies'/'gel.png')).convert_alpha()
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.w,self.h)
    def update(self,dt,world,player):
        if random.random()<0.008 and abs(player.x-self.x)<220:
            self.vy=-6.5; self.vx = 1.6 if player.x>self.x else -1.6
        self.x+=self.vx; self.vy+=0.35
        if self.vy>8: self.vy=8
        self.y+=self.vy
        rect=self.rect()
        left=rect.left//TILE; right=(rect.right-1)//TILE; top=rect.top//TILE; bottom=(rect.bottom-1)//TILE
        for ty in range(top,bottom+1):
            for tx in range(left,right+1):
                tid=world.get_tile(tx,ty)
                if tid!=tiles.AIR and tiles.TILE_SOLID.get(tid,False):
                    trect=pygame.Rect(tx*TILE,ty*TILE,TILE,TILE)
                    if rect.colliderect(trect):
                        if rect.bottom - trect.top < 10 and self.vy>0:
                            self.y = trect.top - self.h; self.vy = -4.5
                        else:
                            self.vx *= -1
    def draw(self,surf,camx,camy):
        if self.dead: return
        surf.blit(self.sprite,(int(self.x-camx),int(self.y-camy)))
