from django import forms
import configparser
import os

CONFIGROOT = './muradefect/static/conf'

def GetSP(CONFIGROOT):
    ## 数据筛选的主要属性 和 数据库连接信息
    config=configparser.ConfigParser()
    config.read(os.path.join(CONFIGROOT,'conf.ini'))
    settings = dict(config['settings'].items())
    return settings

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
    th1 = forms.FloatField(label = "管控限1")
    th2 = forms.FloatField(label = "管控限2")
    ppa_x  = forms.FloatField(label = "PPAX报警上限")
    ppa_y  = forms.FloatField(label = "PPAY报警上限")
    offset_x  = forms.FloatField(label = "OFFSETX报警上限")
    offset_y  = forms.FloatField(label = "OFFSETY报警上限")
    offset_tht = forms.FloatField(label = "OFFSETTHETA报警上限")
    
    def __init__(self,settings):
        super(OptionForm,self).__init__(settings)
        for i in ['th1',"th2","ppa_x","ppa_y","offset_x","offset_y","offset_tht"]:
            self.fields[i].initial = float(settings[i])
            self.fields[i].widget.attrs.update({'class': 'form-control'})
        
    