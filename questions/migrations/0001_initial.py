# Generated by Django 3.2.2 on 2022-09-13 02:03

from django.db import migrations, models
import questions.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=250)),
                ('right_answer', models.CharField(default='default', max_length=150)),
                ('answer_01', models.CharField(default='default', max_length=150)),
                ('answer_02', models.CharField(default='default', max_length=150)),
                ('answer_03', models.CharField(default='default', max_length=150)),
                ('answer_04', models.CharField(default='default', max_length=150)),
                ('difficulty_level', models.CharField(choices=[('NB', 'новичок'), ('AV', 'середнячок'), ('SP', 'умник')], db_index=True, default='NB', max_length=2, verbose_name='уровень')),
                ('available', models.BooleanField(db_index=True, default=False)),
                ('tag', models.CharField(default='IT', max_length=250)),
                ('image_01', models.ImageField(blank=True, upload_to=questions.models.question_image_path)),
                ('image_02', models.ImageField(blank=True, upload_to=questions.models.question_image_path)),
                ('image_03', models.ImageField(blank=True, upload_to=questions.models.question_image_path)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField(blank=True)),
                ('image', models.ImageField(blank=True, upload_to=questions.models.category_image_path)),
                ('available', models.BooleanField(db_index=True, default=True)),
            ],
        ),
    ]
