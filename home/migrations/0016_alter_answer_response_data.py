# Generated by Django 5.0 on 2024-01-11 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0015_remove_answer_response_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='response_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
