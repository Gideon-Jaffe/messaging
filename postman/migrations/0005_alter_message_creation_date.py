# Generated by Django 4.0.5 on 2022-06-10 08:35

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('postman', '0004_message_read'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='creation_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='date sent'),
        ),
    ]
