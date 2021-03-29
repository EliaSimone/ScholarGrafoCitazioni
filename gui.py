import tkinter as tk
from tkinter import ttk
#from scholarly import scholarly as sch
#from scholarly import ProxyGenerator
#from fp.fp import FreeProxy
import fakescholarly as sch
import grafocitazioni as gc
#import re

def search():
    paper_dict=sch.search_single_pub(e.get())
    gc.Paper.createUnique(paper_dict)
    drawPapers()
    sr=setScrollRegion()
    drawGrid(sr)
    cs.tag_lower('grid')

def mouseClick(e):
    #get pos relativa
    x = cs.canvasx(e.x)
    y = cs.canvasy(e.y)
    global selected

    """
    for p in gc.getAllPapers():
        if p.checkPoint(x, y):
            print("Ho cliccato su", p.title)
            selected=p
            break
    """
    
    if hover:
        print("Ho cliccato su", hover.title)
        selected=hover

        autori=''
        for a in selected.dict['bib']['author']:
            autori+=a+', '
                    
        l_title['text']='Titolo: '+selected.title
        l_author['text']='Autori: '+autori[:-2]
        l_year['text']='Anno: '+selected.dict['bib']['pub_year']
        l_venue['text']='Venue: '+selected.dict['bib']['venue']
        l_abstr['text']='Abstract: '+selected.dict['bib']['abstract']
        paperFrame.tkraise()
    else:
        for p in gc.getAllPapers():
            for c in p.cites.values():
                if c.checkPoint(x,y):
                    print('ho cliccato su un arco')
                    selected=c
                    cb_tag.set('<vuoto>' if c.tag=='' else c.tag)
                    cb_colors.current(0)
                    citFrame.tkraise()
                    break
            else:
                continue
            break
    tooltip.tkraise()

def mouseMove(e):
    #get pos relativa
    x = cs.canvasx(e.x)
    y = cs.canvasy(e.y)

    global hover
    
    for p in gc.getAllPapers():
        if p.checkPoint(x, y):
            if not hover is p:
                hover=p
                tooltip.place(x=cs.winfo_x()+e.x+p.x-x+35, y=cs.winfo_y()+e.y+p.y-y+35)
                text=p.title+'\nauthors: '
                for a in p.dict['bib']['author']:
                    text+=a+', '
                text=text[:-2]
                text+='\nyear: '+p.dict['bib']['pub_year']
                text+='\nvenue: '+p.dict['bib']['venue']
                text+='\nabstract: '+p.dict['bib']['abstract']
                tooltip['text']=text
            break
    else:
        if hover:
            tooltip.place_forget()
            hover=None

def mouseLeave(e):
    global hover
    if hover:
            tooltip.place_forget()
            hover=None

def citedbyClick():
    cited=sch.citedby(selected.dict)
    for c in cited:
        selected.addCite(gc.Paper.createUnique(c))
        
    drawPapers()
    sr=setScrollRegion()
    drawGrid(sr)
    cs.tag_lower('grid')

def onSizeChanged(e):
    sr=setScrollRegion()
    drawGrid(sr)
    cs.tag_lower('grid')

def drawPapers():
    cs.delete('grafo')
    
    for p in gc.getAllPapers():
        for c in p.cites.values():
            cs.create_line(c.x1, c.y1, c.x2, c.y2, arrow=tk.LAST, tag='grafo')
            cs.create_text((c.x1+c.x2)/2, (c.y1+c.y2)/2, text=c.tag, angle=c.textAngle, anchor='sw', tag='grafo')
        cs.create_oval(p.x, p.y, p.x+gc.Paper.WIDTH, p.y+gc.Paper.HEIGHT, fill='white', tag='grafo')
        cs.create_text(p.x+gc.Paper.WIDTH/2, p.y+gc.Paper.HEIGHT+12, text=p.title, font="Tahoma 9", tag='grafo')
    
def drawGrid(scrollregion):
    x = scrollregion[0]
    y = scrollregion[1]
    xw = scrollregion[2]
    yw = scrollregion[3]
    
    cs.delete('grid')
    for i in range(int(x/gc.Paper.XSEP)*gc.Paper.XSEP, xw, gc.Paper.XSEP):
        cs.create_line(i, y, i, yw, dash=(3,1), fill='#9EA', tag='grid')
    if gc.minYear()!=None:
        for i in range(int(x/gc.Paper.XSEP)*gc.Paper.XSEP, xw, gc.Paper.XSEP*2):
            year=(i-gc.minX())/gc.Paper.XSEP+gc.minYear()
            cs.create_text(i, cs.canvasy(cs.winfo_height()-50), text=f'{year:.0f}', tag='grid')

def setScrollRegion():
    """set scrollregion in modo da centrare il grafo, return new scrollregion"""
    bb=cs.bbox('grafo')
    if not bb:
        bb=(0,0,0,0)
    x=bb[0]
    y=bb[1]
    w=bb[2]-bb[0]
    h=bb[3]-bb[1]
    cw=cs.winfo_width()-4
    ch=cs.winfo_height()-4
    if w<cw:
        x=int(x-(cw-w)/2)
        w=cw
    if h<ch:
        y=int(y-(ch-h)/2)
        h=ch
    sr=(x, y, x+w, y+h)
    cs.configure(scrollregion=sr)
    return sr

#Paper col mouse sopra
hover=None
selected=None

#window gui    
window = tk.Tk()
window.geometry("800x600")
window.title("Scholar")

tk.Grid.columnconfigure(window, 1, weight=1)
tk.Grid.rowconfigure(window, 1, weight=1)

e=ttk.Entry(window)
e.grid(column=0, row=0, padx=5, pady=5, sticky=tk.E)

b=ttk.Button(window,text="Cerca",command=search)
b.grid(column=1, row=0, padx=5, pady=5, sticky=tk.W)

cs=tk.Canvas(window, bg='white', borderwidth=2, relief='ridge', highlightthickness=0)
cs.grid(column=0, row=1, columnspan=2, sticky=tk.NSEW)
cs.bind('<Button-1>', mouseClick)
cs.bind('<Motion>', mouseMove)
cs.bind('<Leave>', mouseLeave)
cs.bind('<Configure>', onSizeChanged)

scrollbar = tk.Scrollbar(window, orient='horizontal', command=cs.xview)
scrollbar.grid(column=0, row=2, columnspan=2, sticky=tk.EW)

cs.configure(xscrollcommand=scrollbar.set)

#Frame Opzioni Paper
paperFrame=tk.Frame(window, width=250, padx=12)
paperFrame.grid(column=2, row=1, sticky=tk.NS)
paperFrame.grid_propagate(False)
tk.Grid.columnconfigure(paperFrame, 0, weight=1)
tk.Grid.columnconfigure(paperFrame, 1, weight=1)

tk.Label(paperFrame, text='Opzioni Paper').grid(column=0, columnspan=2, row=0, pady=5)
l_title=tk.Label(paperFrame, text='Titolo:', justify=tk.LEFT, wraplengt=225)
l_title.grid(column=0, columnspan=2, row=1, sticky=tk.W)
l_author=tk.Label(paperFrame, text='Autori:', justify=tk.LEFT, wraplengt=225)
l_author.grid(column=0, columnspan=2, row=2, sticky=tk.W)
l_year=tk.Label(paperFrame, text='Anno:')
l_year.grid(column=0, columnspan=2, row=3, sticky=tk.W)
l_venue=tk.Label(paperFrame, text='Venue:', justify=tk.LEFT, wraplengt=225)
l_venue.grid(column=0, columnspan=2, row=4, sticky=tk.W)
l_abstr=tk.Label(paperFrame, text='Abstract:', justify=tk.LEFT, wraplengt=225)
l_abstr.grid(column=0, columnspan=2, row=5, sticky=tk.W)

ttk.Button(paperFrame, text='Citato da', command=citedbyClick).grid(column=0, row=6, pady=5)
ttk.Button(paperFrame, text='Cita').grid(column=1, row=6, pady=5)

#Frame Opzioni Citazione
citFrame=tk.Frame(window, width=250, padx=12)
citFrame.grid(column=2, row=1, sticky=tk.NS)
citFrame.grid_propagate(False)
tk.Grid.columnconfigure(citFrame, 0, weight=1)
tk.Grid.columnconfigure(citFrame, 1, weight=1)

tk.Label(citFrame, text='Opzioni Citazione').grid(column=0, columnspan=2, row=0, pady=5)
tk.Label(citFrame, text='tag:').grid(column=0, row=1, pady=5)
cb_tag=ttk.Combobox(citFrame, values=['<vuoto>','cita','citato da','correlato'])
cb_tag.grid(column=1, row=1)

tk.Label(citFrame, text='colore:').grid(column=0, row=2, pady=5)
cb_colors=ttk.Combobox(citFrame, state='readonly', values=['nero', 'blu', 'rosso', 'verde', 'giallo'])
cb_colors.grid(column=1, row=2)

def settag(e):
    tag=cb_tag.get()
    selected.tag=tag if tag!='<vuoto>' else ''
    drawPapers()
    sr=setScrollRegion()
    drawGrid(sr)
    cs.tag_lower('grid')
cb_tag.bind("<<ComboboxSelected>>", settag)
cb_tag.bind("<Return>", settag)

paperFrame.tkraise()

tooltip=tk.Label(window, anchor=tk.NW, borderwidth=1, relief='solid', justify=tk.LEFT, wraplengt=250)

tk.mainloop()
