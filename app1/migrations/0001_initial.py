# Generated by Django 5.1 on 2024-08-28 08:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_no', models.CharField(editable=False, max_length=100, unique=True)),
                ('user_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('dprt', models.CharField(max_length=100)),
                ('post', models.CharField(max_length=100)),
                ('env', models.CharField(max_length=100)),
                ('pc_name', models.CharField(editable=False, max_length=100)),
                ('pc_ip', models.GenericIPAddressField()),
                ('hw_sn', models.CharField(max_length=100)),
                ('spa_no', models.CharField(max_length=100)),
                ('report_type', models.CharField(default='Default Value', max_length=100)),
                ('hw_type', models.CharField(max_length=100)),
                ('hw_type_encode', models.CharField(max_length=100)),
                ('hw_model', models.CharField(max_length=100)),
                ('apps_sw', models.CharField(blank=True, max_length=255, null=True)),
                ('report_desc', models.TextField()),
                ('act_taken', models.TextField()),
                ('act_stat', models.CharField(max_length=100)),
                ('date_created', models.DateField(editable=False)),
                ('time_created', models.TimeField(editable=False)),
                ('date_action', models.DateField(blank=True, null=True)),
                ('time_action', models.TimeField(blank=True, null=True)),
                ('taken_by', models.CharField(max_length=100)),
                ('ftr_act', models.TextField(blank=True, null=True)),
                ('fu_act', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('user', 'User'), ('tech_support', 'Tech Support')], default='user', max_length=20)),
                ('dprt', models.CharField(max_length=100)),
                ('post', models.CharField(max_length=100)),
                ('env', models.CharField(max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
