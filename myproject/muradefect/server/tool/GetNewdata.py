#coding=utf-8
'''
王吉东做的更改：
1、Pmaskid中：在line==2的情况下，port A/B改成 C/D


'''
import pandas as pd
import itertools
import numpy as np
import json
from .myemail import *
import datetime

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
    print (p4[['glass_id','sub_id']].head())    
    p4 = p4[p4.glass_id == p4.sub_id].drop(['sub_id'], axis=1)    
    print ("p4.shape",p4.shape)
    p4['mask_set'] = p4.mask_id.str[-4:]    
    print('p4.subunitname',p4.subunitname)
    p4['eva_chamber'] = 'OC_'+p4.subunitname.str[-2]
    p4['line'] = p4.subunitname.str[-1].astype(int)  
    ####若line=2，port的A,B改成C,D
    p4.loc[p4[(p4.line==2)&(p4.port=='A')].index,'port']='C'
    p4.loc[p4[(p4.line==2)&(p4.port=='B')].index,'port']='D'
    print (p4[['line','port']].head())
    
    
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

def Get_Label(df):
     def func0(var):
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
     df = df.groupby(['glass_id','eva_chamber']).apply(func0)
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
    print('###########    start ppa')
    DF1=PPA(starttime,endtime,conn)
    print('###########    end ppa')
    print ("DF1.shape",DF1.shape)
    if not len(DF1):
        DF=pd.DataFrame([],columns=col)
    else:
        Glass_ID=DF1.glass_id.unique().tolist()
        ##步骤2：maskID数据 
        print('###########    start pmaskid')
        DF2=Pmaskid(Glass_ID,conn)
        print('###########    end pmaskid')
        print ("DF2.shape",DF2.shape)
        ##步骤3：合并
        if not len(DF2):
            return pd.DataFrame([],columns=col)
        print("DF2",DF2[['product_id','glass_id','eva_chamber','eventtime']])
        print("DF1",DF1[DF1.glass_id.isin(DF2.glass_id)][['product_id','glass_id','eva_chamber']].drop_duplicates())
        DF=pd.merge(DF1,DF2,on=['product_id','glass_id','eva_chamber'])
        print ("DF.shape",DF.shape)
        DF=DF[col]   
    return DF

def CycleJudge(df,conn):
    ## df 是本周期 获取的数据
    groupid = pd.read_sql_query("select max(groupid) from eva_all",conn)['max'].iloc[0]
    cycleid = pd.read_sql_query("select max(cycleid) from eva_all \
                                where groupid=%d"%(groupid),conn)['max'].iloc[0]
    
    ###############
    TimeNew=df.eventtime.min()
    TimeOld=pd.read_sql_query("select max(eventtime) from eva_all",conn)['max'].iloc[0]
    
    if (pd.to_datetime(TimeNew)-pd.to_datetime(TimeOld))>pd.to_timedelta(22,unit='h'):
        datachoose = [groupid,cycleid]
        datachoose=pd.DataFrame([datachoose],columns=['groupid','cycleid'])
        groupid+=1
        cycleid=0
        df['groupid']=groupid
        df['cycleid']=cycleid   
    else:
        data = pd.read_sql_query('''
                select distinct cycleid,eva_chamber,port,mask_id,eventtime
                from eva_all where groupid =%d and cycleid = %d'''%(groupid,cycleid),conn)

        data = data.sort_values("eventtime").drop_duplicates(['eva_chamber','port'],keep='last').\
                drop("eventtime",axis=1)
        data.rename(columns={'mask_id':'mask_id_old'},inplace=True)
        
        cycleids = {}
        for glass_id in df.glass_id.unique():
            cycleids[glass_id] = cycleid  #默认cycle不变
            '''
            temp中，按照glassid取出所有chamber，随后选出最大的
            '''
            temp = df[df.glass_id==glass_id][['eva_chamber','port','mask_id']].drop_duplicates() #针对每片Glass，一一判断cycle   
            temp=temp[temp.eva_chamber==temp.eva_chamber.max()]
            temp.rename(columns={'mask_id':'mask_id_new'},inplace=True)
            '''
            1、新旧均rename一下mask_id;
            2、首先判断新数据里[chamber, port] 在不在旧数据中，不在的话，暂时无法判别其 cycleid，默认为原cycleid
            具体体现就是：merge(on=[chamber, port])后，若为空，则保持原cycle
            3、若不为空，则判断maskid是否相同。            
            '''                
            temp1 = pd.merge(temp,data,on = ['port','eva_chamber']) 
            temp1['judge']=(temp1.mask_id_old!=temp1.mask_id_new) #因为指定了glassID，因此len(temp1)只有可能等于0或1
            if (temp1.judge.max()==True): #temp1.judge.max()可能存在3种情况：True，False，nan
                cycleids[glass_id] = cycleids[glass_id]+1
            
        #df1 = df[df.eva_chamber=='OC_8'][['glass_id','eventtime']].drop_duplicates().sort_values("eventtime")  
        df1=df.sort_values("eventtime").drop_duplicates(['glass_id'],keep='last')            
        df1['cycleid'] = df1['glass_id'].map(cycleids)
        for i in range(len(df1)):
            df1['temp'] = df1["cycleid"].diff()
            if len(df1[df1['temp']<0])==0:
                break
            df1.loc[df1[df1.temp<0].index,'cycleid'] = np.nan
            df1["cycleid"]= df1["cycleid"].fillna(method = "ffill")            
        cycleids = dict(zip(df1['glass_id'],df1["cycleid"]))         
        
        df['groupid']=groupid
        df['cycleid'] = df["glass_id"].map(cycleids)
        df=df.sort_values('eventtime')           
        if df['cycleid'].max()!= cycleid:
            datachoose = [groupid,cycleid]
            datachoose=pd.DataFrame([datachoose],columns=['groupid','cycleid'])
        else:
            datachoose = pd.DataFrame([],columns=['groupid','cycleid'])
  
    return df,datachoose

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

def GetCalPPA(datachoose,conn,number = 3):
    groupid=datachoose.groupid.tolist()[-1]
    cycleid=datachoose.cycleid.tolist()[-1]
    '''
    sql1:取出指定cycle内所有的数据    
    '''
    sql1='''
        select * from eva_all where groupid=%d and cycleid=%d
        '''%(groupid,cycleid)
    data1=pd.read_sql_query(sql1,conn)
    ###########
    '''
    获得整个cycle数据的静态属性
    '''
    starttime=data1.eventtime.min()
    endtime=data1.eventtime.max()
    glasscount=len(data1.glass_id.unique())
    
    #############
    Njudge1=data1[['mask_id','glass_id','port']].drop_duplicates()
    NGlass=Njudge1.groupby(['mask_id','port']).count()
    MaskInCom=NGlass[NGlass.glass_id<number].index.tolist()    
    #如果不足3片，则后续补足3片的时候，必须从相同maskid+相同port中选择Glass去补
    for mask,port in MaskInCom:
        if not len(MaskInCom):
            continue
        sql00 = '''
              select distinct glass_id,eventtime from eva_all 
              where mask_id ='%s' and port = '%s'
                  order by eventtime desc limit %d
            ''' %(mask,port,number)
            
        d0=pd.read_sql_query(sql00,conn)
        GlassAdd=d0.glass_id.tolist()
        if GlassAdd:
            sql2 = '''
                  select * from eva_all 
                  where glass_id in (%s)
                  and mask_id ='%s' and port = '%s'
                ''' %(str(GlassAdd)[1:-1],mask,port)
            data2=pd.read_sql_query(sql2,conn)
            data1=data1.append(data2).drop_duplicates()
    
    data1['glasscount']=glasscount
    data1['starttime']=starttime
    data1['endtime']=endtime
    data1['cycleid']=cycleid
    data1.sort_values('eventtime',inplace=True)
    data1.index=range(len(data1))
    return data1

def CreateOffsetAfter(g):
    g1 =g[['eventtime','glass_id','offset_x','offset_y','offset_tht']].sort_values('eventtime').\
            drop_duplicates().set_index("glass_id")
    t1 = (g1.loc[g1.index[-1]]-g1).reset_index().drop('eventtime',axis=1).apply(pd.to_numeric,errors='ignore')
    t1.offset_tht=(-1)*t1.offset_tht
    t1 =t1.rename(dict(zip(['offset_x','offset_y','offset_tht'],['delta_y','delta_x','delta_t'])),axis=1)
    t2 = pd.merge(g,t1,on = ['glass_id'])
    t2['ppa_x'] = t2['ppa_x']+t2['delta_x']-t2['delta_t']*t2['pos_y'] * np.pi / 180 / 100
    t2['ppa_y'] = t2['ppa_y']+t2['delta_y']+t2['delta_t']*t2['pos_x'] * np.pi / 180 / 100
    
    return t2.drop(['delta_x','delta_y','delta_t'],axis=1)
    
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
                g[key] = g[key].fillna(g[key].mean())
            return g
        df2 = df2.groupby(['glass_id',"eva_chamber"]).apply(func)        
        df2.index = range(len(df2))
        res = rightdf.append(df2)
        res=res.dropna()
        res.index = range(len(res))
        return res
    else:
        return df1
    
