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
from .optimize_offset_threshold import cal_optimized_offset, plot_data
import pandas as pd
from imp import reload
import datetime

conn = GetConn()

################################################## 通用函数 ##############################################
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
    endtime = datetime.datetime.now()
    starttime = endtime - datetime.timedelta(days=7)
    sql = '''
    select GroupID,cycleID,product_id,min(eventtime) as starttime,max(eventtime) \
    as endtime, GlassCount as count
    from offset  where eventtime >='%s' and eventtime <= '%s' 
    group by GroupID,cycleID,product_id,GlassCount    
    '''%(starttime.strftime("%Y-%m-%d"),endtime.strftime("%Y-%m-%d"))
    data = pd.read_sql_query(sql,con=conn.obj.conn)
    return data

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

def PlotBeforeData(data):
    data['nx'] = data.pos_x+data.ppa_x
    data['ny'] = data.pos_y+data.ppa_x
    data['n1x'] = data.pos_x+data.ppa_y
    data['n1y'] = data.pos_y+data.ppa_y
    res = {"PPA_X":data[['nx','ny']].values.tolist(),\
           "PPA_Y":data[['n1x','n1y']].values.tolist()}
    return res

def PlotAfterData(data):
    res = PlotBeforeData(data)
    return res


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
    sql = '''
    select * from offset  where groupid ='%s' and cycleid = '%s' and PRODUCT_ID = '%s'
    '''%(groupid,cycleid,product)
    df = pd.read_sql_query(sql,con=conn.obj.conn)
    data,fields = GenerateTable(df)
    return HttpResponse(json.dumps({"data":data,"fields":fields})\
                            ,content_type="application/json,charset=utf-8")

@need_logged_in
def GetOpsPpa(request):
    ## 绘制散点图所需数据, 优化反算
    print ("获取GetOpsPpa数据请求")
    glassid = request.POST.get("glassid")
    chamber = request.POST.get("chamber") 
    data = pd.read_sql_query("select ppa_x,ppa_y,offset_x,offset_y, offset_tht, \
                             x_label,y_label,pos_x,pos_y  from eva_all where \
                             glass_id = '%s' and eva_chamber = '%s' \
                             "%(glassid,chamber), con=conn.obj.conn)
    
    adf = PlotAfterData(data)
    bdf = PlotBeforeData(data)
    return HttpResponse(json.dumps({"before":adf,"after":bdf})\
                            ,content_type="application/json,charset=utf-8")
    
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
    data = GetOffsetSta()  ## Offset 近一周的统计表
    stadata,stafields = GenerateTable(data)
    return render(request, 'offset.html',{'username': username,"products":products,"stadata":json.dumps(stadata),\
                                          "stafields":json.dumps(stafields)})

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
    data,fields = GenerateTable(df)
    return render(request, 'alarm.html',{'username': username,"data":json.dumps(data),\
                 "fields":json.dumps(fields)})

@need_logged_in
def Data(request):
    username=  request.session.get("username")
    df = pd.read_sql_query("select * from eva_all ORDER BY EVENTTIME DESC limit 500 ",con = conn.obj.conn)
    df = df.drop(['x_label','y_label'],axis=1)
    print ('debug',1)
    data,fields = GenerateTable(df)
    print ('debug',2)
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

    
#def plot(request):
#    p1 = pd.read_csv("./muradefect/data/EVA_ALL.csv")
#    p1['EVENTTIME'] = pd.to_datetime(p1['EVENTTIME'])
#
#    all_glasses = p1[p1.EVA_CHAMBER == 'B'][['RECIPE', 'GLASS_ID', 'MASK_ID']].drop_duplicates()
#    glass = p1.GLASS_ID.iloc[0]
#    chamber = p1.EVA_CHAMBER.iloc[0]
#
#    ppa_teg, ppa_val = plot_data(p1, glass, chamber)
#
#    form = GlassPlotForm()
#    data = {'form': form,
#            'all_glasses': all_glasses.to_html(index=False),
#            'title': json.dumps(glass + '-' + chamber),
#            'ppa_teg': json.dumps(ppa_teg),
#            'ppa_val': json.dumps(ppa_val)
#            }
#
#    if request.method == 'POST':
#        form = GlassPlotForm(request.POST)
#
#        if form.is_valid():
#            glass = form.cleaned_data['glasses']
#            chamber = form.cleaned_data['chamber']
#
#            ppa_teg, ppa_val = plot_data(p1, glass, chamber)
#
#        data = {'form': form,
#                'all_glasses': all_glasses.to_html(index=False),
#                'title': json.dumps(glass + '-' + chamber),
#                'ppa_teg': json.dumps(ppa_teg),
#                'ppa_val': json.dumps(ppa_val)
#                }
#
#    return render(request, 'plot.html', data)
#
#
#def glasses_optimize(request):
#    p1 = pd.read_csv("./muradefect/data/EVA_ALL.csv")
#    p1['EVENTTIME'] = pd.to_datetime(p1['EVENTTIME'])
#
#    all_glasses = p1[p1.EVA_CHAMBER == 'B'][['RECIPE', 'GLASS_ID', 'MASK_ID']].drop_duplicates()
#
#    form = GlassForm()
#    data = {'form': form, 'all_glasses': all_glasses.to_html(index=False)}
#
#    if request.method == 'POST':
#        mask_id = pd.read_sql_table('MASK_ID', con=conn).set_index('index')
#        form = GlassForm(request.POST)
#        glass_ids = request.session['glass_ids']
#        info = 'This is the optimize page'
#        optimize_result = 'No glasses available to optimize!'
#
#        if form.is_valid():
#            glass = form.cleaned_data['glasses']
#
#            if request.POST.get('add'):
#                glass_ids = glass_ids + [glass]
#
#                info = 'This is an add'
#            elif request.POST.get('delete'):
#                if len(glass_ids):
#                    glass_ids.pop()
#
#                info = 'This is a delete'
#            elif request.POST.get('clear'):
#                glass_ids = []
#
#                info = 'This is a clear'
#            elif request.POST.get('optimize'):
#                p2 = p1[p1.GLASS_ID.isin(glass_ids)]
#
#                if p2.shape[0]:
#                    r4 = p2.groupby(['RECIPE', 'exp_label', 'prd_label', 'grp_label',
#                                     'EVA_CHAMBER', 'MASK_ID', 'line']).\
#                        apply(cal_optimized_offset).reset_index()
#
#                    r4.EVENTTIME = pd.to_datetime(r4.EVENTTIME)
#
#                    r5 = r4.rename(columns={'EVA_CHAMBER': 'OC'})\
#                        [['RECIPE', 'EVENTTIME', 'OC', 'MASK_ID', 'line',
#                          'OFFSET_X', 'OFFSET_Y', 'OFFSET_T',
#                          'AFTER_X', 'AFTER_Y', 'AFTER_T',
#                          'PPA', 'PPA_BEFORE']].sort_values('EVENTTIME')
#
#                    optimize_result = r5.to_html(index=False)
#
#                info = 'This is an optimize'
#            else:
#                info = 'Something is wrong!'
#
#        request.session['glass_ids'] = glass_ids
#
#        glass_pars = mask_id[mask_id.GLASS_ID.isin(glass_ids)].sort_values('EVENTTIME')
#        glass_selected = all_glasses[all_glasses.GLASS_ID.isin(glass_ids)]
#
#        data = {'info': info, 'form': form,
#                'glass_selected': glass_selected.to_html(index=False),
#                'all_glasses': all_glasses.to_html(index=False),
#                'glass_pars': glass_pars.to_html(index=False),
#                'optimize_result': optimize_result}
#
#    return render(request, 'glasses.html', data)

    
    














































