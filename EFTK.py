class EFTK:
    
    def __init__(self, node, pst):
        self.matches = set([])
        if node.value in pst.root.posVector[0].keys():
            self.matches.update(pst.root.posVector[0][node.value].ruleList)
            if len(node.children[0].children)>0:
                self.matchChildren(node.children, pst.root.posVector[0][node.value])

    def matchChildren(self, children, pstnode):
        if len(self.matches)>0:
            if len(children)>len(pstnode.posVector):
                self.matches = set([])
            else:
                for i in range(0, len(children)):
                    child = children[i]
                    if child.value in pstnode.posVector[i].keys():
                        self.matches = self.matches & pstnode.posVector[i][child.value].ruleList
                        if len(child.children[0].children)>0 and len(self.matches)>0:
                            self.matchChildren(child.children, pstnode.posVector[i][child.value])
                    else:
                        self.matches = set([])

class RawData:
    
    def __init__(self, inPath, outPath):
        self.labels = []

        inTrain = open(inPath, 'r')
        outTrain = open(outPath, 'w')
        for line in inTrain:
            data = line.split()
            self.labels.append(data[0].strip()[0:data[0].strip().find(':')])
            sentence = ''
            for i in range(1, len(data)):
                sentence += data[i] + ' '
            sentence = sentence.strip()
            outTrain.write(sentence + '\n')
            
        inTrain.close()
        outTrain.close()
        
#Class responsible for holding a generic Tree node
class TreeNode:
    def __init__(self):
        self.value = ''
        self.parent = ''
        self.children = []
    
    def setValue(self, v):
        self.value = v
    
    def setParent(self, tn):
        self.parent = tn
        
    def addChild(self, c):
        self.children.append(c)

#Class responsible for holding a generic Tree
class Tree:
    def __init__(self, treeString=None):
        if treeString == None:
            self.root = None
        else:
            self.root = self.createTreeFromString(treeString)
            self.root.setParent(None)
        
    def printTree(self):
        self.printNode(self.root, 0)
        
    def printNode(self, node, tabulation):
        prefix = ''
        for i in range(0, tabulation):
            prefix = prefix + '\t'
        print(prefix+node.value)
        for child in node.children:
            self.printNode(child, tabulation+1)
                
    def printTreeWithAAKData(self, pstdata):
        self.printNodeWithAAKData(self.root, 0, pstdata)
        
    def printNodeWithAAKData(self, node, tabulation, pstdata):
        prefix = ''
        for i in range(0, tabulation):
            prefix = prefix + '\t'
        print(prefix+node.value)
        if node in pstdata.link:
            PSTNode = pstdata.link[node]
            for rule in PSTNode.ruleList:
                print(prefix+rule)
        for child in node.children:
            self.printNodeWithAAKData(child, tabulation+1, pstdata)
            
    def saveTreeWithAAKData(self, pstdata, file):
        self.saveNodeWithAAKData(self.root, 0, pstdata, file)
        
    def saveNodeWithAAKData(self, node, tabulation, pstdata, file):
        prefix = ''
        for i in range(0, tabulation):
            prefix = prefix + '\t'
        file.write(prefix+node.value+'\n')
        if node in pstdata.link:
            PSTNode = pstdata.link[node]
            for rule in PSTNode.ruleList:
                file.write(prefix+rule+'\n')
        for child in node.children:
            self.saveNodeWithAAKData(child, tabulation+1, pstdata, file)
        
    def createTreeFromString(self, treeString):
        auxC = 1
        value = ''
        while not treeString[auxC]==' ':
            value = value+treeString[auxC]
            auxC = auxC+1
        value = value.strip()
        
        if not treeString[auxC+1]=='(':
            auxC = auxC+1
            child = ''
            while not treeString[auxC]==')':
                child = child+treeString[auxC]
                auxC = auxC+1
            result = TreeNode()
            result.setValue(value)
            childNode = TreeNode()
            childNode.setValue(child)
            childNode.setParent(result)
            result.addChild(childNode)
            return result
        else:
            result = TreeNode()
            result.setValue(value)
            auxC = auxC+1
            start = auxC
            level = 2
            walker = auxC+1
            while not level==0:
                if treeString[walker]=='(':
                    level = level+1
                elif treeString[walker]==')':
                    level = level-1
                    if level==1:
                        substring = treeString[start:walker+1]
                        substringNode = self.createTreeFromString(substring)
                        substringNode.setParent(result)
                        result.addChild(substringNode)
                        start = walker+1
                walker = walker+1
            return result

#Holds the information of an Agile Adaptive Knowledge Tree's node
class AAKNode:
    def __init__(self):
        self.value = ''
        self.parent = ''
        self.ruleList = set([])
        self.posVector = []
        self.alignments = {}
        
    def setParent(self, p):
        self.parent = p
        
    def setValue(self, v):
        self.value = v
        
    def addRule(self, r):
        self.ruleList.add(r)
        
class PSTree:
    def __init__(self):
        self.root = AAKNode()
        self.root.setValue('None')
        self.root.setParent('None')
        self.root.posVector.append({})
        
        self.prevAmount = 0;
        self.currAmount = 0;
        self.totalAmount = 0;
        self.savedAmount = 0;
    
    def addTreeToPST(self, tree, id):
        if isinstance(tree, Tree):
            self.prevAmount = self.currAmount
            self.addNodeToPST(tree.root, id, self.root.posVector[0], self.root)
        elif isinstance(tree, TreeNode):
            self.prevAmount = self.currAmount
            self.addNodeToPST(tree, id, self.root.posVector[0], self.root)
        
    def addNodeToPST(self, node, id, dict, parent):
        self.totalAmount += 1
        if node.value in dict.keys():
            self.savedAmount += 1
            PSTNode = dict[node.value]
            PSTNode.addRule(id)
            if len(node.children)>0:
                for i in range(0, len(node.children)):
                    if len(PSTNode.posVector)==i:
                        PSTNode.posVector.append({})
                    self.addNodeToPST(node.children[i], id, PSTNode.posVector[i], PSTNode)
        else:
            self.currAmount += 1
            PSTNode = AAKNode()
            PSTNode.setValue(node.value)
            PSTNode.setParent(parent)
            PSTNode.addRule(id)
            dict[node.value] = PSTNode
            if len(node.children)>0:
                for i in range(0, len(node.children)):
                    if len(PSTNode.posVector)==i:
                        PSTNode.posVector.append({})
                    self.addNodeToPST(node.children[i], id, PSTNode.posVector[i], PSTNode)
                    
    def printPSTree(self):
        self.printPSTNode(self.root, 0)
        
    def printPSTNode(self, node, tabulation):
        prefix = ''
        for i in range(0, tabulation):
            prefix = prefix + '\t'
            
        print(prefix + 'Value: ' + node.value)
        print(prefix + 'Rules:')
        for rule in node.ruleList:
            print(prefix + '\t' + rule)
        print(prefix + 'Vector Positions:')
        for i in range(0, len(node.posVector)):
            print(prefix + '\t Position ' + str(i) + ':')
            for key in node.posVector[i]:
                self.printPSTNode(node.posVector[i][key], tabulation+1)
   
class Utilities:
    
    @staticmethod
    def getLinearTrees(inPath):
        result = []
        
        tree = ''
        f1 = open(inPath, 'r')
        for line in f1: 
            if line.strip()=='':
                tree = tree.replace(') (', ')(')
                if not tree.strip()=='':
                    tree = tree.strip()[0:len(tree)-2]
                    result.append(tree)
                tree = ''
            else:
                if not line.strip()=='(ROOT':
                    tree = tree + line.strip() + ' ' 
        
        f1.close()
        
        return result

            
#Extract labels from sentences of the training set:
rawData_train = RawData('question_classification_train.txt', 'question_classification_train_sents.txt')

#Get linear trees from stanford parser training file:
linearTrees_train = Utilities.getLinearTrees('question_classification_train_sents_parsed.txt')


#Add all training ST's to PST:
nodecount = []
nodemeans = []
nodemean = 0

pst = PSTree()
M = {}
currIndex = 0
for i in range(0, len(linearTrees_train)):
    tree = Tree(linearTrees_train[i])
    visitedLabels = {}
    pile = [tree.root]
    initialIndex = currIndex
    maxIndex = -1

    while len(pile)>0:
        node = pile[0]
        pile.remove(node)
        if node.value in visitedLabels.keys():
            shift = visitedLabels[node.value]
            pst.addTreeToPST(node, currIndex + shift)
            visitedLabels[node.value] += 1
        else:
            pst.addTreeToPST(node, currIndex)
            visitedLabels[node.value] = 1
        if visitedLabels[node.value]>maxIndex:
            maxIndex = visitedLabels[node.value]
        if len(node.children[0].children)>0:
            pile.extend(node.children)

    for j in range(currIndex, currIndex + maxIndex):
        M[j] = i
    currIndex += maxIndex

#Extract labels from sentences of the test set:    
rawData_test = RawData('question_classification_test.txt', 'question_classification_test_sents.txt')

#Get linear trees from stanford parser test file:
linearTrees = Utilities.getLinearTrees('question_classification_test_sents_parsed.txt')

#Classify test sentences:
for string in linearTrees:
    K = {}
    tree = Tree(string)
    
    pile = [tree.root]
    while len(pile)>0:
        node = pile[0]
        pile.remove(node)
        if len(node.children[0].children)>0:
            pile.extend(node.children)
           
        matches = EFTK(node, pst).matches
        for match in matches:
            eqID = M[match]
            if eqID in K.keys():
                K[eqID] += 1
            else:
                K[eqID] = 1