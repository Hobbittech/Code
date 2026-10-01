from tkinter import *

blockx = []
blocky = []
blocklen = []
blockwid = []
blocktype = []
blockname = []
blockcol = []
playerspawn = [0, 0]
mousex = 0
mousey = 0
def createblock(x, y, len, wid, type, name, fill, out):
    global blockx, blocky, blocklen, blockwid, blocktype, blockname, blockcol
    blockx.append(x)
    blocky.append(y)
    blocklen.append(len)
    blockwid.append(wid)
    blocktype.append(type)
    blockname.append(name)
    blockcol.append([fill, out])
def setspawn(x, y):
    global playerspawn
    playerspawn = [x, y]














#edit mode starts here
''' 
possible blocks (in block type):
-  block (fill = None, outline = #000000)
-  danger (fill = None, outline = #000000)
-  water (fill = None, outline = #000000)
-  ladder (fill = None, outline = #000000)
-  enemy (fill = None, outline = #000000)
-  moveblock (fill = #000000, outline = #000000)
-  end (fill = green, outline = #000000)


also, the rules are:
-  the block name should always be different

possible blocks:

-  createblock((x position), (y position), (length), (width), (fill), (outline))
-  setspawn((spawn x), (spawn y))
'''
setspawn(200, 200)

createblock(100, 250, 150, 50, 'Start Block', 'Start Block', 'Turquoise', "#30EDCD")
createblock(801, 267, 100, 100, 'danger', 'danger1', 'red', "#F60909")
createblock(665, 328, 200, 50, 'water', 'water1', 'blue', "#516EB8")
createblock(597, 198, 50, 150, 'ladder', 'ladder1', 'yellow', "#CFC919")
createblock(900, 350, 100, 100, 'enemy', 'enemy1', 'red', "#D60909")
createblock(1200, 400, 150, 50, 'moveblock', 'moveblock1', 'grey', '#808080')
createblock(298, 158, 200, 50, 'block', 'block1', 'black', '#000000')
createblock(1032, 156, 100, 100, 'end', 'end1', 'green', "#00ff44")
#edit mode ends here













w = Tk()
w.geometry('500x500')

def getmousepos():
    mousex = w.winfo_pointerx() - w.winfo_rootx()
    mousey = w.winfo_pointery() - w.winfo_rooty()
    print(mousex, mousey)

c = Canvas(w, width=1350, height=690)
c.pack()

def square(x1, y1, x2, y2, Fill, out):
    c.create_rectangle(x1, y1, x2, y2, outline=out, fill=Fill)

print([blockx, blocky, blocklen, blockwid, blocktype, blockname, blockcol, playerspawn])


while 1:
    c.delete("all")
    square(playerspawn[0], playerspawn[1], playerspawn[0] + 20, playerspawn[1] + 20, None, '#0d00ff')
    for i in range(len(blockname)):
        square(blockx[i],blocky[i],blockx[i] + blocklen[i],blocky[i] + blockwid[i], blockcol[i][0], blockcol[i][1])
    square(5, 5, 1350, 690, None, '#000000')

    getmousepos()
    c.create_text(mousex + 5, mousey - 5, text=f"X: {mousex} Y: {mousey}", font=("Arial", 12), fill="#000000")
    c.update()

w.mainloop()
