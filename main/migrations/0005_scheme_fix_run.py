import django.db.models.deletion
import django.utils.timezone
import main.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_scheme_schemeroyaltycrowdfunding_and_more'),
    ]

    operations = [
        # Fix Scheme.id: add max_length + default generator
        migrations.AlterField(
            model_name='scheme',
            name='id',
            field=models.CharField(
                default=main.models.generate_scheme_id,
                editable=False,
                max_length=32,
                primary_key=True,
                serialize=False,
            ),
        ),
        # Add updated_at to Scheme
        migrations.AddField(
            model_name='scheme',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Create Run model
        migrations.CreateModel(
            name='Run',
            fields=[
                ('id', models.CharField(
                    default=main.models.generate_run_id,
                    editable=False,
                    max_length=32,
                    primary_key=True,
                    serialize=False,
                )),
                ('status', models.CharField(
                    choices=[
                        ('running', 'Running'),
                        ('completed', 'Completed'),
                        ('failed', 'Failed'),
                    ],
                    default='running',
                    max_length=20,
                )),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('experiment', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='runs',
                    to='main.experiment',
                )),
            ],
            options={
                'db_table': 'runs',
            },
        ),
        migrations.AddIndex(
            model_name='run',
            index=models.Index(fields=['experiment', '-started_at'], name='runs_experim_started_idx'),
        ),
    ]
