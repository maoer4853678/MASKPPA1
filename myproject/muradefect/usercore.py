from .my2sql import Mysql
import json,os,configparser
import datetime


CONFIGROOT = './muradefect/static/conf'

def GetSP(CONFIGROOT):
    ## 数据筛选的主要属性 和 数据库连接信息
    config=configparser.ConfigParser()
    config.read(os.path.join(CONFIGROOT,'conf.ini'))
    settings = dict(config['settings'].items())
    return settings

def GetConn():
    conn = Mysql(**GetDataBase(CONFIGROOT))
    return conn

def GetRole(user):
    admins = ['admin']
    return user in admins

def GetDataBase(CONFIGROOT):
    ## 数据筛选的主要属性 和 数据库连接信息
    config=configparser.ConfigParser()
    config.read(os.path.join(CONFIGROOT,'conf.ini'))
    database = dict(config['datebase2'].items())
    return database

def SetSP(CONFIGROOT,settings):
    ## 数据筛选的主要属性 和 数据库连接信息
    config=configparser.ConfigParser()
    config.read(os.path.join(CONFIGROOT,'conf.ini'))
    for key,value in settings.items():
        config.set('settings',key,str(value))
    with open(os.path.join(CONFIGROOT,'conf.ini'),'w') as configfile:
        config.write(configfile)