"""
Clickable Cookie Clicker Game using Tkinter

This version uses Python's built-in Tkinter library (no extra installs needed).
It provides a GUI with clickable buttons for clicking the cookie and buying upgrades.
Real-time CPS updates cookies automatically.

Run: python cookie_clicker_game.py

"""

import tkinter as tk
from tkinter import messagebox
import time
import json
from pathlib import Path

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

class CookieClickerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Cookie Clicker")
        self.cookies = 0.0
        self.total_cookies = 0.0
        self.click_power = 1.0
        self.ascend_points = 0
        self.ascend_multiplier = 1.0
        self.shop = []
        self.make_shop()
        self.load_game()

        self.last_update = time.time()

        # GUI Elements
        self.cookie_label = tk.Label(master, text="Cookies: 0", font=("Arial", 20))
        self.cookie_label.pack(pady=10)

        self.click_button = tk.Button(master, text="Click Cookie", font=("Arial", 20), command=self.click_cookie, width=20, height=2)
        self.click_button.pack(pady=10)

        self.status_label = tk.Label(master, text=self.status_text(), font=("Arial", 14))
        self.status_label.pack(pady=10)

        self.shop_frame = tk.Frame(master)
        self.shop_frame.pack(pady=10)
        self.make_shop_buttons()

        self.save_button = tk.Button(master, text="Save", command=self.save_game)
        self.save_button.pack(side="left", padx=10)
        self.load_button = tk.Button(master, text="Load", command=self.load_game)
        self.load_button.pack(side="left", padx=10)
        self.ascend_button = tk.Button(master, text="Ascend", command=self.ascend)
        self.ascend_button.pack(side="left", padx=10)

        self.update_loop()

    def make_shop(self):
        self.shop = [
            ShopItem('cursor', "Cursor", 15, 0.1, "Automatically clicks for you."),
            ShopItem('grandma', "Grandma", 100, 1.0, "Bakes cookies passively."),
            ShopItem('farm', "Farm", 1100, 8.0, "Cookie crop fields."),
            ShopItem('mine', "Mine", 12000, 47.0, "Excavates cookie ore."),
        ]

    def make_shop_buttons(self):
        for widget in self.shop_frame.winfo_children():
            widget.destroy()
        for it in self.shop:
            btn = tk.Button(self.shop_frame, text=f"{it.name} (Lvl {it.level}) - Cost: {it.cost}", command=lambda i=it: self.buy(i), width=30)
            btn.pack(pady=2)

    def status_text(self):
        return f"Cookies: {int(self.cookies)} | Total: {int(self.total_cookies)} | CPS: {self.cps():.1f} | Ascend Points: {self.ascend_points} (x{self.ascend_multiplier:.2f})"

    def cps(self):
        return sum(it.cps * it.level for it in self.shop) * self.ascend_multiplier

    def update_cookies(self):
        now = time.time()
        elapsed = now - self.last_update
        if elapsed > 0:
            earned = self.cps() * elapsed
            self.cookies += earned
            self.total_cookies += earned
            self.last_update = now

    def click_cookie(self):
        self.update_cookies()
        gained = self.click_power * self.ascend_multiplier
        self.cookies += gained
        self.total_cookies += gained
        self.update_gui()

    def buy(self, item):
        self.update_cookies()
        if self.cookies >= item.cost:
            self.cookies -= item.cost
            item.buy()
            self.make_shop_buttons()
            self.update_gui()
        else:
            messagebox.showinfo("Not enough cookies", f"You need {item.cost} cookies to buy {item.name}.")

    def ascend(self):
        self.update_cookies()
        gained = int((self.total_cookies / 1_000) ** 0.5)
        if gained > 0:
            self.ascend_points += gained
            self.ascend_multiplier = 1.0 + (self.ascend_points * 0.1)
            self.cookies = 0.0
            self.total_cookies = 0.0
            self.make_shop()
            self.make_shop_buttons()
            self.update_gui()
            messagebox.showinfo("Ascend!", f"You gained {gained} ascend points.")
        else:
            messagebox.showinfo("Cannot Ascend", "Need at least 1,000 total cookies to ascend.")

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
        messagebox.showinfo("Saved", "Game saved successfully.")

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
        self.make_shop_buttons()
        self.update_gui()

    def update_gui(self):
        self.cookie_label.config(text=f"Cookies: {int(self.cookies)}")
        self.status_label.config(text=self.status_text())

    def update_loop(self):
        self.update_cookies()
        self.update_gui()
        self.master.after(100, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    game = CookieClickerGUI(root)
    root.mainloop()