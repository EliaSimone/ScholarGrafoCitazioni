import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
#import fakescholarly as sch
from scholar_req import ScholarRequests
import grafocitazioni as gc
#import re

def search():
    try:
        paper_dict=sch.search_single_pub(e.get())
        gc.Paper.createUnique(paper_dict)
    except Exception:
        print('niente paper')
    drawAll()

def mouseClick(e):
    #get pos relativa
    x = cs.canvasx(e.x)
    y = cs.canvasy(e.y)
    global selected, clicked
    
    if hover:
        selected=hover
        clicked=True
                    
        l_title['text']='Titolo: '+selected.title
        l_author['text']='Autori: '+selected.dict['author']
        l_year['text']='Anno: '+selected.dict['pub_year']
        l_venue['text']='Venue: '+selected.dict['venue']
        l_abstr['text']='Abstract: '+selected.dict['abstract']
        paperFrame.tkraise()
    else:
        for p in gc.getAllPapers():
            for c in p.cites.values():
                if (c.checkPoint(x,y) and c.draw):
                    print('ho cliccato su un arco')
                    selected=c
                    cb_tag.set('<vuoto>' if c.tag=='' else c.tag)
                    cb_colors.current(colors.index(c.color))
                    #cb_colors.current(0)
                    citFrame.tkraise()
                    break
            else:
                continue
            break
    drawAll()
    tooltip.tkraise()

def mouseMove(e):
    #get pos relativa
    x = cs.canvasx(e.x)
    y = cs.canvasy(e.y)

    global hover

    if clicked:
        if y-gc.Paper.HEIGHT/2<0:
            selected.y=0
        elif y-gc.Paper.HEIGHT/2>gc.Y_HEIGHT:
            selected.y=gc.Y_HEIGHT
        else:
            selected.y=y-gc.Paper.HEIGHT/2
        drawAll()
    else:
        for p in gc.getAllPapers():
            if p.checkPoint(x, y):
                if (hover is not p and p.draw):
                    hover=p
                    tooltip.place(x=cs.winfo_x()+e.x+p.x-x+35, y=cs.winfo_y()+e.y+p.y-y+35)
                    text=p.title
                    text+='\nauthors: '+p.dict['author']
                    text+='\nyear: '+p.dict['pub_year']
                    text+='\nvenue: '+p.dict['venue']
                    text+='\nabstract: '+p.dict['abstract']
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

def mouseRelease(e):
    global clicked
    clicked=False
    mouseMove(e)

def citedbyClick():
    cited=sch.cited_by(selected.dict)
    for c in cited:
        selected.addCite(gc.Paper.createUnique(c))
    drawAll()

def onSizeChanged(e):
    sr=setScrollRegion()
    drawGrid(sr)
    cs.tag_lower('grid')

def drawPapers():
    cs.delete('grafo')
    
    for p in gc.getAllPapers():
        if p.draw:
            for c in p.cites.values():
                if c.draw:
                    if selected is c:
                        cs.create_line(c.x1, c.y1, c.x2, c.y2, width=2, arrow=tk.LAST, fill=c.color, tag='grafo')
                    else:
                        cs.create_line(c.x1, c.y1, c.x2, c.y2, arrow=tk.LAST, fill=c.color, tag='grafo')
                    cs.create_text((c.x1+c.x2)/2, (c.y1+c.y2)/2, text=c.tag, angle=c.textAngle, anchor='s', tag='grafo')
            if selected is p:
                cs.create_oval(p.x, p.y, p.x+gc.Paper.WIDTH, p.y+gc.Paper.HEIGHT, width=1, fill='#FD1', tag='grafo')
            else:
                cs.create_oval(p.x, p.y, p.x+gc.Paper.WIDTH, p.y+gc.Paper.HEIGHT, fill='#46B', tag='grafo')
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

def drawAll():
    drawPapers()
    sr=setScrollRegion()
    drawGrid(sr)
    cs.tag_lower('grid')
    
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

def showFilter():
    filtrFrame.tkraise()
    tooltip.tkraise()

def updateFilter():
    if fltListbox.size()==0:
        clearFilter()
        drawAll()
        return

    fl=list(fltListbox.get(0,fltListbox.size()-1))
    target_list=[]
    for p in gc.getAllPapers():
        p.draw=False
        for c in p.cites.values():
            if c.tag in fl:
                c.draw=True
                p.draw=True
                target_list.append(c.paper2)
            else:
                c.draw=False
                
    for p in target_list:
        p.draw=True 
    drawAll()

def clearFilter():
    for p in gc.getAllPapers():
        p.draw=True
        for c in p.cites.values():
            c.draw=True
            
def updateCit(e):
    tag=cb_tag.get()
    color=colors[cb_colors.current()]
    
    selected.tag=tag if tag!='<vuoto>' else ''
    selected.color=color
    drawAll()

def save():
    f=filedialog.asksaveasfile(mode='wb', defaultextension='.grf', filetypes=[('grafi','*.grf')])
    if f:
        try:
            gc.save(f)
        except:
            print('not possible to save')
        f.close()

def load():
    f=filedialog.askopenfile(mode='rb', filetypes=[('grafi','*.grf')])
    if f:
        try:
            gc.load(f)
        except Exception as e:
            print('not possible to load:', e)
        f.close()
    selected=None
    hover=None
    clicked=False
    drawAll()

#Paper col mouse sopra
hover=None
selected=None

clicked=False

sch=ScholarRequests()

#window gui    
window = tk.Tk()
window.geometry("800x600")
window.title("Scholar")
window.minsize(550,280)

tk.Grid.columnconfigure(window, 1, weight=1)
tk.Grid.rowconfigure(window, 1, weight=1)

e=ttk.Entry(window)
e.grid(column=0, row=0, padx=5, pady=5, sticky=tk.E)

b=ttk.Button(window,text="Cerca",command=search)
b.grid(column=1, row=0, padx=5, pady=5, sticky=tk.W)

cs=tk.Canvas(window, bg='white', borderwidth=2, relief='ridge', highlightthickness=0)
cs.grid(column=0, row=1, columnspan=2, sticky=tk.NSEW)
cs.bind('<Button-1>', mouseClick)
cs.bind("<ButtonRelease-1>", mouseRelease)
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
tk.Grid.columnconfigure(citFrame, 2, weight=1)

tk.Label(citFrame, text='Opzioni Citazione').grid(column=0, columnspan=2, row=0, pady=5)
tk.Label(citFrame, text='tag:').grid(column=0, row=1, pady=5)
cb_tag=ttk.Combobox(citFrame, values=['<vuoto>','estende','usa','compete con'])
cb_tag.grid(column=1, columnspan=2, row=1, pady=5)

colors=['black','blue','red','green','yellow']

tk.Label(citFrame, text='colore:').grid(column=0, row=2, pady=5)
cb_colors=ttk.Combobox(citFrame, state='readonly', values=['nero','blu','rosso','verde','giallo'])
cb_colors.grid(column=1, columnspan=2, row=2, pady=5)

def addTag():
    elem=tag_entry.get()
    if elem not in cb_tag['values']:
        cb_tag['values']+=(elem,)

tag_entry=ttk.Entry(citFrame)
tag_entry.grid(column=0, columnspan=2, row=3, padx=5, pady=5)
ttk.Button(citFrame, text='aggiungi', command=addTag).grid(column=2, row=3, padx=5, pady=5)

cb_tag.bind("<<ComboboxSelected>>", updateCit)
cb_colors.bind("<<ComboboxSelected>>", updateCit)
cb_tag.bind("<KeyRelease>", updateCit)

#Frame Filtri
filtrFrame=tk.Frame(window, width=250, padx=12)
filtrFrame.grid(column=2, row=1, sticky=tk.NS)
filtrFrame.grid_propagate(False)
tk.Grid.columnconfigure(filtrFrame, 0, weight=1)
tk.Grid.columnconfigure(filtrFrame, 1, weight=5)
tk.Grid.columnconfigure(filtrFrame, 2, weight=2)
tk.Grid.rowconfigure(filtrFrame, 5, weight=1)

tk.Label(filtrFrame, text='Opzioni Filtri').grid(column=0, columnspan=3, row=0, pady=5)
tk.Label(filtrFrame, text='Filtra per citazioni che contengono uno dei seguenti tag:', justify=tk.LEFT, wraplengt=225).grid(column=0, columnspan=3, row=1, pady=5)
fltListbox=tk.Listbox(filtrFrame)
fltListbox.grid(column=0, row=2, columnspan=3, sticky=tk.EW, padx=5)

def listAdd():
    elm=fltEntry.get()
    if elm!="":
        fltListbox.insert(fltListbox.size(), elm)
        #updateFilter()

def listDelete():
    elm=fltListbox.curselection()
    if len(elm)>0:
        fltListbox.delete(elm[0])
    #updateFilter()

def listClear():
    size=fltListbox.size()
    if size>0:
        fltListbox.delete(0,size-1)
    #updateFilter()

def apply():
    updateFilter()
    
ttk.Button(filtrFrame, text='Elimina', command=listDelete).grid(column=0, row=3, padx=5, pady=5, sticky=tk.EW)
ttk.Button(filtrFrame, text='Elimina tutti', command=listClear).grid(column=1, row=3, columnspan=2, padx=5, pady=5, sticky=tk.EW)
fltEntry=ttk.Entry(filtrFrame)
fltEntry.grid(column=0, row=4, columnspan=2, padx=5, pady=5, sticky=tk.EW)
ttk.Button(filtrFrame, text='Aggiungi', command=listAdd).grid(column=2, row=4, padx=5, pady=5)
ttk.Button(filtrFrame, text='Applica', command=apply).grid(column=0, row=5, sticky=tk.SW, padx=5, pady=5)

paperFrame.tkraise()

#menubar
menubar=tk.Menu(window)
filemenu=tk.Menu(menubar, tearoff=0)
filemenu.add_command(label='Salva', command=save)
filemenu.add_command(label='Carica', command=load)
#filemenu.add_command(label='Esporta json')
filemenu.add_command(label='Esci', command=window.destroy)
menubar.add_cascade(label='File', menu=filemenu)
menubar.add_command(label='Filtra', command=showFilter)
window['menu']=menubar

tooltip=tk.Label(window, anchor=tk.NW, borderwidth=1, relief='solid', justify=tk.LEFT, wraplengt=250)

tk.mainloop()
sch.exit()
