__papers__=[]

class Paper:
    """crea un paper da un dizionario nel formato scholarly"""
    def __init__(self, paperDict, x=0, y=0):
        self.dict=paperDict
        self.title=paperDict['bib']['title']
        self.x=x
        self.y=y
        self.cites=[]
        __papers__.append(self)

    def addCite(self, tag, paper):
        """aggiunge citazione con tag e riferimento al paper""" 
        #paper.x=self.x+90
        #paper.y=len(self.cites)*60
        self.cites.append((tag,paper))

    def clearCites(self):
        """svuota lista citazioni"""
        self.cites.clear()

def getAllPapers():
    return __papers__

def clearPapers():
    for i in __papers__:
        i.clearCites()
    __papers__.clear()
