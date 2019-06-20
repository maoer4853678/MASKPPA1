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
    '''
    问郭晓：GLASS_ID和SUB_ID不同的行，代表什么？
    '''
    p4 = p4[p4.GLASS_ID == p4.SUB_ID].drop(['SUB_ID'], axis=1) 
    p4['MASK_SET'] = p4.MASK_ID.str[-4:]
    p4['EVA_CHAMBER'] = 'OC_'+p4.SUBUNITNAME.str[-2]
    p4['LINE'] = p4.SUBUNITNAME.str[-1]
    p4 = p4.drop(['SUBUNITNAME'], axis=1).\
         rename({'X': 'OFFSET_X','Y': 'OFFSET_Y','tht': 'OFFSET_tht'}, axis=1)
    p4 = p4.sort_values(['PRODUCT_ID', 'GLASS_ID', 'EVA_CHAMBER','EVENTTIME']).drop_duplicates(['PRODUCT_ID', 'GLASS_ID', 'EVA_CHAMBER'],keep='last')     
    return p4

def PPA(starttime,endtime,conn):
    sql_ppa='''
    SELECT PRODUCT_ID
    , EVA_CHAMBER
    , GLASS_ID
    , POINT_NO
    , GLASS_START_TIME
    , GLASS_END_TIME
    , POS_X
    , POS_Y
    , PPA_X
    , PPA_Y
    FROM EDADB.EDA_EVA_PPA where 
    (GLASS_START_TIME BETWEEN TO_DATE('%s','YYYY-MM-DD HH24:MI:SS')
    AND TO_DATE('%s','YYYY-MM-DD HH24:MI:SS'))  
    '''%(starttime,endtime)
    P0 = pd.read_sql_query(sql_ppa, conn)    
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
    p1 = P2.sort_values(['GLASS_START_TIME'])
    p1=Get_Label(p1)
    return p1

def Get_Label(df):
    var=df[(df.GLASS_ID==df.GLASS_ID[2])&(df.EVA_CHAMBER==df.EVA_CHAMBER[0])]
    var.POS_X.astype(int).unique()    
    var.POS_Y.astype(int).unique()
    temp_x=var.POS_X.astype(int).drop_duplicates().sort_values()
    x=temp_x[temp_x.diff().fillna(10)>5]    
    temp_y=var.POS_Y.astype(int).drop_duplicates().sort_values()
    y=temp_y[temp_y.diff().fillna(10)>5]
    xbins=GetBins(x)
    ybins=GetBins(y)
    df['X_Label'] = pd.cut(df.POS_X,bins = xbins,labels=range(1,len(xbins)))
    df['X_Label']= df['X_Label'].astype(int)
    df['Y_Label'] = pd.cut(df.POS_Y,bins = ybins,labels=[j+1 for j in range(len(ybins))][::-1])
    df['Y_Label']= df['Y_Label'].astype(int)
    return df

def GetBins(x,gap=50):
    ## 通过坐标生成bins
    x = x.sort_values()
    bins = x.rolling(2).mean().dropna().round(3).tolist()
    bins.insert(0,x.iloc[0]-gap)
    bins.append(x.iloc[-1]+gap)
    return bins

def DataCollect(starttime,endtime,conn):
    ##步骤1：PPA数据
    DF1=PPA(starttime,endtime,conn)
    Glass_ID=DF1.GLASS_ID.unique().tolist()
    ##步骤2：maskID数据    
    DF2=Pmaskid(Glass_ID,conn)
    #DF2=Pmaskid(S,E)    
    ##步骤3：合并
    DF=pd.merge(DF1,DF2,on=['GLASS_ID','EVA_CHAMBER'])
    
    DF=DF[['PRODUCT_ID','EVENT_TIME','GLASS_ID','EVA_CHAMBER','MASK_ID',
           'MASK_SET','PORT','LINE','POS_X','POS_Y','X_Label','Y_Label',
           'PPA_X','PPA_Y','OFFSET_X','OFFSET_Y','OFFSET_tht']]
    
    
    return DF

def CycleJudge(df,conn):
    #####新cycle判断(groupby到新的颗粒度的基础上)
    df01=df[['LINE','EVA_CHAMBER','PORT','MASK_SET']].drop_duplicates()
    df_cj=df01.groupby(['LINE','EVA_CHAMBER','PORT'])['MASK_SET'].\
    apply(lambda x:[k for k, v in itertools.groupby(x)]).\
    reset_index().rename(columns={'MASK_SET':'MASK_SET_0'})
    df_cj['Cycle_num']=df_cj.MASK_SET_0.apply(len)
    DF00=pd.merge(df01,df_cj,on=['LINE','EVA_CHAMBER','PORT'])    
    #########针对Cycle_num=1的情况    
    DF100=DF00[DF00.Cycle_num==1]
    DF100.MASK_SET_0=DF100.MASK_SET_0.apply(lambda x:x[0])
    sql='''
    SELECT distinct eventtime, line, eva_chamber, port, mask_set from public.eva_all
    where (eventtime, line, eva_chamber, port) in(
    	SELECT max(EVENTTIME),LINE,EVA_CHAMBER,PORT FROM public.eva_all
    	group by LINE,EVA_CHAMBER,PORT)
    '''
    DF_sql=pd.read_sql_query(sql,conn)
    DF_sql.columns=DF_sql.columns.str.upper()    
    data_choose1=DF100[DF100.MASK_SET!=DF100.MASK_SET_0][['LINE','EVA_CHAMBER','PORT','MASK_SET']]
    #########针对Cycle>1的情况
    DF200=DF00[DF00.Cycle_num>1]
    '''
    希望实现列A是个元素，列2是个list；如果列1的元素不再列2，则去除。
    DF200.MASK_SET_0=DF200.drop('MASK_SET',axis=1).MASK_SET_0.apply(lambda x:str(x[0:-1]))
    DF300=DF200[DF200.MASK_SET.isin(DF200.MASK_SET_0)]
    '''    
#    DF200=DF200
    if len(DF200):
        DF200.MASK_SET_0=DF200.MASK_SET_0.apply(lambda x:x[0:-1])
        data_choose2 = DF200[DF200.apply(lambda x:x['MASK_SET'] in x['MASK_SET_0'],axis=1)].\
            drop(['MASK_SET_0',"Cycle_num"],axis=1).drop_duplicates()
    else:
        data_choose2 = pd.DataFrame([],columns=  ['LINE', 'EVA_CHAMBER', 'PORT', 'MASK_SET'])
            
    data_choose=data_choose1.append(data_choose2)
    return data_choose


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
    print (df.columns)
    df.columns = df.columns.str.upper()
    df = df.sort_values(['LINE','EVA_CHAMBER','MASK_SET','EVENTTIME']) 
    return df

def CreateOffsetAfter(g):
    g1 =g[['GLASS_ID','OFFSET_X','OFFSET_Y','OFFSET_tht']].drop_duplicates().set_index("GLASS_ID")
    t1 = (g1-g1.loc[g1.index[-1]]).reset_index()
    t1 =t1.rename(dict(zip(['OFFSET_X','OFFSET_Y','OFFSET_tht'],['deltaX','deltaY','deltaT'])),axis=1)
    t2 = pd.merge(g,t1,on = ['GLASS_ID'])
    t2['PPA_X_After'] = t2['PPA_X']+t2['deltaY']-t2['deltaT']*t2['POS_Y']
    t2['PPA_Y_After'] = t2['PPA_Y']+t2['deltaX']+t2['deltaT']*t2['POS_X']
    return t2.drop(['deltaX','deltaY','deltaT'],axis=1)


def Alarm(df,threshold={},exclude=[],conn=None):  
    columns = list(set(threshold.keys()) - set(exclude))
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
    