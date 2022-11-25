from django.contrib import admin
from blog import models
from django_summernote.admin import SummernoteModelAdmin
# Register your models here.

class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
admin.site.register(models.Post,PostAdmin)
admin.site.register(models.Comment)
admin.site.register(models.Reply)
admin.site.register(models.Category)
