from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0006_rename_runs_experim_started_idx_runs_experim_b6b4df_idx"),
    ]

    operations = [
        # SchemeBankLoan
        migrations.AlterField(
            model_name="schemebankloan",
            name="loan_amount",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name="schemebankloan",
            name="term_years",
            field=models.IntegerField(blank=True, null=True),
        ),
        # SchemeEquityCrowdfunding
        migrations.AlterField(
            model_name="schemeequitycrowdfunding",
            name="platform_fee_percent",
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name="schemeequitycrowdfunding",
            name="crowd_share_percent",
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=6, null=True),
        ),
        # SchemeLendingCrowdfunding
        migrations.AlterField(
            model_name="schemelendingcrowdfunding",
            name="platform_fee_percent",
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name="schemelendingcrowdfunding",
            name="loan_amount",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name="schemelendingcrowdfunding",
            name="term_years",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="schemelendingcrowdfunding",
            name="fixed_interest_rate",
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=6, null=True),
        ),
        # SchemeRoyaltyCrowdfunding
        migrations.AlterField(
            model_name="schemeroyaltycrowdfunding",
            name="platform_fee_percent",
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name="schemeroyaltycrowdfunding",
            name="loan_amount",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name="schemeroyaltycrowdfunding",
            name="term_years",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="schemeroyaltycrowdfunding",
            name="fixed_interest_rate",
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=6, null=True),
        ),
        # SchemeEPCSharedSavings
        migrations.AlterField(
            model_name="schemeepcsharedsavings",
            name="esco_fee_percent",
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name="schemeepcsharedsavings",
            name="term_years",
            field=models.IntegerField(blank=True, null=True),
        ),
        # SchemeEPCGuaranteedSavings
        migrations.AlterField(
            model_name="schemeepcguaranteedsavings",
            name="guaranteed_savings_amount",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name="schemeepcguaranteedsavings",
            name="term_years",
            field=models.IntegerField(blank=True, null=True),
        ),
        # SchemeGreenBondLoan
        migrations.AlterField(
            model_name="schemegreenbondloan",
            name="loan_amount",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name="schemegreenbondloan",
            name="term_years",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="schemegreenbondloan",
            name="fixed_interest_rate",
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name="schemegreenbondloan",
            name="maintenance_cost",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True),
        ),
        # SchemeGreenBondBullet
        migrations.AlterField(
            model_name="schemegreenbondbullet",
            name="loan_amount",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name="schemegreenbondbullet",
            name="term_years",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="schemegreenbondbullet",
            name="fixed_interest_rate",
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name="schemegreenbondbullet",
            name="maintenance_cost",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True),
        ),
        # SchemeOnBill
        migrations.AlterField(
            model_name="schemeonbill",
            name="fixed_interest_rate",
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name="schemeonbill",
            name="term_years",
            field=models.IntegerField(blank=True, null=True),
        ),
        # SchemeOperationalLease
        migrations.AlterField(
            model_name="schemeoperationallease",
            name="lease_payment",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name="schemeoperationallease",
            name="term_years",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
