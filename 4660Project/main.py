from QSet import *


#Create 12 sets of 1001 sample queries, each query is a list (feature vector) where each sub-list is an atom (attribute,op,value)
def CreateSets():
    ret = list(13*[None])
    QS = QSet()
    #Set 1 is batched queries
    QS.GenerateSet(1)
    ret[0] = QS.querySet
    #set 2 is cycled queries
    QS.GenerateSet(2)
    ret[1] = QS.querySet
    #set 3-12 is random order
    for i in range(2,12):
        QS.GenerateSet(3)
        ret[i] = QS.querySet
    return ret

qsets = CreateSets()
print("hello")