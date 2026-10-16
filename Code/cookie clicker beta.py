import pygame # type: ignore
import sys
import time
import os
import json

pygame.init()

# Window setup
WIDTH, HEIGHT = 600, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cookie Clicker")

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BROWN = (210, 180, 140)
GOLD = (255, 215, 0)

# Fonts
font = pygame.font.SysFont(None, 32)
small_font = pygame.font.SysFont(None, 24)

# Game variables
cookies = 0
cookies_per_click = 1
upgrade_cost = 10
auto_clicker_cost = 50
auto_clicker_count = 0
grandma_cost = 200
grandma_count = 0
factory_cost = 1000
factory_count = 0
ascend_available = False
ascend_bonus = 0

# Button rects
cookie_rect = pygame.Rect(250, 100, 100, 100)
upgrade_rect = pygame.Rect(50, 250, 180, 40)
auto_clicker_rect = pygame.Rect(270, 250, 180, 40)
grandma_rect = pygame.Rect(50, 310, 180, 40)
factory_rect = pygame.Rect(270, 310, 180, 40)
ascend_rect = pygame.Rect(200, 400, 200, 40)

# Timer for auto clicker
AUTO_CLICK_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(AUTO_CLICK_EVENT, 1000)

# Save/load
SAVE_FILE = "cookie_clicker_save.json"

def save_game():
    data = {
        "cookies": cookies,
        "cookies_per_click": cookies_per_click,
        "upgrade_cost": upgrade_cost,
        "auto_clicker_cost": auto_clicker_cost,
        "auto_clicker_count": auto_clicker_count,
        "grandma_cost": grandma_cost,
        "grandma_count": grandma_count,
        "factory_cost": factory_cost,
        "factory_count": factory_count,
        "ascend_bonus": ascend_bonus,
        "last_time": time.time()
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_game():
    global cookies, cookies_per_click, upgrade_cost, auto_clicker_cost, auto_clicker_count
    global grandma_cost, grandma_count, factory_cost, factory_count, ascend_bonus
    if os.path.exists(SAVE_FILE): 
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            cookies = data.get("cookies", 0)
            cookies_per_click = data.get("cookies_per_click", 1)
            upgrade_cost = data.get("upgrade_cost", 10)
            auto_clicker_cost = data.get("auto_clicker_cost", 50)
            auto_clicker_count = data.get("auto_clicker_count", 0)
            grandma_cost = data.get("grandma_cost", 200)
            grandma_count = data.get("grandma_count", 0)
            factory_cost = data.get("factory_cost", 1000)
            factory_count = data.get("factory_count", 0)
            ascend_bonus = data.get("ascend_bonus", 0)
            last_time = data.get("last_time", time.time())
            # Offline progress
            elapsed = int(time.time() - last_time)
            offline_cps = get_cps()
            offline_cookies = elapsed * offline_cps
            if offline_cookies > 0:
                print(f"You earned {offline_cookies} cookies while offline!")
            add_cookies(offline_cookies)

def get_cps():
    # 1 per auto clicker, 5 per grandma, 20 per factory, plus ascend bonus
    return auto_clicker_count * 1 + grandma_count * 5 + factory_count * 20 + ascend_bonus

def add_cookies(amount):
    global cookies
    cookies += int(amount)

def draw():
    screen.fill(WHITE)
    # Draw cookie (circle)
    pygame.draw.ellipse(screen, BROWN, cookie_rect)
    pygame.draw.ellipse(screen, BLACK, cookie_rect, 2)
    cookie_text = font.render("Cookie", True, BLACK)
    screen.blit(cookie_text, (cookie_rect.x + 10, cookie_rect.y + 35))

    # Draw stats
    cookies_text = font.render(f"Cookies: {int(cookies)}", True, BLACK)
    screen.blit(cookies_text, (20, 20))
    cps_text = small_font.render(f"Cookies/sec: {get_cps()}", True, BLACK)
    screen.blit(cps_text, (20, 60))
    auto_clickers_text = small_font.render(f"Auto Clickers: {auto_clicker_count}", True, BLACK)
    screen.blit(auto_clickers_text, (20, 90))
    grandma_text = small_font.render(f"Grandmas: {grandma_count}", True, BLACK)
    screen.blit(grandma_text, (20, 120))
    factory_text = small_font.render(f"Factories: {factory_count}", True, BLACK)
    screen.blit(factory_text, (20, 150))
    if ascend_bonus > 0:
        bonus_text = small_font.render(f"Ascend Bonus: +{ascend_bonus} CPS", True, GOLD)
        screen.blit(bonus_text, (20, 180))

    # Draw buttons
    pygame.draw.rect(screen, GRAY, upgrade_rect)
    pygame.draw.rect(screen, BLACK, upgrade_rect, 2)
    upgrade_text = small_font.render(f"Upgrade (+1/click) ({int(upgrade_cost)})", True, BLACK)
    screen.blit(upgrade_text, (upgrade_rect.x + 10, upgrade_rect.y + 10))

    pygame.draw.rect(screen, GRAY, auto_clicker_rect)
    pygame.draw.rect(screen, BLACK, auto_clicker_rect, 2)
    auto_clicker_text = small_font.render(f"Auto Clicker (+1/sec) ({int(auto_clicker_cost)})", True, BLACK)
    screen.blit(auto_clicker_text, (auto_clicker_rect.x + 10, auto_clicker_rect.y + 10))

    pygame.draw.rect(screen, GRAY, grandma_rect)
    pygame.draw.rect(screen, BLACK, grandma_rect, 2)
    grandma_btn_text = small_font.render(f"Grandma (+5/sec) ({int(grandma_cost)})", True, BLACK)
    screen.blit(grandma_btn_text, (grandma_rect.x + 10, grandma_rect.y + 10))

    pygame.draw.rect(screen, GRAY, factory_rect)
    pygame.draw.rect(screen, BLACK, factory_rect, 2)
    factory_btn_text = small_font.render(f"Factory (+20/sec) ({int(factory_cost)})", True, BLACK)
    screen.blit(factory_btn_text, (factory_rect.x + 10, factory_rect.y + 10))

    # Ascend button
    if cookies >= 1000:
        pygame.draw.rect(screen, GOLD, ascend_rect)
        pygame.draw.rect(screen, BLACK, ascend_rect, 2)
        ascend_text = font.render("ASCEND!", True, BLACK)
        screen.blit(ascend_text, (ascend_rect.x + 40, ascend_rect.y + 5))

    pygame.display.flip()

def ascend():
    global cookies, cookies_per_click, upgrade_cost, auto_clicker_cost, auto_clicker_count
    global grandma_cost, grandma_count, factory_cost, factory_count, ascend_bonus
    # Give +1 CPS per 1000 cookies spent on ascend
    bonus = int(cookies // 1000)
    ascend_bonus += bonus
    cookies = 0
    cookies_per_click = 1
    upgrade_cost = 10
    auto_clicker_cost = 50
    auto_clicker_count = 0
    grandma_cost = 200
    grandma_count = 0
    factory_cost = 1000
    factory_count = 0

load_game()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game()
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if cookie_rect.collidepoint(mx, my):
                add_cookies(cookies_per_click)
            elif upgrade_rect.collidepoint(mx, my):
                if cookies >= upgrade_cost:
                    cookies -= int(upgrade_cost)
                    cookies_per_click += 1
                    upgrade_cost *= 1.5
            elif auto_clicker_rect.collidepoint(mx, my):
                if cookies >= auto_clicker_cost:
                    cookies -= int(auto_clicker_cost)
                    auto_clicker_count += 1
                    auto_clicker_cost *= 1.5
            elif grandma_rect.collidepoint(mx, my):
                if cookies >= grandma_cost:
                    cookies -= int(grandma_cost)
                    grandma_count += 1
                    grandma_cost *= 1.5
            elif factory_rect.collidepoint(mx, my):
                if cookies >= factory_cost:
                    cookies -= int(factory_cost)
                    factory_count += 1
                    factory_cost *= 1.5
            elif cookies >= 1000 and ascend_rect.collidepoint(mx, my):
                ascend()

        elif event.type == AUTO_CLICK_EVENT:
            add_cookies(get_cps())

    draw()

pygame.quit()
sys.exit()
