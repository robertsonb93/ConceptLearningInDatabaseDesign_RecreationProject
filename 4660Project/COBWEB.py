class COBWEBTree(object):
   #Is the actual classfication tree
    def __init__(self):
        self.root = COBWEBNode() #When created, we will create our first node.
        self.root.tree = self


    #The core of running cobweb, https://en.wikipedia.org/wiki/Cobweb_(clustering)
    def cobweb(self,root,featureVector):
        if not len(root.children): #If dont have any children (aka a leaf)
            root.children.append(copy(root)) #we create a child in our exact likeness
            root.newcategory(featureVector) #Add a new child that uses this feature vectors values
            root.insert(featureVector)  #Update this roots information
        else:
            root.insert(featureVector) #update this roots statistics
            bestCU = 0
            bestChild = root.children[0]
            bestChild2 = root.children[1]

            for child in root.children:#Find the children with the best CU if the feature vector went to them
                cu = root.getCUInserted(child,featureVector)
                if (bestCU < cu):
                    bestChild2 = bestChild
                    bestChild = child
            #Now we need to find what the CU would be for three different actions, and pick the best action
            newCatCu = root.getCUNewCategory(featureVector) #Get the CU for if we just make a new child from the record
            mergeCU = root.getMergeCU(bestChild,bestChild2)
            splitCU = root.getSplitCU(bestChild)
            passOnCU = root.getCobwebCU(bestChild,featureVector)

            d = {"newCatCu" : newCatCu, "mergeCU" : mergeCU, "splitCU" : splitCU, "passOnCU" : passOnCU} #Create a dictionary with the operations and their values
            maxVar = max(d,key=d.get)#find the key with the max value
           
            if maxVar == "newCatCU":
                root.newcategory(featureVector)
            elif maxVar == "mergeCU":
                root.merge(bestChild,bestChild2)
                cobweb(root,featureVector)
            elif maxVar == "splitCU":
                root.split(bestChild)
                cobweb(root,featureVector)
            elif maxVar == "passOnCU":
                cobweb(bestChild,featureVector)
            else:
                print(("SomeThing wen wrong and maxVar was not determined to match : maxVar = " + maxVar))




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
        self.featureCount = dict() #each element will be a pair of feature and count
        self.parent = None
        self.children = []
        self.tree = None


    #Calculates the category utility, https://en.wikipedia.org/wiki/Category_utility
    #helpful guide I am based off of https://msdn.microsoft.com/en-us/magazine/dn198247.aspx
    def categoryUtility(self):
        #It is described in as being three parts
        #Part one is caluclation of the P(C_k), which is the probability of a cluster (in this case the probability of a node and its children)
        #For each child in the self node, divide the number of feature vectors each child has seen by the number of feature vectors the parent has seen.
        probCK = list()
        for child in self.children:           
            probCK.append((child.vectorCount / self.vectorCount))

        #the second and third part are the same, only the second part is on the children, and the third is on the self.
        
        #Lets do the children first, which corresponds to the middle double summation in the CU formula, known as the childs expected correct guesses, or conditional probability terms
        # it works like this, get the total number of feature vectors seen in by the child (ie. cust_name, = , name), which is child.vectorCount
        # get the number of times we have seen each unique feature (ie cust_name)
        # for each feature count divide it by the feature vector count, and add the (results**2)
        conditionalProbabilities = list()
        for child in self.children:
            partialSum = 0
            for feature in child.featureCount: #remember that feature in this is a pair of the feature and the count for it
                partialSum += (feature.value / child.vectorCount)**2
            
            conditionalProbabilities.append(partialSum) # a list of all our conditional probabilities for each child

        #Now step three is the repeat the same as above, but for the self node, this is the selfs expected correct guess, or unconditional probability term
        unconditional_probability = 0
        for feature in self.featureCount:
            unconditional_probability += (feature.value / self.vectorCount)**2
        
        #step Four is to finish the first summation, ands combine the terms,
        #sum += step1 * (step2 - step3)
        #and then do the division from the beginning of the formula
        sum = 0
        for i in range(len(self.children)):
            sum += probCK[i] * (conditionalProbabilities[i] - unconditional_probability)
        CU = sum / len(self.children)
        return CU

    #used to declare that a new node should be created in the tree, (using the feature vector as the feature values)           
    def newcategory(self,featureVector):
        newChild = COBWEBNode()
        newChild.vectorCount = 1
        for atom in featureVector:
            for feature in atom:
                newChild.featureCount[feature] = 1 

        newChild.parent = self
        newChild.tree = self.tree

        self.children.append(newChild)

    #used to show that a feature vector has been seen by the node
    #updates the number of unique features that this node has seen and updates the feature counts it has seen
    def insert(self,featureVector):
        
        for atom in featureVector:            
            for feature in atom:
                isunique = False
                if feature in self.featureCount:
                    self.featureCount[feature] += 1
                else:
                    isunique = True #One of the features in the atom was different thus it is a novel atom to see
                    self.featureCount[feature] = 1
            
            if isunique: #For each atom, check if it is novel, if it is then insert it
                self.vectorCount += 1

    #It has been determined the CU for having these two child nodes would be improved if they became the same node
    #Merging two nodes means replacing them by a node whose children is the union of the original nodes' sets of children
    # and which summarizes the attribute-value distributions of all objects classified under them.

    #wikipedia doesnt describe the merge making the two children the children of the new node, but the paper and the online example show different
    #https://github.com/cmaclell/concept_formation/blob/master/concept_formation/cobweb.py
    #http://axon.cs.byu.edu/~martinez/classes/678/Papers/Fisher_Cobweb.pdf

    def merge(self,bestChild,bestChild2):
        #From the paper, merging nodes is creating a new node, and summing the attribute-value counts of the nodes being merged,
        # the original nodes are made children of the newly created node. pg.151,152

        newNode = COBWEBNode()
        newNode.parent = self
        newNode.tree = self.tree

        #Take the counts from the merging children
        newNode.vectorCount += bestChild.vectorCount #update counts from the children
        newNode.vectorCount += bestChild2.vectorCount
        for feature in bestChild.featureCount:
            newNode.featureCount[feature] = bestChild.featureCount[feature] #Copy all the feature counts from the best child into our new node

        for feature in bestChild2.featureCount:
             if feature not in newNode.featureCount:
                newNode.featureCount[feature] = 0#If the feature was not in bestChild, then it is set to zero in newnode, 
             newNode.featureCount[feature] += bestChild2.featureCount[feature] #The feature is then incremented by the count from bestChild2
        
        newNode.vectorCount = len(newNode.featureCount)#Our initial unique features seen is the len of the features we have in our dictionary
                   

        #The merging nodes are made the children of the new node
        bestChild.parent = newNode
        bestChild2.parent = newNode
        newNode.children.append(bestChild)
        newNode.children.append(bestChild2)

        #remove the children from the old parent (self) and add the new node
        self.children.remove(bestChild)
        self.children.remove(bestChild2)
        self.children.append(newNode)



