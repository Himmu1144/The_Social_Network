# Generated by Django 4.1.4 on 2023-01-01 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_alter_account_hide_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='hide_email',
            field=models.BooleanField(default=True),
        ),
    ]
