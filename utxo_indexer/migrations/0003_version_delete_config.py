# Generated by Django 5.1.1 on 2025-01-20 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utxo_indexer', '0002_config'),
    ]

    operations = [
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('node_version', models.CharField(max_length=256)),
                ('git_tag', models.CharField(max_length=256)),
                ('git_hash', models.CharField(max_length=40)),
                ('build_date', models.PositiveIntegerField()),
                ('num_confirmations', models.PositiveIntegerField()),
                ('history_seconds', models.PositiveIntegerField()),
            ],
        ),
        migrations.DeleteModel(
            name='Config',
        ),
    ]
