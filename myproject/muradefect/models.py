from django.db import models

## 用户注册表
class User(models.Model):
    '''用户表'''
    name = models.CharField(max_length=128,unique=True)
    password = models.CharField(max_length=256)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
 
    class Meta:
        db_table = 'users'
        ordering = ['c_time']
        verbose_name = 'user'