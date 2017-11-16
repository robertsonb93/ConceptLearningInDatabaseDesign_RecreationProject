from QSet import *
from COBWEB import *

#Create 12 sets of 1001 sample queries, each query is a list (feature vector) where each sub-list is an atom (attribute,op,value)
def CreateSets():
    ret = list(12*[None])
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
reformattedSet = list()

#we have 2 issues, I believe that feature vectors for cobweb need all be the same length. any length difference needs to be filled with unknown. But were do they belong?
#see page 281 part B
for qset in qsets: 
    subset = list()
    for featureVec in qset:
        newFV = list()
        for atom in featureVec:
            newstr = ''.join(filter(lambda ch: ch not in " \",\'[]", repr(atom)))
            newFV.append(newstr) #WE are converting all the atoms (a list) to a string representation, and removing certain characters
        subset.append(newFV)
    reformattedSet.append(subset)



cobwebTree = COBWEBTree()
for fv in reformattedSet[0]:
    cobwebTree.cobweb(cobwebTree.root,fv)
    treeprint = (cobwebTree.root.pretty_print(0))
    #print(treeprint)


print("hello")