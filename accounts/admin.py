from django.contrib import admin

from accounts.models import Role,Permission, Profile

# Register your models here.
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(Profile)


