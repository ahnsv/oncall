from django.contrib import admin

# Register your models here.
from .models import Schedule

# register Schedule to admin
admin.site.register(Schedule)
