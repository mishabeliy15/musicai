# Generated by Django 4.0.4 on 2022-06-19 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0026_instrument_font_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='aiorder',
            name='accepted',
            field=models.BooleanField(default=False, max_length=200),
        ),
    ]
