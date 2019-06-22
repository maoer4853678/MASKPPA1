from .my2sql import Mysql
import json,os,configparser
import datetime


CONFIGROOT = './muradefect/static/conf'

def GetUserMaskset():
    if os.path.exists(os.path.join(CONFIGROOT,"masksetdict.json")):
        msg = json.load(open(os.path.join(CONFIGROOT,"masksetdict.json"),"r"))
        return msg
    else:
        return {}

def SetUserMaskset(product,newset,maskids):
    msg = GetUserMaskset()
    if product not in msg:
        msg[product] ={}
    msg[product][newset] = maskids
    with open(os.path.join(CONFIGROOT,"masksetdict.json"),"w") as f:
        f.write(json.dumps(msg))

def DelUserMaskset(product,newset):
    msg = GetUserMaskset()
    if product not in msg:
        return 
    else:
        if newset in msg[product] :
            del msg[product][newset]
            with open(os.path.join(CONFIGROOT,"masksetdict.json"),"w") as f:
                f.write(json.dumps(msg))
        else:
            return 

def GetSP():
    ## 数据筛选的主要属性 和 数据库连接信息
    config=configparser.ConfigParser()
    config.read(os.path.join(CONFIGROOT,'conf.ini'))
    settings = dict(config['settings'].items())
    return settings

def GetConn():
    conn = Mysql(**GetDataBase())
    return conn

def GetRole(user):
    admins = ['admin']
    return user in admins

def GetDataBase():
    ## 数据筛选的主要属性 和 数据库连接信息
    config=configparser.ConfigParser()
    config.read(os.path.join(CONFIGROOT,'conf.ini'))
    database = dict(config['datebase2'].items())
    return database

def SetSP(settings):
    ## 数据筛选的主要属性 和 数据库连接信息
    config=configparser.ConfigParser()
    config.read(os.path.join(CONFIGROOT,'conf.ini'))
    for key,value in settings.items():
        config.set('settings',key,str(value))
    with open(os.path.join(CONFIGROOT,'conf.ini'),'w') as configfile:
        config.write(configfile)