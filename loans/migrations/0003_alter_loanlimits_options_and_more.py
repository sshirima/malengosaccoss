# Generated by Django 4.0.1 on 2022-02-24 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0002_alter_loan_options_alter_loan_id_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='loanlimits',
            options={'verbose_name': 'LoanLimits', 'verbose_name_plural': 'Loan Limits'},
        ),
        migrations.RenameField(
            model_name='loanlimits',
            old_name='duration_limit',
            new_name='max_duration',
        ),
        migrations.RenameField(
            model_name='loanlimits',
            old_name='principle_limit',
            new_name='max_principle',
        ),
        migrations.AddField(
            model_name='loanlimits',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='inactive', max_length=20),
        ),
    ]
