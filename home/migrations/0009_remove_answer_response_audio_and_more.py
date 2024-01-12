# Generated by Django 4.1 on 2023-12-11 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_remove_answer_questionnaire'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answer',
            name='response_audio',
        ),
        migrations.RemoveField(
            model_name='answer',
            name='response_video',
        ),
        migrations.AddField(
            model_name='answer',
            name='response_file',
            field=models.FileField(blank=True, null=True, upload_to='answer_file/'),
        ),
    ]
