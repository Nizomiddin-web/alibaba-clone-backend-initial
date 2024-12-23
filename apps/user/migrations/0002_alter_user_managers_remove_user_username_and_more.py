# Generated by Django 4.2.14 on 2024-10-25 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
        migrations.AddField(
            model_name='buyeruser',
            name='bio',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='buyeruser',
            name='company',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='Email Address'),
        ),
    ]
