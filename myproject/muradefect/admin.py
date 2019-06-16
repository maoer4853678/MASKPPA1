from django.contrib import admin
from .models import People, Article


admin.site.site_title = 'MyDjango backend'
admin.site.site_header = 'MyDjango'


# Register your models here.
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'update_time',)


@admin.register(People)
class PeopleAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'age', 'company', 'description')
