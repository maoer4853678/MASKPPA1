# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 23:08:03 2019

@author: 王吉东
"""
import glob
import pandas as pd
Files=glob.glob(r'D:\data_Visionox\Visionox\Data*.csv')
DF=[]
for F in Files[0:300]:
    df=pd.read_csv(F,index_col=0)    
    if not (len(df)):
        continue
    df.EVENTTIME=pd.to_datetime(df.EVENTTIME)
    DF.append(df)
######GroupID
DF=pd.concat(DF)
DF=DF.sort_values('EVENTTIME')
DF['GroupID']=DF.EVENTTIME.diff()>pd.to_timedelta(36,unit='h')
DF.GroupID=DF.GroupID.cumsum()


F=Files[300]

df=pd.read_csv(F,index_col=0)
df.EVENTTIME=pd.to_datetime(df.EVENTTIME)

######################   根据历史数据赋值cycleID    ######################

def func(value):
    value2=value.sort_values(['EVENTTIME'])
    value2['cycleID']=(value2.MASK_SET!=value2.MASK_SET.shift(-1)).shift(1).fillna(0).astype(int)
    value2['cycleID']=value2.cycleID.cumsum()
    return value2

def func2(value):
    value2=value.sort_values(['EVENTTIME'])
    value2['cycleJudge']=(value2.MASK_SET!=value2.MASK_SET.shift(-1)).shift(1).fillna(0).astype(int)
    value2['cycleID']=value2['cycleID'].fillna(method='ffill')
    value2['cycleID']=value2.cycleID+value2.cycleJudge
    return value2

DFA=DF[(DF.EVA_CHAMBER==DF.EVA_CHAMBER.min())&(DF.PORT=='A')].sort_values(['GroupID','LINE','EVA_CHAMBER','PORT','EVENTTIME'])[['GroupID','LINE','EVA_CHAMBER','PORT','EVENTTIME','MASK_SET','GLASS_ID']].drop_duplicates()
DFB=DF[(DF.EVA_CHAMBER==DF.EVA_CHAMBER.min())&(DF.PORT=='B')].sort_values(['GroupID','LINE','EVA_CHAMBER','PORT','EVENTTIME'])[['GroupID','LINE','EVA_CHAMBER','PORT','EVENTTIME','MASK_SET','GLASS_ID']].drop_duplicates()

DFA2=DFA.groupby(['LINE','EVA_CHAMBER','PORT']).apply(func)
DFB2=DFB.groupby(['LINE','EVA_CHAMBER','PORT']).apply(func)

DATA=pd.merge(DFA2,DFB2,how='outer')
DF=pd.merge(DF,DATA,how='left')

#def func3(value):
#    value2=value.sort_values(['cycleID']).fillna(method='ffill')
#    return value2
#
#DF2=DF.groupby('GLASS_ID').apply(func3)

DF=DF.sort_values(['GLASS_ID','cycleID']).fillna(method='ffill')
DF.cycleID=DF.cycleID.astype(int)

#########################   判断GroupID   ###########################
NewTimeMin=df.EVENTTIME.min()
#sql_MaxTime='select max(eventtime),max(GroupID) from eva_all'
#Value=conn2.exec_(sql_MaxTime)
Value=DF[['EVENTTIME','GroupID']].max()
OldTimeMax=Value[0]
groupID=Value[1]
if NewTimeMin-OldTimeMax>pd.to_timedelta(36,unit='h'):
    df['GroupID']=groupID+1
else:
    df['GroupID']=groupID

#########################   判断cycleID   ###########################

#sql='''
#SELECT distinct groupid, line, eva_chamber, port, eventtime,mask_set,cycleid from public.eva_all
#where (eventtime, line, eva_chamber, port) in(
# SELECT max(EVENTTIME) as eventtime,LINE,EVA_CHAMBER,PORT FROM public.eva_all
# group by LINE,EVA_CHAMBER,PORT)
#'''
#data_last=pd.read_sql_query(sql)#旧数据

data_last=DF.sort_values(['LINE','EVA_CHAMBER','PORT','EVENTTIME']).\
drop_duplicates(['LINE','EVA_CHAMBER','PORT'],keep='last')\
[['GroupID','LINE','EVA_CHAMBER','PORT','EVENTTIME','MASK_SET','cycleID']]

#df2是新数据
df2=df.sort_values(['LINE','EVA_CHAMBER','PORT','EVENTTIME']).drop_duplicates(['LINE','EVA_CHAMBER','PORT'],keep='first')[['LINE','EVA_CHAMBER','PORT','EVENTTIME','MASK_SET']]
DF_M=pd.concat([data_last,df2]).sort_values(['EVENTTIME'])
#####新旧数据之间判别
DF_M.GroupID=DF_M.GroupID.fillna(method='ffill')

#############################
'''
这一部分需要仔细检查，为什么产生了新周期却筛不出来。包括函数里的命名也太乱了，目前包含cycleID，cycleJudge，cycleID
'''
DF_M2=DF_M.groupby(['LINE','EVA_CHAMBER','PORT']).apply(func2)#.drop(['cycleID'],axis=1)
DF_M2.index=range(len(DF_M2))
#
'''
df_m2是新数据每个颗粒度下首条，包含判别是否有跨周期的情况（cycleJudge为标志位）（这个在这一条没用上，在判断内部周期是否变化时会用上）
包含了：判断新数据的初始cycleID
'''
df_m=pd.merge(df2,DF_M2,on=['LINE','EVA_CHAMBER','PORT','EVENTTIME','MASK_SET'])
df_m2=df_m[['LINE', 'EVA_CHAMBER', 'PORT', 'EVENTTIME', 'MASK_SET', 'GroupID','cycleID']]
#判断是否需要计算，要以DF_M2为依据。
d0=DF_M2.groupby(['LINE','EVA_CHAMBER','PORT'])[['cycleJudge']].max()
d0=d0.reset_index()
d0['temp']=1
'''
merge后会出现两列cyclejudge不相同的情况。事实上存在了cyclejudge的变化了有True必有False，但是却筛不出False）
'''
#下面这一行会出现问题
d1=pd.merge(DF_M2,d0,on=['LINE','EVA_CHAMBER','PORT','cycleJudge'],how='left').fillna(0)
data_choose1=d1[d1.temp==0][['GroupID','LINE','EVA_CHAMBER','PORT','cycleID']].rename(columns={'cycleID':'cycleID'}) 

#############################

#####新数据内部判别+给新数据赋值cycleID
data2=df.groupby(['LINE','EVA_CHAMBER','PORT']).apply(func).rename(columns={'cycleID':'cycleJudge'})
data2.index=range(len(data2))
###df_m2有问题
data_new=pd.merge(data2,df_m2,how='outer').sort_values(['LINE', 'EVA_CHAMBER', 'PORT','EVENTTIME'])
data_new.cycleID=data_new.cycleID.fillna(method='ffill')
data_new['cycleID']=data_new.cycleID+data_new.cycleJudge
col=['GroupID','PRODUCT_ID','LINE', 'EVA_CHAMBER', 'PORT', 'EVENTTIME', 'MASK_ID','MASK_SET', \
     'GLASS_ID', 'POS_X','POS_Y', 'X_Label', 'Y_Label', 'PPA_X', 'PPA_Y', 'OFFSET_X',
     'OFFSET_Y', 'OFFSET_tht', 'cycleID']    
data_new2=data_new[col]
data_new3=data_new[['GroupID','LINE','EVA_CHAMBER','PORT','cycleJudge','cycleID']]
temp0=data_new3.groupby(['GroupID','LINE','EVA_CHAMBER','PORT'])[['cycleJudge']].max()#Dcycle代表组内Cycle是否存在变化
temp0=temp0.reset_index()
temp0['temp']=1
#data_new3=data_new3.set_index()
temp1=pd.merge(data_new3,temp0,on=['GroupID','LINE','EVA_CHAMBER','PORT','cycleJudge'],how='left').fillna(0)
data_choose2=temp1[temp1.temp==0][['GroupID','LINE','EVA_CHAMBER','PORT','cycleID']]
data_choose=pd.concat([data_choose1,data_choose2])
#return data_choose,data_new2
