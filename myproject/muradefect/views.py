from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

import json,os,configparser

from .forms import AddForm, GlassForm, GlassPlotForm,OptionForm
from .utils_db import db
from .optimize_offset_threshold import cal_optimized_offset, plot_data
import pandas as pd
from imp import reload


CONFIGROOT = './muradefect/static/conf'

def GetSP(CONFIGROOT):
    ## 数据筛选的主要属性 和 数据库连接信息
    config=configparser.ConfigParser()
    config.read(os.path.join(CONFIGROOT,'conf.ini'))
    settings = dict(config['settings'].items())
    return settings

def SetSP(CONFIGROOT,settings):
    ## 数据筛选的主要属性 和 数据库连接信息
    config=configparser.ConfigParser()
    config.read(os.path.join(CONFIGROOT,'conf.ini'))
    for key,value in settings.items():
        config.set('settings',key,str(value))
    with open(os.path.join(CONFIGROOT,'conf.ini'),'w') as configfile:
        config.write(configfile)

# data initialization
def need_logged_in(func):
    def wrapper(request, *args, **kwargs):
        print (request.session.get('logged'))
        if request.session.get('logged'):
            return func(request, *args, **kwargs)
        else:
            return redirect('/login')

    return wrapper

def Login(request): 
    if request.method == 'POST': 
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username=='root' and password=='root':
            request.session['logged'] = True
            request.session['glass_ids'] = []

            return redirect('/')
        else:
            return redirect('/login')
        
    return render(request, 'login.html')

def Logout(request): 
    request.session['logged'] = False
    request.session['glass_ids'] = []
    return redirect('/login')

@need_logged_in
def index(request):
#    p1 = pd.read_sql_table('EVA_ALL', con=db).set_index('index')
    p1 = pd.read_csv("./muradefect/data/EVA_ALL.csv")
    p1['EVENTTIME'] = pd.to_datetime(p1['EVENTTIME'])
    
    p0 = p1.groupby(['exp_label', 'prd_label', 'grp_label', 'RECIPE']). \
        EVENTTIME.agg(['min', 'max', 'count']).reset_index()

    p0['count'] = p0['count'] // 570

#    p3 = pd.read_sql_table('OFFSET', con=db).set_index('index')
    p3 = pd.read_csv("./muradefect/data/EVA_ALL.csv")

    info = p0.to_html(index=False)

    if request.method == 'POST':  # when the forms are submitted

        form = AddForm(request.POST)  # form contains the data to be submitted

        if form.is_valid():  # if the data submitted is valid
            exp_label = int(form.cleaned_data['exp_label'])
            prd_label = int(form.cleaned_data['prd_label'])
            grp_label = int(form.cleaned_data['grp_label'])
            recipe = form.cleaned_data['recipe']

            p4 = p3[(p3.exp_label == exp_label) &
                    (p3.prd_label == prd_label) &
                    (p3.grp_label == grp_label) &
                    (p3.RECIPE == recipe)]

            if p4.shape[0] > 0:
                result = p4.iloc[:, :12].to_html(index=False)
            else:
                result = 'No available glasses for optimization.'

    else:  # when it is visited normally
        form = AddForm()

        result = 'No glasses selected!'

    return render(request, 'index.html', {'form': form, 'info': info, 'result': result})


def plot(request):
    p1 = pd.read_csv("./muradefect/data/EVA_ALL.csv")
    p1['EVENTTIME'] = pd.to_datetime(p1['EVENTTIME'])

    all_glasses = p1[p1.EVA_CHAMBER == 'B'][['RECIPE', 'GLASS_ID', 'MASK_ID']].drop_duplicates()
    glass = p1.GLASS_ID.iloc[0]
    chamber = p1.EVA_CHAMBER.iloc[0]

    ppa_teg, ppa_val = plot_data(p1, glass, chamber)

    form = GlassPlotForm()
    data = {'form': form,
            'all_glasses': all_glasses.to_html(index=False),
            'title': json.dumps(glass + '-' + chamber),
            'ppa_teg': json.dumps(ppa_teg),
            'ppa_val': json.dumps(ppa_val)
            }

    if request.method == 'POST':
        form = GlassPlotForm(request.POST)

        if form.is_valid():
            glass = form.cleaned_data['glasses']
            chamber = form.cleaned_data['chamber']

            ppa_teg, ppa_val = plot_data(p1, glass, chamber)

        data = {'form': form,
                'all_glasses': all_glasses.to_html(index=False),
                'title': json.dumps(glass + '-' + chamber),
                'ppa_teg': json.dumps(ppa_teg),
                'ppa_val': json.dumps(ppa_val)
                }

    return render(request, 'plot.html', data)


def glasses_optimize(request):
    p1 = pd.read_csv("./muradefect/data/EVA_ALL.csv")
    p1['EVENTTIME'] = pd.to_datetime(p1['EVENTTIME'])

    all_glasses = p1[p1.EVA_CHAMBER == 'B'][['RECIPE', 'GLASS_ID', 'MASK_ID']].drop_duplicates()

    form = GlassForm()
    data = {'form': form, 'all_glasses': all_glasses.to_html(index=False)}

    if request.method == 'POST':
        mask_id = pd.read_sql_table('MASK_ID', con=db).set_index('index')
        form = GlassForm(request.POST)
        glass_ids = request.session['glass_ids']
        info = 'This is the optimize page'
        optimize_result = 'No glasses available to optimize!'

        if form.is_valid():
            glass = form.cleaned_data['glasses']

            if request.POST.get('add'):
                glass_ids = glass_ids + [glass]

                info = 'This is an add'
            elif request.POST.get('delete'):
                if len(glass_ids):
                    glass_ids.pop()

                info = 'This is a delete'
            elif request.POST.get('clear'):
                glass_ids = []

                info = 'This is a clear'
            elif request.POST.get('optimize'):
                p2 = p1[p1.GLASS_ID.isin(glass_ids)]

                if p2.shape[0]:
                    r4 = p2.groupby(['RECIPE', 'exp_label', 'prd_label', 'grp_label',
                                     'EVA_CHAMBER', 'MASK_ID', 'line']).\
                        apply(cal_optimized_offset).reset_index()

                    r4.EVENTTIME = pd.to_datetime(r4.EVENTTIME)

                    r5 = r4.rename(columns={'EVA_CHAMBER': 'OC'})\
                        [['RECIPE', 'EVENTTIME', 'OC', 'MASK_ID', 'line',
                          'OFFSET_X', 'OFFSET_Y', 'OFFSET_T',
                          'AFTER_X', 'AFTER_Y', 'AFTER_T',
                          'PPA', 'PPA_BEFORE']].sort_values('EVENTTIME')

                    optimize_result = r5.to_html(index=False)

                info = 'This is an optimize'
            else:
                info = 'Something is wrong!'

        request.session['glass_ids'] = glass_ids

        glass_pars = mask_id[mask_id.GLASS_ID.isin(glass_ids)].sort_values('EVENTTIME')
        glass_selected = all_glasses[all_glasses.GLASS_ID.isin(glass_ids)]

        data = {'info': info, 'form': form,
                'glass_selected': glass_selected.to_html(index=False),
                'all_glasses': all_glasses.to_html(index=False),
                'glass_pars': glass_pars.to_html(index=False),
                'optimize_result': optimize_result}

    return render(request, 'glasses.html', data)


def option(request):
    print ("init")
#    settings,alarm = GetSP(CONFIGROOT)
    settings =  GetSP(CONFIGROOT)
    form = OptionForm(settings)
    if request.method == 'POST':
        form = OptionForm(request.POST)
        if form.is_valid():
            SetSP(CONFIGROOT,form.cleaned_data)
            messages.success(request,"设置成功")
        
    return render(request, 'option.html', {"form":form})
    
    
    














































