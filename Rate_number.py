# reference
'''
https://blog.csdn.net/william_djj/article/details/88729431
https://blog.csdn.net/weixin_42521211/article/details/89152975
https://www.169it.com/article/4815380975527872753.html
https://hui-liu.github.io/blog/networkx-%E7%AC%94%E8%AE%B0/
https://blog.csdn.net/lucdaopencv/article/details/107150912
'''

'''
1 首先确定设计stream属性的一些参数表，需要满足的一点：传输时间Ci/发送间隔Ti < 1 而利用率u = ∑ 传输时间/发送间隔T 不比小于1 故而需要根据论文设计流的一些属性
2 绘制一组图，展现成功传输的流的比率 - 一组流的利用率之间的关系曲线
3 Ci/Ti 在某个范围内可能导致 在一条链路上 互相干扰的流的 X 迭代结果最终相同【这里或许我们可以作图找一个临界点】
4 其余一些可改变的量 流的数量，节点数量，路径长度 【暂时改变节点数量、网络形状比较麻烦，而改变路径长度的话emmm一组流里的每一条流长度本身不固定。具体怎么进行控制变量设计还得探讨下】
5 其余的一些图，可以看下流的数量和流的成功传输比例之间的关系，这里应该需要控制流的利用率（严格的话应该是利用率保持一致。或者利用率在某个范围）
'''

# 随机生成一些列有权无向图
# firstly 先画一个手工图来测试 Graph（V，E，W）
import random
import matplotlib.pyplot as plt
import networkx as nx
import string
from _collections import defaultdict
import numpy as np
from numpy import  mean
import math
import matplotlib.pyplot as plt
G = nx.Graph()
elist = [('ES1','SW1',random.randint(1,30)),('ES1','SW2',random.randint(1,10)),
         ('ES2','SW1',random.randint(1,30)),('ES2','SW2',random.randint(1,10)),
         ('SW1','SW3',random.randint(1,30)),('SW1','SW5',random.randint(1,10)),
         ('SW5','SW4',random.randint(1,30)),('SW3','SW4',random.randint(1,10)),
         ('SW2','SW3',random.randint(1,30)),('SW4','ES3',random.randint(1,10))]

G.add_weighted_edges_from(elist)

pos = nx.spring_layout(G)  # positions for all nodes

# nodes
#nx.draw_networkx_nodes(G, pos, node_size=1000)

# edges
#nx.draw_networkx_edges(G, pos, width=5)

# labels
edge_labels = nx.get_edge_attributes(G,'weight')
#nx.draw_networkx_labels(G, pos, edge_labels=edge_labels)
# font_size=20,,font_family='sans-serif
'''
plt.axis('off')
plt.show()
'''

# Rate - Number of streams
Ratelist = []
TotalU = []
Slist=[]
def Simulate_numver(m):
    for i in range(m):
        #设计20条stream
        Stuple = [] # 表示一个stream的4元组(pathwalk,Fk,Dk,Tk)
        # 确定src和target
        s2t = random.sample(range(1,4),2)
        # print('--------------source&target flag-----------------')
        src = 'ES'+str(s2t[0])
        sink = 'ES'+str(s2t[1])
        # print(src)
        # print(sink)
        Allpath = []
        for path in nx.all_simple_paths(G,source=src,target=sink):
            # 过滤掉中间节点中有ES的情况
            for j in range(len(path)-2):
                if path[j+1].startswith('ES'):
                    break;
            if j == len(path)-3:
                Allpath.append(path)

        #print('-------------all path------')
        #print(Allpath)
        #print(len(Allpath))
        index = random.randint(0,len(Allpath)-1)
        #print(index)
        pathwalk = Allpath[index]
        Stuple.append(i+1)
        Stuple.append(pathwalk)
        Fk = random.randint(5,20)
        Stuple.append(Fk)
        Stuple.append(0)
        Stuple.append(0)
        Slist.append(Stuple)

    for k in range(20):
        totalu = 0
        for i in range(len(Slist)):
            # ∑ Fk * trij
            SumC = 0
            for j in range(len(Slist[i][1])-1):
                SumC += G[Slist[i][1][j]][Slist[i][1][j+1]]['weight']
            SumC *= Fk
            Tk = random.randint(5*SumC,10*SumC+1)
            Dk = random.randint(int(0.8*Tk),Tk)
            Slist[i][3]=Dk
            Slist[i][4]=Tk
            # total utilization
            totalu += SumC/Tk
        TotalU.append(totalu)
        print('-------------all stream show---------------------')
        print(Slist)

        # 对每一条流进行分析
        # 拆分每一个流的路径为链路（SWi，SWj),每一个链路寻找有共同stream流过的流标号
        StreamId = []
        Sdict = defaultdict(list)
        for i in range(len(Slist)):
            for j in range(len(Slist[i][1])-2):
                # linktuple : link,streadmID1,ID2,xxxx
                # pathlinke : link ('SW1','SW2')
                pathlink = (Slist[i][1][j+1],Slist[i][1][j+2])
                Sdict[pathlink].append(i+1)
        print('------------show each stream on link---------------------')
        print(Sdict)
        print('-----------------------enter into core part------------------------------')
        Out = defaultdict()
        for key in Sdict.keys():
            #if len(Sdict[key]) > 1:
            print('机器段:'+str(key))
            seq = Sdict[key]
            #print(seq)
            # 对这段机器上每一条流进行计算
            for k in range(len(seq)):
                # 设定一个初始状态值 以传输时间为初始状态值 Ck = Fk x weight
                #print(G[key[0]][key[1]]['weight'])
                #print(Slist[seq[k]-1][2])
                Ck =  Slist[seq[k]-1][2] * G[key[0]][key[1]]['weight']
                #print(Ck)# 可以在Slist去除标号的情况下修改
                #print('-------------------进入不动点迭代状态------------------------')
                xlist = []
                Xk = Ck
                xlist.append(Xk)
                while(1):
                 # 计算干扰项之和
                    SumIntf = 0
                    for i in range(len(seq)):
                        if i != k:
                            Ti = Slist[seq[i]-1][4]
                            Ci = Slist[seq[i]-1][2] * G[key[0]][key[1]]['weight']
                            Intf = math.floor(Xk//Ti) * Ci + min(max(0,Xk%Ti),Ci)
                            SumIntf += Intf
                        Xk1 = Ck + math.floor(SumIntf)
                        xlist.append(Xk1)
                    if (Xk1-Xk< 100 * np.spacing(1)):
                        break;
                    else:
                        Xk = Xk1
                print("Xk:%d" %Xk)
                print("xlist[-1]:%d" %xlist[-1])
                print(xlist)
                # xlist 为迭代过程, 最终的Xk为迭代结果
                # 考虑一种存储结构 :(src,sink,StreamId) ---> xlist xk
                streamInmachine = (key[0],key[1],seq[k])
                Out[streamInmachine] = Xk
        print(Out)
        # 进行一下验证，计算一条流的active time之和情况并且和 Di进行比较 (pathwalk,Fk,Dk,Tk) Slist存放了所有流的相关信息
        SumOfAct = []
        for i in range(len(Slist)):
            SumOfAct.append(0)
        print(SumOfAct)
        for key in Out.keys():
                #print("StreamID:%d"%key[2])
                #print("SumOfAct:%d"%SumOfAct[key[2]-1])
                #print("Out:%d"%Out[key])
            SumOfAct[key[2]-1] += Out[key]
        print(SumOfAct)

        counter = 0
        for i in range(len(Slist)):
            if SumOfAct[i] < Slist[i][3]:
                counter+=1
            print("--------------------streamID:{0}--------------------------".format(i+1))
            print("sum of all active time: %d"%SumOfAct[i])
            print("current stream's Deadline: %d"%Slist[i][3])
        SuccessRate = counter / len(Slist)
        Ratelist.append(SuccessRate)
    avgrate = mean(Ratelist)
    return avgrate


x_axis = []
y_axis = []
for i in range(4):
    rate = Simulate_numver((i+1)*5)
    y_axis.append(rate)
    x_axis.append((i+1)*5)

plt.plot(x_axis,y_axis,label='Utilization:[0.1-0.5]')
plt.xlabel('Number of Streams ')
plt.ylabel('Success Transmission Rate ')
plt.title("Success Rate - Number of Streams")
plt.legend()
plt.show()





