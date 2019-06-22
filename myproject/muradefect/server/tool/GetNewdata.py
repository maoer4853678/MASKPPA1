#coding=utf-8
import pandas as pd
import itertools
import numpy as np

def Pmaskid(Glass_ID,conn): 
    sql='''SELECT DISTINCT
      SHOPNAME
    , MACHINENAME
    , SUBUNITNAME
    , PRODUCTNAME
    , PRODUCTSPECNAME
    , EVENTTIME
    , ITEMNAME
    , SITEVALUE
    FROM  edadb.EDC_PROCESS_DATA_VIEW
    WHERE SHOPNAME = 'OLED'
    AND MACHINENAME = '2CEE01'
    AND SUBUNITNAME IS NOT NULL    
    AND PRODUCTNAME IN (%s)
    AND ITEMNAME NOT LIKE ('%%Reserve%%')
    AND PRODUCTSPECNAME NOT like ('%%MQC%%') 
    '''%(str(Glass_ID)[1:-1])
    p1 = pd.read_sql_query(sql, conn)
    if not (len(p1)):
        return pd.DataFrame([])
    p1.columns = p1.columns.str.upper()
    p1 = p1.rename({'PRODUCTNAME': 'GLASS_ID','PRODUCTSPECNAME': 'PRODUCT_ID'}, axis=1)
    p2 = p1[p1.ITEMNAME.str.contains('MASK_ID|SUB_ID|ALIGN_OFFSET')]
    p3 = p2[['PRODUCT_ID', 'GLASS_ID', 'SUBUNITNAME', 'ITEMNAME',
             'SITEVALUE', 'EVENTTIME']]
    p3['PORT'] = p3.ITEMNAME.str[3]
    p3.ITEMNAME = p3.ITEMNAME.str.replace('EV_A_|EV_B_|ALIGN_OFFSET1_', '') #语法有改善空间
    p4 = p3.set_index(['PRODUCT_ID', 'GLASS_ID', 'SUBUNITNAME', 'EVENTTIME',
                       'PORT', 'ITEMNAME']).unstack()   
    p4.columns = p4.columns.levels[1]
    p4 = p4.reset_index()
    p4.columns.name=None
    p4 = p4[p4.GLASS_ID == p4.SUB_ID].drop(['SUB_ID'], axis=1)
    p4['MASK_SET'] = p4.MASK_ID.str[-4:]
    p4['EVA_CHAMBER'] = 'OC_'+p4.SUBUNITNAME.str[-2]
    p4['LINE'] = p4.SUBUNITNAME.str[-1]
    p4 = p4.drop(['SUBUNITNAME'], axis=1).\
         rename({'X': 'OFFSET_X','Y': 'OFFSET_Y','tht': 'OFFSET_THT'}, axis=1)
    p4 = p4.sort_values(['PRODUCT_ID', 'GLASS_ID', 'EVA_CHAMBER','EVENTTIME']).drop_duplicates(['PRODUCT_ID', 'GLASS_ID', 'EVA_CHAMBER'],keep='last') 
    p4=p4.apply(pd.to_numeric,errors='ignore')
    p4.EVENTTIME=pd.to_datetime(p4.EVENTTIME)
    return p4

def PPA(starttime,endtime,conn):
    sql_ppa='''
    SELECT
      T1.GLASS_ID,
      T2.EVA_CHAMBER,
      T1.PRODUCT_ID,
      T2.POS_X,
      T2.POS_Y,
      T2.PPA_X,
      T2.PPA_Y,
      T1.PANEL_X,
      T1.PANEL_Y, 
      T1.TEG_GROUP,
      T1.TEG_COUNT
    FROM edadb.EDA_EVA_PPA_GLASS_INFO T1
    left join edadb.EDA_EVA_PPA_RAW T2 on t1.glass_key = t2.glass_key
    where GLASS_START_TIME  > = TO_DATE('2019-06-15 10:00:00','YYYY-MM-DD HH24:MI:SS')
    and  GLASS_START_TIME  <  TO_DATE('2019-06-15 11:00:00','YYYY-MM-DD HH24:MI:SS')
    AND PRODUCT_ID NOT like ('%%MQC%%')
    '''%(starttime,endtime)
    P0 = pd.read_sql_query(sql_ppa, conn)
    if not (len(P0)):
        return pd.DataFrame([])
    P0 = P0.dropna(axis=1, how='all').drop_duplicates()    
    P0.columns = P0.columns.str.upper()  
    P0.EVA_CHAMBER = P0.EVA_CHAMBER.str.replace(' ', '')    
    P0.GLASS_START_TIME = pd.to_datetime(P0.GLASS_START_TIME)
    P0.GLASS_END_TIME = pd.to_datetime(P0.GLASS_END_TIME)
    P0 = P0[P0.GLASS_ID.str.startswith('L2E')]
    P1 = P0[(~P0.PPA_X.isna()) &
            (~P0.PRODUCT_ID.isna())]
    P2 = P1.sort_values(['GLASS_ID', 'EVA_CHAMBER', 'POINT_NO','GLASS_START_TIME']).drop_duplicates(['GLASS_ID', 'EVA_CHAMBER', 'POINT_NO'],keep='first') 
    P2.EVA_CHAMBER = P2.EVA_CHAMBER.map({'OC_B\'':'OC_3',
                                         'OC_B'  :'OC_4',
                                         'OC_G\'':'OC_5',
                                         'OC_G'  :'OC_6',
                                         'OC_R\'':'OC_7',
                                         'OC_R'  :'OC_8'})
    P2.POS_X = P2.POS_X.apply(lambda x: round(x, 3))
    P2.POS_Y = P2.POS_Y.apply(lambda x: round(x, 3))
    p1 = P2.sort_values(['GLASS_START_TIME'])
    TagN=int(p1.TEG_COUNT.unique())
    p1=Get_Label(p1)
    return p1

#def Get_Label0(df):
#    var=df[(df.GLASS_ID==df.GLASS_ID[0])&(df.EVA_CHAMBER==df.EVA_CHAMBER[0])]
##    var.POS_X.astype(int).unique()    
##    var.POS_Y.astype(int).unique()
#    temp_x=var.POS_X.astype(int).drop_duplicates().sort_values()
#    x=temp_x[temp_x.diff().fillna(10)>5]
#    temp_y=var.POS_Y.astype(int).drop_duplicates().sort_values()
#    y=temp_y[temp_y.diff().fillna(10)>5]
#    xbins=GetBins(x)
#    ybins=GetBins(y)
#    df['X_Label'] = pd.cut(df.POS_X,bins = xbins,labels=range(1,len(xbins)))
#    df['X_Label']= df['X_Label'].astype(int)
#    df['Y_Label'] = pd.cut(df.POS_Y,bins = ybins,labels=range(1,len(ybins))[::-1])
#    df['Y_Label']= df['Y_Label'].astype(int)
#    return df

def Get_Label(df,TagN):
    var=df[(df.GLASS_ID==df.iloc[0,]['GLASS_ID'])&(df.EVA_CHAMBER==df.iloc[0,]['EVA_CHAMBER'])]
    temp_y=var.POS_Y.astype(int).drop_duplicates().sort_values()
    y=temp_y[temp_y.diff().fillna(10)>5]
    ybins=GetBins(y)
    df['Y_Label'] = pd.cut(df.POS_Y,bins = ybins,labels=range(1,len(ybins))[::-1])
    df['Y_Label']= df['Y_Label'].astype(int)
    
    df['X_Label']=df.sort_values(['Y_Label','POS_X']).reset_index().index//3+1
    temp=df.sort_values(['POS_Y','POS_X'])
    temp.index=range(len(temp))    
    temp['X_Label']=temp.index//TagN+1
    return temp

def GetBins(x,gap=50):
    ## 通过坐标生成bins
    x = x.sort_values()
    bins = x.rolling(2).mean().dropna().round(3).tolist()
    bins.insert(0,x.iloc[0]-gap)
    bins.append(x.iloc[-1]+gap)
    return bins

def DataCollect(starttime,endtime,conn):
    ##步骤1：PPA数据
    col=['PRODUCT_ID','EVENTTIME','GLASS_ID','EVA_CHAMBER','MASK_ID',
           'MASK_SET','PORT','LINE','POS_X','POS_Y','X_Label','Y_Label',
           'PPA_X','PPA_Y','OFFSET_X','OFFSET_Y','OFFSET_THT']
    DF1=PPA(starttime,endtime,conn)
    if not len(DF1):
        DF=pd.DataFrame([],columns=col)
    else:
        Glass_ID=DF1.GLASS_ID.unique().tolist()
        ##步骤2：maskID数据 
        DF2=Pmaskid(Glass_ID,conn1)
        ##步骤3：合并
        DF=pd.merge(DF1,DF2,on=['PRODUCT_ID','GLASS_ID','EVA_CHAMBER']) 
        DF=DF[col]   
    return DF

def AddInitDataID(df):
    df.EVENTTIME=pd.to_datetime(df.EVENTTIME)
    dfA=df[(df.EVA_CHAMBER==df.EVA_CHAMBER.min())&(df.PORT=='A')].sort_values(['GroupID','LINE','EVA_CHAMBER','PORT','EVENTTIME'])[['GroupID','LINE','EVA_CHAMBER','PORT','EVENTTIME','MASK_SET','GLASS_ID']].drop_duplicates()
    dfB=df[(df.EVA_CHAMBER==df.EVA_CHAMBER.min())&(df.PORT=='B')].sort_values(['GroupID','LINE','EVA_CHAMBER','PORT','EVENTTIME'])[['GroupID','LINE','EVA_CHAMBER','PORT','EVENTTIME','MASK_SET','GLASS_ID']].drop_duplicates()
    
    dfA2=dfA.groupby(['LINE','EVA_CHAMBER','PORT']).apply(func)
    dfB2=dfB.groupby(['LINE','EVA_CHAMBER','PORT']).apply(func)
    
    DATA=pd.merge(dfA2,dfB2,how='outer')
    df=pd.merge(df,DATA,how='left')
    df=df.sort_values(['GLASS_ID','cycleID']).fillna(method='ffill')
    df.cycleID=df.cycleID.astype(int)
    df=df.sort_values(['GroupID','LINE','EVA_CHAMBER','PORT','EVENTTIME','MASK_SET','X_Label','Y_Label'])
    return df

#def CycleJudge(df,conn):
#    #####新cycle判断(groupby到新的颗粒度的基础上)
#    df01=df[['LINE','EVA_CHAMBER','PORT','MASK_SET']].drop_duplicates()
#    df_cj=df01.groupby(['LINE','EVA_CHAMBER','PORT'])['MASK_SET'].\
#    apply(lambda x:[k for k, v in itertools.groupby(x)]).\
#    reset_index().rename(columns={'MASK_SET':'MASK_SET_0'})
#    df_cj['Cycle_num']=df_cj.MASK_SET_0.apply(len)
#    DF00=pd.merge(df01,df_cj,on=['LINE','EVA_CHAMBER','PORT'])    
#    #########针对Cycle_num=1的情况    
#    DF100=DF00[DF00.Cycle_num==1]
#    DF100.MASK_SET_0=DF100.MASK_SET_0.apply(lambda x:x[0])
#    sql='''
#    SELECT distinct eventtime, line, eva_chamber, port, mask_set from public.eva_all
#    where (eventtime, line, eva_chamber, port) in(
#    	SELECT max(EVENTTIME),LINE,EVA_CHAMBER,PORT FROM public.eva_all
#    	group by LINE,EVA_CHAMBER,PORT)
#    '''
#    DF_sql=pd.read_sql_query(sql,conn)
#    DF_sql.columns=DF_sql.columns.str.upper()    
#    data_choose1=DF100[DF100.MASK_SET!=DF100.MASK_SET_0][['LINE','EVA_CHAMBER','PORT','MASK_SET']]
#    #########针对Cycle>1的情况
#    DF200=DF00[DF00.Cycle_num>1]
#    if len(DF200):
#        DF200.MASK_SET_0=DF200.MASK_SET_0.apply(lambda x:x[0:-1])
#        data_choose2 = DF200[DF200.apply(lambda x:x['MASK_SET'] in x['MASK_SET_0'],axis=1)].\
#            drop(['MASK_SET_0',"Cycle_num"],axis=1).drop_duplicates()
#    else:
#        data_choose2 = pd.DataFrame([],columns=  ['LINE', 'EVA_CHAMBER', 'PORT', 'MASK_SET'])
#
#    data_choose=data_choose1.append(data_choose2)
#    return data_choose
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

def CycleJudge(df,conn):
    #####新cycle判断(groupby到新的颗粒度的基础上)    
    sql='''
    SELECT distinct groupid, line, eva_chamber, port, eventtime,mask_set,cycleid from public.eva_all
    where (eventtime, line, eva_chamber, port) in(
     SELECT max(EVENTTIME) as eventtime,LINE,EVA_CHAMBER,PORT FROM public.eva_all
     group by LINE,EVA_CHAMBER,PORT)
    '''
    data_last=pd.read_sql_query(sql,conn)
    #df2是新数据各个颗粒度的第一个数值
    df2=df.sort_values(['LINE','EVA_CHAMBER','PORT','EVENTTIME']).drop_duplicates(['LINE','EVA_CHAMBER','PORT'],keep='first')[['GroupID','LINE','EVA_CHAMBER','PORT','EVENTTIME','MASK_SET']]
    DF_M=pd.concat([data_last,df2]).sort_values(['EVENTTIME'])
    #####新旧数据之间判别，将旧数据的相关标志位传给新数据
    DF_M2=DF_M.groupby(['LINE','EVA_CHAMBER','PORT']).apply(func2)
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
    temp1=pd.merge(data_new3,temp0,on=['GroupID','LINE','EVA_CHAMBER','PORT','cycleJudge'],how='left').fillna(0)
    data_choose2=temp1[temp1.temp==0][['GroupID','LINE','EVA_CHAMBER','PORT','cycleID']]
    data_choose=pd.concat([data_choose1,data_choose2])
    return data_choose,data_new2

def GetCalPPA(DataChoose,conn):
    ####将输出的4列存到temp表中，覆盖式写入。 
#    DataChoose.to_sql(name='temp',con=conn,if_exists='replace')
    conn.delete_table("temp")
    conn.creat_table_from_df("temp",DataChoose)
    conn.insert_df("temp",DataChoose)
    
    sql='''
    select * from public.eva_all inner join (
    select eventtime, line, eva_chamber, port, mask_set
    from(
     select eventtime, line, eva_chamber, port, mask_set,row_number()
     over(partition by (line, eva_chamber, port, mask_set)
       order by eventtime desc)as RowNumber
     from(SELECT distinct a.eventtime, a.line, a.eva_chamber, a.port, a.mask_set from public.eva_all as a
         inner join public.temp as b on
         (a.line=b.line and a.eva_chamber=b.eva_chamber and a.port=b.port and a.mask_set=b.mask_set)
         order by a.eventtime desc)as t1)as X
         where X.RowNumber<=3)as t3 on
     public.eva_all.eventtime=t3.eventtime and
     public.eva_all.line=t3.line and
     public.eva_all.eva_chamber=t3.eva_chamber and
     public.eva_all.port=t3.port and
     public.eva_all.mask_set=t3.mask_set 
    '''
    df = pd.read_sql_query(sql,conn.obj.conn)
    df=df.T.drop_duplicates().T.drop_duplicates()
    print (df.columns)
    df.columns = df.columns.str.upper()
    df = df.sort_values(['LINE','EVA_CHAMBER','MASK_SET','EVENTTIME'])
    return df

def CreateOffsetAfter(g):
    '''
    1、deltaX,Y的顺序可能需要做调整
    2、考虑到通用性，建议返回值不删除这几个delta
    '''
    g1 =g[['GLASS_ID','OFFSET_X','OFFSET_Y','OFFSET_THT']].drop_duplicates().set_index("GLASS_ID")
    t1 = (g1-g1.loc[g1.index[-1]]).reset_index()
    t1 =t1.rename(dict(zip(['OFFSET_X','OFFSET_Y','OFFSET_THT'],['deltaX','deltaY','deltaT'])),axis=1)
    t2 = pd.merge(g,t1,on = ['GLASS_ID'])
    t2['PPA_X_After'] = t2['PPA_X']+t2['deltaY']-t2['deltaT']*t2['POS_Y']
    t2['PPA_Y_After'] = t2['PPA_Y']+t2['deltaX']+t2['deltaT']*t2['POS_X']
    return t2.drop(['deltaX','deltaY','deltaT'],axis=1)

def Alarm(df,threshold={},exclude=[],conn=None):
    '''
    df总出现重复列，需要研究原因
    '''
    columns = list((set(threshold.keys()) - set(exclude)).intersection(set(df.columns)))
    def func(g):
        res = g[columns].apply(lambda x:x[x.abs()>threshold[x.name]].\
          describe().loc[['count','max','min']],axis=0).T.reset_index()\
               .rename(columns ={"index":"key"})
        return res

    res = df.groupby(['LINE','EVA_CHAMBER','PORT','MASK_SET','GLASS_ID','EVENTTIME']).apply(func).reset_index()
    ## 插入数据库
    res = res[res['count']>0]
    if len(res):
        res = res.drop("level_6",axis=1)
        res['LINE'] = res['LINE'].astype(int)
        if 'alarm' not in conn.list_table():
            conn.creat_table_from_df(tablename='alarm', df=res)
        conn.insert_df(tablename='alarm',df=res)
        return True
    else:
        return False
    