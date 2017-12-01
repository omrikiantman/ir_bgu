#define a term in a document
class Term():

    def __init__(self,name = None,isHeader = False):
        self.name = name
        self.count = 1 if name else 0
        self.isHeader = isHeader

    def add_count(self):
        self.count = self.count + 1

    def __repr__(self):
        return "token name is %s, has %s counts and isHeader:%s" %(self.name,self.count,self.isHeader)

    def __str__(self):
        return self.__repr__()