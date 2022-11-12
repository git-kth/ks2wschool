# Generated by Django 4.1.3 on 2022-11-04 17:13

import account.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('nickname', models.CharField(max_length=24)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=16)),
                ('birth_date', models.DateField()),
                ('short_info', models.TextField(blank=True, max_length=128, null=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to=account.models.User.date_uuid_upload_to)),
            ],
            options={
                'db_table': 'user',
            },
        ),
    ]