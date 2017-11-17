from QSet import *
from COBWEB import *

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
    vertices.appendleft(cobwebTree.root)
    nr_vertices = 1
    v_label = [cobwebTree.root.category]
    while len(vertices):
              curr = vertices.popleft()
              for child in curr.children:
                    vertices.append(child)
                    nr_vertices +=1
                    child.category = child.category + child.nameFromInfo()
                    v_label.append(child.category)

    G = Graph.Tree(nr_vertices, 3)
    lay = G.layout('rt')
    position = {k: lay[k] for k in range(nr_vertices)}
    Y = [lay[k][1] for k in range(nr_vertices)]
    M = max(Y)  
    es = EdgeSeq(G)#Sequence of edges
    E = [e.tuple for e in G.es] # list of edges
    L = len(position)
    Xn = [position[k][0] for k in range(L)]
    Yn = [(2*M-position[k][1]) for k in range (L)]
    Xe = []
    Ye = []

    for edge in E:
        Xe+=[position[edge[0]][0],position[edge[1]][0], None]
        Ye+=[2*M-position[edge[0]][1],2*M-position[edge[1]][1], None]

    labels = v_label

    #Used for adding the annotation style to the nodes in our display tree
    def make_annotations(pos, text, font_size=10, font_color='rgb(250,250,250)'):
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

    layout = dict(title= 'Tree with Reingold-Tilford Layout',
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



#########################################################
#
#
#                    BODY
#
#
#########################################################
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
for atom in reformattedSet[0]:
    cobwebTree.cobweb(atom)
    treeprint = (cobwebTree.root.pretty_print(0))
    print(treeprint)


makeTreeGraphCOBWEB(cobwebTree)


print("hello")