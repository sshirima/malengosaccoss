# Generated by Django 4.0.1 on 2022-03-30 17:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0003_alter_banktransaction_created_by_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='banktransaction',
            options={'ordering': ['-date_trans']},
        ),
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ['-reference__date_trans']},
        ),
    ]
