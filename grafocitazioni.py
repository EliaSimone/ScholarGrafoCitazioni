import pickle
import random
import math

#dizionario che ha associato a ogni titolo un paper
_papers={}

_minX=None
_maxX=None
_minYear=None
_maxYear=None

Y_MAX=600
Y_SPAWN=450
XSEP=60

class Paper:
    """crea un paper da un dizionario formato scholarly"""
    WIDTH=32
    HEIGHT=32

    def __init__(self, paperDict):
        self.dict=paperDict
        self.title=paperDict['title']
        self.year=int(paperDict['pub_year'])
        self.cites=set()
        self.citesBack=set()
        self.pdf=""
        self.draw=True
        self.hide=False

        self.vtitle=self.title
        if len(self.vtitle)>50:
            self.vtitle=self.vtitle[:50]+'...'

        if self.title in _papers:
            return
        _papers[self.title]=self

        self._x=(self.year-1900)
        self._y=random.uniform(-Y_SPAWN,Y_SPAWN)

        global _minX
        global _maxX
        global _minYear
        global _maxYear

        if _minX==None:
            _minX=self._x
            _maxX=self._x
            _minYear=self.year
            _maxYear=self.year
        elif self._x<_minX:
            _minX=self._x
            _minYear=self.year
        elif self._x>_maxX:
            _maxX=self._x
            _maxYear=self.year

    @staticmethod
    def createUnique(paperDict):
        """Crea il paper se non è già presente altrimenti ritorna quello già presente"""
        title=paperDict['title']
        if title not in _papers:
            return Paper(paperDict)
        return _papers[title]

    def addCite(self, paper, tag=""):
        """aggiunge citazione con tag e riferimento al paper"""
        for c in self.cites:
            if paper is c.paper2:
                return
        cit=Citation(self, paper, tag)
        self.cites.add(cit)
        paper.citesBack.add(cit)

    def clearCites(self):
        """svuota lista citazioni"""
        for c in self.cites:
            c.paper2.citesBack.remove(c)
        self.cites.clear()

    def delete(self):
        """safe delete"""
        self.clearCites()
        for c in self.citesBack:
            c.paper1.cites.remove(c)
        _papers.pop(self.title)

    def checkPoint(self, x, y):
        if x<self.x:
            return False
        if x>self.x+Paper.WIDTH:
            return False
        if y<self.y:
            return False
        if y>self.y+Paper.HEIGHT:
            return False
        return True

    @property
    def x(self):
        return self._x*XSEP

    @x.setter
    def x(self, v):
        self._x=int(v/XSEP)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, v):
        self._y=v

    def jsonDict(self):
        return {'title': self.dict['title'],
            'id': id(self),
            'author': self.dict['author'],
            'year': self.dict['pub_year'],
            'abstract': self.dict['abstract']}

def minX():
    return _minX*XSEP

def maxX():
    return _maxX*XSEP

def minYear():
    return _minYear

def maxYear():
    return _maxYear

class Citation:
    """classe che rappresenta ogni citazione, con tag, papers e coordinate"""
    def __init__(self, paper1, paper2, tag=""):
        self.paper1=paper1
        self.paper2=paper2
        self.tag=tag
        self.color='black'
        self.width=1
        self.draw=True
        if paper2.year>=paper1.year:
            self.right=True
        else:
            self.right=False
        
    @property
    def x1(self):
        return self.paper1.x+Paper.WIDTH/2

    @property
    def y1(self):
        return self.paper1.y+Paper.HEIGHT/2

    @property
    def x2(self):
        if self.right:
            return self.paper2.x
        return self.paper2.x+Paper.WIDTH

    @property
    def y2(self):
        return self.paper2.y+Paper.HEIGHT/2

    @property
    def textAngle(self):
        if self.x2-self.x1==0:
            if (self.y2>self.y1):
                return 270
            return 90
        
        a=math.atan((self.y2-self.y1)/(self.x2-self.x1))
        return math.degrees(-a)

    def checkPoint(self, x, y, stroke=5):
        stroke+=self.width-1
        if (x<self.x1) == (x<self.x2):
            return False
        if (y<self.y1) == (y<self.y2):
            return False
        #proiezione sulla linea
        yy=self.y1+(x-self.x1)*(self.y2-self.y1)/(self.x2-self.x1)
        xx=self.x1+(y-self.y1)*(self.x2-self.x1)/(self.y2-self.y1)
        #area=x1*(y2-y)-y1*(x2-x)+x2*y-x*y2
        if abs(yy-y)>stroke and abs(xx-x)>stroke:
            return False
        return True

    def jsonDict(self):
        return {'cited_paper': id(self.paper1),
            'citer_paper': id(self.paper2),
            'tag': self.tag}

def exists(title):
    if _papers.get(title):
        return True
    return False

def getAllPapers():
    return list(_papers.values())

def clearPapers():
    for i,p in _papers:
        p.clearCites()
    _papers.clear()

def save(filename):
    pickle.dump((_papers,_minX,_maxX,_minYear,_maxYear), filename)

def load(filename):
    global _papers, _minX, _maxX, _minYear, _maxYear
    load=pickle.load(filename)
    _papers=load[0]
    _minX=load[1]
    _maxX=load[2]
    _minYear=load[3]
    _maxYear=load[4]

def saveString():
    return pickle.dumps((_papers,_minX,_maxX,_minYear,_maxYear))

def loadString(s):
    global _papers, _minX, _maxX, _minYear, _maxYear
    load=pickle.loads(s)
    _papers=load[0]
    _minX=load[1]
    _maxX=load[2]
    _minYear=load[3]
    _maxYear=load[4]
