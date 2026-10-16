"""
FAKE Stolen Artifacts World Tracker (Pygame Version)
--------------------------------------------------
FLL SAFE PROJECT – ALL DATA IS FICTIONAL

Uses a static world map image (OpenStreetMap-style).

You must place a file called 'map.png' in the same folder.
"""

import pygame
import math

# -----------------------------
# Settings
# -----------------------------
WIDTH, HEIGHT = 1200, 600
FPS = 30

# -----------------------------
# Helper functions
# -----------------------------

def latlon_to_xy(lat, lon):
    """Convert latitude/longitude to screen coordinates."""
    x = (lon + 180) * (WIDTH / 360)
    y = (90 - lat) * (HEIGHT / 180)
    return int(x), int(y)


def move_towards(lat, lon, tlat, tlon, speed_kmh):
    """Move toward target at a realistic speed."""
    distance = math.sqrt((tlat - lat)**2 + (tlon - lon)**2)
    if distance == 0:
        return lat, lon

    step = speed_kmh / 111 / 3600  # km/h → degrees/frame
    ratio = min(step / distance, 1)

    return (
        lat + (tlat - lat) * ratio,
        lon + (tlon - lon) * ratio
    )

# -----------------------------
# Fake artifacts
# -----------------------------

artifacts = [
    {
        "name": "Golden Sun Idol",
        "lat": 48.8566,
        "lon": 2.3522,
        "tlat": 41.9028,
        "tlon": 12.4964,
        "speed": 2000
    },
    {
        "name": "Crystal Serpent Mask",
        "lat": 34.0522,
        "lon": -118.2437,
        "tlat": 35.6895,
        "tlon": 139.6917,
        "speed": 2000
    },
    {
        "name": "Obsidian Crown",
        "lat": -33.8688,
        "lon": 151.2093,
        "tlat": 1.3521,
        "tlon": 103.8198,
        "speed": 2000
    }
]

# -----------------------------
# Pygame setup
# -----------------------------

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Artifact Tracker (FLL)")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 18)

# You can swap maps by changing this filename
# Examples: 'world_map.png', 'political_map.png', 'satellite_map.png'
MAP_FILE = "map.png"

world_map = pygame.image.load(MAP_FILE)
world_map = pygame.transform.scale(world_map, (WIDTH, HEIGHT))

# -----------------------------
# Main loop
# -----------------------------

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(world_map, (0, 0))

    for art in artifacts:
        art["lat"], art["lon"] = move_towards(
            art["lat"], art["lon"], art["tlat"], art["tlon"], art["speed"]
        )

        x, y = latlon_to_xy(art["lat"], art["lon"])
        pygame.draw.circle(screen, (255, 0, 0), (x, y), 5)

        label = font.render(art["name"], True, (255, 255, 255))
        screen.blit(label, (x + 6, y - 6))

    pygame.display.flip()

pygame.quit()
