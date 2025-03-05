# Generated by Django 5.1.6 on 2025-03-05 06:37

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True, validators=[django.core.validators.EmailValidator()])),
                ('phone', models.CharField(max_length=50, validators=[django.core.validators.RegexValidator(message='Invalid phone number', regex='^\\+?[\\d\\-x\\.()]+$')])),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('project_id', models.AutoField(primary_key=True, serialize=False)),
                ('building_type', models.CharField(choices=[('Residential', 'Residential'), ('Commercial', 'Commercial'), ('Industrial', 'Industrial')], max_length=50)),
                ('address', models.CharField(max_length=255)),
                ('job_type', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('area_size_sqft', models.FloatField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('total_gain', models.FloatField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='pending', max_length=20)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='api.client')),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('wage', models.FloatField()),
                ('hours_worked', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='PDFDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='pdfs/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'csv'])])),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('processed', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='Cost',
            fields=[
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='api.project')),
                ('body_paint_cost', models.FloatField(default=0.0)),
                ('trim_paint_cost', models.FloatField(default=0.0)),
                ('other_paint_cost', models.FloatField(default=0.0)),
                ('supplies_cost', models.FloatField(default=0.0)),
                ('additional_service_cost', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='AdditionalService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_name', models.CharField(max_length=100)),
                ('service_cost', models.FloatField()),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='api.project')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectEmployee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hours_worked', models.IntegerField()),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.employee')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.project')),
            ],
        ),
    ]
