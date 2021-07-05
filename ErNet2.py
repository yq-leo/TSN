from igraph import Graph,plot
import random
from numpy import mean
import networkx as nx
import copy
import matplotlib.pyplot as plt
from _collections import defaultdict
import math
import numpy as np,numpy.random
import time
# Task两个相关参数  Fn、TotalU 、plength
Fn = 100

plength = 10
# 存放一组Task的所有stream
slist = []
# stream 元组 [path,u,Fk,Tk,Dk]
# add 

# Fk【1-20】 u【0.1-0.5】 => TU 【0.1-0.5】*Fn

# 根据节点数和边数创建网络图 平均度=2*m/n
degree = 4
SWn = 20
Edge_n = int(degree * SWn / 2)
g = Graph.Erdos_Renyi(n=SWn,m=Edge_n,directed =False,loops = False)
g_e = g.get_edgelist()
net = nx.Graph(g_e)
# 添加边的权重
for edge in net.edges():
    #edge.update({"weight":random.randint(1,11)})
    net[edge[0]][edge[1]]['weight'] = random.randint(1,10)


def  generate_util(TU):
    x = np.ones(Fn)*25
    a = np.random.dirichlet(x, 1)*TU
    ulist = a[0]
    # print(ulist)
    # print(len(ulist))
    return ulist

def smallnet_stream_path(Sn,pl):
    count = 0
    while count!= Sn:
        s2t = random.sample(list(net.nodes),2)
        src = s2t[0]
        sink= s2t[1]
        if nx.has_path(net,src,sink):
            for path in nx.all_simple_paths(net,source=src,target=sink):
                if (len(path) == pl+1):
                    stuple = []
                    stuple.append(path)
                    Fk = random.randint(1,20)
                    stuple.append(Fk)
                    slist.append(stuple)
                    break
            count+=1


def stream_generate(ulist):
    pathlist = copy.deepcopy(slist)
    for i in range(len(slist)):
        pathlist[i].append(ulist[i])
        Ci = 0
        for j in range(len(pathlist[i][0])-1):
            Ci +=net[pathlist[i][0][j]][pathlist[i][0][j+1]]['weight']
        Ci *= pathlist[i][1]
        Ti = int(Ci/ulist[i])
        while 1:
            Di = random.randint(int(0.8*Ti),Ti)
            if Di > Ci :
                break
        pathlist[i].append(Ti)
        pathlist[i].append(Di)
    return pathlist

def core_algorighm(Sdict,streamlist):
    Out = defaultdict()
    #print('len(streamlist):'+str(len(streamlist)))
    for key in Sdict.keys():
        print('------------------------------------------------------------------------------')
        print('当前计算的链路为：'+str(key))
        print('当前链路上传输一帧的时间: '+str(net[key[0]][key[1]]['weight']))
        seq = Sdict[key]
        print("当前链路段上冲突的流seq:"+str(seq))
        c = 0
        for k in range(len(seq)):
            Ck = streamlist[seq[k]-1][1] * net[key[0]][key[1]]['weight']
            Xk = Ck
            process_count = 0
            print('当前求Xk的流序号seq[k]:'+str(seq[k])+' 该流的相关属性'+str(streamlist[seq[k]-1]))
            xlist = []
            xlist.append(Xk)
            while(1):
                det = []
                iseq = []
                CI = []
                Sum_It = 0
                if (len(seq)>1):
                    for j in range(len(seq)) :
                        if j!=k:
                            #print('j:'+str(j))
                            detj = Xk%streamlist[seq[j]-1][3]
                            det.append(detj)
                            iseq.append(j)
                    zipper = zip(iseq,det)
                    sort_zipper = sorted(zipper,key=lambda x:(x[1],x[0]),reverse=False)
                    result = zip(*sort_zipper)
                    iseq,det = [list(x) for x in result]
                    # print('-------------------------iseq-------------------------------')
                    # print(iseq)
                    # print('---------------------------det------------------------------')
                    # print(det)
                    for j in range(len(iseq)):
                        Sum_other_ci = 0
                        for i in range(len(seq)) :
                            # iseq 存放 seq元素的索引
                            if i!=iseq[j]:
                                Ni = math.floor(det[j]/streamlist[seq[i]-1][3])-1
                                if Ni < 0:
                                    Ni = 0
                                Sum_other_ci +=Ni * streamlist[seq[i]-1][1] * net[key[0]][key[1]]['weight']
                        if len(CI):
                            other = max(det[j]-Sum_other_ci+sum(CI),0)
                        else:
                            other = max(det[j]-Sum_other_ci,0)
                        Cj =  streamlist[seq[iseq[j]]-1][1] * net[key[0]][key[1]]['weight']
                        CIj = min(Cj,other)
                        CI.append(CIj)
                        Ij = CIj+math.floor(Xk//streamlist[iseq[j]-1][3])*Cj
                        Sum_It+=Ij
                        #print('seq[j]:'+str(seq[iseq[j]])+' Sum_other_ci:'+str(Sum_other_ci)+' other:'+str(other)+' CIj:'+str(CIj)+' Cj:'+str(Cj)+' Xk:'+str(Xk)+' Tj:'+str(streamlist[j-1][3])+' Ij:'+str(Ij))
                Xk1 = Ck+Sum_It
                xlist.append(Xk1)
                #print(Xk1)
                process_count+=1
                if (Xk1-Xk< 100 * np.spacing(1)):
                    c+=1
                    print('迭代成果的流的迭代过程Xlist:'+str(xlist))
                    break
                elif  (process_count>10000):
                    print("failed："+str(seq[k])+str(streamlist[seq[k]-1]))
                    return 0
                else:
                    Xk = Xk1
            # if Xk1<streamlist[k][4]:
            #     print('Xk1:'+str(Xk1))
            #     streamInmachine = (key[0],key[1],k)
            #     Out[streamInmachine] = Xk1
            # else:
            #     return 0
            streamInmachine = (key[0],key[1],seq[k])
            Out[streamInmachine] = Xk1
        # print('success:'+str(c)+' len(seq):'+str(len(seq)))
    # 求一条流的 ∑ Xk 和Dk进行比较
    print(Out)
    SumOfAct = []
    for i in range(len(streamlist)):
        SumOfAct.append(0)
    for key in Out.keys():
        SumOfAct[key[2]-1] += Out[key]
    print('------------------SumofAct-----------------------')
    print(SumOfAct)
    counter = 0
    for i in range(len(streamlist)):
        if SumOfAct[i] <= streamlist[i][4]:
            counter+=1
            print('Sum:'+str(SumOfAct[i])+'    Deadline:'+str(streamlist[i][4]))

    print('-------------------counter:'+str(counter))

    if counter == len(streamlist):
        print('该次实验成功!')
        return 1
    else:
        print('该次实验失败!')
        return 0

# 在这个函数内实现完整的实验模拟
def simulate_Rate_TU(down,uper,step,epoch):
    x_list = []
    ratelist = []
    smallnet_stream_path(Fn,plength)
    # 找所有在同一链路上有冲突的stream
    Sdict = defaultdict(list)
    for i in range(len(slist)):
        for j in range(len(slist[i][0])-2):
            pathlink = (slist[i][0][j],slist[i][0][j+1])
            Sdict[pathlink].append(i+1)
    print(Sdict)
    for i in range(int((uper-down)/step)+1):
        suc_counter = 0
        TU = down+i*step
        print('--------------------实验组TU：'+str(TU))
        for j in range(epoch):
            print('--------------------------epoch:'+str(j+1))
            ulist = []
            ulist = generate_util(TU)
            streamlist = stream_generate(ulist)
            print(streamlist)
            if (core_algorighm(Sdict,streamlist)):
                suc_counter+=1
        rate = suc_counter / epoch
        ratelist.append(rate)
        x_list.append(TU)
    return x_list,ratelist


if __name__=='__main__':
    s_t = time.clock()
    x_axis,y_axis = simulate_Rate_TU(1.0,2.0,1,1)
    e_t = time.clock()
    print('cosume time:'+str(e_t-s_t))
    plt.plot(x_axis,y_axis,label='Success Rate')
    plt.xlabel('Total Utilization ')
    plt.ylabel('Success Transmission Rate ')
    plt.title("Success Rate - Total Utilization")
    plt.show()





