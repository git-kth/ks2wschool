from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import User
# Register your models here.

USER_INFO = ['email', 'password1', 'password2', 'nickname', 'name', 'birth_date', 'is_admin', 'is_active']

class MyUserAdmin(UserAdmin):
    list_display = ['email', 'nickname', 'created_at', 'last_login', 'is_admin', 'is_active']
    search_fields = ('email', 'nickname',)
    # readonly_fields = ('last_login', 'password', 'nickname', 'name', 'created_at', 'birth_date', 'short_info', 'profile_image')
    readonly_fields = ()

    ordering = ["email",]
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': USER_INFO,}),)

admin.site.register(User, MyUserAdmin)