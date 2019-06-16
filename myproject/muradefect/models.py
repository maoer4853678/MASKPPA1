# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

##### 新表
class EvaAll(models.Model):
    product_id = models.TextField(db_column='PRODUCT_ID', blank=True, null=True)  
    event_time = models.DateTimeField(db_column='EVENT_TIME', blank=True, null=True)  
    glass_id = models.TextField(db_column='GLASS_ID', blank=True, null=True)  
    eva_chamber = models.TextField(db_column='EVA_CHAMBER', blank=True, null=True)  
    mask_id = models.TextField(db_column='MASK_ID', blank=True, null=True)  
    mask_set = models.TextField(db_column='MASK_SET', blank=True, null=True)  
    port = models.TextField(db_column='PORT', blank=True, null=True)  
    line = models.BigIntegerField(db_column='LINE', blank=True, null=True)  
    pos_x = models.FloatField(db_column='POS_X', blank=True, null=True)  
    pos_y = models.FloatField(db_column='POS_Y', blank=True, null=True)  
    x_label = models.BigIntegerField(db_column='X_LABEL', blank=True, null=True)  
    y_label = models.BigIntegerField(db_column='Y_LABEL', blank=True, null=True)  
    ppa_x = models.FloatField(db_column='PPA_X', blank=True, null=True)  
    ppa_y = models.FloatField(db_column='PPA_Y', blank=True, null=True)  
    offset_x = models.FloatField(db_column='OFFSET_X', blank=True, null=True)  
    offset_y = models.FloatField(db_column='	OFFSET_Y', blank=True, null=True)  
    offset_tht = models.FloatField(db_column='OFFSET_THT', blank=True, null=True)  
    
    class Meta:
        db_table = 'EVA_ALL'


class Offset(models.Model):
    timekey = models.TextField(db_column='TIMEKEY', blank=True, null=True)  
    maskname = models.TextField(db_column='MASKNAME', blank=True, null=True)  
    chambername = models.TextField(db_column='CHAMBERNAME', blank=True, null=True) 
    linetype = models.TextField(db_column='LINETYPE', blank=True, null=True)  
    evaoffsetx = models.TextField(db_column='EVAOFFSETX', blank=True, null=True)  
    evaoffsety = models.TextField(db_column='EVAOFFSETY', blank=True, null=True)  
    evaoffsettheta = models.TextField(db_column='EVAOFFSETTHETA', blank=True, null=True)  
    ifflag = models.TextField(db_column='IFFLAG', blank=True, null=True)  
    result = models.TextField(db_column='RESULT', blank=True, null=True)  
    resultmessage = models.TextField(db_column='RESULTMESSAGE', blank=True, null=True)  
    eventuser = models.TextField(db_column='EVENTUSER', blank=True, null=True)  
    product_id = models.TextField(db_column='PRODUCT_ID', blank=True, null=True)  
    
    class Meta:
        db_table = 'OFFSET'

class Alarm(models.Model):
    product_id = models.TextField(db_column='PRODUCT_ID', blank=True, null=True)  
    event_time = models.DateTimeField(db_column='EVENT_TIME', blank=True, null=True)  
    glass_id = models.TextField(db_column='GLASS_ID', blank=True, null=True)  
    eva_chamber = models.TextField(db_column='EVA_CHAMBER', blank=True, null=True)  
    mask_id = models.TextField(db_column='MASK_ID', blank=True, null=True)  
    mask_set = models.TextField(db_column='MASK_SET', blank=True, null=True)  
    port = models.TextField(db_column='PORT', blank=True, null=True)  
    line = models.BigIntegerField(db_column='LINE', blank=True, null=True)  
    key = models.TextField(db_column='KEY', blank=True, null=True)  
    value = models.FloatField(db_column='VALUE', blank=True, null=True)  
    
    class Meta:
        db_table = 'ALARM'


class PpaSummary(models.Model):
    product_id = models.TextField(db_column='PRODUCT_ID', blank=True, null=True)  
    event_time = models.DateTimeField(db_column='EVENT_TIME', blank=True, null=True)  
    glass_id = models.TextField(db_column='GLASS_ID', blank=True, null=True)  
    eva_chamber = models.TextField(db_column='EVA_CHAMBER', blank=True, null=True)  
    mask_id = models.TextField(db_column='MASK_ID', blank=True, null=True)  
    mask_set = models.TextField(db_column='MASK_SET', blank=True, null=True)  
    port = models.TextField(db_column='PORT', blank=True, null=True)  
    line = models.BigIntegerField(db_column='LINE', blank=True, null=True)  
    ratiotype = models.TextField(db_column='RATIOTYPE', blank=True, null=True)  
    ratiovalue = models.FloatField(db_column='RATIOVALUE', blank=True, null=True)   
    ppaxmax = models.FloatField(db_column='PPA_XMAX', blank=True, null=True) 
    ppaxmin = models.FloatField(db_column='PPA_XMIN', blank=True, null=True) 
    ppaymax = models.FloatField(db_column='PPA_YMAX', blank=True, null=True) 
    ppaymin = models.FloatField(db_column='PPA_YMIN', blank=True, null=True) 
  
    class Meta:
        db_table = 'PPASUMMARY'

##### 原始表
class EvaPpa(models.Model):
    lot_id = models.TextField(db_column='LOT_ID', blank=True, null=True)  
    glass_id = models.TextField(db_column='GLASS_ID', blank=True, null=True)  
    recipe = models.TextField(db_column='RECIPE', blank=True, null=True)  
    glass_start_time = models.DateTimeField(db_column='GLASS_START_TIME', blank=True, null=True)  
    glass_end_time = models.DateTimeField(db_column='GLASS_END_TIME', blank=True, null=True)  
    eva_chamber = models.TextField(db_column='EVA_CHAMBER', blank=True, null=True)  
    point_no = models.BigIntegerField(db_column='POINT_NO', blank=True, null=True)  
    pos_x = models.FloatField(db_column='POS_X', blank=True, null=True)  
    pos_y = models.FloatField(db_column='POS_Y', blank=True, null=True)  
    ppa_x = models.FloatField(db_column='PPA_X', blank=True, null=True)  
    ppa_y = models.FloatField(db_column='PPA_Y', blank=True, null=True)  

    class Meta:
        db_table = 'EVA_PPA'


class MaskId(models.Model):
    recipe = models.TextField(db_column='RECIPE', blank=True, null=True)  
    glass_id = models.TextField(db_column='GLASS_ID', blank=True, null=True)  
    grp_label = models.BigIntegerField(blank=True, null=True)
    eventtime = models.DateTimeField(db_column='EVENTTIME', blank=True, null=True)  
    mask_id = models.TextField(db_column='MASK_ID', blank=True, null=True)  
    x = models.TextField(db_column='X', blank=True, null=True)  
    y = models.TextField(db_column='Y', blank=True, null=True)  
    t = models.TextField(db_column='T', blank=True, null=True)  
    eva_chamber = models.TextField(db_column='EVA_CHAMBER', blank=True, null=True)  
    line = models.TextField(blank=True, null=True)
    exp_label = models.BigIntegerField(blank=True, null=True)
    prd_label = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'MASK_ID'


class Mvi(models.Model):
    recipe = models.TextField(db_column='RECIPE', blank=True, null=True)  
    panel_id = models.TextField(db_column='PANEL_ID', blank=True, null=True)  
    glass_id = models.TextField(db_column='GLASS_ID', blank=True, null=True)  
    lastloggedintime = models.DateTimeField(db_column='LASTLOGGEDINTIME', blank=True, null=True)  
    lastloggedouttime = models.DateTimeField(db_column='LASTLOGGEDOUTTIME', blank=True, null=True)  
    dmem0 = models.FloatField(db_column='DMEM0', blank=True, null=True)  
    dmem1 = models.FloatField(db_column='DMEM1', blank=True, null=True)  
    dmem5 = models.FloatField(db_column='DMEM5', blank=True, null=True)  
    loc_y = models.TextField(db_column='LOC_Y', blank=True, null=True)  
    loc_x = models.TextField(db_column='LOC_X', blank=True, null=True)  
    pos_x = models.FloatField(db_column='POS_X', blank=True, null=True)  
    pos_y = models.FloatField(db_column='POS_Y', blank=True, null=True)  

    class Meta:
        db_table = 'MVI'


class People(models.Model):
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    age = models.IntegerField(db_column='age', blank=True, null=True)
    company = models.CharField(db_column='company', max_length=50, blank=True, null=True)
    description = models.TextField(db_column='description', max_length=256, blank=True, null=True)

    def my_property(self):
        return str(self.first_name) + ' ' + str(self.last_name)

    my_property.short_description = "Full name of the person"

    full_name = property(my_property)

    def __str__(self):
        return self.full_name


class Article(models.Model):
    title = models.CharField(u'title', max_length=256)
    content = models.TextField(u'context')

    pub_date = models.DateTimeField(u'time_publish', auto_now_add=True, editable=True)
    update_time = models.DateTimeField(u'time_update', auto_now=True, null=True)

    def __str__(self):  # in Python2, use __unicode__ instead of __str__
        return self.title

