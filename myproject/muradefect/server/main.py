# -*- coding: utf-8 -*-
"""
数据获取与新周期判断
"""
import os,configparser
import datetime
from tool.my2sql import Mysql
from tool.GetNewdata import *
import logging
import cx_Oracle
import time
import datetime

CONFIGROOT= '../static/conf'
LOGGING = './log'

def GetOption():
    init = {}
    config=configparser.ConfigParser()
    config.read(os.path.join(CONFIGROOT,'conf.ini'))
    
    time_args = {}
    time_args['starttime'] = config.get("base","starttime")
    end_time=datetime.datetime.now()
    time_args['endtime'] =end_time.strftime('%Y-%m-%d %H:%M:%S')
    #time_args['endtime'] ='2019-06-19 06:00:00'
    cols = ['th1','th2']
    ops_args = dict(zip(cols,map(lambda x:float(config.get("settings",x)),cols)))
    cols = ['ppa_x','ppa_y','offset_delta_x','offset_delta_y','offset_delta_tht']
    th_args = dict(zip(map(lambda x:x.upper(),cols),map(lambda x:float(config.get("settings",x)),cols)))
    
    datebase1 = dict(config['datebase1'].items())  ## 连接生产数据库获取 PPA数据
    datebase2 = dict(config['datebase2'].items())  ## 项目依赖的本地数据库 
    datebase3 = dict(config['datebase3'].items())  ##  OFFSET优化表写入的数据库
    
    init['time']  =time_args
    init['ops']  =ops_args
    init['th']  =th_args
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
            res.EVENTTIME = pd.to_datetime(res.EVENTTIME)
            res['LINE'] =res['LINE'].astype(int)
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

def MyOracle(dbname= "edadb",user = "readonly",\
             password = "readonly",host = "10.69.2.25",port=1521):
    
    conn = cx_Oracle.connect('%s/%s@%s:%s/%s' %\
        (user, password, host, port, dbname))
    return conn

def SetOption(endtime):
    config=configparser.ConfigParser()
    config.read(os.path.join(CONFIGROOT,'conf.ini'))
    config.set("base","starttime",endtime)
    config.write(open(os.path.join(CONFIGROOT,'conf.ini'),'w'))

if __name__=="__main__":    
    #########################   日志文件格式配置文件    #########################
    appst = time.time()    
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

    logger.info('#########################   读取配置文件    #########################')
    init = GetOption()
    starttime = init['time']['starttime']
    endtime = init['time']['endtime']
    logger.info('本次获取时间范围 ： %s -- %s'%(starttime,endtime))
    
    logger.info('#########################   获取数据阶段    #########################')
                
    conn1=MyOracle(**init['datebase1']) ## Ocrale生产数据库
    df=DataCollect(starttime,endtime,conn = conn1)
    
#        df = lambdaGet(starttime,endtime) ## 本地临时测试
         
    if len(df):
        logger.info('获取数据完成 ,数据shape : %s ,耗时 :  %0.2fs'%(str(df.shape),time.time()-appst))
        conn2 =Mysql(**init['datebase2'])
        #### 针对原始PPA 进行异常值报警
        flag = Alarm(df,init['th'],conn=conn2)
        if flag:
            logger.info('本周期原始PPA数据发现异常')
        
        st =time.time()
        
        
        logger.info('#########################   判断eva_ppa表是否存在    #########################')
        st =time.time()
        TableExist=0
        if 'eva_all' in conn2.list_table():
            TableExist=1
            logger.info('eva_ppa表存在')
        else:
            TableExist=0
            data=AddInitDataID(df)
            conn2.creat_table_from_df(tablename='eva_all', df=data)
            conn2.insert_df(tablename='eva_all',df=data)
            logger.info('eva_ppa表不存在。已完成初始数据插入，耗时 :  %0.2fs'%(time.time()-st))

        if TableExist：:
            logger.info('#########################   Group判断阶段    #########################')
            st =time.time()
            NewTimeMin=df.EVENTTIME.min()
            sql_MaxTime='select max(eventtime),max(GroupID) from eva_all'
            Value=conn2.exec_(sql_MaxTime)
            OldTimeMax=Value[0]
            groupID=Value[1]
            if NewTimeMin-OldTimeMax>pd.to_timedelta(36,unit='h'):
                df['GroupID']=groupID+1
            else:
                df['GroupID']=groupID
            logger.info('完成GroupID赋值,耗时 :  %0.2fs'%(time.time()-st))
            
            logger.info('#########################   Cycle判断阶段    #########################')
            ####Cycle判断，取出要优化的数据
            st =time.time()
            df['X_Label'] = df['X_Label'].astype(int)
            df['Y_Label'] = df['Y_Label'].astype(int)
            DataChoose,data2=CycleJudge(df,conn=conn2.obj.conn)
            logger.info('Cycle判断完成 ,DataChoose shape : %s ,耗时 :  %0.2fs'%(str(DataChoose.shape),time.time()-st))
            conn2.insert_df(tablename='eva_all',df=data2)            
            logger.info("完成新数据插入")
            st =time.time()
            ####取出需要计算的所有PPA
            if len(DataChoose):
                df2=GetCalPPA(DataChoose,conn=conn2)
                logger.info('获取本次需计算的PPA数据 ,数据 shape : %s ,耗时 :  %0.2fs'%(str(df2.shape),time.time()-st))
                #### 针对折算后PPA 进行异常值报警
                flag1 = Alarm(df2,init['th'],exclude = ['PPA_X','PPA_Y'],conn=conn2)
                if flag1:
                    logger.info('本周期折算后PPA数据发现异常')
                ####按照cycle颗粒度做PPA折算
                res = df2.groupby(['LINE','EVA_CHAMBER','MASK_SET']).apply(CreateOffsetAfter)
                logger.info('完成跨周期OFFSET折算')      
                ######结束脚本运行成功结束后修改start-time，并写回文件
                #SetOption(endtime)
                logger.info('完成本周期 获取数据阶段，更新时间至 %s ,获取数据阶段耗时 %02.fs'%(endtime,time.time()-appst))
                ######进行offset优化
            
            else:
                logger.info("本周期未发现需要计算的 PPA数据")     
    else:
        logger.info('本周期获取原始数据为空')
    SetOption(endtime)
