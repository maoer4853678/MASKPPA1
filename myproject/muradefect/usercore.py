from .my2sql import Mysql
import json,os,configparser
import datetime
import json

CONFIGROOT = './muradefect/static/conf'

def GetRateTh():
    path = os.path.join(CONFIGROOT,"ratethreahold.json")
    if os.path.exists(path):
        with open(path,"r") as f:
            msg=  json.loads(f.read())
        return msg
    else:
        return {}

def CreateRateTh(product_id):
    path = os.path.join(CONFIGROOT,"ratethreahold.json")
    msg = GetRateTh()
    xchamber = {"xoc3":50,"xoc4":50,"xoc5":50,"xoc6":50,"xoc7":50,"xoc8":50}
    ychamber = {"yoc3":50,"yoc4":50,"yoc5":50,"yoc6":50,"yoc7":50,"yoc8":50}
    xchamber.update(ychamber)
    msg[product_id] = xchamber
    msg1 =json.dumps(msg)
    with open(path,"w") as f:
        f.write(msg1)
    
def SetRateTh(product_id,option):
    path = os.path.join(CONFIGROOT,"ratethreahold.json")
    msg = GetRateTh()
    msg[product_id] = option
    msg1 =json.dumps(msg)
    with open(path,"w") as f:
        f.write(msg1)

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
    init = {}
    for d in ["settings","xth","yth"]:
        dct = dict(config[d].items())
        for key in dct.keys():
            try:
                dct[key] = float(dct[key])
            except:
                pass
        init[d] = dct
    return init

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

def SetSP(settings,session = 'settings'):
    ## 数据筛选的主要属性 和 数据库连接信息
    config=configparser.ConfigParser()
    config.read(os.path.join(CONFIGROOT,'conf.ini'))
    for key,value in settings.items():
        config.set(session,key,str(value))
    with open(os.path.join(CONFIGROOT,'conf.ini'),'w') as configfile:
        config.write(configfile)