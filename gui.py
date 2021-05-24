import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from scholar_req import ScholarRequests
import grafocitazioni as gc
import webbrowser
import json
import os

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
        if selected.dict['abstract']=="":
            l_abstr['text']=""
        else:
            l_abstr['text']='Abstract: '+selected.dict['abstract']
        b_hide['text']='Mostra citazioni' if selected.hide else 'Nascondi citazioni'
        if selected.pdf!="":
            e_pdf.config(state='active')
            e_pdf.delete(0, tk.END)
            e_pdf.insert(0, selected.pdf)
            e_pdf.config(state='readonly')
            b_pdf.config(state='active')
        else:
            e_pdf.config(state='active')
            e_pdf.delete(0, tk.END)
            e_pdf.insert(0, 'No File')
            e_pdf.config(state='readonly')
            b_pdf.config(state='disabled')
        paperFrame.tkraise()
    else:
        for p in gc.getAllPapers():
            for c in p.cites:
                if (c.checkPoint(x,y) and c.draw):
                    selected=c
                    cb_tag.set('<vuoto>' if c.tag=='' else c.tag)
                    cb_colors.current(colors.index(c.color))
                    citFrame.tkraise()
                    updateTagSample()
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
        if y-gc.Paper.HEIGHT/2<-gc.Y_MAX:
            selected.y=-gc.Y_MAX
        elif y-gc.Paper.HEIGHT/2>gc.Y_MAX:
            selected.y=gc.Y_MAX
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
                    if p.dict['abstract']!="":
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

def mouseWheel(e):
    xv=cs.xview()
    gc.XSEP+=int(e.delta/20)
    if gc.XSEP<20:
        gc.XSEP=20
    elif gc.XSEP>250:
        gc.XSEP=250
    drawAll()
    cs.xview_moveto(xv[0])
    mouseMove(e)

def zoomIn():
    xv=cs.xview()
    gc.XSEP+=6
    if gc.XSEP<20:
        gc.XSEP=20
    elif gc.XSEP>250:
        gc.XSEP=250
    drawAll()
    cs.xview_moveto(xv[0])

def zoomOut():
    xv=cs.xview()
    gc.XSEP-=6
    if gc.XSEP<20:
        gc.XSEP=20
    elif gc.XSEP>250:
        gc.XSEP=250
    drawAll()
    cs.xview_moveto(xv[0])

def onSizeChanged(e):
    sr=setScrollRegion()
    drawGrid(sr)
    cs.tag_lower('grid')

def drawPapers():
    cs.delete('grafo')
    
    for p in gc.getAllPapers():
        if p.draw:
            for c in p.cites:
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
            cs.create_text(p.x+gc.Paper.WIDTH/2, p.y+gc.Paper.HEIGHT+12, text=p.vtitle, font="Tahoma 9", tag='grafo')

def drawGrid(scrollregion):
    x = scrollregion[0]
    y = scrollregion[1]
    xw = scrollregion[2]
    yw = scrollregion[3]
    
    cs.delete('grid')
    for i in range(int(x/gc.XSEP)*gc.XSEP, xw, gc.XSEP):
        cs.create_line(i, y, i, yw, dash=(3,1), fill='#9EA', tag='grid')
    if gc.minYear()!=None:
        for i in range(int(x/gc.XSEP)*gc.XSEP, xw, gc.XSEP*2):
            year=(i-gc.minX())/gc.XSEP+gc.minYear()
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
        x=int(x-(cw-w))
        w=cw
    if h<ch:
        y=int(y-(ch-h)/2)
        h=ch
    sr=(x, y, x+w, y+h)
    cs.configure(scrollregion=sr)
    return sr

def yscroll(a,y):
    cs.yview(a,y)
    sr=setScrollRegion()
    drawGrid(sr)
    cs.tag_lower('grid')
    
def search():
    try:
        paper_dict=sch.search_single_pub(search_e.get())
        if paper_dict==None:
            messagebox.showwarning('Nessun risultato','Impossibile trovare il paper')
            return
        gc.Paper.createUnique(paper_dict)
        drawAll()
    except:
        messagebox.showerror('Errore','Impossibile eseguire la ricerca')

def citedbyClick():
    try:
        cited=sch.cited_by(selected.dict)     
        if len(cited)==0:
            messagebox.showwarning('Nessun risultato','Il paper non riceve citazioni')
            return
        for c in cited:
            selected.addCite(gc.Paper.createUnique(c))
        drawAll()
    except:
        messagebox.showerror('Errore','Impossibile eseguire la ricerca')

def referencesClick():
    try:
        cited=sch.references(selected.dict)
        if len(cited)==0:
            messagebox.showwarning('Nessun risultato','Il paper non ha citazioni')
            return
        for c in cited:
            gc.Paper.createUnique(c).addCite(selected)
        drawAll()
    except:
        messagebox.showerror('Errore','Impossibile eseguire la ricerca')

def showInBrowser():
    webbrowser.open(selected.dict['link'])

def toogle_hide():
    if selected.hide:
        selected.hide=False
        b_hide['text']='Nascondi citazioni'
    else:
        selected.hide=True
        b_hide['text']='Mostra citazioni'
    lastFilter()
    """
    draw_set=set()
    exclude_set=set()
    for p in gc.getAllPapers():
        for c in p.cites:
            if p.hide:
                c.draw=False
                exclude_set.add(c.paper2)
            elif c.paper2.draw:
                draw_set.add(c.paper2)
    for p in exclude_set:
        if p not in draw_set:
            p.draw=False
    drawAll()
    """

def showFilter():
    global selected
    selected=None
    drawPapers()
    filtrFrame.tkraise()
    tooltip.tkraise()
    updateTagSample()

def filterLimitTo():
    global lastFilter
    lastFilter=filterLimitTo
    
    fl=list(fltListbox.get(0,fltListbox.size()-1))
    if fl.count('<vuoto>')>0:
        fl.append("")
    draw_set=set()
    exclude_set=set()
    for p in gc.getAllPapers():
        p.draw=True
        for c in p.cites:
            if c.tag not in fl:
                c.draw=False
                exclude_set.add(p)
                exclude_set.add(c.paper2)
            elif p.hide:
                c.draw=False
                exclude_set.add(c.paper2)
            else:
                c.draw=True
                draw_set.add(p)
                draw_set.add(c.paper2)
                
    for p in exclude_set:
        if p not in draw_set:
            p.draw=False
    drawAll()

def filterExclude():
    global lastFilter
    lastFilter=filterExclude
    
    fl=list(fltListbox.get(0,fltListbox.size()-1))
    if fl.count('<vuoto>')>0:
        fl.append("")
    draw_set=set()
    exclude_set=set()
    for p in gc.getAllPapers():
        p.draw=True
        for c in p.cites:
            if c.tag in fl:
                c.draw=False
                exclude_set.add(p)
                exclude_set.add(c.paper2)
            elif p.hide:
                c.draw=False
                exclude_set.add(c.paper2)
            else:
                c.draw=True
                draw_set.add(p)
                draw_set.add(c.paper2)
                
    for p in exclude_set:
        if p not in draw_set:
            p.draw=False
    drawAll()

def clearFilter():
    global lastFilter
    lastFilter=clearFilter
    
    draw_set=set()
    exclude_set=set()
    for p in gc.getAllPapers():
        p.draw=True
        for c in p.cites:
            if p.hide:
                c.draw=False
                exclude_set.add(c.paper2)
            else:
                c.draw=True
                draw_set.add(p)
                draw_set.add(c.paper2)
                
    for p in exclude_set:
        if p not in draw_set:
            p.draw=False
    drawAll()

def updateTagSample():
    preset=('<vuoto>', 'cita', 'estende', 'usa')
    sample=set()
    for p in gc.getAllPapers():
        for c in p.cites:
            if (c.tag != "" and c.tag not in preset):
                sample.add(c.tag)
    cb_tag['values']=preset+tuple(sample)
    cb_filter['values']=preset+tuple(sample)
            
def updateCit(e):
    tag=cb_tag.get()
    color=colors[cb_colors.current()]
    
    selected.tag=tag if tag!='<vuoto>' else ""
    selected.color=color
    drawAll()

def exportJson():
    f=filedialog.asksaveasfile(mode='w', defaultextension='.json', filetypes=[('JSON','*.json')])
    if f:
        with f:
            pl=[]
            cl=[]
            for p in gc.getAllPapers():
                pl.append(p.jsonDict())
                for c in p.cites:
                    cl.append(c.jsonDict())
            json.dump(pl+cl, f, indent=2)

def exportGraql():
    f=filedialog.asksaveasfile(mode='w', defaultextension='.gql', filetypes=[('GraQL','*.gql')])
    if f:
        with f:
            f.reconfigure(encoding='utf-8')
            for p in gc.getAllPapers():
                f.write("insert $p isa paper, has title \"{}\", has year {}, has author \"{}\", has abstract \"{}\";\n".format(p.title,p.year,p.dict['author'],p.dict['abstract']))
            f.write("\n")
            for p in gc.getAllPapers():
                for c in p.cites:
                    f.write("match\n")
                    f.write("$paper1 isa paper, has name \"{}\";\n".format(p.title))
                    f.write("$paper2 isa paper, has name \"{}\";\n".format(c.paper2.title))
                    f.write("insert $citation (citer: $paper1, cited: $paper2) isa citation;\n")
                    f.write("$citation has tag \"{}\";\n\n".format(c.tag))
            f.write("commit")

        try:
            f=open(os.path.dirname(f.name)+'\\schema.gql', 'x')
            with f:
                f.write("define\n\n")
                f.write("paper sub entity,\n\towns title,\n\towns year,\n\towns author,\n\towns abstract,\n\tplays citation:citer,\n\tplays citation:cited;\n\n")
                f.write("citation sub relation,\n\towns tag,\n\trelates citer,\n\trelates cited;\n\n")
                f.write("title sub attribute,\n\tvalue string;\n\n")
                f.write("year sub attribute,\n\tvalue long;\n\n")
                f.write("author sub attribute,\n\tvalue string;\n\n")
                f.write("abstract sub attribute,\n\tvalue string;\n\n")
                f.write("tag sub attribute,\n\tvalue string;\n")
        except FileExistsError:
            messagebox.showwarning('Schema.gql non salvato','Esiste già un file schema.qgl')
        except:
            messagebox.showerror('Errore','Schema.gql non salvato')

def save():
    f=filedialog.asksaveasfile(mode='wb', defaultextension='.grf', filetypes=[('grafi','*.grf')])
    if f:
        try:
            gc.save(f)
        except:
            messagebox.showerror('Errore','Impossibile salvare')
        f.close()

def load():
    f=filedialog.askopenfile(mode='rb', filetypes=[('grafi','*.grf')])
    if f:
        try:
            gc.load(f)
        except Exception as e:
            messagebox.showerror('Errore','Impossibile caricare:\n'+str(e))
        f.close()
    selected=None
    hover=None
    clicked=False
    drawAll()
    updateTagSample()

#Paper col mouse sopra
hover=None
selected=None

clicked=False
lastFilter=clearFilter

sch=ScholarRequests()

#window gui    
window = tk.Tk()
window.geometry("800x600")
window.title("Scholar")
window.minsize(550,280)

tk.Grid.columnconfigure(window, 1, weight=1)
tk.Grid.rowconfigure(window, 1, weight=1)

search_e=ttk.Entry(window)
search_e.grid(column=0, row=0, padx=5, pady=5, sticky=tk.E)

search_b=ttk.Button(window,text="Cerca",command=search)
search_b.grid(column=1, row=0, padx=5, pady=5, sticky=tk.W)

ttk.Button(window,text="Zoom +",command=zoomIn).grid(column=2, row=0, padx=5, pady=5)
ttk.Button(window,text="Zoom -",command=zoomOut).grid(column=3, row=0, padx=5, pady=5)

cs=tk.Canvas(window, bg='white', borderwidth=2, relief='ridge', highlightthickness=0)
cs.grid(column=0, row=1, columnspan=4, sticky=tk.NSEW)
cs.bind('<Button-1>', mouseClick)
cs.bind("<ButtonRelease-1>", mouseRelease)
cs.bind('<Motion>', mouseMove)
cs.bind('<Leave>', mouseLeave)
cs.bind('<Configure>', onSizeChanged)
cs.bind('<MouseWheel>', mouseWheel)

"""DEBUG"""

def test(e):
    print('sel:', selected)
    print('hov:', hover)
    
window.bind('<KeyPress>', test)

"""DEBUG"""

scrollbar = tk.Scrollbar(window, orient='horizontal', command=cs.xview)
scrollbar.grid(column=0, row=2, columnspan=4, sticky=tk.EW)

vscrollbar = tk.Scrollbar(window, orient='vertical', command=yscroll)
vscrollbar.grid(column=4, row=1, rowspan=2, sticky=tk.NS)

cs.configure(xscrollcommand=scrollbar.set)
cs.configure(yscrollcommand=vscrollbar.set)

def choosePdf():
    f=filedialog.askopenfilename(filetypes=[('PDF','*.pdf')])
    if f:
        e_pdf.config(state='active')
        e_pdf.delete(0, tk.END)
        e_pdf.insert(0, f)
        e_pdf.config(state='readonly')
        b_pdf.config(state='active')
        selected.pdf=f

def openPdf():
    webbrowser.open(selected.pdf)

#Frame Opzioni Paper
paperFrame=tk.Frame(window, width=280, padx=12)
paperFrame.grid(column=5, row=1, sticky=tk.NS)
paperFrame.grid_propagate(False)
tk.Grid.columnconfigure(paperFrame, 0, weight=1)
tk.Grid.columnconfigure(paperFrame, 1, weight=1)
tk.Grid.rowconfigure(paperFrame, 9, weight=1)

tk.Label(paperFrame, text='Opzioni Paper').grid(column=0, columnspan=2, row=0, pady=5)
l_title=tk.Label(paperFrame, text='Titolo:', justify=tk.LEFT, wraplengt=250)
l_title.grid(column=0, columnspan=2, row=1, sticky=tk.W, pady=5)
l_author=tk.Label(paperFrame, text='Autori:', justify=tk.LEFT, wraplengt=250)
l_author.grid(column=0, columnspan=2, row=2, sticky=tk.W, pady=5)
l_year=tk.Label(paperFrame, text='Anno:')
l_year.grid(column=0, columnspan=2, row=3, sticky=tk.W, pady=5)
l_abstr=tk.Label(paperFrame, text='Abstract:', justify=tk.LEFT, wraplengt=250)
l_abstr.grid(column=0, columnspan=2, row=4, sticky=tk.W, pady=(5,15))

b_hide=ttk.Button(paperFrame, text='Nascondi citazioni', command=toogle_hide)
b_hide.grid(column=0, row=5, columnspan=2, sticky=tk.W, padx=5, pady=15)

tk.Label(paperFrame, text='PDF del paper').grid(column=0, row=6, sticky=tk.W, pady=5)
e_pdf=ttk.Entry(paperFrame)
e_pdf.grid(column=0, row=7, columnspan=2, sticky=tk.EW, padx=5, pady=5)
e_pdf.insert(0,'No File')
e_pdf.config(state='readonly')
ttk.Button(paperFrame, text='Sfoglia', command=choosePdf).grid(column=0, row=8, sticky=tk.EW, padx=5, pady=5)
b_pdf=ttk.Button(paperFrame, text='Apri', command=openPdf)
b_pdf.grid(column=1, row=8, sticky=tk.EW, padx=5, pady=5)

ttk.Button(paperFrame, text='Apri online', command=showInBrowser).grid(column=0, row=10, sticky=tk.EW, padx=10, pady=5)
ttk.Button(paperFrame, text='Citato da', command=citedbyClick).grid(column=0, row=11, sticky=tk.EW, padx=10, pady=5)
ttk.Button(paperFrame, text='Cita', command=referencesClick).grid(column=1, row=11, sticky=tk.EW, padx=10, pady=5)

#Frame Opzioni Citazione
citFrame=tk.Frame(window, width=280, padx=12)
citFrame.grid(column=5, row=1, sticky=tk.NS)
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
    if elem!="" and elem not in cb_tag['values']:
        cb_tag['values']+=(elem,)
        cb_filter['values']+=(elem,)
        tag_entry.delete(0,tk.END)

#tag_entry=ttk.Entry(citFrame)
#tag_entry.grid(column=0, columnspan=2, row=3, padx=5, pady=5)
#ttk.Button(citFrame, text='aggiungi', command=addTag).grid(column=2, row=3, padx=5, pady=5)

cb_tag.bind("<<ComboboxSelected>>", updateCit)
cb_colors.bind("<<ComboboxSelected>>", updateCit)
cb_tag.bind("<KeyRelease>", updateCit)

#Frame Filtri
filtrFrame=tk.Frame(window, width=280, padx=12)
filtrFrame.grid(column=5, row=1, sticky=tk.NS)
filtrFrame.grid_propagate(False)
tk.Grid.columnconfigure(filtrFrame, 0, weight=1)
tk.Grid.columnconfigure(filtrFrame, 1, weight=1)
tk.Grid.rowconfigure(filtrFrame, 5, weight=1)

tk.Label(filtrFrame, text='Opzioni Filtri').grid(column=0, columnspan=3, row=0, pady=5)
tk.Label(filtrFrame, text='Tag incusi nel filtro:').grid(column=0, columnspan=3, row=1, pady=5)
fltListbox=tk.Listbox(filtrFrame)
fltListbox.grid(column=0, row=2, columnspan=3, sticky=tk.EW, padx=5)

def listAdd():
    fls=fltListbox.get(0,fltListbox.size()-1)
    elm=cb_filter.get()
    if elm!="" and elm not in fls:
        fltListbox.insert(fltListbox.size(), elm)

def listDelete():
    elm=fltListbox.curselection()
    if len(elm)>0:
        fltListbox.delete(elm[0])

def listClear():
    size=fltListbox.size()
    if size>0:
        fltListbox.delete(0,size-1)
    
ttk.Button(filtrFrame, text='Elimina', command=listDelete).grid(column=0, row=3, padx=5, pady=5, sticky=tk.EW)
ttk.Button(filtrFrame, text='Elimina tutti', command=listClear).grid(column=1, row=3, columnspan=2, padx=5, pady=5, sticky=tk.EW)
cb_filter=ttk.Combobox(filtrFrame, values=['<vuoto>','estende','usa','compete con'])
cb_filter.grid(column=0, row=4, columnspan=2, padx=5, pady=5, sticky=tk.EW)
ttk.Button(filtrFrame, text='Aggiugi', command=listAdd).grid(column=2, row=4, padx=5, pady=5)
ttk.Button(filtrFrame, text='Limit to', command=filterLimitTo).grid(column=0, row=6, sticky=tk.EW, padx=5, pady=5)
ttk.Button(filtrFrame, text='Exclude', command=filterExclude).grid(column=1, columnspan=2, row=6, sticky=tk.EW, padx=5, pady=5)
ttk.Button(filtrFrame, text='Remove Filter', command=clearFilter).grid(column=0, columnspan=3, row=7, sticky=tk.EW, padx=5, pady=5)

#paperFrame.tkraise()

#menubar
menubar=tk.Menu(window)
filemenu=tk.Menu(menubar, tearoff=0)
filemenu.add_command(label='Salva', command=save)
filemenu.add_command(label='Carica', command=load)
filemenu.add_command(label='Esporta json', command=exportJson)
filemenu.add_command(label='Esporta GraQL', command=exportGraql)
filemenu.add_command(label='Esci', command=window.destroy)
menubar.add_cascade(label='File', menu=filemenu)
menubar.add_command(label='Filtra', command=showFilter)
window['menu']=menubar

tooltip=tk.Label(window, anchor=tk.NW, borderwidth=1, relief='solid', justify=tk.LEFT, wraplengt=250)

tk.mainloop()
sch.exit()
