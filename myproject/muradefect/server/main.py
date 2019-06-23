# -*- coding: utf-8 -*-
"""
数据获取与新周期判断
"""
import os,configparser
import datetime
from tool.my2sql import Mysql
from tool.GetNewdata import *
from tool.cal_optimized_offset import *
import logging
import cx_Oracle
import time
import datetime
import numpy as np

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
    
    datebase2 = dict(config['datebase2'].items())  ## 项目依赖的本地数据库
    
    init['base']  =base_args
    init['ops']  =ops_args
    init['th']  =th_args
    init['opt']  =opt_args
    init['datebase2']  =datebase2    
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

if __name__=="__main__": 
    
    import glob
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
    
    Files=glob.glob(r'..\data\Data*.csv') 
    i=0
    for F in Files:
        appst = time.time()
        
        logger.info('#########################   读取配置文件    #########################')
        init = GetOption()
        starttime = init['base']['starttime']
        endtime = init['base']['endtime']
        running = init['base']['running']
        logger.info('本次获取时间范围 ： %s -- %s'%(starttime,endtime))
        
        if running == "0" : ## 表示该阶段未有程序运行，可以往下执行

            logger.info('#########################   获取数据阶段    #########################')         
            SetOption("running","1")  ## 将 running状态置为 1 ，表示程序正在执行，防止重复运行
            i+=1
            filename=F.split('\\')[-1]  
            df=pd.read_csv(F,index_col=0)
            logger.info('@@@@@@@@@@@@@@@@@@@@   开始读第%d个文件：%s   @@@@@@@@@@@@@@@@@@@@@@@' %(i,filename))      
            df.columns=df.columns.str.lower()
            if (len(df)):
                df.eventtime=pd.to_datetime(df.eventtime)
                logger.info('获取数据完成 ,数据shape : %s ,耗时 :  %0.2fs'%(str(df.shape),time.time()-appst))            
                #### 针对原始PPA 进行异常值报警
                conn2 =Mysql(**init['datebase2'])
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
                    data.groupid=data.groupid.astype(int)
                    data.cycleid=data.cycleid.astype(int)
                    conn2.creat_table_from_df(tablename='eva_all', df=data)
                    conn2.insert_df(tablename='eva_all',df=data)
                    logger.info('eva_ppa表不存在。已完成初始数据插入，耗时 :  %0.2fs'%(time.time()-st))
                conn2.close()
                
                if TableExist:
                    logger.info('#########################   Group判断阶段    #########################')
                    st =time.time()
                    NewTimeMin=df.eventtime.min()
                    sql_MaxTime='select max(eventtime),max(groupid) from eva_all'
                    conn2 =Mysql(**init['datebase2'])
                    OldTimeMax,groupID=list(conn2.exec_(sql_MaxTime)[0])
                    conn2.close()
                    if NewTimeMin-OldTimeMax>pd.to_timedelta(36,unit='h'):
                        df['groupid']=groupID+1
                    else:
                        df['groupid']=groupID
                    logger.info('完成groupid赋值,耗时 :  %0.2fs'%(time.time()-st))
                    
                    logger.info('#########################   Cycle判断阶段    #########################')
                    ####Cycle判断，取出要优化的数据
                    st =time.time()
                    df['x_label'] = df['x_label'].astype(int)
                    df['y_label'] = df['y_label'].astype(int)
                    conn2 =Mysql(**init['datebase2'])
                    DataChoose,data2=CycleJudge(df,conn=conn2.obj.conn)
                    logger.info("初次筛选后的 DataChoose.shape : %s"%(str(DataChoose.shape)))
                    conn2.close()
                    print (DataChoose)
                    
                     ## 若DataChoose 已存在于 offset_table中则不计算
                    if len(DataChoose):    
                        
                        del DataChoose['port']   ## DataChoose 不应该带有 Port 信息
                        conn2 =Mysql(**init['datebase2'])
                        if "offset_table" in conn2.list_table():
                            temp = Getcalmap(DataChoose,conn2,tablename = 'offset_table')\
                                [DataChoose.columns.tolist()]
                            temp = temp.drop_duplicates()
                            temp['bz'] = 1 ## 以计算标识符
                            DataChoose = pd.merge(DataChoose,temp,on = DataChoose.columns.tolist(),how = "left")
                            ## 删除已计算过的 cycle, 防止重复计算
                            DataChoose = DataChoose[DataChoose['bz']!=1].drop("bz",axis=1)
                            logger.info("本次判断后需要计算的 DataChoose :\n%s"%(str(DataChoose)))
                        conn2.close()
                            
                    if len(DataChoose):    
                        #DataChoose.to_csv(r'D:\data_Visionox\Visionox\DataChooseIn-'+filename)
                        logger.info('Cycle判断完成 ,DataChoose shape : %s ,耗时 :  %0.2fs'%(str(DataChoose.shape),time.time()-st))
                        ####取出需要计算的所有PPA
                        st = time.time()
    #                    DataChoose.to_pickle("DataChoose.pk")
                        ## GetCalPPA 待优化
                        conn2 =Mysql(**init['datebase2'])
                        ## data2 需要在  GetCalPPA 函数执行过程中插入，原因是如果不足 个数的需要按照eventtime 进行搜索时
                        ## 会将刚刚插入的 cycle一起搜索出来，但是新的cycle不应该参与计算，所以计算eventtime时数据库中不应该有 新数据
                        df2=GetCalPPA(DataChoose,data2,conn=conn2,number=init['opt']['opsnumber'])
                        
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
                        
    #                    df3.to_pickle('df3.pk')
                        
                        res=df3.groupby(['product_id', 'groupid','line','eva_chamber','port','cycleid']).apply(cal_optimized_offset)
                        res = pd.merge(res.reset_index(),df2[['product_id', "groupid",'line','eva_chamber','port','cycleid',\
                                       "mask_set",'glasscount', 'starttime', 'endtime']].drop_duplicates(),\
                                       on = ['product_id', "groupid",'line','eva_chamber','port','cycleid']) 
                        ## 获取每个cycle 颗粒度下的 'groupid','glasscount', 'starttime', 'endtime' 静态属性
                        res.columns = res.columns.str.replace(".",'')
    #                    res.to_pickle("offset_table.pk")
                        conn2 =Mysql(**init['datebase2'])
                        if "offset_table" not in conn2.list_table():
                            conn2.creat_table_from_df("offset_table",res)
                        conn2.insert_df("offset_table",res)
                        conn2.close()
                        logger.info("Cal_Optimized_Offset Cal Time %02.fs"%(time.time()-st))
                        
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