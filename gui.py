import tkinter as tk
from scholarly import scholarly as sch
from scholarly import ProxyGenerator
from grafocitazioni import *

def search():
    paper_dict=sch.search_single_pub(e.get())
    paper=Paper(paper_dict,50,50)
    drawPapers()

def mouseClick(e):
    for p in getAllPapers():
        if (e.x>p.x and e.x<p.x+50 and e.y>p.y and e.y<p.y+50):
            print("Ho cliccato su", p.title)
            cited=sch.citedby(p.dict)
            for i in range(5):
                c=next(cited)
                p.addCite(c['bib']['venue'],Paper(c,p.x+80,p.y+25+i*60))
            drawPapers()
            

def drawPapers():
    for p in getAllPapers():
        cs.create_oval(p.x,p.y,p.x+32,p.y+32)
        cs.create_text(p.x+16,p.y+42,text=p.title,font="Tahoma 12")
        for tag, c in p.cites:
            cs.create_line(p.x+32, p.y+16, c.x, c.y+16, arrow=tk.LAST)
    
window = tk.Tk()
window.geometry("800x600")
window.title("Scholar!")

tk.Button(window,text="Cerca",command=search).place(x=150,y=0)
e=tk.Entry(window)
e.place(x=2,y=2)
cs=tk.Canvas(window, bg="white", width=800, height=560)
cs.place(x=0,y=35)
cs.bind('<Button-1>',mouseClick)

pg = ProxyGenerator()
pg.FreeProxies()
#sch.use_proxy(pg)

drawPapers()
tk.mainloop()
