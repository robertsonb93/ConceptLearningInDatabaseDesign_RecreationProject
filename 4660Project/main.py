from QSet import *
from COBWEB import *
import time
import matplotlib.pyplot as plt
from collections import deque

import plotly
import plotly.graph_objs as go
import igraph
from igraph import *




#Used to create a HTML graph of the tree produced by the COBWEB tree,
#Input is the  Tree
def makeTreeGraphCOBWEB(cobwebTree):
    #lets use Igraph to set up the tree, we can then use plotly to display what the tree looks like
    #Count number of vertices in the tree
    vertices = deque()
    nr_vertices = 0
    vertices.appendleft((cobwebTree.root,nr_vertices))
    v_label = [cobwebTree.root.category + cobwebTree.root.nameFromInfo()]
    G = Graph()
    G.add_vertices(1) #add a single vertex to the graph for the root
    while len(vertices):
              (curr,currNumber) = vertices.popleft()
              for child in curr.children:
                    nr_vertices +=1
                    vertices.append((child,nr_vertices))
                    G.add_vertices(1)
                    G.add_edges([(currNumber,nr_vertices)])#create an edge from the parent (curr) to the child(the latest vertice added)                   
                    child.category = child.category + child.nameFromInfo()
                    v_label.append(child.category)

    lay = G.layout('rt',root = [0])#sets the layout to reingold tilford

    #lay = G.layout_reingold_tilford(mode="in", root=0)
    position = {k: lay[k] for k in range(nr_vertices+1)}
    Y = [lay[k][1] for k in range(nr_vertices)]
    M = max(Y)  
    es = EdgeSeq(G)#Sequence of edges
    E = [e.tuple for e in G.es] # list of edges
    L = len(position)
    Xn = [position[k][0] for k in range(L)]#getting the positions for the X locations
    Yn = [(2*M-position[k][1]) for k in range (L)]#getting the positions for Y locations
    Xe = []
    Ye = []

    for edge in E:
        Xe+=[position[edge[0]][0],position[edge[1]][0], None]#seems to be the start-end for each edge 
        Ye+=[2*M-position[edge[0]][1],2*M-position[edge[1]][1], None]

    labels = v_label

    #Used for adding the annotation style to the nodes in our display tree
    def make_annotations(pos, text, font_size=10, font_color='rgb(1,1,1)'):
            L=len(pos)
            if len(text)!=L:
                raise ValueError('The lists pos and text must have the same len')
            annotations = go.Annotations()
            for k in range(L):
                annotations.append(
                    go.Annotation(
                        text=text[k], # or replace labels with a different list for the text within the circle  
                        x=pos[k][0], y=2*M-position[k][1],
                        xref='x1', yref='y1',
                        font=dict(color=font_color, size=font_size),
                        showarrow=False)
                )
            return annotations

    

    lines = go.Scatter(x=Xe,
                       y=Ye,
                       mode='lines',
                       line=dict(color='rgb(210,210,210)', width=1),
                       hoverinfo='none'
                       )
    dots = go.Scatter(x=Xn,
                      y=Yn,
                      mode='markers',
                      name='',
                      marker=dict(symbol='dot',
                                    size=18, 
                                    color='#6175c1',    #'#DB4551', 
                                    line=dict(color='rgb(50,50,50)', width=1)
                                    ),
                      text=labels,
                      hoverinfo='text',
                      opacity=0.8
                      )


    axis = dict(showline=False, # hide axis line, grid, ticklabels and  title
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                )

    layout = dict(title= 'COBWEB Tree',
                  annotations=make_annotations(position, v_label),
                  font=dict(size=12),
                  showlegend=False,
                  xaxis=go.XAxis(axis),
                  yaxis=go.YAxis(axis),          
                  margin=dict(l=40, r=40, b=85, t=100),
                  hovermode='closest',
                  plot_bgcolor='rgb(248,248,248)'          
                  )

    data=go.Data([lines, dots])
    fig=dict(data=data, layout=layout)
    fig['layout'].update(annotations=make_annotations(position, v_label))
    plotly.offline.plot(fig, filename='Tree-COBWEB.html')

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

def countHierarchy(root):
    count = 0
    nodeQueue = deque()
    nodeQueue.append(root)
    while len(nodeQueue):
        count += 1#Count the node when we remove it.
        active = nodeQueue.popleft()
        for child in active.children:
            nodeQueue.append(child)
    return count
    

#########################################################
#
#
#                    BODY
#
#
#########################################################


qsets = CreateSets()
reformattedSets = list()

#we have 2 issues, I believe that feature vectors for cobweb need all be the same length. any length difference needs to be filled with unknown. But were do they belong?
#see page 281 part B

for qset in qsets:#get a specific set of queries
    newQset = list()
    for query in qset:
        newQuery = list()
        for atom in query: #We are turning each atom for just being values, to being featureType,value pairs, Because cobweb is fun.           
            first = ("attr",atom[0])
            second = ("op",atom[1])
            third = ("value",atom[2])
            newAtom = [first,second,third]
            newQuery.append(newAtom)
        newQset.append(newQuery)
    reformattedSets.append(newQset) 



setCount = -1
level1Nodes = list()
level2Nodes = list()
procTime = list()
hierarchySize = list()
for set in reformattedSets:
    
    cobwebTree = COBWEBTree()
    level1Nodes.append(list())
    level2Nodes.append(list())
    
    hierarchySize.append(list())
    setCount += 1#which set we are currently on
    procTime.append(time.time())#Start the timer for running processing this query set
    count =0#How many queries we have processed this set
    for query in set:
        count +=1
        for atom in query:
            cobwebTree.cobweb(atom)            
        print(("Set: "+str(setCount) + "/12 - Iteration: " +str(count)))
        hierarchySize[setCount].append(countHierarchy(cobwebTree.root)) #done at each query

    #We finished building the tree, lets do some statistics on it. 
    #get the first/second level after the root.
    procTime[setCount] -= time.time()
    for nodes in cobwebTree.root.children:
        level1Nodes[setCount].append(nodes)
        for lvl2 in nodes.children:
            level2Nodes[setCount].append(lvl2)

    

    #makeTreeGraphCOBWEB(cobwebTree)#Display the tree we created
#compare how many nodes had atleast 1 matching node on layer 1

def findSameDiff(nodeList):
    matches = 0
    different = 0
    for set in range(len(nodeList)):#Do for every node on the first level of its tree
        for active in nodeList[set]:
            MatchNothing = True #Assume it matches nothing (is a unique concept)
            for setPrime in range(len(nodeList)): #for every other node
                if(setPrime != set):#Not from our current tree
                    for comparee in nodeList[setPrime]:
                        DoesMatch = True #Assume that the active node matches the comparee node
                        for feature in active.featureCount:#Iterate the features they learned.
                            for val in active.featureCount[feature]:
                                if(val not in comparee.featureCount[feature]):
                                    DoesMatch = False
                                    break;
                        if(DoesMatch):
                            MatchNothing = False
                            matches += 1
                            nodeList[setPrime].remove(comparee)#So we dont double count it.
                else:
                    continue
            if(MatchNothing):
                different += 1
            nodeList[set].remove(active)#So we dont double count this.
    return [matches,different]

[matches1,different1] = findSameDiff(level1Nodes)
[matches2,different2] = findSameDiff(level2Nodes)
print(("Number of Same LVL1: " + str(matches1)))
print(("Number of Different LVL1: "+ str(different1)))
print(("Number of Same LVL2: " + str(matches2)))
print(("Number of Different LVL2: "+ str(different2)))

print(("Times for Eval: "))
print(procTime)
x_points = [x for x in range(len(reformattedSets))]

plt.bar(x_points,[y*-1 for y in procTime],1/1.5)
plt.xlabel('QuerySet')
plt.ylabel('Time(Seconds)')
plt.show()#Plot the time it took


avg = list([0] * 1001) # init to the length of number of queries

x_points = [i for i in range(1001)]
for i in range(len(hierarchySize)):
    if i == 0 or i == 1:
        y_points = list()#fill with the heiarchies we collected
        for h in hierarchySize[i]:
            y_points.append(h)
        plt.plot(x_points,y_points)
    else:
        count = 0
        for h in range(len(hierarchySize[i])):
            avg[h] += (hierarchySize[i][h] / 10)#to average it

plt.plot(x_points,avg)
plt.xlabel('Queries')
plt.ylabel('Hierarchy Size')
plt.legend(['QSet1','QSet2','QSet3-12(avg)'],loc = 'upper left')
plt.show()

print("hello")