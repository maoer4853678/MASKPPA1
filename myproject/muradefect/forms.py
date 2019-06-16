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


class GlassForm(forms.Form):
    glasses = forms.CharField(required=False)


class GlassPlotForm(forms.Form):
    glasses = forms.CharField()
    chamber = forms.ChoiceField(choices=(('B', 'B'), ('G\'', 'G\''), ('G', 'G'),
                                         ('R\'', 'R\''), ('R', 'R')))

class OptionForm(forms.Form):
    ## 若初始值 需要从配置文件读取，需要重写 init
    th1_min = forms.FloatField(label = "良品区间_下限")
    th1_max = forms.FloatField(label = "良品区间_上限")
    th2_min = forms.FloatField(label = "管控区间_上限")
    th2_max = forms.FloatField(label = "管控区间_下限")
    ppa_x  = forms.FloatField(label = "PPAX报警上限")
    ppa_y  = forms.FloatField(label = "PPAY报警上限")
    offset_x  = forms.FloatField(label = "OFFSETX报警上限")
    offset_y  = forms.FloatField(label = "OFFSETY报警上限")
    offset_tht = forms.FloatField(label = "OFFSETTHETA报警上限")
    
    def __init__(self,settings):
        super(OptionForm,self).__init__(settings)
        self.fields['th1_min'].initial = float(settings['th1_min'])
        self.fields['th1_max'].initial = float(settings['th1_max'])
        self.fields['th2_min'].initial = float(settings['th2_min'])
        self.fields['th2_max'].initial = float(settings['th2_max'])
        self.fields['ppa_x'].initial = float(settings['ppa_x'])
        self.fields['ppa_y'].initial = float(settings['ppa_y'])
        self.fields['offset_x'].initial = float(settings['offset_x'])
        self.fields['offset_y'].initial = float(settings['offset_y'])
        self.fields['offset_tht'].initial = float(settings['offset_tht'])
        
    