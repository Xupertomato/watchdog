# Generated by Django 4.1 on 2023-12-05 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_alter_question_questionnaire'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='multimedia_content',
        ),
        migrations.AddField(
            model_name='question',
            name='media_content',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_type',
            field=models.CharField(choices=[('text', 'Text'), ('media', 'Media')], default='text', max_length=10),
        ),
    ]
