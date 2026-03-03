# Generated manually (matches models.py additions)

from django.db import migrations, models
import django.db.models.deletion
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.CharField(default=main.models.generate_experiment_id, editable=False, max_length=32, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('ready', 'Ready'), ('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed')], default='draft', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiments', to='main.user')),
            ],
            options={
                'db_table': 'experiments',
            },
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.CharField(default=main.models.generate_building_id, editable=False, max_length=32, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('country', models.CharField(max_length=2)),
                ('region', models.CharField(blank=True, default='', max_length=120)),
                ('year_of_construction', models.PositiveIntegerField()),
                ('floor_area', models.DecimalField(decimal_places=2, max_digits=12)),
                ('eem_capex', models.DecimalField(decimal_places=2, max_digits=14)),
                ('eem_energy_savings', models.DecimalField(decimal_places=4, max_digits=7)),
                ('eem_maintenance_cost', models.DecimalField(decimal_places=2, max_digits=14)),
                ('eem_lifetime', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buildings', to='main.experiment')),
            ],
            options={
                'db_table': 'buildings',
            },
        ),
        migrations.AddIndex(
            model_name='experiment',
            index=models.Index(fields=['user', '-created_at'], name='experiments_user_id_0c3b3f_idx'),
        ),
        migrations.AddIndex(
            model_name='experiment',
            index=models.Index(fields=['user', 'status'], name='experiments_user_id_3f6b77_idx'),
        ),
        migrations.AddIndex(
            model_name='building',
            index=models.Index(fields=['experiment', '-created_at'], name='buildings_experiment_id_7c0f12_idx'),
        ),
    ]