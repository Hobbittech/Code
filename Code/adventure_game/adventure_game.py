import sys
import random
def intro():
    print("Welcome to the Epic Adventure!")
    print("You awaken in a stone chamber. There are doors to the north, east, and west.")
    print("Type 'help' at any time for commands.")
    print("Explore, solve puzzles, and survive!")
    print("Made by Felipe Elexpuru!")
    

def help_menu():
    print("\nCommands:")
    print("  north, east, south, west, up, down - Move in a direction")
    print("  inventory - Show your inventory")
    print("  look - Look around the room")
    print("  take [item] - Take an item")
    print("  use [item] - Use an item")
    print("  talk [npc] - Talk to a character")
    print("  health - Show your health")
    print("  quit - Quit the game\n")

def look(room, rooms, inventory):
    print("\n" + rooms[room]['desc'])
    if rooms[room]['items']:
        print("You see: " + ", ".join(rooms[room]['items']))
    if rooms[room].get('enemy') and not rooms[room].get('enemy_defeated', True):
        print("An enemy is here: " + rooms[room]['enemy'])
    if rooms[room].get('npc'):
        print("You see: " + rooms[room]['npc'])
    # Show available exits
    exits = rooms[room]['exits']
    print("Exits: " + ", ".join(exits.keys()))

def show_map(room, rooms):
    print(f"\nYou are in: {room.replace('_', ' ').title()}")
    exits = rooms[room]['exits']
    print("Available directions:")
    for direction, dest in exits.items():
        print(f"  {direction.title()} -> {dest.replace('_', ' ').title()}")

def show_inventory(inventory):
    if inventory:
        print("Inventory: " + ", ".join(inventory))
    else:
        print("Your inventory is empty.")

def show_health(health):
    print(f"Your health: {health}/100")

def take_item(room, rooms, inventory, item):
    if item in rooms[room]['items']:
        inventory.append(item)
        rooms[room]['items'].remove(item)
        print(f"You take the {item}.")
    else:
        print(f"There is no {item} here.")

def use_item(room, rooms, inventory, item, health):
    if item not in inventory:
        print(f"You don't have a {item}.")
        return health
    # Open the chest in east_room with the key
    if room == 'east_room' and item == 'key' and not rooms[room]['chest_open']:
        print("You use the key to unlock the chest! Inside is a sword.")
        rooms[room]['chest_open'] = True
        rooms[room]['items'].append('sword')
        inventory.remove('key')
        return health
    # Healing potion
    if item == 'potion':
        print("You drink the potion and feel better!")
        inventory.remove('potion')
        return min(100, health + 30)
    # Torch for dark rooms
    if rooms[room].get('dark') and item == 'torch':
        print("You light the torch. The room is now visible!")
        rooms[room]['dark'] = False
        return health
    # Key for locked doors
    if rooms[room].get('locked') and item == 'key':
        print("You use the key to unlock the door!")
        rooms[room]['locked'] = False
        inventory.remove('key')
        return health
    # Rope for climbing
    if room == 'cliff_edge' and item == 'rope':
        print("You use the rope to climb down the cliff safely.")
        rooms[room]['exits']['down'] = 'cave_entrance'
        inventory.remove('rope')
        return health
    print("You can't use that here.")
    return health

def talk_npc(room, rooms, inventory):
    npc = rooms[room].get('npc')
    if not npc:
        print("There's no one to talk to here.")
        return
    if npc == 'old man':
        print("Old Man: 'Beware the dragon in the mountain. Take this map to help you.'")
        if 'map' not in inventory:
            inventory.append('map')
            print("You received a map!")
    elif npc == 'merchant':
        print("Merchant: 'I can trade you a potion for a gold coin.'")
        if 'gold coin' in inventory:
            trade = input("Trade gold coin for potion? (yes/no): ").strip().lower()
            if trade == 'yes':
                inventory.remove('gold coin')
                inventory.append('potion')
                print("You receive a potion!")
            else:
                print("Maybe next time.")
    elif npc == 'herbalist':
        print("Herbalist: 'If you bring me herbs, I can make you a healing potion.'")
        if 'herbs' in inventory:
            trade = input("Give herbs to herbalist? (yes/no): ").strip().lower()
            if trade == 'yes':
                inventory.remove('herbs')
                inventory.append('potion')
                print("The herbalist gives you a potion!")
            else:
                print("Maybe next time.")
    elif npc == 'wizard':
        print("Wizard: 'The magic ring will protect you from great danger.'")
    elif npc == 'baker':
        print("Baker: 'Fresh bread for sale! It will give you strength.'")
    elif npc == 'innkeeper':
        print("Innkeeper: 'Welcome, traveler. Rest here for 10 gold coins.'")
    elif npc == 'blacksmith':
        print("Blacksmith: 'I can upgrade your sword if you bring me ore.'")
    elif npc == 'farmer':
        print("Farmer: 'Help! My sheep are lost! Can you find them?'")
    elif npc == 'fairy':
        print("Fairy: 'I can heal your wounds with a touch of my magic.'")
    elif npc == 'king':
        print("King: 'Brave adventurer, can you defeat the dragon and retrieve the dragon egg for me?'")
    elif npc == 'sailor':
        print("Sailor: 'The sea is full of dangers and treasures. Be prepared!'")
    elif npc == 'vendor':
        print("Vendor: 'Rare goods from distant lands! Come and see!'")
    elif npc == 'shipwright':
        print("Shipwright: 'I can repair and upgrade ships. Need timber!'")
    elif npc == 'explorer':
        print("Explorer: 'I got lost in the jungle. Can you help me find my way?'")
    elif npc == 'spirit':
        print("Guardian Spirit: 'Only the worthy may pass. Prove your strength.'")
    elif npc == 'priest':
        print("Priest: 'Seek the blessings of the ancients. They will guide you.'")
    elif npc == 'librarian':
        print("Librarian: 'Knowledge is the key to wisdom. Read the ancient tomes.'")
    elif npc == 'archmage':
        print("Archmage: 'The skies hold many secrets. Explore them with courage.'")
    elif npc == 'queen':
        print("Queen: 'Brave hero, unite the realms and bring peace to our lands.'")
    else:
        print(f"{npc}: 'Hello, traveler.'")

def move(room, direction, rooms):
    if rooms[room].get('locked'):
        print("The door is locked.")
        return room
    if direction in rooms[room]['exits']:
        return rooms[room]['exits'][direction]
    else:
        print("You can't go that way.")
        return room

def enemy_encounter(room, rooms, inventory, health):
    if rooms[room].get('enemy') and not rooms[room].get('enemy_defeated', True):
        print(f"A {rooms[room]['enemy']} attacks!")
        if 'sword' in inventory:
            print(f"You fight the {rooms[room]['enemy']} with your sword and win!")
            rooms[room]['enemy_defeated'] = True
        else:
            print(f"You have no weapon! The {rooms[room]['enemy']} wounds you.")
            health -= 30
            if health <= 0:
                print("You have died. Game over.")
                sys.exit()
            print("You escape back to the previous room.")
            return health, True
    return health, False

def main():
    rooms = {
        'start': {
            'desc': "You are in the starting chamber. Doors lead north, east, and west.",
            'items': [],
            'exits': {'north': 'north_room', 'east': 'east_room', 'west': 'west_room'},
            'enemy': None,
            'enemy_defeated': True
        },
        'north_room': {
            'desc': "A dusty library. Ancient books line the walls. A key lies on a table.",
            'items': ['key'],
            'exits': {'south': 'start', 'north': 'tower', 'east': 'armory'},
            'enemy': None,
            'enemy_defeated': True
        },
        'east_room': {
            'desc': "A small room with a locked chest.",
            'items': [],
            'exits': {'west': 'start', 'east': 'garden'},
            'enemy': None,
            'enemy_defeated': True,
            'chest_open': False
        },
        'west_room': {
            'desc': "A dark room. A goblin blocks the way to a door north.",
            'items': [],
            'exits': {'east': 'start', 'north': 'treasure_room', 'west': 'cliff_edge'},
            'enemy': 'goblin',
            'enemy_defeated': False
        },
        'tower': {
            'desc': "You climb a spiral staircase to a tower. You see a healing potion.",
            'items': ['potion'],
            'exits': {'south': 'north_room', 'up': 'wizard_lab'},
            'enemy': None,
            'enemy_defeated': True
        },
        'wizard_lab': {
            'desc': "A magical laboratory. A wizard is here, mixing potions.",
            'items': ['magic ring'],
            'exits': {'down': 'tower'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'wizard'
        },
        'armory': {
            'desc': "An old armory. You see a sword and a shield.",
            'items': ['sword', 'shield'],
            'exits': {'west': 'north_room'},
            'enemy': None,
            'enemy_defeated': True
        },
        'garden': {
            'desc': "A peaceful garden. There is a locked gate to the north.",
            'items': ['gold coin'],
            'exits': {'west': 'east_room', 'north': 'final_gate', 'east': 'merchant_stall'},
            'enemy': None,
            'enemy_defeated': True
        },
        'merchant_stall': {
            'desc': "A merchant stall. A merchant stands ready to trade.",
            'items': [],
            'exits': {'west': 'garden'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'merchant'
        },
        'treasure_room': {
            'desc': "A room glittering with gold and jewels. You see a rope.",
            'items': ['rope'],
            'exits': {'south': 'west_room'},
            'enemy': None,
            'enemy_defeated': True
        },
        'cliff_edge': {
            'desc': "A steep cliff edge. It's too dangerous to climb down without a rope.",
            'items': [],
            'exits': {'east': 'west_room'},
            'enemy': None,
            'enemy_defeated': True
        },
        'cave_entrance': {
            'desc': "A dark cave entrance. You need a torch to see inside.",
            'items': ['torch'],
            'exits': {'up': 'cliff_edge', 'in': 'deep_cave'},
            'enemy': None,
            'enemy_defeated': True,
            'dark': True
        },
        'deep_cave': {
            'desc': "A deep, dark cave. You sense danger.",
            'items': ['ancient amulet'],
            'exits': {'out': 'cave_entrance'},
            'enemy': 'giant spider',
            'enemy_defeated': False,
            'dark': True
        },
        'final_gate': {
            'desc': "A massive gate blocks your way. You need a shield to pass.",
            'items': [],
            'exits': {'north': 'mountain_path'},
            'enemy': None,
            'enemy_defeated': True,
            'locked': True
        },
        'mountain_path': {
            'desc': "A winding path up the mountain. The air grows cold.",
            'items': [],
            'exits': {'south': 'final_gate', 'up': 'dragon_lair'},
            'enemy': None,
            'enemy_defeated': True
        },
        'dragon_lair': {
            'desc': "A vast cavern. A sleeping dragon lies atop a pile of treasure!",
            'items': ['dragon egg'],
            'exits': {'down': 'mountain_path'},
            'enemy': 'dragon',
            'enemy_defeated': False
        },
        'forest_edge': {
            'desc': "You stand at the edge of a dense forest. A path leads north into the trees.",
            'items': ['herbs'],
            'exits': {'south': 'garden', 'north': 'deep_forest'},
            'enemy': None,
            'enemy_defeated': True
        },
        'deep_forest': {
            'desc': "Tall trees surround you. You hear rustling. A wild boar blocks the path east.",
            'items': [],
            'exits': {'south': 'forest_edge', 'east': 'river_bank', 'west': 'forest_hut'},
            'enemy': 'wild boar',
            'enemy_defeated': False
        },
        'forest_hut': {
            'desc': "A small hut. An herbalist lives here.",
            'items': [],
            'exits': {'east': 'deep_forest'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'herbalist'
        },
        'river_bank': {
            'desc': "A wide river blocks your path. There's a fishing rod here.",
            'items': ['fishing rod'],
            'exits': {'west': 'deep_forest', 'east': 'old_bridge'},
            'enemy': None,
            'enemy_defeated': True
        },
        'old_bridge': {
            'desc': "An old wooden bridge crosses the river. It looks fragile.",
            'items': [],
            'exits': {'west': 'river_bank', 'east': 'ruins'},
            'enemy': None,
            'enemy_defeated': True
        },
        'ruins': {
            'desc': "Ancient ruins. A silver key glints among the stones.",
            'items': ['silver key'],
            'exits': {'west': 'old_bridge', 'north': 'haunted_house'},
            'enemy': None,
            'enemy_defeated': True
        },
        'haunted_house': {
            'desc': "A spooky, abandoned house. You feel a chill. A ghost appears!",
            'items': ['lantern'],
            'exits': {'south': 'ruins', 'up': 'attic'},
            'enemy': 'ghost',
            'enemy_defeated': False
        },
        'attic': {
            'desc': "The attic is dusty and dark. You find a mysterious diary.",
            'items': ['diary'],
            'exits': {'down': 'haunted_house'},
            'enemy': None,
            'enemy_defeated': True
        },
        'secret_tunnel': {
            'desc': "A hidden tunnel beneath the ruins. It's pitch black.",
            'items': [],
            'exits': {'up': 'ruins', 'north': 'underground_lake'},
            'enemy': None,
            'enemy_defeated': True,
            'dark': True
        },
        'underground_lake': {
            'desc': "A vast underground lake. Something shimmers in the water.",
            'items': ['pearl'],
            'exits': {'south': 'secret_tunnel'},
            'enemy': 'giant eel',
            'enemy_defeated': False
        },
        'castle_gate': {
            'desc': "A grand gate blocks the entrance to the castle. Guards stand watch.",
            'items': [],
            'exits': {'south': 'village_square', 'north': 'castle_hall'},
            'enemy': 'guard',
            'enemy_defeated': False
        },
        'village_square': {
            'desc': "A bustling village square. Shops and homes surround you. A baker offers bread.",
            'items': ['bread'],
            'exits': {'north': 'castle_gate', 'east': 'inn', 'west': 'blacksmith', 'south': 'farm'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'baker'
        },
        'inn': {
            'desc': "A cozy inn. The innkeeper greets you. You can rest here to restore health.",
            'items': [],
            'exits': {'west': 'village_square'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'innkeeper'
        },
        'blacksmith': {
            'desc': "A forge glows. The blacksmith can upgrade your sword if you bring him ore.",
            'items': [],
            'exits': {'east': 'village_square'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'blacksmith'
        },
        'farm': {
            'desc': "A peaceful farm. Chickens roam. The farmer needs help finding lost sheep.",
            'items': ['egg'],
            'exits': {'north': 'village_square', 'east': 'meadow'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'farmer'
        },
        'meadow': {
            'desc': "A wide meadow. You see sheep grazing. A wolf lurks nearby.",
            'items': ['wool'],
            'exits': {'west': 'farm', 'east': 'forest_clearing'},
            'enemy': 'wolf',
            'enemy_defeated': False
        },
        'forest_clearing': {
            'desc': "A magical clearing. A fairy offers you a healing flower.",
            'items': ['healing flower'],
            'exits': {'west': 'meadow', 'north': 'enchanted_forest'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'fairy'
        },
        'enchanted_forest': {
            'desc': "Tall glowing trees. A unicorn blocks the path north.",
            'items': ['magic scroll'],
            'exits': {'south': 'forest_clearing', 'north': 'mountain_pass'},
            'enemy': 'unicorn',
            'enemy_defeated': False
        },
        'mountain_pass': {
            'desc': "A steep pass. You see rare ore here.",
            'items': ['rare ore'],
            'exits': {'south': 'enchanted_forest', 'north': 'mines'},
            'enemy': None,
            'enemy_defeated': True
        },
        'mines': {
            'desc': "Dark mines. Goblins and bats lurk. You find gems and ore.",
            'items': ['gem', 'ore'],
            'exits': {'south': 'mountain_pass', 'east': 'deep_mines'},
            'enemy': 'bat',
            'enemy_defeated': False
        },
        'deep_mines': {
            'desc': "The deepest part of the mines. A goblin king guards a treasure chest.",
            'items': ['treasure chest'],
            'exits': {'west': 'mines'},
            'enemy': 'goblin king',
            'enemy_defeated': False
        },
        'castle_hall': {
            'desc': "A grand hall. The king awaits. You must present a gem to enter.",
            'items': [],
            'exits': {'south': 'castle_gate', 'north': 'throne_room'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'king'
        },
        'throne_room': {
            'desc': "The throne room. The king offers you a quest to defeat the dragon and bring back the dragon egg.",
            'items': [],
            'exits': {'south': 'castle_hall'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'king'
        },
        'port_town': {
            'desc': "A bustling port town. Sailors and merchants fill the docks. Ships can take you to distant lands.",
            'items': ['map fragment'],
            'exits': {'north': 'beach', 'east': 'market', 'west': 'shipyard', 'south': 'sea'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'sailor'
        },
        'beach': {
            'desc': "A sandy beach. You find shells and driftwood. A pirate lurks nearby.",
            'items': ['shell', 'driftwood'],
            'exits': {'south': 'port_town', 'east': 'cliffside'},
            'enemy': 'pirate',
            'enemy_defeated': False
        },
        'market': {
            'desc': "A lively market. Vendors sell rare goods. You can buy or trade items.",
            'items': ['fruit', 'spices'],
            'exits': {'west': 'port_town'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'vendor'
        },
        'shipyard': {
            'desc': "A shipyard. You can repair or upgrade your ship. The shipwright needs timber.",
            'items': ['timber'],
            'exits': {'east': 'port_town'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'shipwright'
        },
        'sea': {
            'desc': "The open sea. You can sail to new continents or islands. Beware sea monsters!",
            'items': [],
            'exits': {'north': 'port_town', 'east': 'island', 'south': 'deep_sea'},
            'enemy': 'kraken',
            'enemy_defeated': False
        },
        'island': {
            'desc': "A mysterious island. Ancient ruins and hidden treasures await.",
            'items': ['ancient coin', 'idol'],
            'exits': {'west': 'sea', 'north': 'jungle'},
            'enemy': 'giant crab',
            'enemy_defeated': False
        },
        'jungle': {
            'desc': "A dense jungle. Exotic plants and animals. A lost explorer needs help.",
            'items': ['herbs', 'banana'],
            'exits': {'south': 'island', 'east': 'temple'},
            'enemy': 'snake',
            'enemy_defeated': False,
            'npc': 'explorer'
        },
        'temple': {
            'desc': "An ancient temple. Solve puzzles to unlock secrets. A guardian spirit watches.",
            'items': ['temple key', 'gemstone'],
            'exits': {'west': 'jungle', 'north': 'altar'},
            'enemy': 'spirit',
            'enemy_defeated': False
        },
        'altar': {
            'desc': "A sacred altar. Place the gemstone to reveal a hidden passage.",
            'items': [],
            'exits': {'south': 'temple', 'down': 'underground_chamber'},
            'enemy': None,
            'enemy_defeated': True
        },
        'underground_chamber': {
            'desc': "A dark chamber beneath the altar. Solve riddles to escape.",
            'items': ['riddle scroll'],
            'exits': {'up': 'altar', 'east': 'catacombs'},
            'enemy': 'shadow',
            'enemy_defeated': False
        },
        'catacombs': {
            'desc': "Twisting catacombs. Skeletons and traps. Find the exit to the surface.",
            'items': ['bone', 'amulet'],
            'exits': {'west': 'underground_chamber', 'up': 'graveyard'},
            'enemy': 'skeleton',
            'enemy_defeated': False
        },
        'graveyard': {
            'desc': "A haunted graveyard. Ghosts and zombies roam. Find the magic lantern to dispel darkness.",
            'items': ['magic lantern'],
            'exits': {'down': 'catacombs', 'north': 'church'},
            'enemy': 'zombie',
            'enemy_defeated': False
        },
        'church': {
            'desc': "An old church. The priest offers blessings and quests.",
            'items': ['blessing'],
            'exits': {'south': 'graveyard', 'east': 'library'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'priest'
        },
        'library': {
            'desc': "A vast library. Ancient tomes and secrets. Find the forbidden book.",
            'items': ['forbidden book'],
            'exits': {'west': 'church', 'north': 'wizard_tower'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'librarian'
        },
        'wizard_tower': {
            'desc': "A tall tower. The archmage offers powerful spells and quests.",
            'items': ['spell scroll'],
            'exits': {'south': 'library', 'up': 'sky_island'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'archmage'
        },
        'sky_island': {
            'desc': "A floating island in the clouds. Rare treasures and magical creatures.",
            'items': ['cloud crystal'],
            'exits': {'down': 'wizard_tower', 'east': 'sky_palace'},
            'enemy': 'griffin',
            'enemy_defeated': False
        },
        'sky_palace': {
            'desc': "A palace in the sky. The queen offers a quest to unite the realms.",
            'items': ['royal seal'],
            'exits': {'west': 'sky_island', 'up': 'celestial_gate'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'queen'
        },
        # --- New Areas Begin ---
        'celestial_gate': {
            'desc': "A shimmering gate to the stars. Only those with the royal seal may pass.",
            'items': [],
            'exits': {'down': 'sky_palace', 'up': 'starship_dock'},
            'enemy': None,
            'enemy_defeated': True,
            'locked': True
        },
        'starship_dock': {
            'desc': "A dock floating in space. A starship awaits, its captain beckoning.",
            'items': ['star map'],
            'exits': {'down': 'celestial_gate', 'aboard': 'starship'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'starship captain'
        },
        'starship': {
            'desc': "A sleek starship. You can travel to distant planets or return to the dock.",
            'items': [],
            'exits': {'dock': 'starship_dock', 'planet': 'alien_planet', 'moon': 'lunar_base'},
            'enemy': None,
            'enemy_defeated': True
        },
        'alien_planet': {
            'desc': "A strange alien world. Exotic plants and creatures abound.",
            'items': ['alien crystal', 'strange fruit'],
            'exits': {'starship': 'starship', 'cave': 'alien_cave'},
            'enemy': 'alien beast',
            'enemy_defeated': False
        },
        'alien_cave': {
            'desc': "A glowing cave filled with crystals. A puzzle blocks the way forward.",
            'items': ['crystal shard'],
            'exits': {'out': 'alien_planet', 'deep': 'ancient_vault'},
            'enemy': None,
            'enemy_defeated': True,
            'puzzle': True
        },
        'ancient_vault': {
            'desc': "A vault of ancient alien technology. A guardian robot stands watch.",
            'items': ['ancient artifact'],
            'exits': {'back': 'alien_cave'},
            'enemy': 'guardian robot',
            'enemy_defeated': False
        },
        'lunar_base': {
            'desc': "A base on the moon. Scientists study rare minerals here.",
            'items': ['moon rock'],
            'exits': {'starship': 'starship', 'lab': 'lunar_lab'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'scientist'
        },
        'lunar_lab': {
            'desc': "A high-tech lab. You can craft new items using moon rock and alien crystals.",
            'items': [],
            'exits': {'base': 'lunar_base'},
            'enemy': None,
            'enemy_defeated': True,
            'crafting': True
        },
        # --- Underwater Expansion ---
        'deep_sea': {
            'desc': "The ocean depths. Strange lights flicker in the darkness.",
            'items': ['pearl', 'ancient coin'],
            'exits': {'north': 'sea', 'down': 'sunken_ruins'},
            'enemy': 'sea serpent',
            'enemy_defeated': False
        },
        'sunken_ruins': {
            'desc': "Ruins of a lost city beneath the waves. A puzzle door blocks the treasure vault.",
            'items': ['coral key'],
            'exits': {'up': 'deep_sea', 'vault': 'treasure_vault'},
            'enemy': None,
            'enemy_defeated': True,
            'puzzle': True
        },
        'treasure_vault': {
            'desc': "A vault filled with sunken treasure. A giant crab guards the hoard!",
            'items': ['crown', 'jeweled chalice'],
            'exits': {'ruins': 'sunken_ruins'},
            'enemy': 'giant crab',
            'enemy_defeated': False
        },
        # --- Volcano & Ice Regions ---
        'volcano_base': {
            'desc': "The base of a smoldering volcano. Lava flows block some paths.",
            'items': ['obsidian shard'],
            'exits': {'up': 'volcano_peak', 'cave': 'lava_cave'},
            'enemy': 'fire lizard',
            'enemy_defeated': False
        },
        'volcano_peak': {
            'desc': "The peak of the volcano. A fire dragon sleeps atop a pile of gems.",
            'items': ['fire gem'],
            'exits': {'down': 'volcano_base'},
            'enemy': 'fire dragon',
            'enemy_defeated': False
        },
        'lava_cave': {
            'desc': "A cave filled with molten lava. Special boots are needed to cross.",
            'items': ['lava boots'],
            'exits': {'base': 'volcano_base'},
            'enemy': None,
            'enemy_defeated': True
        },
        'ice_fields': {
            'desc': "A frozen wasteland. Blizzards make travel dangerous.",
            'items': ['ice crystal'],
            'exits': {'south': 'mountain_pass', 'cave': 'ice_cave'},
            'enemy': 'ice wolf',
            'enemy_defeated': False
        },
        'ice_cave': {
            'desc': "A glittering cave of ice. A puzzle blocks a hidden chamber.",
            'items': ['frost key'],
            'exits': {'fields': 'ice_fields', 'chamber': 'frozen_chamber'},
            'enemy': None,
            'enemy_defeated': True,
            'puzzle': True
        },
        'frozen_chamber': {
            'desc': "A chamber of eternal ice. A frost giant guards a magical staff.",
            'items': ['frost staff'],
            'exits': {'cave': 'ice_cave'},
            'enemy': 'frost giant',
            'enemy_defeated': False
        },
        # --- Jungle & Temple Expansion ---
        'lost_jungle': {
            'desc': "A dense, mysterious jungle. Ancient ruins are hidden among the trees.",
            'items': ['jungle vine'],
            'exits': {'north': 'jungle_temple', 'south': 'jungle'},
            'enemy': 'panther',
            'enemy_defeated': False
        },
        'jungle_temple': {
            'desc': "A temple overgrown with vines. Solve riddles to unlock the inner sanctum.",
            'items': ['temple idol'],
            'exits': {'south': 'lost_jungle', 'sanctum': 'inner_sanctum'},
            'enemy': None,
            'enemy_defeated': True,
            'puzzle': True
        },
        'inner_sanctum': {
            'desc': "The heart of the temple. A serpent god statue holds a legendary blade.",
            'items': ['serpent blade'],
            'exits': {'temple': 'jungle_temple'},
            'enemy': 'serpent guardian',
            'enemy_defeated': False
        },
        # --- More Continents & Islands ---
        'desert_oasis': {
            'desc': "A lush oasis in the middle of a vast desert. Merchants gather here.",
            'items': ['water flask'],
            'exits': {'north': 'desert_ruins', 'south': 'sand_dunes'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'desert merchant'
        },
        'desert_ruins': {
            'desc': "Crumbling ruins half-buried in sand. A mummy guards a golden scarab.",
            'items': ['golden scarab'],
            'exits': {'south': 'desert_oasis'},
            'enemy': 'mummy',
            'enemy_defeated': False
        },
        'sand_dunes': {
            'desc': "Endless dunes stretch to the horizon. Sandstorms can strike at any time.",
            'items': ['sandstone'],
            'exits': {'north': 'desert_oasis'},
            'enemy': 'sand worm',
            'enemy_defeated': False
        },
        # --- End of Expansion ---
        'forgotten_kingdom': {
            'desc': "Ruins of an ancient kingdom, lost to time. Statues and broken towers loom.",
            'items': ['ancient scroll'],
            'exits': {'south': 'mountain_pass', 'east': 'crystal_palace', 'west': 'shadow_forest'},
            'enemy': 'phantom knight',
            'enemy_defeated': False
        },
        'crystal_palace': {
            'desc': "A palace of shimmering crystal. Light refracts in dazzling colors. A riddle blocks the throne room.",
            'items': ['crystal crown'],
            'exits': {'west': 'forgotten_kingdom', 'throne': 'crystal_throne'},
            'enemy': None,
            'enemy_defeated': True,
            'puzzle': True
        },
        'crystal_throne': {
            'desc': "The throne room glows with magic. The Crystal Queen offers a quest to restore the kingdom.",
            'items': ['royal decree'],
            'exits': {'palace': 'crystal_palace'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'crystal queen'
        },
        'shadow_forest': {
            'desc': "A dark, twisted forest. Shadows move between the trees. Only a lantern can reveal the safe path.",
            'items': ['shadow root'],
            'exits': {'east': 'forgotten_kingdom', 'north': 'abyssal_gate'},
            'enemy': 'shadow beast',
            'enemy_defeated': False
        },
        'abyssal_gate': {
            'desc': "A swirling portal to the Abyss. Only those with the royal decree may enter.",
            'items': [],
            'exits': {'south': 'shadow_forest', 'in': 'abyssal_realm'},
            'enemy': None,
            'enemy_defeated': True,
            'locked': True
        },
        'abyssal_realm': {
            'desc': "A realm of darkness and chaos. The air crackles with energy. A demon lord rules here.",
            'items': ['abyssal gem'],
            'exits': {'out': 'abyssal_gate', 'throne': 'demon_throne'},
            'enemy': 'demon lord',
            'enemy_defeated': False
        },
        'demon_throne': {
            'desc': "A throne of bones and fire. The Demon Lord challenges you to a riddle contest.",
            'items': ['demon crown'],
            'exits': {'realm': 'abyssal_realm'},
            'enemy': None,
            'enemy_defeated': True,
            'puzzle': True
        },
        'ancient_portal': {
            'desc': "A mysterious portal. Step through to travel to the past or future.",
            'items': ['time crystal'],
            'exits': {'present': 'forgotten_kingdom', 'past': 'kingdom_past', 'future': 'kingdom_future'},
            'enemy': None,
            'enemy_defeated': True
        },
        'kingdom_past': {
            'desc': "The kingdom in its golden age. Knights and nobles fill the streets.",
            'items': ['old coin'],
            'exits': {'portal': 'ancient_portal'},
            'enemy': 'rogue knight',
            'enemy_defeated': False
        },
        'kingdom_future': {
            'desc': "The kingdom in ruins, overrun by machines. Robots patrol the streets.",
            'items': ['circuit board'],
            'exits': {'portal': 'ancient_portal'},
            'enemy': 'war robot',
            'enemy_defeated': False
        },
        'guild_city': {
            'desc': "A bustling city run by powerful guilds. Join a guild for special quests and rewards.",
            'items': ['guild badge'],
            'exits': {'north': 'arena', 'east': 'market_district', 'west': 'docks', 'south': 'slums'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'guild master'
        },
        'arena': {
            'desc': "A grand arena. Compete in tournaments for fame and prizes.",
            'items': ['trophy'],
            'exits': {'south': 'guild_city'},
            'enemy': 'champion',
            'enemy_defeated': False
        },
        'market_district': {
            'desc': "A lively market. Rare goods and black market items are sold here.",
            'items': ['mysterious box'],
            'exits': {'west': 'guild_city'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'black market dealer'
        },
        'docks': {
            'desc': "Busy docks. Ships depart for distant lands. Smugglers lurk in the shadows.",
            'items': ['contraband'],
            'exits': {'east': 'guild_city'},
            'enemy': 'smuggler',
            'enemy_defeated': False
        },
        'slums': {
            'desc': "The city's poorest district. Gangs control the streets.",
            'items': ['lockpick'],
            'exits': {'north': 'guild_city'},
            'enemy': 'gang leader',
            'enemy_defeated': False
        },
        'fae_glade': {
            'desc': "A mystical glade where the fae gather. Magic is strong here.",
            'items': ['fae dust'],
            'exits': {'south': 'enchanted_forest', 'portal': 'fae_court'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'fae queen'
        },
        'fae_court': {
            'desc': "The court of the fae. Tricksters and spirits play games of wit.",
            'items': ['fae crown'],
            'exits': {'glade': 'fae_glade'},
            'enemy': 'fae trickster',
            'enemy_defeated': False
        },
        'airship_dock': {
            'desc': "A floating dock for airships. Pilots and merchants gather here.",
            'items': ['airship ticket'],
            'exits': {'down': 'port_town', 'aboard': 'airship'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'airship pilot'
        },
        'airship': {
            'desc': "A grand airship. Travel to sky islands, distant continents, or return to the dock.",
            'items': [],
            'exits': {'dock': 'airship_dock', 'sky_island': 'sky_island', 'continent': 'new_continent'},
            'enemy': None,
            'enemy_defeated': True
        },
        'new_continent': {
            'desc': "A vast, unexplored continent. New adventures await!",
            'items': ['mysterious artifact'],
            'exits': {'airship': 'airship', 'jungle': 'lost_jungle', 'desert': 'desert_oasis'},
            'enemy': 'giant ape',
            'enemy_defeated': False
        },
        # --- Further Expansion: New Realms, Cities, and Quests ---
        'mountain_village': {
            'desc': "A remote village high in the mountains. The villagers speak of a hidden monastery.",
            'items': ['mountain herb'],
            'exits': {'south': 'mountain_pass', 'up': 'monastery_path'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'village elder'
        },
        'monastery_path': {
            'desc': "A steep path leads to an ancient monastery. Snow falls gently.",
            'items': [],
            'exits': {'down': 'mountain_village', 'up': 'monastery'},
            'enemy': 'snow leopard',
            'enemy_defeated': False
        },
        'monastery': {
            'desc': "An ancient monastery. Monks train in martial arts and meditation.",
            'items': ['monk staff'],
            'exits': {'down': 'monastery_path', 'garden': 'zen_garden'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'abbot'
        },
        'zen_garden': {
            'desc': "A tranquil garden. Riddles are inscribed on stone tablets.",
            'items': ['wisdom scroll'],
            'exits': {'monastery': 'monastery'},
            'enemy': None,
            'enemy_defeated': True,
            'puzzle': True
        },
        'pirate_cove': {
            'desc': "A hidden cove. Pirates gather around a bonfire, plotting their next raid.",
            'items': ['pirate map'],
            'exits': {'sea': 'sea', 'cave': 'smugglers_cave'},
            'enemy': 'pirate captain',
            'enemy_defeated': False
        },
        'smugglers_cave': {
            'desc': "A dark cave filled with stolen goods. Traps and puzzles abound.",
            'items': ['smuggled jewel'],
            'exits': {'cove': 'pirate_cove'},
            'enemy': None,
            'enemy_defeated': True,
            'puzzle': True
        },
        'undersea_palace': {
            'desc': "A palace beneath the waves. The Sea King rules here.",
            'items': ['trident'],
            'exits': {'up': 'deep_sea', 'throne': 'sea_throne'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'sea king'
        },
        'sea_throne': {
            'desc': "The Sea King's throne room. A giant octopus guards the royal vault.",
            'items': ['pearl crown'],
            'exits': {'palace': 'undersea_palace'},
            'enemy': 'giant octopus',
            'enemy_defeated': False
        },
        'academy_entrance': {
            'desc': "The entrance to a grand magical academy. Students and teachers bustle about.",
            'items': ['academy pass'],
            'exits': {'city': 'guild_city', 'hall': 'academy_hall'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'gatekeeper'
        },
        'academy_hall': {
            'desc': "The main hall of the academy. Magical experiments are underway.",
            'items': ['spellbook'],
            'exits': {'entrance': 'academy_entrance', 'library': 'academy_library'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'headmaster'
        },
        'academy_library': {
            'desc': "A vast library of magical tomes. Ancient secrets are hidden here.",
            'items': ['ancient tome'],
            'exits': {'hall': 'academy_hall'},
            'enemy': 'enchanted book',
            'enemy_defeated': False
        },
        'hidden_city': {
            'desc': "A city hidden by powerful magic. Only those with a special amulet may enter.",
            'items': ['hidden amulet'],
            'exits': {'forest': 'enchanted_forest', 'plaza': 'hidden_plaza'},
            'enemy': None,
            'enemy_defeated': True,
            'locked': True
        },
        'hidden_plaza': {
            'desc': "The heart of the hidden city. Mystics and sages gather here.",
            'items': ['mystic orb'],
            'exits': {'city': 'hidden_city'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'sage'
        },
        # --- End of Further Expansion ---
        # --- Even More Expansion: Islands, Towers, Dwarves, Elves, and Sky Cities ---
        'haunted_isle': {
            'desc': "A fog-shrouded island haunted by restless spirits. Strange lights flicker at night.",
            'items': ['ghost lantern'],
            'exits': {'sea': 'sea', 'tower': 'witch_tower'},
            'enemy': 'wraith',
            'enemy_defeated': False
        },
        'witch_tower': {
            'desc': "A crooked tower rising from the mist. A witch brews potions inside.",
            'items': ['witch hat'],
            'exits': {'isle': 'haunted_isle', 'lab': 'witch_lab'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'witch'
        },
        'witch_lab': {
            'desc': "A laboratory filled with bubbling cauldrons and magical ingredients.",
            'items': ['magic potion'],
            'exits': {'tower': 'witch_tower'},
            'enemy': 'animated broom',
            'enemy_defeated': False
        },
        'dwarven_mines': {
            'desc': "Deep mines carved by dwarves. Gems and precious metals glint in the walls.",
            'items': ['dwarven axe'],
            'exits': {'mountain': 'mountain_pass', 'forge': 'dwarven_forge'},
            'enemy': 'stone golem',
            'enemy_defeated': False
        },
        'dwarven_forge': {
            'desc': "A blazing forge. Dwarven smiths craft legendary weapons here.",
            'items': ['forged blade'],
            'exits': {'mines': 'dwarven_mines'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'dwarven smith'
        },
        'elven_forest': {
            'desc': "A serene forest of towering trees and glowing flowers. Elves watch from the shadows.",
            'items': ['elven bow'],
            'exits': {'meadow': 'meadow', 'village': 'elven_village'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'elven ranger'
        },
        'elven_village': {
            'desc': "A hidden village in the treetops. Elven elders offer wisdom and quests.",
            'items': ['elven amulet'],
            'exits': {'forest': 'elven_forest'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'elven elder'
        },
        'sky_city': {
            'desc': "A city floating among the clouds. Airships and sky bridges connect the towers.",
            'items': ['sky medal'],
            'exits': {'airship': 'airship', 'tower': 'sky_tower'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'sky mayor'
        },
        'sky_tower': {
            'desc': "The tallest tower in the sky city. A wise oracle lives at the top.",
            'items': ['oracle gem'],
            'exits': {'city': 'sky_city'},
            'enemy': None,
            'enemy_defeated': True,
            'npc': 'oracle'
        },
        # --- End of Even More Expansion ---
    }

    inventory = []
    health = 100
    room = 'start'
    print()
    intro()
    look(room, rooms, inventory)

    while True:
        command = input("\n> ").strip().lower()
        if command == 'help':
            help_menu()
        elif command == 'look':
            look(room, rooms, inventory)
        elif command == 'map':
            show_map(room, rooms)
        elif command == 'inventory':
            show_inventory(inventory)
        elif command == 'health':
            show_health(health)
        elif command.startswith('take '):
            item = command[5:]
            take_item(room, rooms, inventory, item)
        elif command.startswith('use '):
            item = command[4:]
            health = use_item(room, rooms, inventory, item, health)
        elif command.startswith('talk '):
            talk_npc(room, rooms, inventory)
        elif command in ['north', 'east', 'south', 'west', 'up', 'down', 'in', 'out']:
            # Check for enemy
            health, retreated = enemy_encounter(room, rooms, inventory, health)
            if retreated:
                room = 'start'
                look(room, rooms, inventory)
                continue
            next_room = move(room, command, rooms)
            if next_room != room:
                room = next_room
                look(room, rooms, inventory)
                # Show available exits after moving
                exits = rooms[room]['exits']
                print("Exits: " + ", ".join(exits.keys()))
                # Special: final gate
                if room == 'final_gate':
                    if 'shield' in inventory:
                        print("You raise your shield and pass through the gate.")
                        rooms[room]['locked'] = False
                    else:
                        print("You need a shield to pass the gate. You return to the garden.")
                        room = 'garden'
                # Special: dragon encounter
                if room == 'dragon_lair' and not rooms[room]['enemy_defeated']:
                    print("The dragon awakens! You must have the magic ring to survive.")
                    if 'magic ring' in inventory:
                        print("The ring glows and protects you. The dragon flees!")
                        rooms[room]['enemy_defeated'] = True
                    else:
                        print("The dragon breathes fire! You are burned.")
                        health -= 100
                        if health <= 0:
                            print("You have died. Game over.")
                            sys.exit()
                        room = 'mountain_path'
        elif command == 'quit':
            print("Thanks for playing!")
            sys.exit()
        else:
            print("I don't understand that command. Type 'help' for a list of commands.")

if __name__ == "__main__":
    main()
