"""
advanced_cookie_clicker.py
Single-file advanced Cookie Clicker clone using pygame.

Features:
- Clickable central cookie with click animation and particles
- Multiple buildings with exponential pricing and CPS
- Upgrades and achievements
- Prestige (ascend) mechanic
- Offline earnings (based on last save timestamp)
- Autosave and manual save/load
- Keyboard shortcuts:
    SPACE - click cookie
    LEFT/RIGHT - cycle selected building
    B - buy selected building
    U - toggle upgrades panel
    A - toggle auto-buy for selected building
    P - prestige (ascend)
    S - save
    L - load
    T - toggle stats
- No external assets required.

"""

import pygame, sys, math, random, json, os, time
from dataclasses import dataclass, field
from typing import List, Dict

# -----------------------
# Config
# -----------------------
SAVE_FILE = "cookie_save.json"
WINDOW_SIZE = (1200, 720)
FPS = 60
AUTOSAVE_INTERVAL = 30  # seconds
FONT_NAME = None  # None picks default pygame font
COOKIE_RADIUS = 100
GOLDEN_COOKIE_CHANCE = 0.0005  # chance per frame
OFFLINE_EARNINGS_CAP_SECONDS = 60*60*24  # cap offline earnings to 24 hours

# -----------------------
# Utility
# -----------------------
def fmt(n: float) -> str:
    """Nice formatting for big numbers."""
    abbreviations = [(1e18,"Q"),(1e15,"q"),(1e12,"T"),(1e9,"B"),(1e6,"M"),(1e3,"k")]
    for val, suf in abbreviations:
        if abs(n) >= val:
            return f"{n/val:,.2f}{suf}"
    if n == int(n):
        return f"{int(n)}"
    return f"{n:,.2f}"

def now_ts() -> float:
    return time.time()

# -----------------------
# Data classes
# -----------------------
@dataclass
class Building:
    name: str
    base_cost: float
    base_cps: float
    count: int = 0
    multiplier: float = 1.0
    auto_buy: bool = False

    def cost(self) -> float:
        # exponential price growth: cost * (1.15^count)
        return self.base_cost * (1.15 ** self.count)

    def cps(self) -> float:
        return self.count * self.base_cps * self.multiplier

@dataclass
class Upgrade:
    id: str
    name: str
    description: str
    price: float
    effect: dict  # e.g. {"mult_building":"Grandma", "factor":2}
    bought: bool = False

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    condition: dict  # e.g. {"total_cookies":1000}
    earned: bool = False

# -----------------------
# Game class
# -----------------------
class CookieGame:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = self.screen.get_size()
        self.click_anim_scale = 0.06
        self.center = (int(self.width*0.35), int(self.height*0.45))
        self.cookie_radius = COOKIE_RADIUS
        self.font = pygame.font.Font(FONT_NAME, 18)
        self.large_font = pygame.font.Font(FONT_NAME, 32)
        self.big_font = pygame.font.Font(FONT_NAME, 48)
        self.clock = pygame.time.Clock()

        # core economy
        self.cookies = 15.0
        self.total_cookies_earned = 15.0
        self.cookie_per_click = 1.0
        self.prestige_level = 0
        self.prestige_multiplier = 1.0

        # buildings
        self.buildings: List[Building] = [
            Building("Cursor", 15.0, 0.1),
            Building("Grandma", 100.0, 1.0),
            Building("Farm", 1100.0, 8.0),
            Building("Mine", 12000.0, 47.0),
            Building("Factory", 130000.0, 260.0),
            Building("Bank", 1_400_000.0, 1400.0),
            Building("Temple", 20_000_000.0, 7800.0),
        ]
        self.selected_building_index = 0

        # upgrades
        self.upgrades: Dict[str, Upgrade] = {}
        self._create_upgrades()

        # achievements
        self.achievements: Dict[str, Achievement] = {}
        self._create_achievements()

        # UI toggles
        self.show_upgrades = False
        self.show_stats = False

        # particles and animations
        self.particles = []
        self.click_anim_progress = 0.0
        self.golden_cookie_active = False
        self.golden_cookie_timer = 0.0
        self.golden_cookie_multiplier = 7.0  # clicking golden cookie gives lot of cookies

        # save/load and offline
        self.last_save_ts = now_ts()
        self.last_save_loaded = None
        self.last_autosave = now_ts()

        # sounds
        pygame.mixer.init()
        self.click_sound = None
        try:
            self.click_sound = pygame.mixer.Sound(self._generate_beep(880, 0.05))
        except Exception:
            self.click_sound = None

        # stats
        self.start_ts = now_ts()
        self.session_clicks = 0

        # golden cookie small UI
        self.golden_cookie_rect = pygame.Rect(0,0,80,40)

        # load if save exists
        if os.path.exists(SAVE_FILE):
            self.load_game()
        else:
            # initial achievements check
            self.evaluate_achievements()

    # -----------------------
    # Procedural beep generator for simple sound
    # -----------------------
    def _generate_beep(self, frequency, duration):
        """Return a pygame Sound object constructed in memory as raw samples bytes."""
        sample_rate = 22050
        n_samples = int(round(duration * sample_rate))
        buf = bytearray()
        volume = 0.2
        for s in range(n_samples):
            t = float(s) / sample_rate
            v = int(127 + 127 * volume * math.sin(2.0 * math.pi * frequency * t))
            buf.append(v)
        arr = bytes(buf)
        import io, wave
        mem = io.BytesIO()
        wf = wave.open(mem, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(1)
        wf.setframerate(sample_rate)
        wf.writeframes(arr)
        wf.close()
        mem.seek(0)
        return mem

    # -----------------------
    # Upgrades & achievements definitions
    # -----------------------
    def _create_upgrades(self):
        up = [
            ("cpc_upgrade", "Reinforced Click", "Double cookie per click.", 100.0, {"mult_click":2.0}),
            ("grandma_2x", "Grandma's Boost", "Double grandmas' output.", 500.0, {"mult_building":"Grandma","factor":2.0}),
            ("farm_tools", "Efficient Farming", "Increase Farm output by 2x.", 5000.0, {"mult_building":"Farm","factor":2.0}),
            ("click_factory", "Factory Buttons", "Click gives +10 CPS for 10s", 25000.0, {"temp_cps":10.0}),
        ]
        for id_, name, desc, price, effect in up:
            self.upgrades[id_] = Upgrade(id_, name, desc, price, effect)

    def _create_achievements(self):
        ach = [
            ("first_click", "First Click", "Click the cookie once", {"clicks":1}),
            ("100_cookies", "Cookie Hoarder", "Accumulate 100 cookies total", {"total_cookies":100}),
            ("grandma_10", "Granny Magnate", "Own 10 grandmas", {"building_count":{"Grandma":10}}),
            ("prestige_once", "Ascendant", "Prestige once", {"prestige_level":1}),
        ]
        for id_, name, desc, cond in ach:
            self.achievements[id_] = Achievement(id_, name, desc, cond)

    # -----------------------
    # Core mechanics
    # -----------------------
    def click_cookie(self, amount=None, golden=False):
        if amount is None:
            amount = self.cookie_per_click
        gain = amount * self.prestige_multiplier
        # clicking golden cookie gives multiplied reward
        if golden:
            gain *= self.golden_cookie_multiplier
        self.cookies += gain
        self.total_cookies_earned += gain
        self.session_clicks += 1
        self.click_anim_progress = 1.0
        self.click_anim_scale = random.uniform(0.04, 0.12)
        # spawn particles
        for _ in range(10 if not golden else 25):
            self._spawn_particle(golden=golden)
        if self.click_sound:
            try:
                self.click_sound.stop()
                self.click_sound.play()
            except Exception:
                pass
        self.evaluate_achievements()

    def buy_building(self, index: int, max_afford=False):
        b = self.buildings[index]
        price = b.cost()
        if max_afford:
            bought = 0
            while self.cookies >= price:
                self.cookies -= price
                b.count += 1
                bought += 1
                price = b.cost()
            if bought:
                return True
            return False
        else:
            if self.cookies >= price:
                self.cookies -= price
                b.count += 1
                self.evaluate_achievements()
                return True
            return False

    def total_cps(self) -> float:
        base = sum(b.cps() for b in self.buildings)
        # upgrades effect: some upgrades change building multipliers already applied
        return base * self.prestige_multiplier

    def tick(self, dt):
        # passive gain
        cps = self.total_cps()
        gain = cps * dt
        self.cookies += gain
        self.total_cookies_earned += gain

        # reduce click animation progress
        if self.click_anim_progress > 0:
            self.click_anim_progress = max(0.0, self.click_anim_progress - dt*3)

        # particle update
        for p in list(self.particles):
            p['x'] += p['vx']*dt*60
            p['y'] += p['vy']*dt*60
            p['life'] -= dt
            p['alpha'] = max(0.0, p['life'])
            if p['life'] <= 0:
                self.particles.remove(p)

        # golden cookie spawn chance
        if not self.golden_cookie_active and random.random() < GOLDEN_COOKIE_CHANCE:
            self.activate_golden_cookie()

        if self.golden_cookie_active:
            self.golden_cookie_timer -= dt
            if self.golden_cookie_timer <= 0:
                self.golden_cookie_active = False

        # auto-buy buildings
        for i,b in enumerate(self.buildings):
            if b.auto_buy:
                # try to buy one if affordable
                if self.cookies >= b.cost():
                    self.buy_building(i)

        # periodic autosave
        if now_ts() - self.last_autosave > AUTOSAVE_INTERVAL:
            self.save_game()
            self.last_autosave = now_ts()

    # -----------------------
    # Particles and effects
    # -----------------------
    def _spawn_particle(self, golden=False):
        angle = random.random()*math.pi*2
        speed = random.uniform(1,4) * (3 if golden else 1)
        p = {
            'x': self.center[0] + random.randint(-self.cookie_radius//2,self.cookie_radius//2),
            'y': self.center[1] + random.randint(-self.cookie_radius//2,self.cookie_radius//2),
            'vx': math.cos(angle)*speed,
            'vy': math.sin(angle)*speed - 1,
            'life': random.uniform(0.5,1.6),
            'alpha':1.0,
            'golden': golden
        }
        self.particles.append(p)

    # -----------------------
    # Golden cookie
    # -----------------------
    def activate_golden_cookie(self, duration=10.0):
        self.golden_cookie_active = True
        self.golden_cookie_timer = duration
        # position randomly near corner
        x = random.randint(self.width//2+30, self.width-100)
        y = random.randint(30, self.height-150)
        self.golden_cookie_rect.topleft = (x,y)

    # -----------------------
    # Upgrades & achievements handling
    # -----------------------
    def buy_upgrade(self, upgrade_id):
        up = self.upgrades.get(upgrade_id)
        if not up or up.bought:
            return False
        if self.cookies >= up.price:
            self.cookies -= up.price
            up.bought = True
            # apply effect
            eff = up.effect
            if "mult_click" in eff:
                self.cookie_per_click *= eff["mult_click"]
            if "mult_building" in eff:
                name = eff["mult_building"]
                for b in self.buildings:
                    if b.name == name:
                        b.multiplier *= eff.get("factor",1.0)
            self.evaluate_achievements()
            return True
        return False

    def evaluate_achievements(self):
        for a in self.achievements.values():
            if a.earned: continue
            cond = a.condition
            ok = True
            if "clicks" in cond:
                ok = ok and (self.session_clicks >= cond["clicks"])
            if "total_cookies" in cond:
                ok = ok and (self.total_cookies_earned >= cond["total_cookies"])
            if "building_count" in cond:
                for name, cnt in cond["building_count"].items():
                    found = next((b.count for b in self.buildings if b.name==name),0)
                    ok = ok and (found >= cnt)
            if "prestige_level" in cond:
                ok = ok and (self.prestige_level >= cond["prestige_level"])
            if ok:
                a.earned = True
                # spawn celebratory particles
                for _ in range(25):
                    self._spawn_particle(golden=True)

    # -----------------------
    # Prestige / Ascend
    # -----------------------
    def prestige(self):
        # simple prestige: score = total_cookies_earned, get prestige levels at thresholds
        # We'll make each prestige level give +10% global CPS per level as permanent bonus
        next_level_req = 1_000_000 * (2 ** self.prestige_level)
        if self.total_cookies_earned >= next_level_req:
            self.prestige_level += 1
            # compute multiplier
            self.prestige_multiplier = 1.0 + 0.10 * self.prestige_level
            # reset economy but keep prestige benefits
            self.cookies = 15.0
            self.total_cookies_earned = 15.0
            self.cookie_per_click = 1.0
            for b in self.buildings:
                b.count = 0
                b.multiplier = 1.0
            for u in self.upgrades.values():
                u.bought = False
            for a in self.achievements.values():
                a.earned = False
            self.session_clicks = 0
            self.evaluate_achievements()
            return True
        return False

    # -----------------------
    # Save/Load
    # -----------------------
    def save_game(self):
        data = {
            "cookies": self.cookies,
            "total_cookies_earned": self.total_cookies_earned,
            "cookie_per_click": self.cookie_per_click,
            "prestige_level": self.prestige_level,
            "prestige_multiplier": self.prestige_multiplier,
            "buildings":[{"name":b.name,"count":b.count,"multiplier":b.multiplier,"auto_buy":b.auto_buy} for b in self.buildings],
            "upgrades":[{"id":u.id,"bought":u.bought} for u in self.upgrades.values()],
            "achievements":[{"id":a.id,"earned":a.earned} for a in self.achievements.values()],
            "last_save_ts": now_ts(),
            "session_clicks": self.session_clicks,
            "total_time": now_ts() - self.start_ts,
        }
        with open(SAVE_FILE,"w") as f:
            json.dump(data,f)
        self.last_save_ts = now_ts()

    def load_game(self):
        try:
            with open(SAVE_FILE,"r") as f:
                data = json.load(f)
            self.cookies = data.get("cookies", self.cookies)
            self.total_cookies_earned = data.get("total_cookies_earned", self.total_cookies_earned)
            self.cookie_per_click = data.get("cookie_per_click", self.cookie_per_click)
            self.prestige_level = data.get("prestige_level", self.prestige_level)
            self.prestige_multiplier = data.get("prestige_multiplier", self.prestige_multiplier)
            bd = data.get("buildings", [])
            for bdata in bd:
                for b in self.buildings:
                    if b.name == bdata.get("name"):
                        b.count = bdata.get("count", b.count)
                        b.multiplier = bdata.get("multiplier", b.multiplier)
                        b.auto_buy = bdata.get("auto_buy", False)
            upg = data.get("upgrades", [])
            for ud in upg:
                u = self.upgrades.get(ud["id"])
                if u:
                    u.bought = ud.get("bought", u.bought)
                    # reapply effects for bought upgrades
                    if u.bought:
                        eff = u.effect
                        if "mult_click" in eff:
                            self.cookie_per_click *= eff["mult_click"]
                        if "mult_building" in eff:
                            for b in self.buildings:
                                if b.name == eff["mult_building"]:
                                    b.multiplier *= eff.get("factor",1.0)
            ach = data.get("achievements",[])
            for ad in ach:
                a = self.achievements.get(ad["id"])
                if a:
                    a.earned = ad.get("earned", a.earned)
            last_ts = data.get("last_save_ts", now_ts())
            self.last_save_ts = last_ts
            # offline earnings
            elapsed = now_ts() - last_ts
            if elapsed > 0:
                elapsed = min(elapsed, OFFLINE_EARNINGS_CAP_SECONDS)
                offline_gain = self.total_cps() * elapsed
                self.cookies += offline_gain
                self.total_cookies_earned += offline_gain
                self.last_save_loaded = elapsed
            self.evaluate_achievements()
            return True
        except Exception as e:
            print("Load failed:", e)
            return False

    # -----------------------
    # Render functions
    # -----------------------
    def render(self):
        self.screen.fill((25, 28, 34))
        # left side: cookie + particles
        self._render_cookie_area()

        # right side: buildings & upgrades
        self._render_sidebar()

        # top bar: stats
        self._render_topbar()

        # upgrades panel
        if self.show_upgrades:
            self._render_upgrades_panel()

        # achievements / stats
        if self.show_stats:
            self._render_stats_panel()

        pygame.display.flip()

    def _render_cookie_area(self):
        cx, cy = self.center
        # cookie hover/click animation scale
        scale = 1.0 + 0.06 * self.click_anim_progress
        r = int(self.cookie_radius * scale)
        # cookie gradient
        cookie_color = (245, 220, 150)
        inner_color = (255, 238, 160)
        # larger circle shadow
        shadow_rect = pygame.Rect(cx - r - 10, cy - r + 20, (r+10)*2, (r+10)*2)
        pygame.draw.ellipse(self.screen, (20,20,20,80), shadow_rect)
        # cookie main
        pygame.draw.circle(self.screen, cookie_color, (cx,cy), r)
        pygame.draw.circle(self.screen, inner_color, (cx-10,cy-10), int(r*0.85))
        # chocolate chips
        random.seed(0)  # deterministic chips positions
        for i in range(8):
            ang = (i / 8.0) * 2*math.pi + 0.2
            px = cx + int(math.cos(ang)*r*0.6)
            py = cy + int(math.sin(ang)*r*0.48)
            pygame.draw.circle(self.screen, (80,40,20), (px,py), max(6,int(r*0.06)))
        # cookie label
        txt = self.big_font.render(fmt(self.cookies) + " cookies", True, (240,240,240))
        self.screen.blit(txt, (cx - txt.get_width()//2, cy + r + 10))
        # click instruction
        instr = self.font.render("SPACE or Click the cookie", True, (200,200,200))
        self.screen.blit(instr, (cx - instr.get_width()//2, cy - r - 30))

        # particles
        for p in self.particles:
            col = (255,215,0) if p['golden'] else (255, 255, 255)
            a = int(255 * p['alpha'])
            surf = pygame.Surface((6,6), pygame.SRCALPHA)
            surf.fill(col)
            self.screen.blit(surf, (p['x'], p['y']))

        # golden cookie draw
        if self.golden_cookie_active:
            rect = self.golden_cookie_rect
            pygame.draw.ellipse(self.screen, (255,200,0), rect)
            txt = self.font.render("GOLD!", True, (50,20,0))
            self.screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

    def _render_sidebar(self):
        sx = int(self.width*0.55)
        margin = 20
        y = margin
        header = self.large_font.render("Buildings", True, (230,230,230))
        self.screen.blit(header, (sx, y)); y += header.get_height() + 8

        # CPS display
        cps_txt = self.font.render(f"CPS: {fmt(self.total_cps())}", True, (200,200,255))
        self.screen.blit(cps_txt, (sx, y)); y += cps_txt.get_height() + 8

        for i, b in enumerate(self.buildings):
            selected = (i == self.selected_building_index)
            bg_rect = pygame.Rect(sx, y, self.width - sx - margin, 60)
            pygame.draw.rect(self.screen, (40,40,50) if not selected else (60,60,80), bg_rect, border_radius=8)
            # name
            name = self.font.render(f"{b.name} x{b.count}", True, (220,220,220))
            self.screen.blit(name, (sx+10, y+8))
            # cost
            cost = b.cost()
            cost_txt = self.font.render(f"Cost: {fmt(cost)}", True, (200,200,200))
            self.screen.blit(cost_txt, (sx+10, y+28))
            # buy button small
            buy_txt = self.font.render("[B] Buy", True, (10,10,10))
            bt_rect = pygame.Rect(self.width-160, y+12, 120, 36)
            pygame.draw.rect(self.screen, (150,210,150) if self.cookies >= cost else (100,100,100), bt_rect, border_radius=6)
            self.screen.blit(buy_txt, (bt_rect.x+10, bt_rect.y+6))
            # auto-buy toggle marker
            abtxt = self.font.render("A" if b.auto_buy else "-", True, (255,255,255))
            self.screen.blit(abtxt, (bt_rect.right+8, bt_rect.y+8))
            y += 70

        # bottom: quick info
        y = self.height - 140
        pygame.draw.rect(self.screen, (40,40,50), (sx, y, self.width - sx - margin, 120), border_radius=8)
        info = [
            f"Click Power: {fmt(self.cookie_per_click)}",
            f"Total Earned: {fmt(self.total_cookies_earned)}",
            f"Prestige Level: {self.prestige_level} (x{self.prestige_multiplier:.2f})",
            "Keys: SPACE-click, B-buy, U-upgrades, P-prestige, S-save, L-load, T-stats"
        ]
        iy = y+8
        for line in info:
            t = self.font.render(line, True, (220,220,220))
            self.screen.blit(t, (sx+10, iy))
            iy += t.get_height() + 6

    def _render_upgrades_panel(self):
        w = int(self.width*0.8)
        h = int(self.height*0.45)
        x = (self.width - w)//2
        y = (self.height - h)//2
        pygame.draw.rect(self.screen, (18,18,24), (x,y,w,h), border_radius=12)
        pygame.draw.rect(self.screen, (60,60,60), (x,y,w,40), border_radius=12)
        title = self.font.render("Upgrades (click to buy)", True, (230,230,230))
        self.screen.blit(title, (x+12, y+8))
        # list upgrades
        uy = y + 56
        for up in self.upgrades.values():
            bg = pygame.Rect(x+8, uy, w-16, 48)
            pygame.draw.rect(self.screen, (30,30,36), bg, border_radius=8)
            name = self.font.render(up.name, True, (220,220,220))
            self.screen.blit(name, (bg.x+8, bg.y+6))
            desc = self.font.render(up.description, True, (170,170,170))
            self.screen.blit(desc, (bg.x+8, bg.y+26))
            price_txt = self.font.render(fmt(up.price), True, (200,200,200))
            self.screen.blit(price_txt, (bg.right-80, bg.y+14))
            if up.bought:
                bought = self.font.render("BOUGHT", True, (100,255,100))
                self.screen.blit(bought, (bg.right-160, bg.y+14))
            uy += 56

    def _render_stats_panel(self):
        w = int(self.width*0.6)
        h = int(self.height*0.5)
        x = (self.width - w)//2
        y = (self.height - h)//2
        pygame.draw.rect(self.screen, (15,15,20), (x,y,w,h), border_radius=12)
        txt = self.font.render("Statistics / Achievements", True, (230,230,230))
        self.screen.blit(txt, (x+12,y+8))
        ay = y+44
        for a in self.achievements.values():
            col = (200,230,200) if a.earned else (180,180,180)
            t = self.font.render(f"[{'X' if a.earned else ' '}] {a.name} - {a.description}", True, col)
            self.screen.blit(t, (x+12, ay))
            ay += t.get_height() + 6

        if self.last_save_loaded:
            off = self.font.render(f"Offline earnings applied for {int(self.last_save_loaded)}s", True, (200,200,200))
            self.screen.blit(off,(x+12, ay+10))

    def _render_topbar(self):
        # top left: game title
        title = self.large_font.render("Cookie Forge", True, (255,220,150))
        self.screen.blit(title, (16,8))
        # top right: small clock
        t = self.font.render(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), True, (170,170,170))
        self.screen.blit(t, (self.width - t.get_width() - 12, 12))

    # -----------------------
    # Input handling
    # -----------------------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.save_game()
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx,my = event.pos
            # click cookie?
            if (mx-self.center[0])**2 + (my-self.center[1])**2 <= (self.cookie_radius*1.2)**2:
                # click cookie
                self.click_cookie()
            # golden cookie click
            if self.golden_cookie_active and self.golden_cookie_rect.collidepoint(mx,my):
                self.click_cookie(amount=self.cookie_per_click, golden=True)
                self.golden_cookie_active = False
            # upgrades panel click
            if self.show_upgrades:
                self._handle_upgrades_click(mx,my)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.click_cookie()
            if event.key == pygame.K_RIGHT:
                self.selected_building_index = (self.selected_building_index + 1) % len(self.buildings)
            if event.key == pygame.K_LEFT:
                self.selected_building_index = (self.selected_building_index - 1) % len(self.buildings)
            if event.key == pygame.K_b:
                # buy selected
                self.buy_building(self.selected_building_index)
            if event.key == pygame.K_a:
                b = self.buildings[self.selected_building_index]
                b.auto_buy = not b.auto_buy
            if event.key == pygame.K_u:
                self.show_upgrades = not self.show_upgrades
            if event.key == pygame.K_p:
                ok = self.prestige()
                if ok:
                    print("Prestiged! level:", self.prestige_level)
            if event.key == pygame.K_s:
                self.save_game()
            if event.key == pygame.K_l:
                self.load_game()
            if event.key == pygame.K_t:
                self.show_stats = not self.show_stats

    def _handle_upgrades_click(self, mx, my):
        # find which upgrade clicked
        w = int(self.width*0.8)
        h = int(self.height*0.45)
        x = (self.width - w)//2
        y = (self.height - h)//2 + 56
        uy = y
        i = 0
        for up in self.upgrades.values():
            rect = pygame.Rect(x+8, uy, w-16, 48)
            if rect.collidepoint(mx,my):
                if not up.bought and self.cookies >= up.price:
                    self.buy_upgrade(up.id)
                else:
                    # insufficient funds or already bought: maybe show tooltip; we'll just flash particles
                    for _ in range(8):
                        self._spawn_particle(golden=False)
            uy += 56
            i += 1

# -----------------------
# Main loop
# -----------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Advanced Cookie Clicker - Cookie Forge")
    game = CookieGame(screen)

    last_time = time.perf_counter()
    running = True
    while running:
        # delta time
        now = time.perf_counter()
        dt = now - last_time
        last_time = now
        if dt > 1/15:
            dt = 1/15

        # events
        for event in pygame.event.get():
            game.handle_event(event)

        # update game
        game.tick(dt)

        # render
        game.render()

        # cap
        game.clock.tick(FPS)

if __name__ == "__main__":
    main()
