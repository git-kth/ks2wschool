# Generated by Django 4.1.3 on 2022-11-21 04:49

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0004_alter_category_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='voter',
            field=models.ManyToManyField(related_name='voter_post', to=settings.AUTH_USER_MODEL),
        ),
    ]
