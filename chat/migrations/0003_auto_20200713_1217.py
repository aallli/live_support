# Generated by Django 3.0.7 on 2020-07-13 12:17

import datetime
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('authtoken', '0002_auto_20160226_1747'),
        ('chat', '0002_auto_20200706_1459'),
    ]

    operations = [
        migrations.CreateModel(
            name='System',
            fields=[
                ('token_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='authtoken.Token')),
                ('name', models.CharField(max_length=500, verbose_name='Name')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'verbose_name': 'System',
                'verbose_name_plural': 'Systems',
                'ordering': ['name'],
            },
            bases=('authtoken.token',),
        ),
        migrations.AlterField(
            model_name='operator',
            name='status',
            field=models.CharField(choices=[('ready', 'Ready'), ('busy', 'Busy'), ('off', 'Off')], default='off', max_length=10, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='session',
            name='request_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 7, 13, 12, 17, 35, 916348), null=True, verbose_name='Request Date'),
        ),
        migrations.AlterField(
            model_name='session',
            name='room_uuid',
            field=models.UUIDField(default=uuid.UUID('99f8e08d-6909-4bfa-842a-2bf83b2e13e7'), unique=True, verbose_name='Room UUID'),
        ),
    ]
