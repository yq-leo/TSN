# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 21:33:54 2021
@author: QI YU
@email: yq123456leo@outlook.com
"""

from classes import System
import time
from _collections import defaultdict

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
    
    return res_dict
    
def PlotRes():
    pass

if __name__ == "__main__":
    init_start_time = time.perf_counter()
    sys = System(num_switch = 20, num_link = 40)
    sys.GenNet()
    sys.PrintNetInfo()
    init_end_time = time.perf_counter()
    
    util_list = [1.0, 2.0, 3.0, 4.0]
    sim_start_time = time.perf_counter()
    res_dict = Simulation(sys, num_stream = 100, len_path = 10, epoch = 10, util_list = util_list)
    sim_end_time = time.perf_counter()
    
    print('Initialization Time Consumed: %.4f' % (init_end_time - init_start_time))
    print('Simulation Time Consumed: %.4f' % (sim_end_time - sim_start_time))