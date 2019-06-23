from django.http import HttpResponse
from django.shortcuts import render, redirect,render_to_response
from django.views import View
from django.template import RequestContext
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import User
import json,os
from .usercore import *

from .forms import AddForm, GlassForm, GlassPlotForm,OptionForm,RegisterForm
#from .utils_db import db
#from django.db import connection as conn
import pandas as pd
import numpy as np
from imp import reload
import datetime
import random
import string
from django.http import FileResponse

conn = GetConn()

################################################## 通用函数 ##############################################
def siplitlist(listx,n,axis = 0):
    '''
    listx: 待分组序列，类型可以是list，np.array,pd.Series...
    n: 若axis=0 n为组别个数,计算生成元素个数,若axis=1 n为每组元素个数,计算生成组别个数
    axis: 若axis=0 按照固定组别个数分组, 若axis=1 按照固定元素个数分组
    '''
    if axis ==0:
        a1,a2 = divmod(len(listx),n)
        N = [a1]*(n-a2)+[a1+1]*a2 if a1!=0 else [1]*len(listx)
        res = [listx[s:s+i] for s,i in enumerate(N) if len(listx[s:s+i])!=0]
    else:
        N = int(len(listx)/n)+1
        res = [listx[i*n:(i+1)*n] for i in range(N) if len(listx[i*n:(i+1)*n])!=0]
    return res

def GetFilename():
    a=''.join(random.sample(string.ascii_letters+string.digits,random.randint(3,12)))+".csv"
    return a


def GetProducts():
    products = pd.read_sql_query("select distinct product_id from eva_all ",con=conn.obj.conn)
    return products['product_id'].tolist()

def GetProductDict():
    data = pd.read_sql_query("select distinct product_id,mask_id from eva_all ",con=conn.obj.conn)
    productdict = dict(list(map(lambda x:[x[0],x[1]['mask_id'].tolist()],data.groupby("product_id"))))
#    maskids = data.mask_id.sort_values().unique().tolist()
    return productdict

def GetOffsetSta():
    ## 最近一周的 offset统计结果，可以改成sql 执行返回结果
    try:
        endtime = datetime.datetime.now()
    #    starttime = endtime - datetime.timedelta(days=7) ## 正常看一周
        starttime = endtime - datetime.timedelta(days=90)
        sql = '''
        select distinct product_id as productid,groupid,line,eva_chamber as chamber,\
         port,cycleid,starttime,endtime,glasscount as count from offset_table  \
          where starttime >='%s' and starttime <= '%s' order by starttime desc\
         '''%(starttime.strftime("%Y-%m-%d"),endtime.strftime("%Y-%m-%d"))
        data = pd.read_sql_query(sql,con=conn.obj.conn)
        data['count'] = data['count'].astype(int)
        data['starttime'] = pd.to_datetime(data['starttime'])
        data['endtime'] = pd.to_datetime(data['endtime'])
        res =  data.groupby(['productid','groupid','line','cycleid']).\
            agg({"starttime":"min","endtime":"max","count":"mean"}).reset_index()
        res = res.sort_values(["starttime",'productid','groupid','line','cycleid'],\
               ascending=False)
        res.columns =res.columns.str.upper()
        return data,res
    except:
        return pd.DataFrame(),pd.DataFrame()

def GetPpaData(starttime,endtime,product,maskids):
    data = pd.read_sql_query("select ppa_x,ppa_y,glass_id,mask_id from eva_all \
                             where eventtime >='%s' and eventtime <= '%s' \
                             and product_id = '%s' and mask_id in (%s) \
                             "%(starttime,endtime,\
                             product,str(maskids)[1:-1]),con=conn.obj.conn)
    th = 6.5
    res = []
    for mask_id in data.mask_id.unique():
        temp = data[data.mask_id==mask_id]
        res1 = temp.groupby("glass_id").apply(lambda y:y[['ppa_x','ppa_y']].apply\
                    (lambda x:len(x[x.abs()<=th]),axis=0)/len(y)*100).round(2)
        res.append({"mask_id":mask_id,"glass_id":res1.index.tolist(),\
                    "ppa_x":res1['ppa_x'].tolist(),"ppa_y":res1['ppa_y'].tolist()})
    return res


def GenerateTable(df):
    if len(df)==0:
        return [],[]
    d = {"int64":"int","int32":"int","float64":"float","float32":"float",\
     "datetime64[ns]":"text","object":"text" }
    df.columns = df.columns.str.upper()
    df1 = df.dtypes.astype(str).reset_index()
    df1.columns = ['name','type']
    df[df1[df1['type']=='datetime64[ns]']['name']]=\
        df[df1[df1['type']=='datetime64[ns]']['name']].astype(str)
    df1['type'] = df1['type'].map(d)
    df[df1[df1['type']=='float']['name']] = \
        df[df1[df1['type']=='float']['name']].round(3)
    df1["sortable"] = True    
    ## 计算各列初始化宽度
    w1  =df[df1[df1['type']=='text']['name']].apply(lambda x:x.str.len().max(),axis=0)
    w2 = df[df1[df1['type'].isin(['int','float'])]['name']].astype(str).\
          apply(lambda x:x.str.len().max(),axis=0)
    w = pd.concat([w1,w2])+30 ## 4是 宽度折算系数  
    df1['width'] = df1['name'].map(w.to_dict())    
#    df1['width'] = 40
    df1['align'] =  "center"
    df1['hide'] = True
    fields = list(df1.T.to_dict().values())
    data = list(df.T.to_dict().values())
    return data,fields


def plot_data(df):
    ppa_teg = []
    ppa_ver = []
    ppa_hor = []
    if len(df)!=0:
        df = df.sort_values(['pos_y', 'pos_x'])
        ppa_teg = df[['pos_x', 'pos_y']].values.tolist()
        df.ppa_x = df.pos_x + 10 * df.ppa_x
        df.ppa_y = df.pos_y + 10 * df.ppa_y
        ppa_ver = list(map(lambda x:x[1][['ppa_x', 'ppa_y']].values.tolist()\
                           ,df.groupby('x_label'))) ## 垂直方向
        ppa_hor = list(map(lambda x:x[1][['ppa_x', 'ppa_y']].values.tolist()\
                           ,df.groupby('y_label'))) ## 水平方向
    plots = {"ppa_teg":ppa_teg,"PPA_X":ppa_ver,"PPA_Y":ppa_hor}
    return plots

def BeforeData(glassid,chamber):
    ## BeforeData 是从 EVA_ALL表获取的数据 ,需要获取到 glassid颗粒度的所有属性信息
    data = pd.read_sql_query("select product_id,groupid, line, \
                             eva_chamber,mask_set, port,cycleid,glass_id,\
                          ppa_x,ppa_y, offset_x,offset_y, offset_tht, \
                         x_label,y_label,pos_x,pos_y  from eva_all where \
                         glass_id = '%s' and eva_chamber = '%s' \
                         "%(glassid,chamber), con=conn.obj.conn)
    return data

def AfterData(data):
    ## tAfterData 是按照before中的属性信息从 offset_table中取出优化结果
    cols = ["product_id",'eva_chamber',"mask_set",'port']
    cols1 = ["groupid",'line','cycleid']
    conditon = list(map(lambda x:"%s = '%%s' "%x,cols))+list(map(lambda x:"%s = %%s "%x,cols1))
    conditon = ' and '.join(conditon)
    product_id,eva_chamber,mask_set,port,groupid,line,cycleid= data[cols+cols1].iloc[0].tolist()
    sql = "select delta_x,delta_y,delta_t from offset_table where %s"%conditon
    sql = sql%(product_id,eva_chamber,mask_set,port,groupid,line,cycleid)
    delta_args = pd.read_sql_query(sql, con=conn.obj.conn)
    print (delta_args,"delta_args")
    if len(delta_args)>0:
        delta_x,delta_y,delta_tht = delta_args.iloc[0].tolist()
        ## 将该glass所在的组别中 offset结果作用于他
        data['ppa_x'] = data['ppa_x']+delta_x-delta_tht*data['pos_y']*(np.pi / 180 / 100)
        data['ppa_y'] = data['ppa_y']+delta_y+delta_tht*data['pos_x']*(np.pi / 180 / 100)
        return data
    else:
        return pd.DataFrame()


################################################## 注册系统  ##############################################
def need_logged_in(func):
    def wrapper(request, *args, **kwargs):
        if request.session.get('logged'):
            return func(request, *args, **kwargs)
        else:
            return redirect('/login')

    return wrapper

def Login(request): 
    if request.method == 'POST': 
        username = request.POST.get('username')
        password = request.POST.get('password')
        namefilter = User.objects.filter(name = username)
        if len(namefilter)==0:
             return render(request,'login.html',{'error':"用户名不存在"})
        else:
            if namefilter[0].password!=password:
                return render(request,'login.html',{'error':"密码错误"})
            else:
                request.session['logged'] =True
                request.session['offset'] = {}
                request.session['username'] = username
                return redirect('/')     
    else:
        return render(request, 'login.html')

def Logout(request): 
    request.session['logged'] = False
    request.session['glass_ids'] = []
    return redirect('/login')


def Register(request):
    if request.method == 'POST':
        name=request.POST.get('username')
        password=request.POST.get('password')
        password1=request.POST.get('password1')
        namefilter = User.objects.filter(name = name)
        if len(namefilter) > 0:
            return render(request,'register.html',{'error':'用户名已存在'})
        
        if password != password1:
            return render(request,'register.html',{'error':'两次输入的密码不一致！'})
        else:
            c_time = datetime.datetime.now()
            user = User.objects.create(name=name,password=password,c_time= c_time)
            user.save()
            request.session['logged'] =True
            request.session['username'] = name
            return redirect('/')
            
    return render(request,'register.html')

def GetInfo(df,settings):
    if len(df)==0:
        return {}
    infos ={}
    for key in ['ppa_x','ppa_y']:
        info = {}
        for th in ['th1','th2']:
            key1 = "±%sum"%(str(settings[th]))
            info[th+"_name"] = key1
            info[th+"_len"]  = len(df[df[key].abs()<= float(settings[th])])
            info[th+"_per"] = "%02.f%%"%(float(info[th+"_len"])/len(df)*100)      
        info["min"] = round(df[key].min(),3)
        info["max"] = round(df[key].max(),3)
        infos[key.upper()] = info
    return infos

################################################## Rest后台接口  ##############################################
@need_logged_in
def NewSet(request):
    if request.is_ajax():
        print ("获取NewSet数据请求")
        maskset = request.POST.get("maskset")
        maskids = request.POST.get("maskids").split(",")
        product = request.POST.get("product")
        maskids = list(map(lambda x:x.strip(),maskids))
        print ("新套别名称: %s"%maskset)
        print ("套别对应 MASKID: %s"%(str(maskids)))       
        print ("套别对应 Product: %s"%(product))  
        SetUserMaskset(product,maskset,maskids)
        return HttpResponse("ok")
 
@need_logged_in
def DelSet(request):
    if request.is_ajax():
        print ("获取DelSet数据请求")
        maskset = request.POST.get("maskset")
        product = request.POST.get("product")
        print ("删除套别名称: %s"%maskset)    
        DelUserMaskset(product,maskset)
        return maskset
       
@need_logged_in
def GetPpa(request):
    if request.is_ajax():
        print ("获取GetPPA数据请求")
        starttime = request.POST.get("starttime")
        endtime = request.POST.get("endtime")
        product = request.POST.get("productselect")
        maskids = request.POST.get("maskselect").split(",")
        maskids = list(map(lambda x:x.strip(),maskids))
        print ("请求参数 starttime: %s, endtime: %s\n product :%s , maskset :%s"\
               %(starttime,endtime,product,maskids))
        res = GetPpaData(starttime,endtime,product,maskids)
        print ("查询结果长度 %d"%(len(res)))
        return HttpResponse(json.dumps(res),content_type="application/json,charset=utf-8")

@need_logged_in
def GetOffset(request):
    print ("获取GetOffset数据请求")
    groupid = request.POST.get("groupid")
    cycleid = request.POST.get("cycleid") 
    product = request.POST.get("product") 
    line = request.POST.get("line") 
    sql = '''
    select product_id as productid,groupid,line,eva_chamber as chamber,\
         port,cycleid,starttime,endtime, delta_x,delta_y, delta_t as delta_tht,\
         offset_x, offset_y, offset_tht from offset_table  \
         where groupid =%s and cycleid = %s and PRODUCT_ID = '%s' and line = %s
    '''%(groupid,cycleid,product,line)
    df = pd.read_sql_query(sql,con=conn.obj.conn)
    df.columns = df.columns.str.upper()
    data,fields = GenerateTable(df)
    return HttpResponse(json.dumps({"data":data,"fields":fields})\
                            ,content_type="application/json,charset=utf-8")
@need_logged_in
def DownOffset(request):
    print ("获取封装下载数据请求")
    data = request.POST.get("data").split(",")
    fields = request.POST.get("fields").split(",")
    data = siplitlist(data,len(fields),axis=1)
    if not os.path.exists("tempdir"):
        os.makedirs("tempdir")
    filename = GetFilename()
    df = pd.DataFrame(data,columns = fields)
    df.to_csv("./tempdir/%s"%filename,index=False)
    return HttpResponse(json.dumps({"filename":filename}),content_type="application/json,charset=utf-8")

@need_logged_in
def DownLoad(request,filename):
    print ("获取下载文件请求")
    file=open("./tempdir/%s"%filename,'rb')  
    response =FileResponse(file)  
    response['Content-Type']='application/octet-stream'  
    response['Content-Disposition']='attachment;filename="%s"'%filename
    return response

@need_logged_in
def GetOpsPpa(request):
    ## 绘制散点图所需数据, 优化反算
    print ("获取GetOpsPpa数据请求")
    glassid = request.POST.get("glassid")
    chamber = request.POST.get("chamber") 
    ## 优化前的 PPA数据  
    bdf = BeforeData(glassid,chamber)
    print (bdf.shape,"bdf.shape")
    bplot = plot_data(bdf)
    
    adf = AfterData(bdf)
    print (adf.shape,"adf.shape")
    aplot = plot_data(adf)
    
    settings =  GetSP()   
    glassinfo = {}
    glassinfo["before"] =  GetInfo(bdf,settings)
    glassinfo["after"] =  GetInfo(adf,settings)   

    return HttpResponse(json.dumps({"before":bplot,"after":aplot,"glassinfo":glassinfo})\
                            ,content_type="application/json,charset=utf-8")
    
def LogEtl(request):
    print ("获取 LogEtl 数据请求")
    logpath = './muradefect/server/log'
    files = os.listdir(logpath)
    if len(files):
        path = os.path.join(logpath,files[-1])
        file=open(path,'rb')  
        response =FileResponse(file)  
        response['Content-Type']='application/octet-stream'  
        response['Content-Disposition']='attachment;filename="%s"'%path
        return response

################################################## 主要视图  ##############################################
    
@need_logged_in
def index(request):
    username=  request.session.get("username")
    if username:
        productdict = GetProductDict()
        masksetdict = GetUserMaskset()
#        res = GetPpaData(starttime,endtime,products[0],masksets[0])
        return render(request, 'index.html', {'username': username,"data":'[]',\
                "productdict":productdict,"masksetdict":masksetdict})
    else:
        return redirect('/login')

@need_logged_in
def Offset(request):
    username=  request.session.get("username")
    products = GetProducts()
    data,res = GetOffsetSta()  ## Offset 近一周的统计表
    if len(res):
        groupid,line,cycleid = res[['GROUPID','LINE','CYCLEID']].iloc[0].tolist()
    else:
        groupid,line,cycleid =0,1,0
    stadata,stafields = GenerateTable(res)
    return render(request, 'offset.html',{'username': username,"products":products,"stadata":json.dumps(stadata),\
                                          "stafields":json.dumps(stafields),"groupid":groupid,"line":line,\
                                          "cycleid":cycleid})

@need_logged_in
def Ppa(request):
    username=  request.session.get("username")
    data = pd.read_sql_query("select distinct glass_id,eva_chamber from eva_all", con=conn.obj.conn)
    glassids = data.glass_id.sort_values().unique().tolist()
    chambers = data.eva_chamber.sort_values().unique().tolist()
    return render(request, 'ppa.html',{'username': username,"glassids":glassids,"chambers":chambers,\
                  "alldata":{}})

@need_logged_in
def Alarm(request):
    username=  request.session.get("username")
    df = pd.read_sql_query("select * from alarm ORDER BY EVENTTIME DESC limit 20 ",con = conn.obj.conn)
    df.columns = df.columns.str.upper()
    data,fields = GenerateTable(df)
    return render(request, 'alarm.html',{'username': username,"data":json.dumps(data),\
                 "fields":json.dumps(fields)})

@need_logged_in
def Data(request):
    username=  request.session.get("username")
    df = pd.read_sql_query("select * from eva_all ORDER BY EVENTTIME DESC limit 500 ",con = conn.obj.conn)
    df = df.drop(['x_label','y_label'],axis=1)
    df.columns = df.columns.str.upper()
    data,fields = GenerateTable(df)
    return render(request, 'data.html',{'username': username,"data":json.dumps(data),\
                 "fields":json.dumps(fields)})

@need_logged_in
def Option(request):
    username=  request.session.get("username")
    settings =  GetSP()
    form = OptionForm(settings)
    if request.method == 'POST':
        if GetRole(username):
            form = OptionForm(request.POST)
            if form.is_valid():
                SetSP(form.cleaned_data)
                return render(request, 'option.html', {'username': username,"form":form,\
                                                       "message":"设置成功","status":200})
        else:
            return render(request, 'option.html', {'username': username,"form":form,\
                                                   "message":"设置失败, 你不是管理员账户","status":400})
        
    return render(request, 'option.html', {'username': username,"form":form,"status":200})
