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
    newAtomVec = list()
    for atomVec in qset:
        newAtom = list()
        for atom in atomVec: #We are turning each atom for just being values, to being featureType,value pairs, Because cobweb is fun.
            first = ("attr",atom[0])
            second = ("op",atom[1])
            third = ("value",atom[2])
            newAtom = [first,second,third]

        newAtomVec.append(newAtom) 

    reformattedSet.append(newAtomVec) 



cobwebTree = COBWEBTree()
for atom in reformattedSet[11]:
    cobwebTree.cobweb(cobwebTree.root,atom)
    treeprint = (cobwebTree.root.pretty_print(0))
    print(treeprint)


print("hello")