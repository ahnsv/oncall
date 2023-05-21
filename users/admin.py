from django.contrib import admin

# Register your models here.
from .models import Profile, Team

admin.site.register(Profile)
admin.site.register(Team)
