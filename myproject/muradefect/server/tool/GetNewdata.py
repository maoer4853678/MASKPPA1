#coding=utf-8
import pandas as pd
import itertools
import numpy as np

def Pmaskid(Glass_ID,conn): 
    sql='''SELECT DISTINCT
      SHOPNAME
    , MACHINENAME
    , subunitname
    , productname
    , PRODUCTSPECNAME
    , eventtime
    , itemname
    , SITEVALUE
    FROM  edadb.EDC_PROCESS_DATA_VIEW
    WHERE SHOPNAME = 'OLED'
    AND MACHINENAME = '2CEE01'
    AND subunitname IS NOT NULL    
    AND productname IN (%s)
    AND itemname NOT LIKE ('%%Reserve%%')
    AND PRODUCTSPECNAME NOT like ('%%MQC%%') 
    '''%(str(Glass_ID)[1:-1])
    p1 = pd.read_sql_query(sql, conn)
    if not (len(p1)):
        return pd.DataFrame([],columns = ['product_id','glass_id','eva_chamber'])
    p1.columns = p1.columns.str.lower()
    p1 = p1.rename({'productname': 'glass_id','productspecname': 'product_id'}, axis=1)
    p2 = p1[p1.itemname.str.contains('MASK_ID|SUB_ID|ALIGN_OFFSET')]
    p3 = p2[['product_id', 'glass_id', 'subunitname', 'itemname',
             'sitevalue', 'eventtime']]
    p3['port'] = p3.itemname.str[3]
    p3.itemname = p3.itemname.str.replace('EV_A_|EV_B_|ALIGN_OFFSET1_', '') #语法有改善空间
    p4 = p3.set_index(['product_id', 'glass_id', 'subunitname', 'eventtime',
                       'port', 'itemname']).unstack()
    p4.columns = p4.columns.levels[1]
    p4.columns=p4.columns.str.lower()
    p4 = p4.reset_index()
    p4.columns.name=None
    print ("p4.shape",p4.shape)
    print (p4.columns)
    if not len(p4) or "sub_id" not in p4.columns.tolist():
        return pd.DataFrame([],columns = ['product_id','glass_id','eva_chamber'])
    p4 = p4[p4.glass_id == p4.sub_id].drop(['sub_id'], axis=1)
    p4['mask_set'] = p4.mask_id.str[-4:]
    p4['eva_chamber'] = 'OC_'+p4.subunitname.str[-2]
    p4['line'] = p4.subunitname.str[-1]
    p4 = p4.drop(['subunitname'], axis=1).\
         rename({'x': 'offset_x','y': 'offset_y','tht': 'offset_tht'}, axis=1)
    p4 = p4.sort_values(['product_id', 'glass_id', 'eva_chamber','eventtime']).drop_duplicates(['product_id', 'glass_id', 'eva_chamber'],keep='last') 
    p4=p4.apply(pd.to_numeric,errors='ignore')
    p4.eventtime=pd.to_datetime(p4.eventtime)
    return p4

def PPA(starttime,endtime,conn):
    sql_ppa='''
    SELECT
      T1.glass_id,
      glass_start_time,
      T2.eva_chamber,
      T1.product_id,
      T2.pos_x,
      T2.pos_y,
      T2.ppa_x,
      T2.ppa_y,
      T1.PANEL_X,
      T1.PANEL_Y, 
      T1.TEG_GROUP,
      T1.TEG_COUNT
    FROM edadb.EDA_EVA_PPA_GLASS_INFO T1
    left join edadb.EDA_EVA_PPA_RAW T2 on t1.glass_key = t2.glass_key
    where glass_start_time  >= TO_DATE('%s','YYYY-MM-DD HH24:MI:SS')
    and  glass_start_time  <  TO_DATE('%s','YYYY-MM-DD HH24:MI:SS')
    AND product_id NOT like ('%%MQC%%')
    '''%(starttime,endtime)
    P0 = pd.read_sql_query(sql_ppa, conn)
    if not (len(P0)):
        return pd.DataFrame([])
    P0 = P0.dropna(axis=1, how='all').drop_duplicates()   
    P0.columns = P0.columns.str.lower()
    P0.glass_start_time = pd.to_datetime(P0.glass_start_time)
    P0.eva_chamber = P0.eva_chamber.str.replace(' ', '')    
    P0 = P0[P0.glass_id.str.startswith('L2E')]
    P1 = P0[(~P0.ppa_x.isna()) &
            (~P0.product_id.isna())]
    #P2 = P1.sort_values(['glass_id', 'eva_chamber','glass_start_time']).drop_duplicates(['glass_id', 'eva_chamber'],keep='first') 
    P1.eva_chamber = P1.eva_chamber.map({'OC_B\'':'OC_3',
                                         'OC_B'  :'OC_4',
                                         'OC_G\'':'OC_5',
                                         'OC_G'  :'OC_6',
                                         'OC_R\'':'OC_7',
                                         'OC_R'  :'OC_8'})
    P1.pos_x = P1.pos_x.apply(lambda x: round(x, 3))
    P1.pos_y = P1.pos_y.apply(lambda x: round(x, 3))
    p1 = P1.sort_values(['glass_start_time'])
#    TagN=int(p1.teg_count.unique())
    p1=Get_Label(p1)
#    print (p1.shape)
#    print (p1.head())
    p1 = ResetValue(p1) ## 9999 插值  
#    print (p1.shape)
#    print (p1.head())
    
    return p1

#def Get_Label0(df):
#    var=df[(df.glass_id==df.glass_id[0])&(df.eva_chamber==df.eva_chamber[0])]
##    var.pos_x.astype(int).unique()    
##    var.pos_y.astype(int).unique()
#    temp_x=var.pos_x.astype(int).drop_duplicates().sort_values()
#    x=temp_x[temp_x.diff().fillna(10)>5]
#    temp_y=var.pos_y.astype(int).drop_duplicates().sort_values()
#    y=temp_y[temp_y.diff().fillna(10)>5]
#    xbins=GetBins(x)
#    ybins=GetBins(y)
#    df['pos_y'] = pd.cut(df.pos_x,bins = xbins,labels=range(1,len(xbins)))
#    df['pos_y']= df['pos_y'].astype(int)
#    df['y_label'] = pd.cut(df.pos_y,bins = ybins,labels=range(1,len(ybins))[::-1])
#    df['y_label']= df['y_label'].astype(int)
#    return df

def Get_Label(df):
     def func(var):
         temp_y=var.pos_y.astype(int).drop_duplicates().sort_values()
         y=temp_y[temp_y.diff().fillna(10)>5]
         ybins=GetBins(y)
         var['y_label'] = pd.cut(var.pos_y,bins = ybins,labels=range(1,len(ybins))[::-1])
         var['y_label']= var['y_label'].astype(int)
         var = var.sort_values(['y_label','pos_x'])
         panel_x = int(var.panel_x.iloc[0])
         teg_count = int(var.teg_count.iloc[0])
         var['x_label'] = np.repeat(range(panel_x),teg_count).tolist()*len(var['y_label'].unique())
         return var
     df = df.groupby(['glass_id','eva_chamber']).apply(func)
    
#    var=df[(df.glass_id==df.iloc[0,]['glass_id'])&(df.eva_chamber==df.iloc[0,]['eva_chamber'])]
#    
#    y=temp_y[temp_y.diff().fillna(10)>5]
#    ybins=GetBins(y)
#    df['y_label'] = pd.cut(df.pos_y,bins = ybins,labels=range(1,len(ybins))[::-1])
#    df['y_label']= df['y_label'].astype(int)
#    
#    #df['x_label']=df.sort_values(['y_label','pos_x']).reset_index().index//TagN+1
#    temp=df.sort_values(['pos_y','pos_x'])
#    temp.index=range(len(temp))    
#    temp['x_label']=temp.index//TagN+1
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
    col=['product_id','eventtime','glass_id','eva_chamber','mask_id',
           'mask_set','port','line','pos_x','pos_y','x_label','y_label',
           'ppa_x','ppa_y','offset_x','offset_y','offset_tht']
    DF1=PPA(starttime,endtime,conn)
    if not len(DF1):
        DF=pd.DataFrame([],columns=col)
    else:
        Glass_ID=DF1.glass_id.unique().tolist()
        ##步骤2：maskID数据 
        DF2=Pmaskid(Glass_ID,conn)
        ##步骤3：合并
        if not len(DF2):
            return pd.DataFrame([],columns=col)
        DF=pd.merge(DF1,DF2,on=['product_id','glass_id','eva_chamber']) 
        DF=DF[col]   
    return DF

def AddInitDataID(df):
    df['groupid']=0
    dfA=df[(df.eva_chamber==df.eva_chamber.min())&(df.port=='A')].sort_values(['groupid','line','eva_chamber','port','eventtime'])[['groupid','line','eva_chamber','port','eventtime','mask_set','glass_id']].drop_duplicates()
    dfB=df[(df.eva_chamber==df.eva_chamber.min())&(df.port=='B')].sort_values(['groupid','line','eva_chamber','port','eventtime'])[['groupid','line','eva_chamber','port','eventtime','mask_set','glass_id']].drop_duplicates()
    
    dfA2=dfA.groupby(['line','eva_chamber','port']).apply(func1)
    dfB2=dfB.groupby(['line','eva_chamber','port']).apply(func1)
    
    DATA=pd.concat([dfA2,dfB2])
    DATA.index = range(len(DATA))
    df=pd.merge(df,DATA,how='left',on = ['groupid', 'line', 'eva_chamber', 'port', 'eventtime', 'mask_set',\
       'glass_id'])
    df=df.sort_values(['glass_id','cycleid']).fillna(method='ffill')
    df.cycleid=df.cycleid.astype(int)
    df=df.sort_values(['groupid','line','eva_chamber','port','eventtime','mask_set','x_label','y_label'])
    return df

#def CycleJudge(df,conn):
#    #####新CYCLE判断(groupby到新的颗粒度的基础上)
#    df01=df[['line','eva_chamber','port','mask_set']].drop_duplicates()
#    df_cj=df01.groupby(['line','eva_chamber','port'])['mask_set'].\
#    apply(lambda x:[k for k, v in itertools.groupby(x)]).\
#    reset_index().rename(columns={'mask_set':'mask_set_0'})
#    df_cj['Cycle_num']=df_cj.mask_set_0.apply(len)
#    DF00=pd.merge(df01,df_cj,on=['line','eva_chamber','port'])    
#    #########针对Cycle_num=1的情况    
#    DF100=DF00[DF00.Cycle_num==1]
#    DF100.mask_set_0=DF100.mask_set_0.apply(lambda x:x[0])
#    sql='''
#    SELECT distinct eventtime, line, eva_chamber, port, mask_set from public.eva_all
#    where (eventtime, line, eva_chamber, port) in(
#    	SELECT max(eventtime),line,eva_chamber,port FROM public.eva_all
#    	group by line,eva_chamber,port)
#    '''
#    DF_sql=pd.read_sql_query(sql,conn)
#    DF_sql.columns=DF_sql.columns.str.upper()    
#    data_choose1=DF100[DF100.mask_set!=DF100.mask_set_0][['line','eva_chamber','port','mask_set']]
#    #########针对Cycle>1的情况
#    DF200=DF00[DF00.Cycle_num>1]
#    if len(DF200):
#        DF200.mask_set_0=DF200.mask_set_0.apply(lambda x:x[0:-1])
#        data_choose2 = DF200[DF200.apply(lambda x:x['mask_set'] in x['mask_set_0'],axis=1)].\
#            drop(['mask_set_0',"Cycle_num"],axis=1).drop_duplicates()
#    else:
#        data_choose2 = pd.DataFrame([],columns=  ['line', 'eva_chamber', 'port', 'mask_set'])
#
#    data_choose=data_choose1.append(data_choose2)
#    return data_choose
def func1(value):
    value2=value.sort_values(['eventtime'])
    value2['cycleid']=(value2.mask_set!=value2.mask_set.shift(-1)).shift(1).fillna(0).astype(int)
    value2['cycleid']=value2.cycleid.cumsum()
    return value2

def func2(value):
    value2=value.sort_values(['eventtime'])
    value2['cyclejudge']=(value2.mask_set!=value2.mask_set.shift(-1)).shift(1).fillna(0).astype(int)
    value2['cycleid']=value2['cycleid'].fillna(method='ffill').fillna(0).astype(int)
    value2['cycleid']=value2.cycleid+value2.cyclejudge
    return value2

def CycleJudge(df,conn):
    #####新CYCLE判断(groupby到新的颗粒度的基础上)    
    sql='''
    SELECT distinct product_id,groupid, line, eva_chamber, port, eventtime,mask_set,CYCLEid from public.eva_all
    where (eventtime, line, eva_chamber, port) in(
     SELECT max(eventtime) as eventtime,line,eva_chamber,port FROM public.eva_all
     group by line,eva_chamber,port)
    '''
    data_last=pd.read_sql_query(sql,conn)
    #df2是新数据各个颗粒度的第一个数值;data_last有cycleid,df2没有cycleid，因此concat后会出现一些nan
    df2=df.sort_values(["product_id","groupid",'line','eva_chamber','port','eventtime']).\
        drop_duplicates(["product_id",'groupid','line','eva_chamber','port'],keep='first')\
        [['product_id','groupid','line','eva_chamber','port','eventtime','mask_set']]
    DF_M=pd.concat([data_last,df2]).sort_values(['eventtime'])#必然有一部分行的cycleid是nan
    #####新旧数据之间判别，将旧数据的相关标志位传给新数据
    DF_M2=DF_M.groupby(['product_id','groupid','line','eva_chamber','port']).apply(func2)
    DF_M2.index=range(len(DF_M2))
    #
    '''
    df_m2是新数据每个颗粒度下首条，包含判别是否有跨周期的情况（cyclejudge为标志位）（这个在这一条没用上，在判断内部周期是否变化时会用上）
    包含了：判断新数据的初始cycleid
    '''
    df_m=pd.merge(df2,DF_M2,on=["product_id",'groupid','line','eva_chamber','port','eventtime','mask_set'])
    df_m2=df_m[['line', 'eva_chamber', 'port', 'eventtime', 'mask_set','product_id', 'groupid','cycleid']]
    #判断是否需要计算，要以DF_M2为依据。
    d0=DF_M2.groupby(['product_id', 'groupid','line','eva_chamber','port'])[['cyclejudge']].max()
    d0=d0.reset_index()
    d0['temp']=1

    d1=pd.merge(DF_M2,d0,on=['product_id', 'groupid','line','eva_chamber','port','cyclejudge'],how='left').fillna(0)
    data_choose1=d1[d1.temp==0][["product_id",'groupid','line','eva_chamber','port','cycleid']]
    #####新数据内部判别+给新数据赋值cycleid
    data2=df.groupby(['product_id', 'groupid','line','eva_chamber','port']).apply(func1).rename(columns={'cycleid':'cyclejudge'})
    data2.index=range(len(data2))
    ###df_m2有问题
    data_new=pd.merge(data2,df_m2,how='outer').sort_values(['line', 'eva_chamber', 'port','eventtime'])
    data_new.cycleid=data_new.cycleid.fillna(method='ffill')
    data_new['cycleid']=data_new.cycleid+data_new.cyclejudge
    print ("data_new.shape: ", data_new.shape)
    ###  data_new 存在数据重复记录 
    data_new = data_new.drop_duplicates()
    print ("data_new.shape: ", data_new.shape)    
    col=['groupid','product_id','line', 'eva_chamber', 'port', 'eventtime', 'mask_id','mask_set', \
         'glass_id', 'pos_x','pos_y', 'x_label', 'y_label', 'ppa_x', 'ppa_y', 'offset_x',
         'offset_y', 'offset_tht', 'cycleid']    
    data_new2=data_new[col]
    data_new3=data_new[['groupid',"product_id",'line','eva_chamber','port','cyclejudge','cycleid']]
    temp0=data_new3.groupby(['groupid',"product_id",'line','eva_chamber','port'])[['cyclejudge']].max()#DCYCLE代表组内Cycle是否存在变化
    temp0=temp0.reset_index()
    temp0['temp']=1
    temp1=pd.merge(data_new3,temp0,on=['groupid',"product_id",'line','eva_chamber','port','cyclejudge'],how='left').fillna(0)
    data_choose2=temp1[temp1.temp==0][['groupid',"product_id",'line','eva_chamber','port','cycleid']]
    data_choose=pd.concat([data_choose1,data_choose2]).drop_duplicates()
    ## data_choose 可能全为空
    return data_choose,data_new2

#def GetCalPPA(DataChoose,conn):
#    ####将输出的4列存到temp表中，覆盖式写入。 
##    DataChoose.to_sql(name='temp',con=conn,if_exists='replace')
#    conn.delete_table("temp")
#    conn.creat_table_from_df("temp",DataChoose)
#    conn.insert_df("temp",DataChoose)
#    
#    sql='''
#    select * from public.eva_all inner join (
#    select eventtime, line, eva_chamber, port, mask_set
#    from(
#     select eventtime, line, eva_chamber, port, mask_set,row_number()
#     over(partition by (line, eva_chamber, port, mask_set)
#       order by eventtime desc)as RowNumber
#     from(SELECT distinct a.eventtime, a.line, a.eva_chamber, a.port, a.mask_set from public.eva_all as a
#         inner join public.temp as b on
#         (a.line=b.line and a.eva_chamber=b.eva_chamber and a.port=b.port and a.mask_set=b.mask_set)
#         order by a.eventtime desc)as t1)as X
#         where X.RowNumber<=3)as t3 on
#     public.eva_all.eventtime=t3.eventtime and
#     public.eva_all.line=t3.line and
#     public.eva_all.eva_chamber=t3.eva_chamber and
#     public.eva_all.port=t3.port and
#     public.eva_all.mask_set=t3.mask_set 
#    '''
#    df = pd.read_sql_query(sql,conn.obj.conn)
#    df=df.T.drop_duplicates().T.drop_duplicates()
#    print (df.columns)
#    df.columns = df.columns.str.upper()
#    df = df.sort_values(['line','eva_chamber','mask_set','eventtime'])
#    return df
def Getcalmap(data,conn,tablename = 'eva_all'):
    conn.delete_table("temp")
    conn.creat_table_from_df("temp",data)
    conn.insert_df("temp",data)
    cols = conn.show_schema("temp")['Field'].tolist()
    conditon = ' and '.join(map(lambda x:" t1.%s=t2.%s "%(x,x),cols))
    sql='''
    select t1.* from %s t1 inner join temp as t2
    on %s
    '''%(tablename,conditon)
    data = pd.read_sql_query(sql,conn.obj.conn)
    return data

def GetCalPPA(DataChoose,data2,conn,number = 3):
    ####将输出的4列存到temp表中，覆盖式写入。 
#    DataChoose.to_sql(name='temp',con=conn,if_exists='replace')
    ## 本次1小时获取的数据中  存在需要计算的eva_all表
    data2.groupid=data2.groupid.astype(int)
    data2.cycleid=data2.cycleid.astype(int)
    DataChoose.cycleid = DataChoose.cycleid.astype(int)
    data3 = pd.merge(data2,DataChoose) 
    df = Getcalmap(DataChoose,conn)
    df = df.append(data3)  ## 完成发现需要计算 周期的 完整的 eva_all表
    
    cols = ["product_id","groupid",'line', 'eva_chamber','cycleid']
    df1 = df[cols+['glass_id','eventtime']].drop_duplicates().groupby(cols).\
        agg({"glass_id":len,"eventtime":['min',"max"]})
    
    ## 'glasscount','starttime','endtime' 为 本次需要组别的 所有真实静态属性 
    static = ['glasscount','starttime','endtime'] 
    df1.columns = static
    df1 = df1.reset_index()

    res = []
    temp = df1[df1.glasscount<number]  ## 首先 获取 cal2 及不满足3组的数据
    ## cal2_ppa_1 为 本次1小时中 需要计算的 但是glassid又不足 number 的eva_all表 +static
    cal2_ppa_1 = pd.merge(data3,temp,on=['product_id', 'groupid', 'line', 'eva_chamber', 'cycleid'])
    
    if len(temp) !=0:
#        sql = '''
#          select distinct product_id,groupid,line,eva_chamber,eventtime from eva_all t1 where eventtime in(
#            select distinct eventtime from eva_all 
#            where 
#            line = t1.line and 
#            product_id = t1.product_id and 
#            groupid = t1.groupid and 
#            eva_chamber = t1.eva_chamber
#            order by eventtime desc
#            limit %d
#            )
#            group by product_id,groupid,line,eva_chamber,eventtime
#        '''%number
        sql = '''
          select distinct product_id,groupid,line,eva_chamber,eventtime 
              from eva_all order by eventtime desc limit 10000
        '''%number
        df2_sql = pd.read_sql_query(sql,conn.obj.conn)
        df2_sql = df2_sql.sort_values('eventtime',ascending=False)
        df2 = df2_sql.groupby(["product_id","groupid",\
                "line","eva_chamber"]).apply(lambda x:x['eventtime'].iloc[:3]).reset_index()
        df2 = df2.drop("level_2",axis=1)
        #### df2 是 通过 'line','eva_chamber'分组后 每组下最后的三个 eventtime
#        df2 = pd.read_sql_query(sql,conn.obj.conn)
        #### cal2 只取 df2 对本次需要不全的temp的 'line','eva_chamber'进行筛选
        cal2 = pd.merge(df2,temp,on = ["product_id","groupid",'line','eva_chamber']).sort_values('eventtime')
        ####  cal2_ppa 是 按照 "line", "eva_chamber",  "eventtime" 到数据库中选取数据的 
        cal2_ppa = Getcalmap(cal2[["product_id","groupid","line", "eva_chamber", "eventtime"]],conn)
        ####  temp保留了 本次需要补全组的  cycleid 和  glasscount 信息，所以需要将 temp的这两个重要信息 merge回ppa数据
        ###   cal2_ppa 中的 cycleid 在同一 'line','eva_chamber' 一定不止一个，但是这里需要改为一个
        ####  cal2_ppa 是目前数据库中 提取到的 本次1小时内需要计算且 glassid不足 number的eva_all表 +static
        cal2_ppa = pd.merge(cal2_ppa.drop("cycleid",axis=1),temp, on = \
                            ["product_id","groupid",'line','eva_chamber'])
        ## 此时的 cal2_ppa 能保证的是 同一 'line','eva_chamber'只有一个 cycleid
        ## staic 是 这个cycle 真实的静态属性
        cal2_ppa = cal2_ppa.append(cal2_ppa_1)
        
        res.append(cal2_ppa) ## 不足个数的补全后筛选
    
    data2.groupid=data2.groupid.astype(int)
    data2.cycleid=data2.cycleid.astype(int)
    conn.insert_df(tablename='eva_all',df=data2)  ##将本周期的所有数据插入到数据库中
    
    cal1 = df1[df1.glasscount>=number].drop(static,axis=1)
    if len(cal1)>0:
        cal1_ppa = Getcalmap(cal1,conn)
        ## 并且确保 cycleid 在同一 'line', 'eva_chamber', 'port'是唯一的， 将 static merge到 cal1_ppa中
        cal1_ppa = pd.merge(cal1_ppa,df1,on= cols)
        res.append(cal1_ppa) ## 符合条件的数据t1.ev
        
    df = pd.concat(res)
    df = df.sort_values(['line','eva_chamber','mask_set','eventtime'])
    return df



def CreateOffsetAfter(g):
    '''
    1、deltaX,Y的顺序可能需要做调整
    2、考虑到通用性，建议返回值不删除这几个delta
    '''
    g1 =g[['glass_id','offset_x','offset_y','offset_tht']].drop_duplicates().set_index("glass_id")
    t1 = (g1-g1.loc[g1.index[-1]]).reset_index()
    t1 =t1.rename(dict(zip(['offset_x','offset_y','offset_tht'],['deltax','deltay','deltat'])),axis=1)
    t2 = pd.merge(g,t1,on = ['glass_id'])
    t2['ppa_x'] = t2['ppa_x']+t2['deltay']-t2['deltat']*t2['pos_y'] * np.pi / 180 / 100
    t2['ppa_y'] = t2['ppa_y']+t2['deltax']+t2['deltat']*t2['pos_x'] * np.pi / 180 / 100
        
    return t2.drop(['deltax','deltay','deltat'],axis=1)

def Alarm(df,threshold={},exclude=[],conn=None):
    '''
    df总出现重复列，需要研究原因
    '''
    columns = list((set(threshold.keys()) - set(exclude)).intersection(set(df.columns)))
    def func(g):
        rr = g[columns]
        rr.index = range(len(rr))
        res = rr.apply(lambda x:x[x.abs()>threshold[x.name]].\
          describe().loc[['count','max','min']],axis=0).T.reset_index()\
               .rename(columns ={"index":"key"})
        return res

    res = df.groupby(['line','eva_chamber','port','mask_set','glass_id','eventtime']).apply(func).reset_index()
    ## 插入数据库
    res = res[res['count']>0]
    if len(res):
        res = res.drop("level_6",axis=1)
        res['line'] = res['line'].astype(int)
        if 'alarm' not in conn.list_table():
            conn.creat_table_from_df(tablename='alarm', df=res)
        conn.insert_df(tablename='alarm',df=res)
        return True
    else:
        return False
    
    
def ResetValue(df):
    df = df.sort_values(['glass_id','eva_chamber','pos_x','pos_y'])
    df.index = range(len(df))
    df.ppa_x = df.ppa_x.replace(9999,np.nan)
    df.ppa_x = df.ppa_x.replace(-9999,np.nan)
    df.ppa_y = df.ppa_y.replace(-9999,np.nan)
    df.ppa_y = df.ppa_y.replace(9999,np.nan)
    
    df1 = df.dropna(how ="any")
    df1["area"] = df['panel_x'].astype(float)*df['panel_y'].astype(float)
    res = df1.groupby(['glass_id','eva_chamber']).agg({'teg_count':len,"area":"mean"})\
        .reset_index()
    res1 = res[res['teg_count']!=res['area']] ## 出现有NaN值的 数据了
    df1 = df1.drop("area",axis=1)
    ##  df2为 需要处理的数据
    if len(res1)!=0:
        df['bz'] = range(len(df))
        df2 = pd.merge(df,res1[['glass_id',"eva_chamber"]].drop_duplicates(),\
                 on = ['glass_id',"eva_chamber"])
        rightdf = df[~df['bz'].isin(df2['bz'])] ## 无异常的数据
        rightdf = rightdf.drop("bz",axis=1)
        df2 = df2.drop("bz",axis=1)
        rightdf = rightdf.dropna()
        def func(g):
            for key in ['ppa_x','ppa_y']:
                temp = pd.pivot_table(g,index = 'x_label',\
                    columns = 'y_label',values = key)
                temp = temp[temp.columns.sort_values()]
                temp = temp.sort_index()
                s = g[['ppa_x','ppa_y','x_label','y_label']]
                s['index'] = s.index
                s1 = s[s[key].isnull()]
                for i in s1.index:
                    index = s1.loc[i,'index']
                    x_label = s1.loc[i,"x_label"]
                    y_label = s1.loc[i,"y_label"]
                    temp1 = temp.loc[x_label-1:x_label+1,y_label-1:y_label+1]
                    temp2 = pd.Series(temp1.values.reshape(len(temp1)*len(temp1.columns)))
                    g.loc[index,key] = temp2.mean() 
            return g
        df2 = df2.groupby(['glass_id',"eva_chamber"]).apply(func)
        df2.index = range(len(df2))
        res = rightdf.append(df2)
        res.index = range(len(res))
        return res
    else:
        return df1