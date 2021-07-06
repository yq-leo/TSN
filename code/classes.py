# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 22:29:00 2021
@author: QI YU
@email: yq123456leo@outlook.com
"""

import random
import networkx as nx
from igraph import Graph

class Stream:
    def __init__(self, network, len_path, max_fk = 20):
        self.max_fk = max_fk
        
        self.network = network
        self.len_path = len_path
        self.path = []
        
    def GenPath(self):
        while True:
            org_and_dst = random.sample(list(self.network.nodes), 2)
            src, sink = org_and_dst[0], org_and_dst[1]
            if nx.has_path(self.network, src, sink):
                flag = False
                for path in nx.all_simple_paths(self.network, source = src, target = sink):
                    if len(path) == (self.len_path + 1):
                        self.path = path
                        flag = True
                        break
                if flag:
                    break
    
    def GenPara(self, util):
        self.util = util                            # utilization
        self.Fk = random.randint(1, self.max_fk)    # number of frames
        
        self.Ck = 0                                 # total delay
        for i in range(len(self.path)):
            sw1, sw2 = self.path[i], self.path[i + 1]
            self.Ck += self.network[sw1][sw2]['weight']
        self.Ck *= self.Fk
        
        self.Tk = int(self.Ck / self.util)          # stream interval
        while True:
            Dk = random.randint(int(0.8 * self.Tk), self.Tk)
            if Dk > self.Ck:
                self.Dk = Dk                        # deadline
                break
    
class System:
    def __init__(self, num_switch, num_link, num_stream):
        self.num_switch = num_switch
        self.num_link = num_link
        
    def GenNet(self, max_weight = 10):
        graph = Graph.Erdos_Renyi(n = self.num_switch, m = self.num_link, directed = False, loops = False)
        self.network = nx.Graph(graph.get_edgelist())
        for edge in self.network.edges():
            src_node, sink_node = edge[0], edge[1]
            self.network[src_node][sink_node]['weight'] = random.randint(1, max_weight)
    
    def GenStreamPath(self, num_stream, len_path):
        self.streams = []
        
        for i in range(num_stream):
            s = Stream(network = self.network, len_path = len_path)
            s.GenPath()
            self.streams.append(s)
    
    def UpdateStreamPara(self, total_U):
        pass
            
            
    
    