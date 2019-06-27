# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s 

Authenticated by Sherk
Any question please refer to:
    sherkfung@gmail.com
"""


'''
20190621客户需求：需要设定阈值。当结果（分数）中的before和after差别小于该阈值的时候，选择不优化。

'''



#p2=DF.head(114)
'''
POINT_NO是指TAG的编号。共len(x)/114是因为共有114个点；
不理解物理意义，推测是计算此过程经过了几道工序（每道工序需要经过114个点）。
后面的似乎没有用上p3这个量。（后面cal_ratio_bna函数中用到的p3和这个p3不一样。）
'''

# Define optimizing functions

import numpy as np
import itertools
import pandas as pd

OFFSETS = np.vstack(
    map(
        np.ravel, 
        np.meshgrid(
            np.arange(-8, 8.5, .5),
            np.arange(-8, 8.5, .5),
            np.arange(-25, 26)
            )
        )
    ).T

#THRESHOLD = 6.5
WEIGHT = 1

def cal_offseted(data, off=np.zeros(3)):
    #返回调整后的ppa_x和ppa_y
    '''
    王吉东备注：这一个的公式需要核实。主要是off[[0,1]]，如果严格按照ppt中的公式看，应该是off[[1,0]]
    '''
    data=data[['pos_x', 'pos_y','ppa_x', 'ppa_y']]
    data=data.values
    data_offseted = data[:, [1, 0]] * [-1, 1] *\
        off[2] * np.pi / 180 / 100 + off[[0, 1]] +\
        data[:, 2:]
    
    '''
    追溯函数中定义的函数cal_offseted里的data，应该是指的是:
   data=p2[['pos_x', 'pos_y', 'ppa_x', 'ppa_y']]
    
    '''
    
    return data_offseted

'''
    Below, is the first version of offset optimization algorithm
    Which, consider even importance of ppa_x, ppa_y
    However, we usually face the fact that improving ppa_x 
        while ppa_y is detiriated, which is unacceptable.
    
    
def cal_offseted_count(data, off=np.zeros(3)):
    # count the panels that exceed the threshold
    rst = np.sum(np.abs( cal_offseted(data, off) ) < 6.5) +\
        WEIGHT * np.sum(np.abs( cal_offseted(data, off) ) < 4)
    return  rst
'''

def cal_offseted_count(data, off=np.zeros(3)):
    '''
    用来计算offset后的数据（ppa_after_offset）中良品的数量。
    【这里存在和管控线以及对应权重的耦合。】
    '''
    
    '''
        This is the improved version of optimiziation method
        Which increases the weight of ppa_y
    '''
    # count the panels that exceed the threshold
    data_offseted = np.abs(cal_offseted(data, off))
    rst = np.sum(data_offseted < 6.5) + WEIGHT * np.sum(data_offseted < 4)
    '''
    由于weight为1，故rst返回值为(双倍的)(X列和Y列加起来的)数量；
    即：如果全部合格，count值等于len(data)的4倍
    '''
 
#    data_abs = np.abs(cal_offseted(data))
#    
#    rst_a = np.mean(data_offseted < 4, axis=0)
#    rst_b = np.mean(data_abs < 4, axis=0)
#    
#    rst_c = np.mean(data_offseted < 6.5, axis=0)
#    rst_d = np.mean(data_abs < 6.5, axis=0)
#    
#    if any(rst_a < rst_b) | any(rst_c < rst_d):
#        rst = np.mean(WEIGHT * rst_b + rst_d)
#    else:
#        rst = np.mean(WEIGHT * rst_a + rst_c)
        
    return  rst


def optimize_offset(p2):
    #用来分别计算每一个offset组下，调整后的ppa中良品的数量（如前文所说，全部合格则为4倍的行数）    
    datasets = itertools.repeat(p2, OFFSETS.shape[0]) 
    '''
    这里的函数定义括号里的dataset，指的是：
    p2[['pos_x', 'pos_y', 'ppa_x', 'ppa_y']].values
    '''
    
    '''
    datasets表示生成一个循环器，将dataset重复len(OFFSET)遍，
    意义在于每个dataset的对应上所有的OFFSET可能；
    
    map(cal_offseted_count, datasets, OFFSETS)，表示datasets在对应的OFFSETS下做cal_offseted_count函数；
    亦即让dataset组合每一个OFFSETS中的元素，计算出cal_offseted_count函数。    
    '''
    
    rst = np.fromiter(
            map(cal_offseted_count, datasets, OFFSETS), dtype=np.float)
    '''
    
    '''
    #每个datasets
#            map(cal_offseted_ratio, datasets, OFFSETS, 'X'), dtype=np.float)    
    return rst

#计算比例用的，功能和Excel中统计部分很相似???
#p3 = p2[p2.EVA_CHAMBER == 'B']

def cal_ratio_bna(p3, off=np.zeros(3)):
    #返回调整前后，ppa在阈值之内的数值的平均值。b是调整前，a是调整后
    
    p3 = p3[['pos_x', 'pos_y', 'ppa_x', 'ppa_y']]#这里的p3，在应用中使用的实际是p2
    
    
    def cal_ratio(p3, threshold):
        #计算符合条件的均值。
        b1 = (p3[['ppa_x', 'ppa_y']].abs() < threshold).mean()
        b1['ppa_t'] = (p3[['ppa_x', 'ppa_y']].abs().max(axis=1) < threshold).\
            mean()
        #这里的T是Total的意思（不是theta的意思），即X和Y一同考虑
        b1.index = [x + str(threshold) for x in b1.index]
        
        return round(b1, 4)
    
    b = pd.concat([cal_ratio(p3, 4), cal_ratio(p3, 6.5)])
    b.index = ['before_' + x for x in b.index]
    
    p3_offseted = p3.copy()
    
    p3_offseted[['ppa_x', 'ppa_y']] = cal_offseted(p3, off)
    
    a = pd.concat([cal_ratio(p3_offseted, 4), cal_ratio(p3_offseted, 6.5)])
    a.index = ['after_' + x for x in a.index]
    
    return pd.concat([b, a])


def cal_optimized_offset(p2):
    '''
    感觉这一部分有优化甚至逻辑修改的空间。
    需求是应对rst有多个最大值的情况。
    一方面，将最大的10个值求平均，可能会导致得到的结果不是最大值；
    另一方面，可能会造成offset值过大。
    '''
    #rst = optimize_offset(p2[['pos_x', 'pos_y', 'ppa_x', 'ppa_y']].values)
    rst = optimize_offset(p2[['pos_x', 'pos_y', 'ppa_x', 'ppa_y']])
    
    r1 = pd.DataFrame(OFFSETS)
    r1.columns = ['delta_x', 'delta_y', 'delta_t']
    r1['ppa'] = rst #体现良品数量
    #能得到最佳count的10个值,求平均
    r0 = r1[r1.ppa.isin(r1.ppa.nlargest(10))]
    r2 = r0.mean()
    r2['ppa'] = round(r2['ppa'])
    #计算调整前的ppa，用来体现调整后是不是变好了
    r2['ppa_before'] =cal_offseted_count(p2[['pos_x', 'pos_y', 'ppa_x', 'ppa_y']])
    
#    r2['eventtime'] = p2['eventtime'].max()
    #找到计算平均得到的offset值最接近的meshgrid点
    
    r2[['delta_x', 'delta_y']] = (r2[['delta_x', 'delta_y']] * 2).apply(round) / 2
#    r2['delta_T'] = r2['delta_T'].apply(round)
    r2['offset_x'] = p2['offset_x'].mean()
    '''p2的X,Y,T来自maskID，具体意义尚不知'''
    r2['offset_y'] = p2['offset_y'].mean()
    r2['offset_tht'] = p2['offset_tht'].mean()
    
    '''
    X,Y是否调换，需要再核实。
    
    '''
    r2['after_x'] = r2['offset_x'] + r2['delta_y'] # 经过delta_offset调整后    ????
    r2['after_y'] = r2['offset_y'] + r2['delta_x']
    r2['after_t'] = r2['offset_tht'] - r2['delta_t']
    off = r2[['delta_X', 'offset_y', 'offset_tht']].values
    
#r3 = cal_ratio_bna(p2, off)
    return pd.concat([r2, cal_ratio_bna(p2, off)])

#if __name__=='__main__':
#    tic=datetime.datetime.now()
#    DF=pd.read_csv(r'D:\VisionoxLayout\muradefect\DataNeedToCalppa.csv')
#    df=DF.head(114)
#    Temp=cal_optimized_offset(df)
#    
#    toc=datetime.datetime.now()
#    print('Done using %d s'%(toc-tic).total_seconds())
