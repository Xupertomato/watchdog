# Generated by Django 4.1 on 2023-12-05 13:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_question_questionnaire_alter_user_birthday'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='questionnaire',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions_set', to='home.questionnaire'),
        ),
    ]
