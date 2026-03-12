from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0007_nullable_scheme_child_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="building",
            name="eem_energy_savings",
            field=models.DecimalField(decimal_places=2, max_digits=14),
        ),
    ]
