# Generated by Django 3.2.9 on 2022-02-12 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20220212_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='activation_key_created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
