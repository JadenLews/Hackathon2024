# Generated by Django 4.2.16 on 2024-10-20 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_profile_skills'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectpost',
            name='categories',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='projectpost',
            name='description_long',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='projectpost',
            name='description',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='projectpost',
            name='skills',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='projectpost',
            name='workersneeded',
            field=models.IntegerField(default=2),
        ),
    ]
