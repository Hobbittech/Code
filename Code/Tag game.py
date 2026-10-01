import sys
import pygame


# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2 Player Tag Game")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Player settings
PLAYER_SIZE = 40
player1 = pygame.Rect(100, 100, PLAYER_SIZE, PLAYER_SIZE)
player2 = pygame.Rect(600, 400, PLAYER_SIZE, PLAYER_SIZE)
player1_speed = 5
player2_speed = 5

# Tag state
tagged = 1  # 1 means player1 is "it", 2 means player2 is "it"
font = pygame.font.SysFont(None, 48)

clock = pygame.time.Clock()

def draw():
    screen.fill(WHITE)
    pygame.draw.rect(screen, RED if tagged == 1 else BLUE, player1)
    pygame.draw.rect(screen, BLUE if tagged == 1 else RED, player2)
    tag_text = font.render(f"Player {tagged} is IT!", True, BLACK)
    screen.blit(tag_text, (WIDTH // 2 - tag_text.get_width() // 2, 20))
    pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    # Player 1 controls (WASD)
    if keys[pygame.K_w]:
        player1.y -= player1_speed
    if keys[pygame.K_s]:
        player1.y += player1_speed
    if keys[pygame.K_a]:
        player1.x -= player1_speed
    if keys[pygame.K_d]:
        player1.x += player1_speed
    # Player 2 controls (Arrow keys)
    if keys[pygame.K_UP]:
        player2.y -= player2_speed
    if keys[pygame.K_DOWN]:
        player2.y += player2_speed
    if keys[pygame.K_LEFT]:
        player2.x -= player2_speed
    if keys[pygame.K_RIGHT]:
        player2.x += player2_speed

    # Keep players inside the screen
    player1.clamp_ip(screen.get_rect())
    player2.clamp_ip(screen.get_rect())

    # Tag logic
    if player1.colliderect(player2):
        tagged = 2 if tagged == 1 else 1

    draw()
    clock.tick(60)