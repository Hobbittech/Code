import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Paddle settings
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
PADDLE_SPEED = 7

# Ball settings
BALL_SIZE = 20

# Score
score_left = 0
score_right = 0
FONT = pygame.font.SysFont("Arial", 36)

# Paddle positions
left_paddle = pygame.Rect(30, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(WIDTH-40, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Ball position
ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)
ball_dx, ball_dy = 0, 0

clock = pygame.time.Clock()

def random_speed():
    speed_x = random.choice([-1, 1]) * random.randint(4, 7)
    speed_y = random.choice([-1, 1]) * random.randint(3, 7)
    return speed_x, speed_y

def reset_ball():
    global ball_dx, ball_dy
    ball.center = (WIDTH//2, HEIGHT//2)
    ball_dx, ball_dy = random_speed()

def start_screen():
    SCREEN.fill(BLACK)
    title = FONT.render("PONG GAME", True, WHITE)
    prompt = FONT.render("Press any key to start", True, WHITE)
    SCREEN.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 60))
    SCREEN.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 + 10))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

# Show start screen
start_screen()
reset_ball()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Paddle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and left_paddle.top > 0:
        left_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
        left_paddle.y += PADDLE_SPEED
    if keys[pygame.K_UP] and right_paddle.top > 0:
        right_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and right_paddle.bottom < HEIGHT:
        right_paddle.y += PADDLE_SPEED

    # Ball movement
    ball.x += ball_dx
    ball.y += ball_dy

    # Ball collision with top/bottom
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_dy *= -1

    # Ball collision with paddles
    if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
        ball_dx *= -1

    # Ball out of bounds
    if ball.left <= 0:
        score_right += 1
        reset_ball()
    if ball.right >= WIDTH:
        score_left += 1
        reset_ball()

    # Drawing
    SCREEN.fill(BLACK)
    pygame.draw.rect(SCREEN, WHITE, left_paddle)
    pygame.draw.rect(SCREEN, WHITE, right_paddle)
    pygame.draw.ellipse(SCREEN, WHITE, ball)
    pygame.draw.aaline(SCREEN, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))

    score_text = FONT.render(f"{score_left}   {score_right}", True, WHITE)
    SCREEN.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))

    pygame.display.flip()
    clock.tick(60)
