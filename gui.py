import tkinter as tk
from scholarly import scholarly as sch
from scholarly import ProxyGenerator
from grafocitazioni import *

def search():
    paper_dict=sch.search_single_pub(e.get())
    paper=Paper(paper_dict)
    drawPapers()

def mouseClick(e):
    for p in getAllPapers():
        if (e.x>p.x and e.x<p.x+50 and e.y>p.y and e.y<p.y+50):
            print("Ho cliccato su", p.title)
            cited=sch.citedby(p.dict)
            for i in range(5):
                c=next(cited)
                p.addCite(c['bib']['venue'],Paper(c,p.x+50,p.y+i*50))
            drawPapers()
            

def drawPapers():
    for p in getAllPapers():
        cs.create_oval(p.x,p.y,p.x+50,p.y+50)
        cs.create_text(p.x+25,p.y+25,text=p.title,font="Times 12")
        for tag, c in p.cites:
            cs.create_line(p.x, p.y, c.x, c.y, arrow=tk.LAST)
    
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
pg.get_next_proxy()
sch.use_proxy(pg)

drawPapers()
tk.mainloop()
