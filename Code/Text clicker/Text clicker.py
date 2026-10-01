import time
import json
from pathlib import Path
import keyboard

SAVE_FILE = Path("cookie_clicker_save.json")

class ShopItem:
    def __init__(self, id, name, base_cost, cps, description, cost_multiplier=1.15):
        self.id = id
        self.name = name
        self.base_cost = base_cost
        self.cps = cps 
        self.level = 0
        self.cost_multiplier = cost_multiplier
        self.description = description
    @property
    def cost(self):
        return int(self.base_cost * (self.cost_multiplier ** self.level))

    def buy(self, qty=1):
        self.level += qty

class CookieClicker:
    def __init__(self):
        self.cookies = 0.0
        self.total_cookies = 0.0
        self.click_power = 1.0      
        self.ascend_points = 0
        self.ascend_multiplier = 1.0
        self.shop = []
        self.make_shop()
        self.load_game()
        self.last_update = time.time()

    def make_shop(self):
        self.shop = [
            ShopItem('cursor', "Cursor", 15, 0.1, "Automatically clicks for you."),
            ShopItem('grandma', "Grandma", 100, 1.0, "Bakes cookies passively."),
            ShopItem('farm', "Farm", 1100, 8.0, "Cookie crop fields."),
            ShopItem('mine', "Mine", 12000, 47.0, "Excavates cookie ore."),
        ]

    @property
    def cps(self):
        return sum(it.cps * it.level for it in self.shop) * self.ascend_multiplier

    def update_cookies(self):
        now = time.time()
        elapsed = now - self.last_update
        if elapsed > 0:
            earned = self.cps * elapsed
            self.cookies += earned
            self.total_cookies += earned
            self.last_update = now

    def click(self):
        self.update_cookies()
        gained = self.click_power * self.ascend_multiplier
        self.cookies += gained
        self.total_cookies += gained
        print(f"You clicked! +{gained:.1f} cookies")

    def setup_hotkeys(self):
        def space_click():
            print("(Space click!) 🍪")
            self.click()
        keyboard.add_hotkey("space", space_click)

    def buy(self, item_id):
        self.update_cookies()
        for it in self.shop:
            if it.id == item_id:
                if self.cookies >= it.cost:
                    self.cookies -= it.cost
                    it.buy()
                    print(f"Bought {it.name}! Now level {it.level}.")
                else:
                    print("Not enough cookies!")
                return
        print("Invalid item ID.")

    def ascend(self):
        self.update_cookies()
        gained = int((self.total_cookies / 1_000) ** 0.5)
        if gained > 0:
            self.ascend_points += gained
            self.ascend_multiplier = 1.0 + (self.ascend_points * 0.1)
            self.cookies = 0.0
            self.total_cookies = 0.0
            self.make_shop()
            print(f"Ascended! Gained {gained} points. Total: {self.ascend_points}")
        else:
            print("Not enough cookies to ascend. Earn at least 1,000 total.")

    def save_game(self):
        self.update_cookies()
        data = {
            'cookies': self.cookies,
            'total_cookies': self.total_cookies,
            'click_power': self.click_power,
            'ascend_points': self.ascend_points,
            'shop': [{ 'id': it.id, 'level': it.level } for it in self.shop]
        }
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f)
        print("Game saved!")

    def load_game(self):
        if not SAVE_FILE.exists():
            return
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
        self.cookies = data.get('cookies', 0.0)
        self.total_cookies = data.get('total_cookies', 0.0)
        self.click_power = data.get('click_power', 1.0)
        self.ascend_points = data.get('ascend_points', 0)
        saved = {s['id']: s['level'] for s in data.get('shop', [])}
        for it in self.shop:
            it.level = saved.get(it.id, 0)
        self.ascend_multiplier = 1.0 + (self.ascend_points * 0.1)
        self.last_update = time.time()
        print("Game loaded!")

    def show_status(self):
        self.update_cookies()
        print("\n--- STATUS ---")
        print(f"Cookies: {self.cookies:.1f}")
        print(f"Total: {self.total_cookies:.1f}")
        print(f"CPS: {self.cps:.1f}")
        print(f"Ascend Points: {self.ascend_points} (x{self.ascend_multiplier:.2f})")
        print("---------------")

    def show_shop(self):
        self.update_cookies()
        print("\n--- SHOP ---")
        for it in self.shop:
            print(f"{it.id}: {it.name} (Lvl {it.level}) | Cost: {it.cost} | +{it.cps} CPS | {it.description}")
        print("-------------")

    def run(self):
        print("Welcome to Cookie Clicker (Text Edition, Real-Time)!\n")
        print("Commands: click, shop, buy <id>, status, ascend, save, load, quit")
        self.setup_hotkeys()
        while True:
            self.update_cookies()
            cmd = input("\n> ")  
            if not cmd:
                continue
            if cmd == "click":
                self.click()
            elif cmd == "shop":
                self.show_shop()
            elif cmd == "buy" and len(cmd) > 1:
                self.buy(cmd[1])
            elif cmd == "status":
                self.show_status()
            elif cmd == "ascend":
                self.ascend()
            elif cmd == "save":
                self.save_game()
            elif cmd == "load":
                self.load_game()
            elif cmd == "quit":
                self.save_game()
                print("Goodbye!")
                break
        

if __name__ == "__main__":
    game = CookieClicker() 
    game.run()