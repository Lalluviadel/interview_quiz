# Generated by Django 3.2.2 on 2022-03-26 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0005_alter_question_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='available',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='question',
            name='difficulty_level',
            field=models.CharField(choices=[('NB', 'новичок'), ('AV', 'середнячок'), ('SP', 'умник')], db_index=True, default='NB', max_length=2, verbose_name='уровень'),
        ),
        migrations.AlterField(
            model_name='questioncategory',
            name='available',
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]