from pathlib import Path
ASSETS = Path(__file__).parent / 'assets' / 'tiles'
AIR=0; GRASS=1; DIRT=2; STONE=3; SAND=4; WATER=5; WOOD=6; TORCH=12; COAL_ORE=20; IRON_ORE=19; GOLD_ORE=18
TILE_NAME={0:'air',1:'grass',2:'dirt',3:'stone',4:'sand',5:'water',6:'wood',12:'torch',18:'gold_ore',19:'iron_ore',20:'coal_ore'}
TILE_SOLID={1:True,2:True,3:True,4:True,5:False,6:True,12:False,18:True,19:True,20:True}
TILE_HARDNESS={1:0.8,2:1.0,3:3.0,4:0.9,5:0.2,6:1.2,12:0.2,18:5.0,19:4.5,20:3.5}
TILE_SPRITE={tid:ASSETS/f"{name}.png" for tid,name in TILE_NAME.items()}

