import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from scholar_req import ScholarRequests
from statebuffer import StBuffer
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
                    cb_tag.set('<vuoto>' if c.tag=="" else c.tag)
                    cb_colors.current(colors.index(c.color))
                    cs_width.set(c.width)
                    citFrame.tkraise()
                    updateTagSample()
                    break
            else:
                continue
            break
    drawAll()
    window.focus_set()
    tooltip.tkraise()

def globalClick(e):
    global archOpzChange
    if archOpzChange:
        buff.push(gc.saveString())
        archOpzChange=False

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
    gc.XSEP+=int(e.delta/12)
    if gc.XSEP<20:
        gc.XSEP=20
    elif gc.XSEP>250:
        gc.XSEP=250
    drawAll()
    cs.xview_moveto(xv[0])
    mouseMove(e)

def zoomIn():
    xv=cs.xview()
    gc.XSEP+=10
    if gc.XSEP<20:
        gc.XSEP=20
    elif gc.XSEP>250:
        gc.XSEP=250
    drawAll()
    cs.xview_moveto(xv[0])

def zoomOut():
    xv=cs.xview()
    gc.XSEP-=10
    if gc.XSEP<20:
        gc.XSEP=20
    elif gc.XSEP>250:
        gc.XSEP=250
    drawAll()
    cs.xview_moveto(xv[0])

def onSizeChanged(e):
    sr=setScrollRegion()
    drawGrid(sr)

def drawPapers():
    cs.delete('grafo')
    
    for p in gc.getAllPapers():
        if p.draw:
            for c in p.cites:
                if c.draw:
                    if selected is c:
                        cs.create_line(c.x1, c.y1, c.x2, c.y2, width=c.width+1, arrow=tk.LAST, fill=c.color, tag='grafo')
                    else:
                        cs.create_line(c.x1, c.y1, c.x2, c.y2, width=c.width, arrow=tk.LAST, fill=c.color, tag='grafo')
                    cs.create_text((c.x1+c.x2)/2, (c.y1+c.y2)/2, text=c.tag, angle=c.textAngle, anchor='s', tag='grafo')
            if selected is p:
                cs.create_oval(p.x, p.y, p.x+gc.Paper.WIDTH, p.y+gc.Paper.HEIGHT, fill='#FD1', tag='grafo')
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
    cs.tag_lower('grid')

def drawAll():
    drawPapers()
    sr=setScrollRegion()
    drawGrid(sr)
    
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

def yscroll(a,y):
    cs.yview(a,y)
    sr=setScrollRegion()
    drawGrid(sr)
    
def search():
    try:
        paper_dict=sch.search_single_pub(search_e.get())
        if paper_dict==None:
            messagebox.showwarning('Nessun risultato','Impossibile trovare il paper')
            return
        gc.Paper.createUnique(paper_dict)
        drawAll()
        buff.push(gc.saveString())
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
        buff.push(gc.saveString())
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
        buff.push(gc.saveString())
    except:
        messagebox.showerror('Errore','Impossibile eseguire la ricerca')

def showInBrowser():
    webbrowser.open(selected.dict['link'])

def deletePaper():
    selected.delete()
    showFilter()
    sr=setScrollRegion()
    drawGrid(sr)
    buff.push(gc.saveString())

def toogle_hide():
    if selected.hide:
        selected.hide=False
        b_hide['text']='Nascondi citazioni'
    else:
        selected.hide=True
        b_hide['text']='Mostra citazioni'
    lastFilter()
    buff.push(gc.saveString())

def showFilter():
    global selected
    selected=None
    drawPapers()
    filtrFrame.tkraise()
    window.focus_set()
    tooltip.tkraise()
    updateTagSample()

def filterLimitTo():
    global lastFilter
    lastFilter=filterLimitTo
    
    fl=list(fltListbox.get(0,fltListbox.size()-1))
    if fl.count('<vuoto>')>0:
        fl.append("")

    for p in gc.getAllPapers():
        p.draw=True
        for c in p.cites:
            c.draw=True
    for p in gc.getAllPapers():
        for c in p.cites:
            if c.tag not in fl:
                c.draw=False
                p.draw=False
                c.paper2.draw=False
            elif p.hide:
                c.draw=False
                if not c.paper2.hide:
                    c.paper2.draw=False
        if p.hide:
            for c in p.citesBack:
                c.draw=False
                if not c.paper1.hide:
                    c.paper1.draw=False
    for p in gc.getAllPapers():
        if not p.hide:
            for c in p.cites:
                if c.draw:
                    p.draw=True
                    c.paper2.draw=True
    drawAll()

def filterExclude():
    global lastFilter
    lastFilter=filterExclude
    
    fl=list(fltListbox.get(0,fltListbox.size()-1))
    if fl.count('<vuoto>')>0:
        fl.append("")

    for p in gc.getAllPapers():
        p.draw=True
        for c in p.cites:
            c.draw=True
    for p in gc.getAllPapers():
        for c in p.cites:
            if c.tag in fl:
                c.draw=False
                p.draw=False
                c.paper2.draw=False
            elif p.hide:
                c.draw=False
                if not c.paper2.hide:
                    c.paper2.draw=False
        if p.hide:
            for c in p.citesBack:
                c.draw=False
                if not c.paper1.hide:
                    c.paper1.draw=False
    for p in gc.getAllPapers():
        if not p.hide:
            for c in p.cites:
                if c.draw:
                    p.draw=True
                    c.paper2.draw=True
    drawAll() 

def clearFilter():
    global lastFilter
    lastFilter=clearFilter
    
    #draw_set=set()
    #exclude_set=set()
    for p in gc.getAllPapers():
        p.draw=True
        for c in p.cites:
            c.draw=True
    for p in gc.getAllPapers():
        if p.hide:
            for c in p.cites:
                c.draw=False
                if not c.paper2.hide:
                    c.paper2.draw=False
            for c in p.citesBack:
                c.draw=False
                if not c.paper1.hide:
                    c.paper1.draw=False
    for p in gc.getAllPapers():
        if not p.hide:
            for c in p.cites:
                if c.draw:
                    p.draw=True
                    c.paper2.draw=True
    """
    for p in exclude_set:
        if p not in draw_set:
            p.draw=False
    """
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
    global archOpzChange
    tag=cb_tag.get()
    tag=tag if tag!='<vuoto>' else ""
    color=colors[cb_colors.current()]
    width=round(cs_width.get())

    if selected.tag!=tag:
        selected.tag=tag
        archOpzChange=True
    if selected.color!=color:
        selected.color=color
        buff.push(gc.saveString())
    if selected.width!=width:
        selected.width=width
        buff.push(gc.saveString())
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
            messagebox.showwarning('Schema.gql non salvato','Esiste gi?? un file schema.qgl')
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
    global selected, hover, clicked, lastFilter, archOpzChange
    f=filedialog.askopenfile(mode='rb', filetypes=[('grafi','*.grf')])
    if f:
        try:
            gc.load(f)
            buff.clear()
            buff.push(gc.saveString())
        except Exception as e:
            messagebox.showerror('Errore','Impossibile caricare:\n'+str(e))
        f.close()
    selected=None
    hover=None
    clicked=False
    lastFilter=clearFilter
    archOpzChange=False
    drawAll()
    updateTagSample()

def undo():
    global selected, hover, clicked, archOpzChange
    s=buff.back()
    if s:
        gc.loadString(s)
        selected=None
        hover=None
        clicked=False
        archOpzChange=False
        showFilter()
        sr=setScrollRegion()
        drawGrid(sr)

def redo():
    global selected, hover, clicked, archOpzChange
    s=buff.forward()
    if s:
        gc.loadString(s)
        selected=None
        hover=None
        clicked=False
        archOpzChange=False
        showFilter()
        sr=setScrollRegion()
        drawGrid(sr)

"""variabili globali"""
#Paper col mouse sopra
hover=None
selected=None

clicked=False
lastFilter=clearFilter
archOpzChange=False

sch=ScholarRequests()
buff=StBuffer()
"""variabili globali"""

#window gui    
window = tk.Tk()
window.geometry("800x600")
window.title("Scholar")
window.minsize(550,280)
window.bind('<Control-z>', lambda e: undo())
window.bind('<Control-y>', lambda e: redo())
window.bind('<Control-s>', lambda e: save())
window.bind('<Control-l>', lambda e: load())
window.bind('<Button-1>', globalClick)

"""DEBUG"""
saved=''
def ciao(e):
    global saved
    st=gc.saveString()
    if st==saved:
        print('UGUALE')
    else:
        print('DIVERSO')
    saved=st

window.bind('<space>', ciao)

"""DEBUG"""

tk.Grid.columnconfigure(window, 1, weight=1)
tk.Grid.rowconfigure(window, 1, weight=1)

search_e=ttk.Entry(window)
search_e.grid(column=0, row=0, padx=5, pady=5, sticky=tk.E)

search_b=ttk.Button(window,text="Cerca",command=search)
search_b.grid(column=1, row=0, padx=5, pady=5, sticky=tk.W)

im_zoom=tk.PhotoImage(file='zoom1.png')
im_zoom2=tk.PhotoImage(file='zoom2.png')
ttk.Button(window, image=im_zoom, command=zoomIn).grid(column=2, row=0, padx=5, pady=5, ipadx=2)
ttk.Button(window, image=im_zoom2, command=zoomOut).grid(column=3, row=0, padx=5, pady=5, ipadx=2)

cs=tk.Canvas(window, bg='white', borderwidth=2, relief='ridge', highlightthickness=0)
cs.grid(column=0, row=1, columnspan=4, sticky=tk.NSEW)
cs.bind('<Button-1>', mouseClick)
cs.bind("<ButtonRelease-1>", mouseRelease)
cs.bind('<Motion>', mouseMove)
cs.bind('<Leave>', mouseLeave)
cs.bind('<Configure>', onSizeChanged)
cs.bind('<MouseWheel>', mouseWheel)

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
ttk.Button(paperFrame, text='Elimina', command=deletePaper).grid(column=1, row=10, sticky=tk.EW, padx=10, pady=5)
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
        
tk.Label(citFrame, text='spessore:').grid(column=0, row=3, pady=5)
cs_width=ttk.Scale(citFrame, from_=1, to=5, command=updateCit, orient=tk.HORIZONTAL)
cs_width.grid(column=1, columnspan=2, row=3, pady=5)

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

#menubar
menubar=tk.Menu(window)
filemenu=tk.Menu(menubar, tearoff=0)
filemenu.add_command(label='Salva', accelerator='Ctrl+S', command=save)
filemenu.add_command(label='Carica', accelerator='Ctrl+L', command=load)
filemenu.add_command(label='Esporta json', command=exportJson)
filemenu.add_command(label='Esporta GraQL', command=exportGraql)
filemenu.add_command(label='Esci', command=window.destroy)
editmenu=tk.Menu(menubar, tearoff=0)
editmenu.add_command(label='Annulla', accelerator='Ctrl+Z', command=undo)
editmenu.add_command(label='Ripeti', accelerator='Ctrl+Y', command=redo)
menubar.add_cascade(label='File', menu=filemenu)
menubar.add_cascade(label='Modifica', menu=editmenu)
menubar.add_command(label='Filtra', command=showFilter)
window.config(menu=menubar)

tooltip=tk.Label(window, anchor=tk.NW, borderwidth=1, relief='solid', justify=tk.LEFT, wraplengt=250)

buff.push(gc.saveString())

tk.mainloop()
sch.exit()
