from collections import defaultdict

class COBWEBTree(object):
   #Is the actual classfication tree
    def __init__(self):
        self.root = COBWEBNode() #When created, we will create our first node.
        self.root.category = "ROOT"
        self.current = self.root
        self.root.tree = self


    #The core of running cobweb, https://en.wikipedia.org/wiki/Cobweb_(clustering)
    def cobweb(self,featureVector):
        root = self.root
        while root:

            if not len(root.children): #If dont have any children (aka a leaf) #This is BASE CASE
                if root.featureVectorsMatch(featureVector) or root.vectorCount == 0: #if the featureVector is an exact match for the leaf node, or it is the first time entering 
                    root.insert(featureVector)#Then just update the values for this node
                

                else: #else its not a match or the first entry
                    newParent = root.__makeCopy__() #create a clone of root, this would be a bug if we didnt check len of children first
                    newParent.insert(featureVector) #Modify roots clone
                    root.parent = newParent #root now the child of roots modified clone
                    newParent.children.append(root)
                    newParent.newcategory(featureVector) #create a sibling leaf for new novel featureVector

                    if not(newParent.parent == None): #True : newParent is an internal node (not tree root)
                        newParent.parent.children.remove(root) #remove root from its ex-parent
                        newParent.parent.children.append(newParent) #Tell the newParent that is has a new child
                    else:
                        self.root = newParent #If there was no parent, newParent is the new root to the tree

                return;
     
            else:#This root is not a leaf node.
                
                notSingleChild = len(root.children) > 1                  
                bestChild = root.children[0]
                if notSingleChild: #Only enter if we arent the only child
                    bestChild2 = root.children[1]
                    bestCU = 0 # we can use zero, because a negative value implies that the child has seen something the parent hasnt, which isnt possible (without bugs)
                    bestCU2 = 0
                    for child in root.children:#Find the children with the best CU if the feature vector went to them
                        cu = root.getCUInserted(child,featureVector)
                        if (bestCU < cu):
                            bestCU2 = bestCU
                            bestChild2 = bestChild
                            bestCU = cu
                            bestChild = child
                        elif (bestCU2 < cu):
                            bestCU2 = cu
                            bestChild2 = child
                    if(bestChild == bestChild2):
                        print("Dupolicate children")
                    mergeCU = root.getMergeCU(bestChild,bestChild2)

                else:#We have only a single child, so cant check for merging, and the best child CU is the only child CU
                    mergeCU = 0
                    bestCU = root.getCUInserted(bestChild,featureVector)

                #Now we need to find what the CU would be for three different actions, and pick the best action
                newCatCu = root.getCUNewCategory(featureVector) #Get the CU for if we just make a new child from the recor            
                splitCU = root.getSplitCU(bestChild)
                #passOnCU = root.getCobwebCU(bestChild,featureVector) #this is related to CUInserted for the best child

                d = {"newCatCU" : newCatCu, "mergeCU" : mergeCU, "splitCU" : splitCU, "passOnCU" : bestCU} #Create a dictionary with the operations and their values
                maxVar = max(d,key=d.get)#find the key with the max value

                if maxVar == "newCatCU":
                    root.insert(featureVector) #update this roots statistics
                    newchild = root.newcategory(featureVector)
                    return; #we created a new child for this feature vector, so we dont need to do anything further with it
                elif maxVar == "mergeCU":
                    root.insert(featureVector) #update this roots statistics
                    newnode = root.merge(bestChild,bestChild2)
                    root = newnode #We will then restart the while loop with this as the new root
                elif maxVar == "splitCU":               
                    root.split(bestChild) # we will restart the loop with the same root                   
                elif maxVar == "passOnCU":
                    root.insert(featureVector) #update this roots statistics
                    root = bestChild # we will restart the loop with bestchild as root, and eval if their is a better fit in best child's children
                else:
                    print(("SomeThing wen wrong and maxVar was not determined to match : maxVar = " + maxVar))
                    return;




class COBWEBNode(object):
    #Is the nodes in the classifcation tree

    def __init__(self):
        #Each node needs the following
        #number of unique feature vectors seen
        #number of times each feature occurs (like in attribute, the number of times we have seen cust_name)
        #Who the parent is
        #List of all the children
        #The tree the node belongs to
        self.category = "Unset"
        self.vectorCount = 0
        self.featureCount = defaultdict(dict) #each key is a feature title(ie, attribute, op, value), then a second dict exists inside using the provided value, then a count of its occurance
        self.parent = None
        self.children = []
        self.tree = None

    def nameFromInfo(self):
        name = "<br>Features: \n<br>"
        for attr in self.featureCount:
            name += str(attr) + "{ "
            for val in self.featureCount[attr]:
                name += str(val) + "\n"

            name += "}<br>"
        name += "Vectors Seen: " + str(self.vectorCount)
        return name

    #utility function to create a duplicate of the given node
    def __makeCopy__(self):        
        temp = COBWEBNode()
        temp.category = (("copy_"+self.category))
        temp.tree = self.tree
        temp.parent = self.parent
        temp.vectorCount = self.vectorCount
        for feature in self.featureCount:
            for val in self.featureCount[feature]:
                temp.featureCount[feature][val] = self.featureCount[feature][val]

        for child in self.children:
            temp.children.append(child)

        return temp

    #Determine if features in the feature vector are the same as the features in self node
    def featureVectorsMatch(self,featureVector):
        for a,b in featureVector: #a Feature vec is a single atom, and each atom contains a list of pairs
            if b not in self.featureCount[a]:
                    print(("Doesnt match any keys "+b + " in feature " + a))
                    return False           
        return True


    #Calculates the category utility, https://en.wikipedia.org/wiki/Category_utility
    #helpful guide I am based off of https://msdn.microsoft.com/en-us/magazine/dn198247.aspx
    def categoryUtility(self):
        #It is described in as being three parts
        #Part one is caluclation of the P(C_k), which is the probability of a cluster (in this case the probability of a node and its children)
        #For each child in the self node, divide the number of feature vectors each child has seen by the number of feature vectors the parent has seen.
        if len(self.children) == 0:
            return 0

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
            for feature in child.featureCount: #remember that feature is a key to another dictionary
                for val in child.featureCount[feature]:
                    count  = child.featureCount[feature][val]
                    partialSum += (count / child.vectorCount)**2
            
            conditionalProbabilities.append(partialSum) # a list of all our conditional probabilities for each child

        #Now step three is the repeat the same as above, but for the self node, this is the selfs expected correct guess, or unconditional probability term
        unconditional_probability = 0
        for feature in self.featureCount:
            for val in self.featureCount[feature]:
                count  = self.featureCount[feature][val]
                unconditional_probability += (count / self.vectorCount)**2
        
        #step Four is to finish the first summation, ands combine the terms,
        #sum += step1 * (step2 - step3)
        #and then do the division from the beginning of the formula
        sum = 0
        for i in range(len(self.children)):
            sum += probCK[i] * (conditionalProbabilities[i] - unconditional_probability)
        CU = sum / len(self.children)
        return CU

    #used to declare that a new node should be created in the tree, (using the feature vector as the feature values)
    ##Returns the newly created child node           
    def newcategory(self,featureVector):
        newChild = COBWEBNode()
        
        newChild.vectorCount = 1
        for feature,value in featureVector: #remember featureVector is a list of pairs
            newChild.featureCount[feature][value] = 1 

        newChild.parent = self
        newChild.tree = self.tree

        self.children.append(newChild)
        newChild.category = "NewCategory\n"

        return newChild

    #used to show that a feature vector has been seen by the node
    #updates the number of unique features that this node has seen and updates the feature counts it has seen
    def insert(self,featureVector):
        isunique = False
        for feature,value in featureVector:                       
            if value in self.featureCount[feature]:
                isunique =True #Put this here for debugging purposed TODO: consider that this needs to be removed
                self.featureCount[feature][value] += 1
            else:
                isunique = True #One of the feature values in the atom was different thus it is a novel atom to see
                self.featureCount[feature][value] = 1
            
        if isunique: #For the feature vector, check if it is novel, if it is then insert it
            self.vectorCount += 1

    #It has been determined the CU for having these two child nodes would be improved if they became the same node
    #Merging two nodes means replacing them by a node whose children is the union of the original nodes' sets of children
    # and which summarizes the attribute-value distributions of all objects classified under them.
    #https://github.com/cmaclell/concept_formation/blob/master/concept_formation/cobweb.py
    #http://axon.cs.byu.edu/~martinez/classes/678/Papers/Fisher_Cobweb.pdf
    ##Returns the newly created child node
    def merge(self,bestChild,bestChild2):
        #From the paper, merging nodes is creating a new node, and summing the attribute-value counts of the nodes being merged,
        # the original nodes are made children of the newly created node. pg.151,152
        newNode = COBWEBNode()
        newNode.category = "Merged\n"
        newNode.parent = self
        newNode.tree = self.tree

        #Take the counts from the merging children
        newNode.vectorCount += bestChild.vectorCount #update counts from the children
        newNode.vectorCount += bestChild2.vectorCount
        for feature in bestChild.featureCount:
            for value in bestChild.featureCount[feature]:
                newNode.featureCount[feature][value] = bestChild.featureCount[feature][value] #Copy all the feature counts from the best child into our new node

        for feature in bestChild2.featureCount:
            for value in bestChild2.featureCount[feature]:
                if value not in newNode.featureCount[feature]:
                    newNode.featureCount[feature][value] = 0#If the feature was not in bestChild, then it is set to zero in newnode, 
                newNode.featureCount[feature][value] += bestChild2.featureCount[feature][value] #The feature is then incremented by the count from bestChild2   
                   
        #The merging nodes are made into children of the new node
        bestChild.parent = newNode
        bestChild2.parent = newNode
        newNode.children.append(bestChild)
        newNode.children.append(bestChild2)

        #remove the children from the old parent (self) and add the new node
        self.children.remove(bestChild)
        self.children.remove(bestChild2)
        self.children.append(newNode)

        return newNode
        
    #splitting is when a nodeA is removed, where the children of nodeA are then reparented to the parent of nodeA
    #its simple, remove the nodeA from its parent (self), and move all of nodeA's children to the parent (root)
    def split(self,bestChild):
        self.children.remove(bestChild)
        for child in bestChild.children:
            child.parent = self
            child.tree = self.tree
            self.children.append(child)



    #Get what the category_utility would be if we gave the featureVector to our child
    def getCUInserted(self,child,featureVector):
        temp = self.__makeCopy__()
        temp.children.remove(child) #We dont want to see the reference of the actual child 

        tempChild = child.__makeCopy__()
        tempChild.parent = temp  # I dont think we need to set who the parent actually is. TODO 
        tempChild.tree = temp.tree  #I dont think setting the parent is needed. TODO      

        temp.children.append(tempChild)
        tempChild.insert(featureVector)

        cu = temp.categoryUtility()
        return cu


    #Get the CU if we just make a new child from the featureVector
    def getCUNewCategory(self,featureVector):
        temp = self.__makeCopy__()

        tempChild = COBWEBNode()
        tempChild.parent = temp  # I dont think we need to set who the parent actually is. TODO 
        tempChild.tree = temp.tree #I dont think setting the parent is needed. TODO       
        tempChild.insert(featureVector)

        temp.children.append(tempChild)

        cu = temp.categoryUtility()
        return cu


    #Get the category_utility for the merge of the 2 best children
    def getMergeCU(self,bestChild,bestChild2):
         #We will create temps of the bestchildren, and the the root (self)

         #Create out self copy, but remove the bestChildren from its children, they will be re added as temps
         tempSelf = self.__makeCopy__()
         tempSelf.children.remove(bestChild)
         tempSelf.children.remove(bestChild2)

         #Create the temporary best children, but set the parent to the tempself (would have been self)
         tempBC = bestChild.__makeCopy__()
         tempBC.parent = tempSelf #I dont think setting the parent is needed. TODO
         tempBC.tree = tempSelf.tree #I dont think setting the tree is needed. TODO

         tempBC2 = bestChild2.__makeCopy__()
         tempBC2.parent = tempSelf #I dont think setting the parent is needed. TODO
         tempBC2.tree = tempSelf.tree #I dont think setting the tree is needed. TODO

         tempSelf.children.append(tempBC)
         tempSelf.children.append(tempBC2)

         #Merge the temp nodes together,so we can calculate the category utility on them.
         tempSelf.merge(tempBC,tempBC2)
         
         cu = tempSelf.categoryUtility()
         return cu

    #Get the category_utility for splitting the best child
    def getSplitCU(self,bestChild):

         #create a temp node as a copy of our current, we will then avoid adding the best child to it, but will add the bestChild children
         temp = self.__makeCopy__()
         temp.children.remove(bestChild)#Remove the best child from the temps children
         
         for child in bestChild.children:
                 temp_child = child.__makeCopy__()
                 temp.children.append(temp_child) #We dont need to set the childrens parent for this split. as it isnt used in the category utility

         cu = temp.categoryUtility()#WE have created our dummy cluster (root node to leafs, now lets calculate the categoryUtility of it)
         return cu




    #Stole this from https://github.com/cmaclell/concept_formation/blob/master/concept_formation/cobweb.py
    def pretty_print(self, depth=0):
        """
        Print the categorization tree
        The string formatting inserts tab characters to align child nodes of
        the same depth.
        :param depth: The current depth in the print, intended to be called
                        recursively
        :type depth: int
        :return: a formated string displaying the tree and its children
        :rtype: str
        """

        ret = str(('\t' * depth) + "|-" + str(self.featureCount) + ":" +
                    str(self.vectorCount) + '\n')

        for c in self.children:
            ret += c.pretty_print(depth+1)

        return ret