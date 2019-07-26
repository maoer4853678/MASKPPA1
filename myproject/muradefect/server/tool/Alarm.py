import pandas as pd
import itertools,os
import numpy as np
import json
from .myemail import *
import datetime
import matplotlib.pyplot as plt
plt.switch_backend('agg')

IMAGE = './image'

def Send(title = '',content='',images = [],recv = [],file=None):
    m = SendMail(username='evappa@visionox.com',
                 passwd='Visionox@2019',
                 email_host = 'smtp.263.net',
                 recv= recv,
                 title = title,
                 content = content,
                 images = images,
                 file= file,
                 ssl=True)
    
#    username='edong_2019@163.com',passwd='v123456789',email_host = 'smtp.163.com'
    
    msg = m.send_mail()
    return msg

def PlotPpa(p2,key = 'ppa_x' ,ops = {},filename=None,weightx = 3.1,weighty = 8.1):
    th1 = min([ops['xth1'],ops['yth1']])    
    th2 = min([ops['xth2'],ops['yth2']])
    filename = os.path.join(IMAGE,filename)
    glass_id = p2.glass_id.iloc[0]
    eva_chamber = p2.eva_chamber.iloc[0]
    mask_id = p2.mask_id.iloc[0]
    plt.figure(figsize=(15,6)) 
    p2 = p2.sort_values(['x_label','y_label','pos_x','pos_y'])
    if key == 'ppa_x':
        for i in p2.x_label.unique():
            p3 = p2[p2.x_label==i]
            ## 绘制管控线
            plt.plot(p3.pos_x,p3.pos_y,"k--")  ## 理论中心点 黑线
            plt.plot(p3.pos_x-th1*weightx,p3.pos_y,"g--")  ## th1左边 绿线
            plt.plot(p3.pos_x+th1*weightx,p3.pos_y,"g--")  ## th1右边 绿线
            plt.plot(p3.pos_x-th2*weightx,p3.pos_y,"r--")  ## th2左边 红线
            plt.plot(p3.pos_x+th2*weightx,p3.pos_y,"r--")  ## th2右边 红线
            plt.plot(p3.pos_x + weightx * p3.ppa_x,
                     p3.pos_y + weighty * p3.ppa_y, 'ko-')
        plt.title("%s  %s  %s  X-Direction"%(glass_id,eva_chamber,mask_id))
    else:
        for i in p2.y_label.unique():
            p3 = p2[p2.y_label==i]
            ## 绘制管控线
            plt.plot(p3.pos_x,p3.pos_y,"k--")  ## 理论中心点 黑线
            plt.plot(p3.pos_x,p3.pos_y-th1*weighty,"g--")  ## th1左边 绿线
            plt.plot(p3.pos_x,p3.pos_y+th1*weighty,"g--")  ## th1右边 绿线
            plt.plot(p3.pos_x,p3.pos_y-th2*weighty,"r--")  ## th2左边 红线
            plt.plot(p3.pos_x,p3.pos_y+th2*weighty,"r--")  ## th2右边 红线
            plt.plot(p3.pos_x + weightx * p3.ppa_x,
                     p3.pos_y + weighty * p3.ppa_y, 'ko-')
        plt.title("%s  %s  %s  Y-Direction"%(glass_id,eva_chamber,mask_id))    
    plt.savefig(filename)
    plt.close()
    return filename

def ppa_table(p2,ops,alarm='ppa_x'):
    send_str = '''
    <table border="1">
    <tr>
    <th colspan="4"> X方向 </th>
    <th colspan="4"> Y方向 </th>
    </tr>
    '''
    for i in range(3):
        send_str +='<tr>'
        for key in ['ppa_x','ppa_y']:
            th1 = ops[key[-1]+"th1"]
            th2 = ops[key[-1]+"th2"]
            len1 = len(p2[p2[key].abs()<th1])
            len2 = len(p2[p2[key].abs()<th2])
            if i==0:
                send_str +='''
                    <td> ±%0.1fum </td>
                    <td> ±%0.1fum </td>
                    <td> 最大值 </td>
                    <td> 最小值 </td>
                    '''%(th2,th1)
            if i==1:
                send_str +='''
                    <td> %s </td>
                    <td> %s </td>
                    <td> %s </td>
                    <td> %s </td>
                    '''%(len2,len1,p2[key].max(),p2[key].min())
            if i==2:
                if alarm == key:
                    format = '''<td bgcolor="#ff3399"> %0.2f%% </td>''' %(len2/len(p2)*100)
                else:
                    format = '''<td> %0.2f%% </td>'''%(len2/len(p2)*100)
                send_str +='''
                    %s
                    <td> %0.2f%% </td>
                    <td>  </td>
                    <td>  </td>
                    '''%(format,len1/len(p2)*100)
        send_str +='</tr>'
        
    send_str+= "</table>"
    return send_str
    
def rate_email(df,messgae,ops,email,title = 'PPA占比超限',content=''):
    messgae = messgae.sort_values(['glass_id', 'eva_chamber'])
    messgae.index = range(len(messgae))
    images = []
    n=0
    for index,messgae1 in messgae.groupby(['glass_id', 'mask_id']):
        p2 = pd.merge(df,messgae1[['glass_id', 'mask_id']].drop_duplicates(),\
                      on = ['glass_id', 'mask_id'])
        for index1 in messgae1.index:
            image = {}
            glass_id = p2.glass_id.iloc[0]
            eva_chamber = p2.eva_chamber.iloc[0]
            mask_id = p2.mask_id.iloc[0]
            key = messgae1.loc[index1,'key'].lower()
            value = messgae1.loc[index1,'value']
            boffset = "(%s)"%(str(",".join(p2[['offset_x', 'offset_y', 'offset_tht']].\
                       iloc[0].astype(str).values)))
            table = ppa_table(p2,ops,key)
            vcontent = '''
            glass ID :  %s<br>
            mask ID :  %s<br>
            蒸镀腔室 :  %s<br>
            offset  :  %s<br>
            当前报警占比设置值 : %s%% <br>
            %s   <br>
            ''' % (glass_id,mask_id,eva_chamber,boffset,value,table)
   
            image['content'] = vcontent
            filename = PlotPpa(p2,key = key ,ops = ops,filename="%s.png"%(n),\
                            weightx = 3.1,weighty = 8.1)
            image['file'] =filename
            images.append(image)
            n+=1
    msg = Send(title = title ,content=content,images = images,recv = email)
    print ("rate_email",msg)


def offset_email(detail_df,messgae,ops,email,title = 'offset调整过大'):
    messgae = messgae.sort_values(['glass_id', 'eva_chamber'])
    messgae.index = range(len(messgae))
    images = []
    n=0
    for index in messgae.index:
        p2 = pd.merge(detail_df,messgae.loc[[index],\
                ['eva_chamber', 'mask_id']],on = ['eva_chamber', 'mask_id'])
        glass_id = ",".join(p2['glass_id'].unique())
        eva_chamber = messgae.loc[index,'eva_chamber']
        mask_id = messgae.loc[index,'mask_id']
        boffset = messgae.loc[index,'boffset']
        aoffset = messgae.loc[index,'aoffset']
        content = '''
        glass ID :  %s<br>
        mask ID :  %s<br>
        蒸镀腔室 :  %s<br>
        调整前offset  :  %s<br>
        调整后offset  :  %s<br><br>
        ''' % (glass_id,mask_id,eva_chamber,boffset,aoffset)
        start = True
        for _,p3 in p2.groupby("glass_id"):
            print ("Glassid: ",p3.glass_id.iloc[0],p3.shape)
            vcontent = ppa_table(p3,ops,'')+"<br>"
            for key in ['ppa_x','ppa_y']:
                image = {}
                if key =='ppa_x':
                    image['content'] = vcontent
                    if start:
                        image['content'] = content+image['content']
                        start=False
                else:
                    image['content'] = ''
                filename = PlotPpa(p3,key = key ,ops = ops,filename="%s.png"%(n),\
                                weightx = 3.1,weighty = 8.1)
                image['file'] =filename
                images.append(image)
                n+=1
    msg = Send(title = title ,content=content,images = images,recv = email)
    print ("offset_email",msg)
  
def Alarmmap(df,conn,threshold ={},ops = {},exclude =[],\
             emailflag =True, emailist = [],offset =[]): 
    alarmflag = False
    columns = list((set(threshold.keys()) - set(exclude)).intersection(set(df.columns)))
    def func(g):
        rr = g[columns]
        rr.index = range(len(rr))
        res = rr.apply(lambda x:x[x.abs()>threshold[x.name]].\
          describe().loc[['count','max','min']],axis=0).T.reset_index()\
               .rename(columns ={"index":"key"})
        return res
    
    gcols = ['product_id','glass_id','mask_id','eva_chamber']
    res = df.groupby(gcols).apply(func).reset_index()
    res = res.drop("level_%d"%(len(gcols)),axis=1)
    res = res[res['count']>0]
    res['bz'] = 1
    
    if len(res):  ### 异常值触发 报警
        print('异常值触发 报警')
        alarmflag = True
        df = pd.merge(df,res[gcols+['bz']].drop_duplicates(),on = gcols,how = "left")
        error = df[~df['bz'].isnull()].drop("bz",axis=1)  ## 所有异常的 PPA数据
        
        dcols = ['glass_id','mask_id','eva_chamber','offset_x', 'offset_y', 'offset_tht']
        if "after_x" in error.columns:
            dcols = dcols+['after_x', 'after_y', 'after_t']
        
        messgae = error[dcols].drop_duplicates()
        messgae['boffset'] =messgae[['offset_x', 'offset_y', 'offset_tht']].astype(str)\
                    .apply(lambda x:"("+','.join(x)+")",axis=1)
        
        if "after_x" in error.columns:
            messgae['aoffset'] = messgae[['after_x', 'after_y', 'after_t']].astype(str)\
                    .apply(lambda x:"("+','.join(x)+")",axis=1) 
            title = 'offset调整过大'
            df = df.drop("bz",axis=1)  ## offset 优化报警 但是不删除 offset结果
        else:
            messgae['aoffset'] = ''
            title = 'PPA单点超限异常'
            df = df[df['bz'].isnull()].drop("bz",axis=1)  ##  那剔除某 PPA异常的数据，其他照常计算
         
        messgae = pd.merge(res,messgae,on = ['glass_id','mask_id','eva_chamber'])
        
        if len(offset):
            print('check$^%&*%(*&^')
            print(offset.columns)
            detail_df = pd.merge(offset,error[['mask_id','groupid','product_id']],\
                                 on=['mask_id','groupid','product_id'])
        else:
            detail_df = error
        ## detail_df 用于绘制 email 中 ppa mapping
        ### 触发邮箱报警, 并且已经过滤掉了 df中的异常数据
        
        if (len(messgae)) and emailflag:
            offset_email(detail_df,messgae,ops,email=emailist,title = title)

        
        messgae.columns =messgae.columns.str.replace("_",'').str.upper()
        messgae = messgae.rename(columns ={"EVA_CHARMBER":"CHARMBER"}).astype(str)
        messgae = messgae[['PRODUCTID','GLASSID','MASKID','EVACHAMBER',\
               'BOFFSET','AOFFSET','KEY','COUNT','MAX', 'MIN']]
        print('error messgae',messgae) ## 插入 ALARM报警的详细信息
        messgae['eventtime']=datetime.datetime.now()
        if 'alarm' not in conn.list_table():
            conn.creat_table_from_df(tablename='alarm', df=messgae)
        conn.insert_df(tablename='alarm',df=messgae)
        
            
    return alarmflag,df

def AlarmPpa(df,init={} ,ops = {},exclude=[],conn=None):
    ## 原始数据报警程序
    alarmflag = False ## 异常值报警标识
    email = init['email']
    emailflag =  email['flag']==1 and len(email['list'])!=0
    rate = init['rate']

    threshold = init['threshold']
    alarmflag,df = Alarmmap(df,conn, threshold =threshold,ops = ops,exclude = exclude,\
     emailflag= emailflag,emailist=email['list'])
    
    if not len(df):
        return alarmflag,df
    
    ths = {"ppa_x":rate['th'][0],"ppa_y":rate['th'][1]}
#    df.to_pickle('df_Alarmppa.pk')
    def func1(g):
        res = g[['ppa_x','ppa_y']].apply(lambda x:len(x[x.abs()<=ths[x.name]]),axis=0)
        res = res/len(g)*100
        return res.round(3)
    temp1=pd.DataFrame([])
    for product in rate['product']:
        temp = pd.Series(rate['product'][product]).to_frame()
        temp = temp.astype(float)
        temp.columns = ['value']
        temp['type'] = "ppa_"+temp.index.str[0]+"_th"
        temp['eva_chamber'] = "OC_"+temp.index.str[1:].str.replace("oc","")
        temp["product_id"] = product
        temp = temp.pivot_table(index = ['product_id','eva_chamber'],columns =\
              'type',values = 'value',aggfunc = 'max').reset_index()
        temp1=temp1.append(temp)
    print('temp1.head:',temp1.head(),temp1.shape,temp1.columns)     
    res1 = df.groupby(['product_id','line','eva_chamber','port','mask_set','mask_id','glass_id','eventtime']).\
            apply(func1).reset_index()
    print('res1.head:',res1.head(),res1.shape,res1.columns)   
    res1 = pd.merge(res1,temp1,on =['product_id','eva_chamber'])
    print('Alarmrate')
    print(res1[['ppa_x','ppa_y','product_id','eva_chamber']])
    temps = []
    for key in ['ppa_x','ppa_y']:
        temp = res1[res1[key]<=res1[key+"_th"]]
        temp = temp[['product_id','glass_id','mask_id','eva_chamber',key,key+"_th"]]
        temp = temp.rename(columns ={key:"value",key+"_th":"threshold"})
        temp['key'] = key.upper()
        temps.append(temp)
    messgae = pd.concat(temps)
    print('alarm message:',messgae)  ## 识别所有超过阈值的 PPA占比信息
        
    if len(messgae):
        messgae['eventtime']=datetime.datetime.now()
        if 'alarmrate' not in conn.list_table():
            conn.creat_table_from_df(tablename='alarmrate', df=messgae)
        conn.insert_df(tablename='alarmrate',df=messgae)      
        alarmflag = True        
        if emailflag:
            rate_email(df,messgae,ops,email['list'],title = 'PPA占比超限',content='PPA占比超限报警')
  
    return alarmflag,df

def check_email(checklist,email):
    send_str = '''
    <table border="1">
    <tr>
    <th> 优化时间 </th>
    <th> 腔室 </th>
    <th> Port </th>
    <th> Mask ID </th>
    <th colspan="3"> 优化前 </th>
    <th colspan="3"> offset改变量 </th>
    <th colspan="3"> 优化后 </th>
    </tr><tr>
    '''
    send_str+=''' <td>  </td>'''*4
    send_str+=''' <td>  X </td> <td>  Y </td> <td>  T </td>'''*3
    send_str+='</tr>'
    
    for i in checklist.index:
        send_str+='<tr>'
        for j in checklist.loc[i].values:
            send_str+='<td>  %s </td>'%j
        send_str+='</tr>'
    send_str+= "</table>"
    filename = os.path.join(IMAGE,"checklist.xlsx")
    checklist.columns = ['优化时间','腔室','Port','Mask ID','优化前X','优化前Y','优化前T',\
                        '改变量X','改变量Y','改变量T','优化后X','优化后Y','优化后T']
    checklist.to_excel(filename,index=False)
    msg = Send(title = '最新offset结果点检表' ,content='',images = [{"content":send_str,"file":""}],\
               recv = email['list'],file =filename)
    print ("checklist",msg)

def AlarmOffset(res,df2,init={},ops = {},exclude=[],conn=None):
    ## offset 优化结果的 异常检测和报警
    alarmflag = False ## 异常值报警标识
    threshold = init['threshold']
    email = init['email']
    emailflag =  email['flag']==1 and len(email['list'])!=0
    
    ## offset 点检表，每次做完offset优化 都需要发送的
    checklist = res[['eva_chamber','port','mask_id','offset_x',\
       'offset_y', 'offset_tht','delta_x', 'delta_y', 'delta_t',\
       'after_x', 'after_y', 'after_t']]
    times= pd.Series([datetime.datetime.now()]*len(checklist))
    checklist.insert(0,"time",times)
    checklist['time'] = checklist['time'].dt.strftime("%Y-%m-%d %H:%M:%S")
    check_email(checklist,email)

    info = df2[['product_id','groupid','cycleid','glass_id']].drop_duplicates().\
        groupby(['product_id','groupid','cycleid']).apply(lambda x:','.join(x["glass_id"])).\
        reset_index()
    info.columns = ['product_id','groupid','cycleid','glass_id']
    
    df1 = pd.merge(res,info,on = ['product_id','groupid','cycleid'])

    alarmflag,df1 = Alarmmap(df1,conn, threshold =threshold,ops = ops,exclude = exclude,\
     emailflag= emailflag,emailist=email['list'],offset = df2)

    df = df1.drop("glass_id",axis=1)
    return alarmflag,df