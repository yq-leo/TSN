# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 22:29:00 2021
@author: QI YU
@email: yq123456leo@outlook.com
"""

import random
import networkx as nx
from igraph import Graph
import numpy as np
import matplotlib.pyplot as plt
from _collections import defaultdict
import math
import time

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
        self.InitActZone()
    
    def InitActZone(self):
        self.act_zone = {}
        for idx in range(len(self.path) - 1):
            link = self.path[idx], self.path[idx + 1]
            self.act_zone[link] = 0
    
    def GenPara(self, util):
        self.util = util                            # Utilization
        self.Fk = random.randint(1, self.max_fk)    # Number of frames
        
        self.Ck = 0                                 # Total delay
        for i in range(len(self.path) - 1):
            sw1, sw2 = self.path[i], self.path[i + 1]
            self.Ck += self.network[sw1][sw2]['weight']
        self.Ck *= self.Fk
        
        self.Tk = int(self.Ck / self.util)          # Stream interval
        while True:
            Dk = random.randint(int(0.8 * self.Tk), self.Tk)
            if Dk > self.Ck:
                self.Dk = Dk                        # Deadline
                break
    
    def PrintInfo(self, is_act_zone = False):
        print('-----Stream Information-----')
        print('path: %s' % str(self.path))
        try:
            print('number of frame: %d' % self.Fk)
            print('utilization: %.3f' % self.util)
            print('total time for one stream: %d' % self.Ck)
            print('stream interval: %d' % self.Tk)
            print('deadline: %d' % self.Dk)
            
            if is_act_zone:
                print('active interval:')
                for index, link in enumerate(self.act_zone.keys()):
                    length = self.act_zone[link]
                    print(str(link) + ': ' + str(length), end = ' ' * (5 - len(str(length))))
                    if index % 3 == 2:
                        print()
                if len(self.act_zone.keys()) % 3 != 0:
                    print()
        except:
            print('NO PARAMETERS! Please call method "GenPara" to generate')
        print('----------------------------')
        print()
    
class System:
    def __init__(self, num_switch, num_link):
        self.num_switch = num_switch
        self.num_link = num_link
        
    def GenNet(self, max_weight = 10):
        graph = Graph.Erdos_Renyi(n = self.num_switch, m = self.num_link, directed = False, loops = False)
        self.network = nx.Graph(graph.get_edgelist())
        for edge in self.network.edges():
            src_node, sink_node = edge[0], edge[1]
            self.network[src_node][sink_node]['weight'] = random.randint(1, max_weight)
    
    def PrintNetInfo(self, is_plot = False):
        print('-----System Network-----')
        print('number of switch: %d' % self.num_switch)
        print('number of link: %d' % self.num_link)
        try:
            print('links & weights: ')
            for index, edge in enumerate(self.network.edges()):
                src, sink = edge
                w = self.network[src][sink]['weight']
                print(str(edge) + (' ' * (8 - len(str(edge)))) + ': ' + str(w), end = ' ' * (4 - len(str(w))))
                if index % 3 == 2:
                    print()
            if self.num_link % 3 != 0:
                print()
             
            if is_plot:
                nx.draw(self.network)
        except:
            print('NO NETWORK! Please call method "GenNet" to generate')
        print('------------------------')
        print()
    
    def GenStreamPath(self, num_stream, len_path):
        self.num_stream = num_stream
        self.streams = []
        
        for i in range(num_stream):
            s = Stream(network = self.network, len_path = len_path)
            s.GenPath()
            self.streams.append(s)
    
    def GenConfilctDict(self):
        self.cft_dict = defaultdict(list)
        for index, stream in enumerate(self.streams):
            for idx in range(len(stream.path) - 1):
                link = stream.path[idx], stream.path[idx + 1]
                self.cft_dict[link].append(index)
    
    def UpdateStreamPara(self, total_U):
        # Generate utilization for each stream
        x = np.ones(self.num_stream) * 25
        a = np.random.dirichlet(x, 1) * total_U
        uList = a[0]
        
        # Generte parameters according to utilizations
        for index, stream in enumerate(self.streams):
            util = uList[index]
            stream.GenPara(util)

    def PrintStreamInfo(self, is_act_zone = False):
        for idx, stream in enumerate(self.streams):
            print('-----Stream index: %d-----' % idx)
            stream.PrintInfo(is_act_zone)
    
    def RunCoreAlg(self):
        for link in self.cft_dict.keys():
            #print('-----')
            #print('Current Link: %s' % str(link))
            s_set = self.cft_dict[link]
            #print('Conflict Streams: %s' % str(s_set))
            #print('-----')
            #print()
            
            # Step 1
            src, sink = link
            weight = self.network[src][sink]['weight']
            for idx in s_set:
                stream = self.streams[idx]
                Ck = stream.Fk * weight
                Xk = Ck
                epoch = 0
                while True:
                    if len(s_set) <= 1:
                        break
                    
                    # Step 2
                    deltas = {}
                    for j in s_set:
                        if j != idx:
                            Tj = self.streams[j].Tk
                            delta_j = Xk % Tj
                            deltas[j] = delta_j
                            
                    # Step 3
                    s_set_sorted = sorted(deltas.keys(), key = lambda x:deltas[x])
                    
                    CI = []
                    sum_I = 0
                    for j in s_set_sorted:
                        # Step 4
                        sj = self.streams[j]
                        sum_nici = 0
                        for i in s_set:
                            si = self.streams[i]
                            if i != j:
                                Ni = max(math.floor(deltas[j] / si.Tk) - 1, 0)
                                sum_nici += Ni * si.Fk * weight
                        other = max(deltas[j] - sum_nici + sum(CI), 0)
                        Cj = sj.Fk * weight
                        CIj = min(Cj, other)
                        CI.append(CIj)
                        
                        # Step 5
                        Ij = CIj + math.floor(Xk / sj.Tk) * Cj
                        sum_I += Ij
                    
                    # Step 6
                    Xk_new = Ck + sum_I
                    epoch += 1
                    if Xk_new - Xk < 100 * np.spacing(1):
                        Xk = Xk_new
                        break
                    elif epoch > 10000:
                        print('Convergence Failed')
                        return
                    else:
                        Xk = Xk_new
                
                stream.act_zone[link] = Xk
        
    
    def IsFeasible(self):
        print('---------------Simulation Results---------------')
        num_success = 0
        for idx, stream in enumerate(self.streams):
            total_length = sum(stream.act_zone.values())
            isF = total_length < stream.Dk
            if isF:
                num_success += 1
            print('S%d' % idx + (' ' * (3 - len(str(idx))))
                  + 'Active Interval: %d' % total_length 
                  + (' ' * (7 - len(str(total_length))))
                  + 'Deadline: %d' % stream.Dk
                  + (' ' * (7 - len(str(stream.Dk))))
                  + str(isF))    
        print('Success Rate: %.2f' % (num_success / self.num_stream))
        print('------------------------------------------------')
            
            
if __name__ == "__main__":
    start_time = time.perf_counter()
    sys = System(num_switch = 20, num_link = 40)
    sys.GenNet()
    sys.PrintNetInfo()
    sys.GenStreamPath(num_stream = 100, len_path = 10)
    sys.GenConfilctDict()
    sys.UpdateStreamPara(total_U = 1.0)
    #sys.PrintStreamInfo(isActZone = False)
    sys.RunCoreAlg()
    sys.IsFeasible()
    end_time = time.perf_counter()
    print('Time Consumed: %.4fs' % (end_time - start_time))
    
    