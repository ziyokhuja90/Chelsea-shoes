from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(references)
admin.site.register(clients)
admin.site.register(staff)
admin.site.register(producement)