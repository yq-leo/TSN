# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 21:33:54 2021
@author: QI YU
@email: yq123456leo@outlook.com
"""

from classes import System
import time

if __name__ == "__main__":
    init_start_time = time.perf_counter()
    sys = System(num_switch = 20, num_link = 40)
    sys.GenNet()
    sys.PrintNetInfo()
    sys.GenStreamPath(num_stream = 10, len_path = 10)
    sys.GenConfilctDict()
    sys.UpdateStreamPara(total_U = 1.0)
    init_end_time = time.perf_counter()
    
    sim_start_time = time.perf_counter()
    sys.RunCoreAlg()
    sys.IsFeasible()
    sim_end_time = time.perf_counter()
    
    print('Initialization Time Consumed: %.4f' % (init_end_time - init_start_time))
    print('Simulation Time Consumed: %.4f' % (sim_end_time - sim_start_time))