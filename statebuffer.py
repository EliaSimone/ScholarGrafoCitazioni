class StBuffer:
    def __init__(self):
        self._l=[]
        self._pos=-1
    
    def push(self, item):
        self._pos+=1
        self._l.insert(self._pos,item)
        self._l=self._l[:self._pos+1]

    def back(self):
        if self._pos<1:
            return None
        self._pos-=1
        return self._l[self._pos]

    def forward(self):
        if self._pos==len(self._l)-1:
            return None
        self._pos+=1
        return self._l[self._pos]

    def clear(self):
        self._l=[]
        self._pos=-1
