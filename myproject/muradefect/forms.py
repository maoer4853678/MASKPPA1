from django import forms
import configparser
import os
from .usercore import *

class AddForm(forms.Form):
    exp_label = forms.IntegerField()
    prd_label = forms.IntegerField()
    grp_label = forms.IntegerField()
    recipe = forms.ChoiceField(choices=(('AL', 'AL'), ('KPQ', 'KPQ')))


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()
    
    
class RegisterForm(forms.Form):
    username = forms.CharField(label='注册用户名', max_length=100)
    password1 = forms.CharField(label='设置密码', widget=forms.PasswordInput())
    password2 = forms.CharField(label='确认密码', widget=forms.PasswordInput())
#    email = forms.EmailField(label='电子邮件')

class GlassForm(forms.Form):
    glasses = forms.CharField(required=False)


class GlassPlotForm(forms.Form):
    glasses = forms.CharField()
    chamber = forms.ChoiceField(choices=(('B', 'B'), ('G\'', 'G\''), ('G', 'G'),
                                         ('R\'', 'R\''), ('R', 'R')))

class OptionForm(forms.Form):
    ## 若初始值 需要从配置文件读取，需要重写 init
    ppa_x  = forms.FloatField(label = "PPAX报警上限")
    ppa_y  = forms.FloatField(label = "PPAY报警上限")
    offset_delta_x  = forms.FloatField(label = "OFFSETX报警上限")
    offset_delta_y  = forms.FloatField(label = "OFFSETY报警上限")
    offset_delta_tht = forms.FloatField(label = "OFFSETTHETA报警上限")
    opsnumber = forms.IntegerField(label = "最低优化GLASS数")
    offsetth  = forms.FloatField(label = "最低优化阈值")
    email = forms.EmailField(label = "报警邮箱设置")
    
    def __init__(self,settings):
        super(OptionForm,self).__init__(settings)
        for i in ["ppa_x","ppa_y","offset_delta_x","offset_delta_y",\
                  "offset_delta_tht","opsnumber","offsetth"]:
            self.fields[i].initial = float(settings[i])
            self.fields[i].widget.attrs.update({'class': 'form-control'})
        self.fields["email"].initial = settings["email"]
        self.fields["email"].widget.attrs.update({'class': 'form-control'})
        self.fields["email"].widget.attrs.update({'style': 'width : 270px'})
  
    
class XOptionForm(forms.Form):
    ## 若初始值 需要从配置文件读取，需要重写 init
    xth2 = forms.FloatField(label = "X方向管控限2")
    xth1 = forms.FloatField(label = "X方向管控限1")
    
    def __init__(self,settings):
        super(XOptionForm,self).__init__(settings)
        for i in ['xth1',"xth2"]:
            self.fields[i].initial = float(settings[i])
            self.fields[i].widget.attrs.update({'class': 'form-control'})   
    
class YOptionForm(forms.Form):
    ## 若初始值 需要从配置文件读取，需要重写 init
    yth2 = forms.FloatField(label = "Y方向管控限2")
    yth1 = forms.FloatField(label = "Y方向管控限1")
    
    
    def __init__(self,settings):
        super(YOptionForm,self).__init__(settings)
        for i in ['yth1',"yth2"]:
            self.fields[i].initial = float(settings[i])
            self.fields[i].widget.attrs.update({'class': 'form-control'})   

    
    
    
    
    