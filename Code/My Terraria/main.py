import pygame, sys, time, random
from pathlib import Path
from settings import SCREEN_W, SCREEN_H, TILE, CHUNK_WIDTH, CHUNK_HEIGHT, RENDER_DISTANCE, FPS
from world import World
from player import Player
from inventory import Inventory
from enemies import Gel
import tiles

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption('Terraria')
clock = pygame.time.Clock()
font = pygame.font.SysFont('Consolas', 16)

seed = random.randint(0, 2**30)
world = World(seed=seed, creative=False)
player = Player(200, 100)
inventory = Inventory()

# Load tile images
TILE_SURF = {}
for tid, path in tiles.TILE_SPRITE.items():
    p = Path(path)
    if p.exists():
        surf = pygame.image.load(str(p)).convert_alpha()
        TILE_SURF[tid] = pygame.transform.scale(surf, (TILE, TILE)) 
    else:
        s = pygame.Surface((TILE, TILE))
        s.fill((255, 0, 255))
        TILE_SURF[tid] = s

# Load player animation frames
pdir = Path(__file__).parent / 'assets' / 'player'
frames = []
for name in ['player_idle.png', 'player_walk0.png', 'player_walk1.png', 'player_walk2.png', 'player_jump.png']:
    fp = pdir / name
    if fp.exists():
        frames.append(pygame.image.load(str(fp)).convert_alpha())

if frames:
    player.frames = [pygame.transform.scale(f, (player.w, player.h)) for f in frames]

# Load enemies
enemies = [Gel(420, 100), Gel(560, 100)]

CAM_X, CAM_Y = 0, 0
MINE_BASE = 0.6
last_save = time.time()
running = True
mouse_held = False

while running:
    dt = clock.tick(FPS) / 1000.0
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            world.save_modified()
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_9:
                inventory.select(event.key - pygame.K_1)
            if event.key == pygame.K_c:
                inventory.creative = not inventory.creative
                world.creative = inventory.creative
            if event.key == pygame.K_m and inventory.creative:
                world = World(seed=random.randint(0, 2**30), creative=True)
            if event.key == pygame.K_f:
                player.start_attack()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click start mining
                mouse_held = True
                gx = int((event.pos[0] + CAM_X) // TILE)
                gy = int((event.pos[1] + CAM_Y) // TILE)
                tid = world.get_tile(gx, gy)
                if tid != tiles.AIR and tiles.TILE_SOLID.get(tid, False):
                    player.mining = True
                    player.mine_target = (gx, gy)
                    player.mine_progress = 0.0
            if event.button == 3:  # Right click place block
                gx = int((event.pos[0] + CAM_X) // TILE)
                gy = int((event.pos[1] + CAM_Y) // TILE)
                sel = inventory.selected_id()
                if sel >= 100:
                    pass
                else:
                    if world.get_tile(gx, gy) == tiles.AIR:
                        if inventory.remove_one_selected():
                            world.set_tile(gx, gy, sel)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_held = False
                player.mining = False
                player.mine_target = None
                player.mine_progress = 0.0

    player.update(keys, world, dt)

    # Player attacking enemies
    if player.attacking:
        for e in list(enemies):
            ex = e.x + e.w / 2
            ey = e.y + e.h / 2
            px = player.x + player.w / 2
            py = player.y + player.h / 2
            if abs(ex - px) < 48 and abs(ey - py) < 32:
                e.hp -= 4
                if e.hp <= 0:
                    e.dead = True

    # Update enemies and remove dead
    for e in list(enemies):
        e.update(dt, world, player)
        if e.dead:
            enemies.remove(e)

    # Camera follows player
    CAM_X = int(player.x + player.w // 2 - SCREEN_W // 2)
    CAM_Y = int(player.y + player.h // 2 - SCREEN_H // 2)

    # Mining progress
    if player.mining and player.mine_target:
        gx, gy = player.mine_target
        tid = world.get_tile(gx, gy)
        if tid == tiles.AIR or not tiles.TILE_SOLID.get(tid, False):
            player.mining = False
            player.mine_target = None
            player.mine_progress = 0.0
        else:
            hardness = tiles.TILE_HARDNESS.get(tid, 1.0)
            mine_time = MINE_BASE * hardness / max(player.tool_power, 1)
            player.mine_progress += dt
            if player.mine_progress >= mine_time:
                world.set_tile(gx, gy, tiles.AIR)
                inventory.add(tid, amount=1)
                player.mining = False
                player.mine_target = None
                player.mine_progress = 0.0

    # Auto-save every 30 seconds
    if time.time() - last_save > 30:
        world.save_modified()
        last_save = time.time()

    screen.fill((120, 180, 255))

    # Draw world
    player_tile_x = int((player.x + player.w // 2) // TILE)
    center_chunk = player_tile_x // CHUNK_WIDTH
    left_chunk = center_chunk - RENDER_DISTANCE
    right_chunk = center_chunk + RENDER_DISTANCE

    for cx in range(left_chunk, right_chunk + 1):
        world.ensure_chunk(cx)
        chunk = world.chunks[cx]
        for y in range(CHUNK_HEIGHT):
            for x in range(CHUNK_WIDTH):
                tid = chunk[y][x]
                if tid == tiles.AIR:
                    continue
                gx = cx * CHUNK_WIDTH + x
                sx = int(gx * TILE - CAM_X)
                sy = int(y * TILE - CAM_Y)
                screen.blit(TILE_SURF.get(tid), (sx, sy))

    # Draw enemies and player
    for e in enemies:
        e.draw(screen, CAM_X, CAM_Y)
    player.draw(screen, CAM_X, CAM_Y)

    # Draw hotbar UI
    for i, (tid, cnt) in enumerate(inventory.hotbar):
        x = 10 + i * (TILE + 6)
        y = SCREEN_H - TILE - 10
        pygame.draw.rect(screen, (60, 60, 60), (x - 2, y - 2, TILE + 4, TILE + 4))
        surf = TILE_SURF.get(tid)
        if surf:
            screen.blit(surf, (x, y))
        screen.blit(font.render(str(cnt), True, (0, 0, 0)), (x + 4, y + 4))
        if i == inventory.selected:
            pygame.draw.rect(screen, (255, 255, 0), (x - 4, y - 4, TILE + 8, TILE + 8), 3)

    pygame.display.flip()