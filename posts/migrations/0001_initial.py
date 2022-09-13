# Generated by Django 3.2.2 on 2022-09-13 02:03

from django.db import migrations, models
import posts.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('body', models.TextField()),
                ('image', models.ImageField(blank=True, upload_to=posts.models.post_image_path)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('available', models.BooleanField(default=False)),
                ('tag', models.CharField(db_index=True, default='IT', max_length=250)),
            ],
        ),
    ]
