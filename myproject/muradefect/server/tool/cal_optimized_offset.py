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

def cal_offseted(data, off=np.zeros(3)):
    #返回调整后的ppa_x和ppa_y
    '''
    王吉东备注：这一个的公式需要核实。主要是off[[0,1]]，如果严格按照ppt中的公式看，应该是off[[1,0]]
    '''
    data=data[['pos_x', 'pos_y','ppa_x', 'ppa_y']]
#    data=data.values
#    data_offseted = data[:, [1, 0]] * [-1, 1] *\
#        off[2] * np.pi / 180 / 100 + off[[0, 1]] +\
#        data[:, 2:]
    data_offseted=pd.DataFrame([],columns=['ppa_x','ppa_y'])
    data_offseted['ppa_x']=data.ppa_x+off[0]-data.pos_y*off[2]* np.pi / 180 / 100
    data_offseted['ppa_y']=data.ppa_y+off[1]+data.pos_x*off[2]* np.pi / 180 / 100
    return data_offseted

#
#xth1 = 4
#xth2 = 7.5
#xweight1 = 0
#xweight2 = 1
#yth1 = 4
#yth2 = 6.5
#yweight1 = 0
#yweight2 = 1

def optimize_offset(p2,ths):
    #用来分别计算每一个offset组下，调整后的ppa中良品的数量（如前文所说，全部合格则为4倍的行数）
    #已包含 cal_offseted    
    xth1 = ths['xth1']
    xth2 = ths['xth2']
    xweight1 = ths['xweight1']
    xweight2 = ths['xweight2']
    yth1 = ths['yth1']
    yth2 = ths['yth2']
    yweight1 = ths['yweight1']
    yweight2 = ths['yweight2']

    st = time.time()
    offset = pd.DataFrame(OFFSETS)
    ##这里的列名“offset”仅在此函数中用得上
    offset.columns = ['offset_x','offset_y','offset_t']
    offset['offset_t1'] = offset['offset_t'] 
    offset['id'] = offset.index
    #N = 1000
    #offset1 = offset.loc[:N-1]
    offset1 = offset
    data1 = p2[['pos_x', 'pos_y','ppa_x', 'ppa_y']]
    datasets = pd.concat(itertools.repeat(data1,len(offset1)))
    print (datasets.shape)
    datasets['id'] = np.repeat(offset1.index,len(data1))
    datasets = pd.merge(datasets,offset,on = 'id')
    print (datasets.shape)
    
    #以下待验证
    datasets["pos_y"] = datasets["pos_y"]*-1
    datasets[["pos_y","pos_x"]] = datasets[["pos_y","pos_x"]].values*\
            datasets[['offset_t','offset_t1']].values*np.pi/180/100
    datasets["pos_y"] = datasets["pos_y"]+datasets['offset_x'] 
    datasets["pos_x"] = datasets["pos_x"]+datasets['offset_y'] 
    datasets[["pos_y","pos_x"]]  = datasets[["pos_y","pos_x"]].values \
        +datasets[["ppa_x","ppa_y"]].values
    print (datasets.shape)    
    datasets[["pos_y","pos_x"]] = datasets[["pos_y","pos_x"]].abs()    
#    WEIGHT=1
#    datasets['bz1'] = (datasets[["pos_y","pos_x"]]<th2).sum(axis=1)
#    datasets['bz2'] = (datasets[["pos_y","pos_x"]]<th1).sum(axis=1)
#    datasets['rst'] = datasets['bz1']+datasets['bz2']*WEIGHT
    
    datasets['bx1'] = (datasets[["pos_x"]]<xth1).sum(axis=1)*xweight1
    datasets['bx2'] = (datasets[["pos_x"]]<xth2).sum(axis=1)*xweight2
    datasets['by1'] = (datasets[["pos_y"]]<yth1).sum(axis=1)*yweight1
    datasets['by2'] = (datasets[["pos_y"]]<yth2).sum(axis=1)*yweight2
    datasets['rst'] = datasets['bx1']+datasets['bx2']+datasets['by1']+datasets['by2']
    print (datasets.shape)   
    rst = datasets.groupby("id")['rst'].sum()
    print ("cost : ",time.time()-st)      
    return rst

def cal_optimized_offset(p2,ths):
    
    xth1 = ths['xth1']
    xth2 = ths['xth2']
    xweight1 = ths['xweight1']
    xweight2 = ths['xweight2']
    yth1 = ths['yth1']
    yth2 = ths['yth2']
    yweight1 = ths['yweight1']
    yweight2 = ths['yweight2']
    
    #rst = optimize_offset(p2[['pos_x', 'pos_y', 'ppa_x', 'ppa_y']].values)
    rst = optimize_offset(p2[['pos_x', 'pos_y', 'ppa_x', 'ppa_y']],ths)
    
    r1 = pd.DataFrame(OFFSETS)
    r1.columns = ['delta_x', 'delta_y', 'delta_t']
    r1['ppa'] = rst #体现良品数量
    #能得到最佳count的10个值,求平均
    r0 = r1[r1.ppa.isin(r1.ppa.nlargest(10))]
    r2 = r0.mean()
    r2['ppa'] = round(r2['ppa'])
    #计算调整前的ppa，用来体现调整后是不是变好了
    r2['ppa_before'] =r1[(r1.delta_x==0)&(r1.delta_y==0)&(r1.delta_t==0)]['ppa'].iloc[0]
    
#    r2['eventtime'] = p2['eventtime'].max()
    #找到计算平均得到的offset值最接近的meshgrid点
    
    r2[['delta_x', 'delta_y']] = (r2[['delta_x', 'delta_y']] * 2).round()/ 2.0
    r2['delta_t'] = r2['delta_t'].round()
    r2['offset_x'] = p2['offset_x'].mean()
    r2['offset_y'] = p2['offset_y'].mean()
    r2['offset_tht'] = p2['offset_tht'].mean()
    
    r2['after_x'] = r2['offset_x'] + r2['delta_y'] # 经过delta_offset调整后    ????
    r2['after_y'] = r2['offset_y'] + r2['delta_x']
    r2['after_t'] = r2['offset_tht'] - r2['delta_t']

    off = r2[['delta_x', 'delta_y', 'delta_t']].values

    adf=cal_offseted(p2, off)
    bdf=cal_offseted(p2)
    
    r2['before_ppa_x4'] = (bdf.ppa_x<xth1).mean()  
    r2['before_ppa_y4'] = (bdf.ppa_y<yth1).mean()
    temp4=pd.concat([bdf.ppa_x<xth1,bdf.ppa_y<yth1],axis=1)
    r2['before_ppa_t4'] = temp4.min(axis=1).mean()
    r2['before_ppa_x6.5'] = (bdf.ppa_x<xth2).mean()
    r2['before_ppa_y6.5'] = (bdf.ppa_y<yth2).mean()
    temp65=pd.concat([bdf.ppa_x<xth2,bdf.ppa_y<yth2],axis=1)
    r2['before_ppa_t6.5'] = temp65.min(axis=1).mean()
    
    r2['after_ppa_x4'] = (adf.ppa_x<xth1).mean()  
    r2['after_ppa_y4'] = (adf.ppa_y<yth1).mean()
    temp4=pd.concat([adf.ppa_x<xth1,adf.ppa_y<yth1],axis=1)
    r2['after_ppa_t4'] = temp4.min(axis=1).mean()
    r2['after_ppa_x6.5'] = (adf.ppa_x<xth2).mean()
    r2['after_ppa_y6.5'] = (adf.ppa_y<yth2).mean()
    temp65=pd.concat([adf.ppa_x<xth2,adf.ppa_y<yth2],axis=1)
    r2['after_ppa_t6.5'] = temp65.min(axis=1).mean()
    r2=round(r2, 4)
    
    return r2