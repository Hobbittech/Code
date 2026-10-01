import tiles
ITEM_SWORD=100; ITEM_PICKAXE=101
class Inventory:
    def __init__(self):
        self.hotbar=[(tiles.DIRT,128),(tiles.GRASS,128),(tiles.STONE,64),(tiles.WOOD,64),(tiles.TORCH,32),(ITEM_SWORD,1),(ITEM_PICKAXE,1),(tiles.COAL_ORE,8),(tiles.IRON_ORE,4)]
        self.selected=0; self.creative=False
    def select(self,idx):
        if 0<=idx<len(self.hotbar): self.selected=idx
    def selected_id(self): return self.hotbar[self.selected][0]
    def remove_one_selected(self):
        if self.creative: return True
        tid,cnt=self.hotbar[self.selected]
        if cnt>0: self.hotbar[self.selected]=(tid,cnt-1); return True
        return False
    def add(self,id,amount=1):
        for i,(tid,cnt) in enumerate(self.hotbar):
            if tid==id: self.hotbar[i]=(tid,cnt+amount); return True
        return False
