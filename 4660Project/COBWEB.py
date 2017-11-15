class COBWEBTree(object):
   #Is the actual classfication tree
   def __init__(self):
       self.root = COBWEBNode() #When created, we will create our first node.
       self.root.tree = self

   #The core of running cobweb, https://en.wikipedia.org/wiki/Cobweb_(clustering)
   def cobweb(self,root,featureVector):
       if not len(root.children): #If dont have any children (aka a leaf)
           root.children.append(copy(root)) #we create a child in our exact likeness
           newcategory(featureVector) #Add a new child that uses this feature vectors values
           root.insert(featureVector)  #Update this roots information
       else:
           root.insert(featureVector) #update this roots statistics
           bestCU = 0
           bestChild = root.children[0]
           bestChild2 = root.children[1]

           for child in root.children:#Find the children with the best CU if the feature vector went to them
               cu = getCUInserted(child,featureVector)
               if (bestCU < cu):
                   bestChild2 = bestChild
                   bestChild = child





class COBWEBNode(object):
    #Is the nodes in the classifcation tree

    def __init__(self):
        #Each node needs the following
        #number of unique feature vectors seen
        #number of times each feature occurs (like in attribute, the number of times we have seen cust_name)
        #Who the parent is
        #List of all the children
        #The tree the node belongs to
        self.vectorCount = 0
        self.featureCount = set() #each element will be a pair of feature and count
        self.parent = None
        self.children = []
        self.tree = None



