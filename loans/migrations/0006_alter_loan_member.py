# Generated by Django 4.0.1 on 2022-03-01 11:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
        ('loans', '0005_remove_loanrepayment_amount_loan_repayment_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='member',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.DO_NOTHING, to='members.member'),
        ),
    ]
