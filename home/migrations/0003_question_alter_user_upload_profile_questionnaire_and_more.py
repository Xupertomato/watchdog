# Generated by Django 4.1 on 2023-11-28 06:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import home.models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_alter_elderrecord_taggedelder_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('question_type', models.CharField(choices=[('text', 'Text'), ('audio', 'Audio'), ('video', 'Video')], default='text', max_length=10)),
                ('multimedia_content', models.FileField(blank=True, null=True, upload_to='question_multimedia/')),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='upload_profile',
            field=models.FileField(blank=True, default=None, null=True, storage=home.models.OverwriteStorage(), upload_to=home.models.upload_profile),
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('assigned_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('deadline', models.DateTimeField()),
                ('assigned_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_questionnaires', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response_text', models.TextField(blank=True, null=True)),
                ('response_audio', models.FileField(blank=True, null=True, upload_to='answer_audio/')),
                ('response_video', models.FileField(blank=True, null=True, upload_to='answer_video/')),
                ('submitted_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='home.question')),
                ('questionnaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='home.questionnaire')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]