# Generated by Django 4.0.1 on 2022-05-19 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0005_remove_member_password_change'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='mobile_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]