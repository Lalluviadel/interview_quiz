# Generated by Django 3.2.2 on 2022-09-13 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_myuser_social_network'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='social_network',
            field=models.BooleanField(default=False),
        ),
    ]
