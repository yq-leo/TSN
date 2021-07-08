# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 21:33:54 2021
@author: QI YU
@email: yq123456leo@outlook.com
"""

from classes import System
import time
from _collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

def Simulation(sys, num_stream, len_path, epoch, util_list):
    res_dict = defaultdict(list)
    print('----------Simulation Start----------')
    for index in range(epoch):
        start_time = time.perf_counter()
        sys.GenStreamPath(num_stream = num_stream, len_path = len_path)
        sys.GenConflictDict()
        for util in util_list:
            sys.UpdateStreamPara(total_U = util)
            sys.RunCoreAlg()
            sys.IsFeasible()
            res_dict[util].append(sys.suc_rate)
        end_time = time.perf_counter()
        print('Epcoh %d Done, Time Consumed: %.4fs' % (index + 1, end_time - start_time))
    print('-----------Simulation End-----------')
    print()
    
    return res_dict
    
def PlotRes(sys, res_dict):
    sucs_rate_dict = {}
    for key in res_dict.keys():
        sucs_rate_dict[key] = sum(res_dict[key]) / len(res_dict[key])
    
    X = np.array(list(sucs_rate_dict.keys()))
    Y = np.array(list(sucs_rate_dict.values()))
    
    plt.plot(X, Y)
    plt.title('Simulation Result')
    plt.xlabel('total untilization')
    plt.ylabel('success rate')

if __name__ == "__main__":
    init_start_time = time.perf_counter()
    sys = System(num_switch = 20, num_link = 40)
    sys.GenNet()
    sys.PrintNetInfo()
    init_end_time = time.perf_counter()
    
    util_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    sim_start_time = time.perf_counter()
    res_dict = Simulation(sys, num_stream = 100, len_path = 5, epoch = 10, util_list = util_list)
    sim_end_time = time.perf_counter()
    
    PlotRes(sys, res_dict)
    
    print('Initialization Time Consumed: %.4fs' % (init_end_time - init_start_time))
    print('Simulation Time Consumed: %.4fs' % (sim_end_time - sim_start_time))