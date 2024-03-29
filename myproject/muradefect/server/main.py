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
import json
from tool.Alarm import *

IMAGE = './image'
CONFIGROOT= '../static/conf'
LOGGING = './log'
SECONDS = 600

## DEBUG 模式
DEBUG = False
DIRNAME = '../../../FromOracle'

def GetRateTh():
    path = os.path.join(CONFIGROOT,"ratethreahold.json")
    if os.path.exists(path):
        with open(path,"r") as f:
            msg=  json.loads(f.read())
        return msg
    else:
        return {}

def GetEmailList():
    path = os.path.join(CONFIGROOT,"email.csv")
    if os.path.exists(path):
        df = pd.read_csv(path,engine = 'python')
        df = df.dropna(subset = [df.columns[1]])
        return df[df.columns[1]].tolist()
    else:
        return []

## Option 修改记录
def GetOption():
    init = {}
    config=configparser.ConfigParser()
    config.read(os.path.join(CONFIGROOT,'conf.ini'))
    
    base_args = {}
    base_args['starttime'] = config.get("base","starttime")
    end_time=datetime.datetime.now()-datetime.timedelta(seconds=SECONDS)  ## 延迟一小时获取数据，保证数据完整性
    base_args['endtime'] =end_time.strftime('%Y-%m-%d %H:%M:%S')
    base_args['running'] =  config.get("base","running")
    #time_args['endtime'] ='2019-06-19 06:00:00'
    ops_args = {}    
    ops_args['xth1'] =float(config.get("xth","xth1"))
    ops_args['xth2'] =float(config.get("xth","xth2"))
    ops_args['xweight1'] =float(config.get("xth","xweight1"))
    ops_args['xweight2'] =float(config.get("xth","xweight2")) 
    ops_args['yth1'] =float(config.get("yth","yth1"))
    ops_args['yth2'] =float(config.get("yth","yth2"))
    ops_args['yweight1'] =float(config.get("yth","yweight1"))
    ops_args['yweight2'] =float(config.get("yth","yweight2"))
    
    cols = ['ppa_x','ppa_y','delta_x','delta_y','delta_t']
    alarm_args = {}
    alarm_args['threshold'] = dict(zip(map(lambda x:x.lower(),cols),map(lambda x:float(config.get("settings",x)),cols)))
    alarm_args['email'] = {"flag":int(config.get("settings","email")),"list":GetEmailList()} ## email 发送列表
    th1 = max(float(config.get("xth","xth1")),float(config.get("xth","xth2")))
    th2 = max(float(config.get("yth","yth1")),float(config.get("yth","yth2")))
    alarm_args['rate'] = {"th":[th1,th2],"product":GetRateTh()}
    
    cols = ['opsnumber','offsetth']
    opt_args = dict(zip(map(lambda x:x.lower(),cols),map(lambda x:float(config.get("settings",x)),cols)))
    
    datebase1 = dict(config['datebase1'].items())  ## 项目依赖的本地数据库
    datebase2 = dict(config['datebase2'].items())  ## 项目依赖的本地数据库
    datebase3 = dict(config['datebase3'].items())  ## 项目依赖的本地数据库
    
    init['base']  = base_args
    init['ops']  = ops_args
    init['alarm'] = alarm_args
    init['opt']  = opt_args
    init['datebase1'] = datebase1
    init['datebase2'] = datebase2
    init['datebase3'] = datebase3
    return init

def lambdaGet(starttime,endtime):
    empty = pd.DataFrame()
    data = '../data'
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
    now = datetime.datetime.now()
    df['timekey'] = pd.date_range(now,periods=len(df),freq="0.000001S")
    df['timekey'] = df['timekey'].astype(str).str.replace(":|-| |\.",'')
    df['maskname'] = df["mask_id"]    
    DD={'OC_3':'EV3','OC_4':'EV3','OC_5':'EV4','OC_6':'EV4','OC_7':'EV5','OC_8':'EV5'}
    df['chambername'] = '2CEE01-'+df.eva_chamber.map(DD)+'-'+\
            df.eva_chamber.str.replace('C_','')+df.line.astype(str)
    df['linetype'] = df.port.str.replace('C','A').replace('D','B')
    
    df['after_x'] = (df['after_x'] * 2).round()/ 2.0
    df['after_y'] = (df['after_y'] * 2).round()/ 2.0
    df['after_t'] = df['after_t'].round()
    
    df['evaoffsetx'] = df["after_x"]
    df['evaoffsety'] = df["after_y"]
    df['evaoffsettheta'] = df["after_t"]
    df['ifflag'] = 'N'
    df = df.astype(str)
    cols = ["timekey","maskname","chambername","linetype",\
            "evaoffsetx","evaoffsety","evaoffsettheta","ifflag"]
    df = df[cols].sort_values(["timekey"])
    init1['engine'] = "o"
    conn3 = Mysql(**init1)
    conn3.insert_df("mes_bigdataif_maskoffset",df)
    conn3.close()
   

def UpdateTime(endtime,appst):
    SetOption("starttime",endtime)
    SetOption("running","0")  ## 将running 置为0 ，以便下次正常运行
    logger.info('完成本周期 获取数据阶段，更新时间至 %s ,获取数据阶段耗时 %02.fs'%(endtime,time.time()-appst))


def GetFile(dirname = '',starttime=''):
    filename = starttime.replace("-","").replace(":","").replace(" ","")[:10]+".csv"
    df = pd.read_csv(os.path.join(dirname,filename))
    df=df.drop(['glass_start_time','glass_end_time'],axis=1)
    df.eventtime=pd.to_datetime(df.eventtime)
    df.line=df.line.astype(int)
    df.loc[df[(df.line==2)&(df.port=='A')].index,'port']='C'
    df.loc[df[(df.line==2)&(df.port=='B')].index,'port']='D'
    return df
    
def Main(logger):    
    appst = time.time()        
    logger.info('#########################   读取配置文件    #########################')
    init = GetOption()
    starttime = init['base']['starttime']
    endtime = init['base']['endtime']    

    running = init['base']['running']
    logger.info('本次获取时间范围 ： %s -- %s'%(starttime,endtime))
    
    if running != "0" : ## 表示该阶段未有程序运行，可以往下执行   
        logger.info('上一周期内程序未执行完成')
        return
           
    logger.info('#########################   获取数据阶段    #########################')
    user = init['datebase1']['user']
    dbname = init['datebase1']['dbname']
    password = init['datebase1']['password']
    host = init['datebase1']['host']
    port = init['datebase1']['port']
    
    if DEBUG:
        DF = GetFile(dirname = DIRNAME,starttime = starttime)
        endtime=pd.to_datetime(starttime)+pd.to_timedelta(1,unit='h')
        endtime=str(endtime)
    else:
        conn1 = cx_Oracle.connect("%s/%s@%s:%s/%s"%(user,password,host,port,dbname))
        DF=DataCollect(starttime,endtime,conn=conn1)
    SetOption("running","1")  ## 将 running状态置为 1 ，表示程序正在执行，防止重复运行
    DF.columns=DF.columns.str.lower()
    DF['x_label'] = DF['x_label'].astype(int)
    DF['y_label'] = DF['y_label'].astype(int)

    if len(DF)==0:
        logger.info("本周期未获取到 PPA数据")     
        UpdateTime(endtime,appst)
        return
        
    DF.eventtime=pd.to_datetime(DF.eventtime)
    DF=DF.sort_values('eventtime')
    logger.info('获取数据完成 ,数据shape : %s ,耗时 :  %0.2fs'%(str(DF.shape),time.time()-appst))
    
    glass=DF.glass_id.unique().tolist()
    logger.info('############本周期共有     %d    片Glass !'%(len(glass)))    
    i=0    
    for g in glass:
        i+=1
        logger.info('############StartGlass No.%d ：%s'%(i,g))
        df=DF[DF.glass_id==g]
        st =time.time()
        logger.info('#########################   CycleID判别逻辑开始   #########################')
        st =time.time()
        conn2 =Mysql(**init['datebase2'])
        if 'eva_all' in conn2.list_table():
            ##########检查新获取的df与eva_all中是否有重复的（通过glass_id）
            logger.info('eva_all表存在')
            ## 防止EVA_ALL重复计算和插入
            ## 判断取出来的这片glass在eva_all中是否有数据，防止EVA_ALL重复计算和插入
            glassid_exist = pd.read_sql_query("select DISTINCT glass_id from eva_all where glass_id ='%s'"%(g)\
                                        ,con = conn2.obj.conn)
            
            if not len(glassid_exist): 
                data2,datachoose=CycleJudge(df,conn2.obj.conn)
                print('GroupID:',data2.groupid.unique())
                print('CycleID:',data2.cycleid.unique())
            else: 
                logger.info('&&&&  这片glass数据已经存在于eva_all中   &&&& ')
                continue
        else:
            logger.info('eva_all表不存在')
            data2=df
            line_new=data2.line.unique()[0]
            data2['groupid']=0
            data2['cycleid']='L'+str(line_new)+'-000'
            datachoose=pd.DataFrame([],columns=['groupid','cycleid'])
            
        conn2.close() 
        ## data2 是 本周期 完整的 EVA_ALL表
        logger.info('#########################   原始PPA数据异常判断阶段   #########################')   
    #    '''        
    #    data_new 的 schema:
    #        ['product_id', 'eventtime', 'glass_id', 'eva_chamber', 'mask_id',
    #           'mask_set', 'port', 'line', 'pos_x', 'pos_y', 'x_label', 'y_label',
    #           'ppa_x', 'ppa_y', 'offset_x', 'offset_y', 'offset_tht', 'groupID',
    #           'groupid', 'cycleid']
    #    '''
        #### 针对原始PPA 进行异常值报警
        conn2 =Mysql(**init['datebase2'])
        data2=data2.groupby(['product_id','eventtime','groupid' ,'line','eva_chamber','mask_id',\
                     'mask_set','port',"cycleid",'x_label', 'y_label',\
                        "glass_id"])[['ppa_x','ppa_y','pos_x','pos_y',\
                      'offset_x','offset_y','offset_tht']].mean().reset_index()
        print("data2.shape before alarm",data2.shape)
        flag,data2 = AlarmPpa(data2,init = init['alarm'],ops = init['ops'],exclude = [] ,conn=conn2)
        print("data2.shape after alarm",data2.shape)
        conn2.close() 
        if flag:
            logger.info('原始PPA数据存在异常！！！')
        if len(data2)==0:
            logger.info('原始PPA数据处理异常 后数据为空')
            continue
        ###########先将新数据插入，再根据datachoose的取数据
        '''
        之所以可以先插入数据：
        1、顺序运行，不会出现重复插入eva_all表
        2、datachoose中指定了要计算的[groupid,cycleid]，故取出待计算的ppa数据是也不存在重复取出的情况。
        '''
        conn2 =Mysql(**init['datebase2'])
        data2.groupid=data2.groupid.astype(int)
        data2.line=data2.line.astype(int)
        data2.x_label=data2.x_label.astype(int)
        data2.y_label=data2.y_label.astype(int)    
        if 'eva_all' not in conn2.list_table():
            conn2.creat_table_from_df(tablename='eva_all', df=data2)
        conn2.insert_df(tablename='eva_all',df=data2)
        logger.info('已完成初始数据插入，耗时 :  %0.2fs'%(time.time()-st))
        '''
        GetCallPPA：
        若datachoose 已存在于 offset_table中则不计算。用到了Getcalmap函数
        '''
        if len(datachoose)==0:
            logger.info("未发现需要计算的PPA数据1") 
            continue
        if "offset_table" in conn2.list_table():
            temp = Getcalmap(datachoose,conn2,tablename = 'offset_table')\
                [datachoose.columns.tolist()]
            temp = temp.drop_duplicates()
            temp['bz'] = 1 ## 以计算标识符
            datachoose = pd.merge(datachoose,temp,on = datachoose.columns.tolist(),how = "left")
            ## 删除已计算过的 cycle, 防止重复计算
            datachoose = datachoose[datachoose['bz']!=1].drop("bz",axis=1)
            
        conn2.close()
        
        if len(datachoose)==0:
            logger.info("未发现需要计算的PPA数据2") 
            continue
        logger.info("本次判断后需要计算的 datachoose :\n%s"%(str(datachoose)))
        logger.info('Cycle判断完成 ,datachoose shape : %s ,耗时 :  %0.2fs'%(str(datachoose.shape),time.time()-st))
        ####取出需要计算的所有PPA
        logger.info('#########################   获取需计算的PPA数据阶段   #########################')
        st = time.time()
        conn2 =Mysql(**init['datebase2'])
        
        df2=GetCalPPA(datachoose,conn=conn2.obj.conn,number=init['opt']['opsnumber'])
        conn2.close()
        logger.info('GetCalPPA shape : %s '%(str(df2.shape)))    
        
        logger.info('#########################   获取后的PPA数据折算阶段   #########################')          
        ####按照cycle颗粒度做PPA折算, CreateOffsetAfter 直接对 PPA_X,PPA_Y进行了修正
        df2 = df2.groupby(['product_id','groupid','line','eva_chamber','mask_id','port']).apply(CreateOffsetAfter)
        logger.info('完成跨周期OFFSET折算 shape : %s ,耗时 :  %0.2fs'%(str(df2.shape),time.time()-st))
        df2.index =range(len(df2))
          
        logger.info('#########################   OFFSET优化阶段   #########################')   
        ###  首先 对每个 Glass 各个 ppa teg 进行mean 合并
        print('df2.columns:',df2.columns)
        df3=df2.groupby(['product_id','groupid' ,'line','eva_chamber','mask_id',\
                     'port',"cycleid",'x_label', 'y_label',"glass_id"])\
                        [['ppa_x','ppa_y','pos_x','pos_y',\
                      'offset_x','offset_y','offset_tht']].mean().reset_index()
        print('df3.columns-1:',df3.columns)
        df4=df3.copy()
        ##  再次，针对同一个cycle 下所有glass 进行合并
        df3=df3.groupby(['product_id',"groupid", 'line','eva_chamber','mask_id','port',"cycleid",'x_label', 'y_label'])\
                [['ppa_x','ppa_y','pos_x','pos_y','offset_x','offset_y','offset_tht']]\
                .mean().reset_index()
        ## df3 仅是用于计算的 数据源
        st = time.time()
        print('df3.columns-2:',df3.columns)
        res=df3.groupby(['product_id', 'groupid','line','eva_chamber','port','cycleid']).apply(cal_optimized_offset,init['ops'])
        print('res.columns-1:',res.columns)
        res = pd.merge(res.reset_index(),df2[['product_id', "groupid",'line','eva_chamber','port','cycleid',\
                       "mask_id","mask_set",'glasscount', 'starttime', 'endtime']].drop_duplicates(),\
                       on = ['product_id', "groupid",'line','eva_chamber','port','cycleid']) 
        print('res.columns-2:',res.columns)
        logger.info('#########################   OFFSET优化结果异常判断阶段   #########################')   
        conn2 =Mysql(**init['datebase2'])
        flag1,res = AlarmOffset(res,df4,init['alarm'],ops = init['ops'],exclude=[],conn=conn2)
        conn2.close()
        if flag1:
            logger.info('OFFSET优化结果中发现异常！！！')
    
        ## 获取每个cycle 颗粒度下的 'groupid','glasscount', 'starttime', 'endtime' 静态属性
        res.groupid=res.groupid.astype(int)
        res.line=res.line.astype(int)
        res.glasscount=res.glasscount.astype(int)
        res.columns = res.columns.str.replace(".",'')
        try:
            del res['key']
        except:
            pass
            
        conn2 =Mysql(**init['datebase2'])
        if "offset_table" not in conn2.list_table():
            conn2.creat_table_from_df("offset_table",res)
        conn2.insert_df("offset_table",res)
        conn2.close()
        logger.info("Cal_Optimized_Offset Cal Time %02.fs"%(time.time()-st))
        
        if not DEBUG:
            try:
                InsertCIM(res,init['datebase3'])
                logger.info("完成CIM表插入")
            except Exception as e:
                logger.info("**** 程序出现异常 异常代码 : %s"%e)
    UpdateTime(endtime,appst)
    ######结束脚本运行成功结束后修改start-time，并写回文件
        
if __name__=="__main__":    
    #########################   日志文件格式配置文件    #########################
    logger = logging.getLogger(__name__)
    logger.setLevel(level = logging.DEBUG)
    now = datetime.datetime.now().strftime("%Y%m%d%H")
    CheckDirname([LOGGING,IMAGE])
    handler = logging.FileHandler(os.path.join(LOGGING,"%s.txt"%now))
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    
    logger.addHandler(handler)
    logger.addHandler(console)   
    
    try:
    	Main(logger)
    except Exception as e:
    	logger.info("**** 程序出现异常 异常代码 : %s"%e)
        Send(title = 'APP ERROR',content = "",images = [{"content":e,"file":""}],\
            recv = ["dongzhaoyu@k2data.com.cn",'wangjidong@k2data.com.cn'])
        
