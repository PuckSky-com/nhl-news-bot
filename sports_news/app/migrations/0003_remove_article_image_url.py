# Generated by Django 5.1.6 on 2025-02-07 17:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_article_image_url_alter_article_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='image_url',
        ),
    ]
