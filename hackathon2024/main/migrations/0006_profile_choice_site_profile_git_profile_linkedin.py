# Generated by Django 4.2.16 on 2024-10-20 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_projectpost_categories_projectpost_description_long_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='choice_site',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='git',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='linkedin',
            field=models.URLField(blank=True),
        ),
    ]
