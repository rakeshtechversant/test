from django.contrib import admin

# Register your models here.
from apps.api.models import AdminProfile

admin.site.register(AdminProfile)
