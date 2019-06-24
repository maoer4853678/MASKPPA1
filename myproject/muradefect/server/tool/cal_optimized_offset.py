import pandas as pd
import numpy as np
import itertools
import time

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
    st = time.time()
    offset = pd.DataFrame(OFFSETS)
    offset.columns = ['offset_x','offset_y','offset_t']
    offset['offset_t1'] = offset['offset_t'] 
    offset['id'] = offset.index
    #N = 1000
    #offset1 = offset.loc[:N-1]
    offset1 = offset
    WEIGHT = 1
    data1 = p2[['pos_x', 'pos_y','ppa_x', 'ppa_y']]
    datasets = pd.concat(itertools.repeat(data1,len(offset1)))
    print (datasets.shape)
    datasets['id'] = np.repeat(offset1.index,len(data1))
    datasets = pd.merge(datasets,offset,on = 'id')
    print (datasets.shape)
    
    datasets["pos_y"] = datasets["pos_y"]*-1
    datasets[["pos_y","pos_x"]] = datasets[["pos_y","pos_x"]].values*\
            datasets[['offset_t','offset_t1']].values*np.pi/180/100
    datasets["pos_y"] = datasets["pos_y"]+datasets['offset_x'] 
    datasets["pos_x"] = datasets["pos_x"]+datasets['offset_y'] 
    datasets[["pos_y","pos_x"]]  = datasets[["pos_y","pos_x"]].values \
        +datasets[["ppa_x","ppa_y"]].values
    print (datasets.shape)  
    
    datasets[["pos_y","pos_x"]] = datasets[["pos_y","pos_x"]].abs()
    datasets['bz1'] = (datasets[["pos_y","pos_x"]]<6.5).sum(axis=1)
    datasets['bz2'] = (datasets[["pos_y","pos_x"]]<4).sum(axis=1)
    datasets['rst'] = datasets['bz1']+datasets['bz2']*WEIGHT
    print (datasets.shape)  
    
    rst = datasets.groupby("id")['rst'].sum()
    print ("cost : ",time.time()-st)      
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
    
    r2[['delta_x', 'delta_y']] = (r2[['delta_x', 'delta_y']] * 2).round()/ 2.0
    r2['delta_t'] = r2['delta_t'].round()
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