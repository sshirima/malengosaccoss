# Generated by Django 4.0.1 on 2022-06-17 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0006_alter_banktransaction_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='banktransaction',
            name='filename',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
