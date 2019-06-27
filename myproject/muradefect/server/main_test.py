# -*- coding: utf-8 -*-
'''
尝试新的cycleID赋值逻辑：
1、以GroupID，line作为颗粒度，取eva_chamber==’OC_8’，分port A、B计算maskset的变化。
2、执行判断新数据内部cycleID是否变化的命令。
3、将计算出来的cycleID下所有的GlassID值赋值成同样的cycleID。

'''

import os,configparser
import datetime
from tool.my2sql import Mysql,oracle_obj
from tool.GetNewdata import *
from tool.cal_optimized_offset import *
import logging
import cx_Oracle
import time
import datetime
import numpy as np
import pandas as pd

CONFIGROOT= '../static/conf'
LOGGING = './log'

def GetOption():
    init = {}
    config=configparser.ConfigParser()
    config.read(os.path.join(CONFIGROOT,'conf.ini'))
    
    base_args = {}
    base_args['starttime'] = config.get("base","starttime")
    end_time=datetime.datetime.now()
    base_args['endtime'] =end_time.strftime('%Y-%m-%d %H:%M:%S')
    base_args['running'] =  config.get("base","running")
    #time_args['endtime'] ='2019-06-19 06:00:00'
    cols = ['th1','th2']
    ops_args = dict(zip(cols,map(lambda x:float(config.get("settings",x)),cols)))
    cols = ['ppa_x','ppa_y','offset_delta_x','offset_delta_y','offset_delta_tht']
    th_args = dict(zip(map(lambda x:x.lower(),cols),map(lambda x:float(config.get("settings",x)),cols)))
    
    cols = ['opsnumber','offsetth']
    opt_args = dict(zip(map(lambda x:x.lower(),cols),map(lambda x:float(config.get("settings",x)),cols)))
    
    datebase1 = dict(config['datebase1'].items())  ## 项目依赖的本地数据库
    datebase2 = dict(config['datebase2'].items())  ## 项目依赖的本地数据库
    datebase3 = dict(config['datebase3'].items())  ## 项目依赖的本地数据库
    
    init['base']  =base_args
    init['ops']  =ops_args
    init['th']  =th_args
    init['opt']  =opt_args
    init['datebase1']  =datebase1
    init['datebase2']  =datebase2
    init['datebase3']  =datebase3
    return init

def lambdaGet(starttime,endtime):
    empty = pd.DataFrame()
    df= pd.DataFrame(list(map(lambda x:os.path.join(data,x),os.listdir(data))),columns = ['name'])
    df['time'] = pd.to_datetime(df['name'].map(lambda x:x.split("_")[-1].split(".")[0]))
    df = df[(df['time']>=starttime)&(df['time']<endtime)]
    if len(df):
        res =pd.concat([pd.read_csv(i) for i in df['name']])
        if len(res):
            res.columns = res.columns.str.upper()
            res.eventtime = pd.to_datetime(res.eventtime)
            res['line'] =res['line'].astype(int)
            res = res.drop(['UNNAMED: 0'],axis=1)
            return res
        else:
            return empty
    else:
        return empty

def CheckDirname(dirname = None):
    if isinstance(dirname,str):
        dirname = [dirname]
    for i in dirname:
        if not os.path.exists(i):
            os.makedirs(i)     

def SetOption(key = "",value = ""):
    config=configparser.ConfigParser()
    config.read(os.path.join(CONFIGROOT,'conf.ini'))
    config.set("base",key,value)
    config.write(open(os.path.join(CONFIGROOT,'conf.ini'),'w'))


def InsertCIM(df,init1):
    df['timekey'] = df['endtime'].dt.strftime("%Y%m%d%H%M%S")+"000000"
    df['maskname'] = df["mask_id"]
    df['chambername'] = df["eva_chamber"]
    df['linetype'] = df["line"]
    df['evaoffsetx'] = df["offset_x"]
    df['evaoffsety'] = df["offset_y"]
    df['evaoffsettheta'] = df["offset_tht"]
    df['ifflag'] = 'N'
    df = df.astype(str)
    cols = ["timekey","maskname","chambername","linetype",\
            "evaoffsetx","evaoffsety","evaoffsettheta","ifflag"]
    df = df[cols]
    init1['engine'] = "o"
    conn3 = Mysql(**init1)
    conn3.insert_df("mes_bigdataif_maskoffset",df)
    conn3.close()

if __name__=="__main__":    
    #########################   日志文件格式配置文件    #########################
    logger = logging.getLogger(__name__)
    logger.setLevel(level = logging.DEBUG)
    now = datetime.datetime.now().strftime("%Y%m%d%H")
    CheckDirname([LOGGING])
    handler = logging.FileHandler(os.path.join(LOGGING,"%s.txt"%now))
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    
    logger.addHandler(handler)
    logger.addHandler(console)   
#    for sadasdasd in range(12*24):
    appst = time.time()        
    logger.info('#########################   读取配置文件    #########################')
    init = GetOption()
    starttime = init['base']['starttime']
    endtime = init['base']['endtime']
#        endtime=pd.to_datetime(starttime)+pd.to_timedelta(1,unit='h')
#        endtime=str(endtime)
    running = init['base']['running']
    logger.info('本次获取时间范围 ： %s -- %s'%(starttime,endtime))
    
#        logger.info('#########################   清理psql死进程    #########################')
#        conn2 =Mysql(**init['datebase2'])
##        pids = pd.read_sql_query("SELECT * FROM pg_stat_activity",conn.obj.conn)
#        pids = pd.read_sql_query("SELECT * FROM pg_stat_activity where \
#                               datname='ppa' and state ='idle in transaction' ",conn2.obj.conn)
#        for pid in pids.pid.tolist():
#            conn2.exec_("select pg_terminate_backend('%s');"%pid)
#        logger.info('#########################   清理psql死进程完成    #########################')      
    
    if running == "0" : ## 表示该阶段未有程序运行，可以往下执行            
        logger.info('#########################   获取数据阶段    #########################')
        user = init['datebase1']['user']
        dbname = init['datebase1']['dbname']
        password = init['datebase1']['password']
        host = init['datebase1']['host']
        port = init['datebase1']['port']
        conn1 = cx_Oracle.connect("%s/%s@%s:%s/%s"%(user,password,host,port,dbname))
        df=DataCollect(starttime,endtime,conn=conn1)
        SetOption("running","1")  ## 将 running状态置为 1 ，表示程序正在执行，防止重复运行
#        filename=F.split('\\')[-1]  
#        df=pd.read_csv(F,index_col=0)
        #logger.info('@@@@@@@@@@@@@@@@@@@@   开始读第%d个文件：%s   @@@@@@@@@@@@@@@@@@@@@@@' %(i,filename))      
        df.columns=df.columns.str.lower()
        df['x_label'] = df['x_label'].astype(int)
        df['y_label'] = df['y_label'].astype(int)
        ##@@##        
        S=starttime.replace(':','').replace('-','').replace(' ','')
        E=endtime.replace(':','').replace('-','').replace(' ','')
        FilePath=r'.\data\OracleFrom%sTo%s'%(S,E)
        if not os.path.exists(FilePath):
            os.makedirs(FilePath)
#            df.to_csv(os.path.join(FilePath,'eva_all.csv'),index=False)
        if (len(df)):
            df.eventtime=pd.to_datetime(df.eventtime)
            logger.info('获取数据完成 ,数据shape : %s ,耗时 :  %0.2fs'%(str(df.shape),time.time()-appst))            
            #### 针对原始PPA 进行异常值报警
            conn2 =Mysql(**init['datebase2'])
            flag = Alarm(df,init['th'],conn=conn2)
            if flag:
                logger.info('本周期原始PPA数据发现异常')
            
            st =time.time()
            logger.info('#########################   判断eva_all表是否存在    #########################')
            st =time.time()
            if len(df):
                if 'eva_all' in conn2.list_table():
                    ##########检查新获取的df与eva_all中是否有重复的（通过glass_id）
                    logger.info('eva_all表存在')
                    conn2 =Mysql(**init['datebase2'])
                    glassid = pd.read_sql_query("select DISTINCT glass_id from eva_all",con = conn2.obj.conn)
                    df = df[~df.glass_id.isin(glassid['glass_id'])]
                    if len(df):
                        GroupID,CycleIDNewInit,datachoose1=NewDataJudge(df,conn2.obj.conn)
                        data2,datachoose=AddCycleID(df,datachoose1=datachoose1,GroupID=GroupID,CycleIDNewInit=CycleIDNewInit)
                    else:
                        data2=pd.DataFrame([],columns=['product_id', 'eventtime', 'glass_id', 'eva_chamber', 'mask_id',
                           'mask_set', 'port', 'line', 'pos_x', 'pos_y', 'x_label', 'y_label',
                           'ppa_x', 'ppa_y', 'offset_x', 'offset_y', 'offset_tht', 'groupID',
                           'groupid', 'cycleid'])
                        datachoose=pd.DataFrame([])
                else:
                    data2,datachoose=AddCycleID(df,datachoose1=datachoose1,GroupID=GroupID,CycleIDNewInit=CycleIDNewInit)
#                    '''        
#                    data_new 的 schema:
#                        ['product_id', 'eventtime', 'glass_id', 'eva_chamber', 'mask_id',
#                           'mask_set', 'port', 'line', 'pos_x', 'pos_y', 'x_label', 'y_label',
#                           'ppa_x', 'ppa_y', 'offset_x', 'offset_y', 'offset_tht', 'groupID',
#                           'groupid', 'cycleid']
#                    '''
                ###########先将新数据插入，再根据datachoose的取数据
                    conn2.creat_table_from_df(tablename='eva_all', df=data_new)
                    logger.info('eva_all表不存在')
                    
                ###########先将新数据插入，再根据datachoose的取数据
                '''
                之所以可以先插入数据：
                1、顺序运行，不会出现重复插入eva_all表
                2、datachoose中指定了要计算的[groupid,cycleid]，故取出待计算的ppa数据是也不存在重复取出的情况。
                '''
                conn2.insert_df(tablename='eva_all',df=data2)
                logger.info('已完成初始数据插入，耗时 :  %0.2fs'%(time.time()-st))

                '''
                GetCallPPA：
                若datachoose 已存在于 offset_table中则不计算。用到了Getcalmap函数
                
                @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                '''
                conn2 =Mysql(**init['datebase2'])
                
                if "offset_table" in conn2.list_table():
                    temp = Getcalmap(datachoose,conn2,tablename = 'offset_table')\
                        [datachoose.columns.tolist()]
                    temp = temp.drop_duplicates()
                    temp['bz'] = 1 ## 以计算标识符
                    datachoose = pd.merge(datachoose,temp,on = datachoose.columns.tolist(),how = "left")
                    ## 删除已计算过的 cycle, 防止重复计算
                    datachoose = datachoose[datachoose['bz']!=1].drop("bz",axis=1)
                    logger.info("本次判断后需要计算的 datachoose :\n%s"%(str(datachoose)))
                conn2.close()
                
                if len(datachoose):    
                    #datachoose.to_csv(r'D:\data_Visionox\Visionox\datachooseIn-'+filename)
                    logger.info('Cycle判断完成 ,datachoose shape : %s ,耗时 :  %0.2fs'%(str(datachoose.shape),time.time()-st))
                    ####取出需要计算的所有PPA
                    st = time.time()
#                    datachoose.to_pickle("datachoose.pk")
                    ## GetCalPPA 待优化
                    conn2 =Mysql(**init['datebase2'])
                    ## data2 需要在  GetCalPPA 函数执行过程中插入，原因是如果不足 个数的需要按照eventtime 进行搜索时
                    ## 会将刚刚插入的 cycle一起搜索出来，但是新的cycle不应该参与计算，所以计算eventtime时数据库中不应该有 新数据
                    
                    df2=GetCalPPA(datachoose,data2,conn=conn2,number=init['opt']['opsnumber'])
                    
                    logger.info('GetCalPPA shape : %s '%(str(df2.shape)))
#                    df2.to_pickle('ppa.pk')  ##  shape =  (*,20)                    
                    ####按照cycle颗粒度做PPA折算, CreateOffsetAfter 直接对 PPA_X,PPA_Y进行了修正
                    df2 = df2.groupby(['product_id','groupid','line','eva_chamber','mask_set']).apply(CreateOffsetAfter)
                    logger.info('完成跨周期OFFSET折算 shape : %s ,耗时 :  %0.2fs'%(str(df2.shape),time.time()-st))
                    df2.index =range(len(df2))
#                   
                    ## df2 中含有所有的 属性信息
                    #### 针对折算后PPA 进行异常值报警
                    flag1 = Alarm(df2,init['th'],exclude = [],conn=conn2)
                    if flag1:
                        logger.info('本周期折算后PPA数据发现异常')
                    conn2.close()
                    ###  首先 对每个 Glass 各个 ppa teg 进行mean 合并
                    df3=df2.groupby(['product_id', 'groupid' ,'line','eva_chamber','port',"cycleid",'x_label', 'y_label',\
                                    "glass_id"])[['ppa_x','ppa_y','pos_x','pos_y',\
                                  'offset_x','offset_y','offset_tht']].mean().reset_index()
                    ##  再次，针对同一个cycle 下所有glass 进行合并
                    df3=df3.groupby(['product_id',"groupid", 'line','eva_chamber','port',"cycleid",'x_label', 'y_label'])\
                            [['ppa_x','ppa_y','pos_x','pos_y','offset_x','offset_y','offset_tht']]\
                            .mean().reset_index()
                    ## df3 仅是用于计算的 数据源
                    st = time.time()
                    
#                        df3.to_pickle('optimize.pk')
                    res=df3.groupby(['product_id', 'groupid','line','eva_chamber','port','cycleid']).apply(cal_optimized_offset)
                    res = pd.merge(res.reset_index(),df2[['product_id', "groupid",'line','eva_chamber','port','cycleid',\
                                   "mask_id","mask_set",'glasscount', 'starttime', 'endtime']].drop_duplicates(),\
                                   on = ['product_id', "groupid",'line','eva_chamber','port','cycleid']) 
                    ## 获取每个cycle 颗粒度下的 'groupid','glasscount', 'starttime', 'endtime' 静态属性
                    res.columns = res.columns.str.replace(".",'')
#                        res.to_pickle("offset_table.pk")
                    
#                        res.to_csv(os.path.join(FilePath,'offset_table.csv'))
                    conn2 =Mysql(**init['datebase2'])
                    if "offset_table" not in conn2.list_table():
                        conn2.creat_table_from_df("offset_table",res)
                    conn2.insert_df("offset_table",res)
                    conn2.close()
                    logger.info("Cal_Optimized_Offset Cal Time %02.fs"%(time.time()-st))

                    try:
                        InsertCIM(res,init['datebase3'])
                        logger.info("完成CIM表插入")
                    except:
                        pass
                    
                    logger.info('获取本次需计算的PPA数据 ,数据 shape : %s ,耗时 :  %0.2fs'%(str(df2.shape),time.time()-st))
                    
                    ######结束脚本运行成功结束后修改start-time，并写回文件
                else:
                    conn2 =Mysql(**init['datebase2'])
                    data2.groupid=data2.groupid.astype(int)
                    data2.cycleid=data2.cycleid.astype(int)
                    conn2.insert_df(tablename='eva_all',df=data2)
                    conn2.close()
                    logger.info("本周期未发现需要计算的 PPA数据")     
        else:
            logger.info('本周期获取原始数据为空')
        SetOption("starttime",endtime)
        SetOption("running","0")  ## 将running 置为0 ，以便下次正常运行
        logger.info('完成本周期 获取数据阶段，更新时间至 %s ,获取数据阶段耗时 %02.fs'%(endtime,time.time()-appst))
    else:
        logger.info('上一周期内程序未执行完成')