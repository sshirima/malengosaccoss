# Generated by Django 4.0.1 on 2022-01-31 15:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BankTransaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.FloatField()),
                ('description', models.CharField(max_length=255, null=True)),
                ('instrument_id', models.CharField(blank=True, max_length=30, null=True)),
                ('balance', models.FloatField()),
                ('type', models.CharField(choices=[('debit', 'DEBIT'), ('credit', 'CREDIT')], max_length=20)),
                ('status', models.CharField(choices=[('imported', 'IMPORTED'), ('assigned', 'ASSIGNED'), ('cancelled', 'CANCELLED')], max_length=20)),
                ('date_trans', models.DateField()),
                ('date_value', models.DateField()),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date_created'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.FloatField()),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('type', models.CharField(blank=True, choices=[('debit', 'DEBIT'), ('credit', 'CREDIT')], max_length=20, null=True)),
                ('status', models.CharField(choices=[('pending', 'PENDING'), ('approved', 'APPROVED'), ('cancelled', 'CANCELLED')], default='pending', max_length=20)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('reference', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='transactions.banktransaction')),
            ],
            options={
                'ordering': ['-date_created'],
            },
        ),
    ]
