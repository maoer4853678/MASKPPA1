from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    model = User
    extra = 3

admin.site.register(User)