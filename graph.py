'''
Created on 12-Nov-2013

@author: Raghavan
'''

class Graph(object):
    '''
    A graph with nodes and edges
    '''

    def __init__(self, comp_fn = None):
        '''
        Initialize the graph
        Comparison function is required for the sorting of components of the graph (see the comments
        for the get_connected_components method
        '''
        # Your code
        self.adjacency = {}#{'A':('C','G'), 'B':('G','C'), 'C':('A','B'), 'D':('F','E'), 'E':('F','D'), 'F':('D','E'), 'G':('A','B')}
        #print self.adjacency

    def is_node(self, node):
        '''
        Check if a given node is part of the graph
        '''
        # Your code
        if node in self.adjacency :
            return True


    def add_node(self, node):
        '''
        Add a new node to the graph without edges
        '''
        # Your code
        if not node in self.adjacency :
            self.adjacency[node] = ()
        #self.adjacency.append(node)
        

    def add_directed_edge(self, node1, node2):
        '''
        Add a directed edge going from node1 to node2
        You may not be able to assume that node1 or node2 are already there in the adjacency list
        '''
        # Your code
        if node1 not in self.adjacency :
            self.add_node(node1)
#         if not node2 in self.adjacency :
#             self.add_node(node2)
        #check later
        self.adjacency[node1] += (node2,)

            
    def add_edge(self, node1, node2):
        '''
        Add an undirected edge between node1 and node2
        This is the same as adding two directed edges
        '''
        # Your code
        self.add_directed_edge(node1, node2)
        self.add_directed_edge(node2, node1)
        
        
        
    
    def get_connected_components(self):
        '''
        Return a list of all the connected components (each connected component will be a sublist of the list that
        is returned). A connected component is just a list of nodes making up that component
        Algorithm:
        1. Keep a hash to assign component numbers to each node - if two nodes have the same component number
        then they belong to the same component.
        2. Walk through all the edges of the graph (for each key - every key is a node of the graph - of the adjacency 
        walk through all the nodes it is connected to - the list self.adacency[node] )
        3. For each edge see if the component numbers of the two endpoints are the same - otherwise, let 'label' be the min
        of two component numbers and let 'node' be the end point which does not have the component number 'label'.
        Make the component number of 'node' and all its neighbours as 'label' (this step is equivalent to merging the 
        two components).
        4. From this extract the list of components (list of lists of nodes with the same component number)
        5. Return the component list arranged as described below:
        The nodes in each component are to be sorted according to the comparison function
        The list returned must be sorted in the decreasing order of the sizes of the components
        '''
        # Your code
        #print "Test",self.adjacency
        connected_list = {}
        i = 1
        for key in self.adjacency :
            connected_list[key] = i
            i += 1       
        for node in self.adjacency :
            for j in self.adjacency[node]:
                if connected_list[node] != connected_list[j] :
                    label = min(connected_list[node], connected_list[j])
                    connected_list[node] = label
                    connected_list[j] = label
                    #print connected_list
                    #for edge in self.adjacency[j] :
                        #connected_list[edge] = label
        connected_components = []  
        for i in connected_list :
            lst = []
            val = connected_list[i]
            for k in connected_list :
                if connected_list[k] == val :
                    lst.append(k)
            if not lst in connected_components :
                connected_components.append(lst)
        connected_components.sort(key = lambda x: len(x))
        connected_components = connected_components[::-1]
        return connected_components

obj = Graph()
obj.get_connected_components()