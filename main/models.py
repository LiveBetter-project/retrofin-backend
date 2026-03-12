import secrets
from django.contrib.auth.models import AbstractUser
from django.db import models


def generate_experiment_id():
    return "exp_" + secrets.token_hex(8)


def generate_building_id():
    return "bld_" + secrets.token_hex(8)


def generate_scheme_id():
    return "fs_" + secrets.token_hex(8)


def generate_run_id():
    return "run_" + secrets.token_hex(8)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username


class Experiment(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        READY = "ready", "Ready"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.CharField(primary_key=True, max_length=32, default=generate_experiment_id, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="experiments")

    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "experiments"
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"{self.id} ({self.name})"


class Building(models.Model):
    id = models.CharField(primary_key=True, max_length=32, default=generate_building_id, editable=False)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name="buildings")

    name = models.CharField(max_length=200)
    country = models.CharField(max_length=2)  # ISO-3166-1 alpha-2 (e.g. GR)
    region = models.CharField(max_length=120, blank=True, default="")
    year_of_construction = models.PositiveIntegerField()
    floor_area = models.DecimalField(max_digits=12, decimal_places=2)

    # v1 aggregated EEM fields embedded in Building
    eem_capex = models.DecimalField(max_digits=14, decimal_places=2)
    eem_energy_savings = models.DecimalField(max_digits=14, decimal_places=2)  # annual kWh
    eem_maintenance_cost = models.DecimalField(max_digits=14, decimal_places=2)
    eem_lifetime = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "buildings"
        indexes = [
            models.Index(fields=["experiment", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.id} ({self.name})"

class Scheme(models.Model):

    class SchemeType(models.TextChoices):
        EQUITY = "equity", "Equity"
        BANK_LOAN = "bank_loan", "Bank Loan"
        EQUITY_CROWDFUNDING = "equity_crowdfunding", "Equity Crowdfunding"
        LENDING_CROWDFUNDING = "lending_crowdfunding", "Lending Crowdfunding"
        ROYALTY_CROWDFUNDING = "royalty_crowdfunding", "Royalty Crowdfunding"
        EPC_FIRST_OUT = "epc_first_out", "EPC First-Out"
        EPC_SHARED_SAVINGS = "epc_shared_savings", "EPC Shared Savings"
        EPC_GUARANTEED_SAVINGS = "epc_guaranteed_savings", "EPC Guaranteed Savings"
        GREEN_BOND_LOAN = "green_bond_loan", "Green Bond Loan"
        GREEN_BOND_BULLET = "green_bond_bullet", "Green Bond Bullet"
        ON_BILL = "on_bill", "On-Bill Financing"
        OPERATIONAL_LEASE = "operational_lease", "Operational Lease"

    id = models.CharField(primary_key=True, max_length=32, default=generate_scheme_id, editable=False)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name="schemes")
    scheme_type = models.CharField(max_length=100, choices=SchemeType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "schemes"

class SchemeEquity(models.Model):
    scheme = models.OneToOneField(Scheme, on_delete=models.CASCADE, related_name="equity")

    class Meta:
        db_table = "scheme_equity"

class SchemeBankLoan(models.Model):
    scheme = models.OneToOneField(Scheme, on_delete=models.CASCADE, related_name="bank_loan")
    loan_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    term_years = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "scheme_bank_loan"

class SchemeEquityCrowdfunding(models.Model):
    scheme = models.OneToOneField(Scheme, on_delete=models.CASCADE, related_name="equity_crowdfunding")
    platform_fee_percent = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    crowd_share_percent = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)

    class Meta:
        db_table = "scheme_equity_crowdfunding"

class SchemeLendingCrowdfunding(models.Model):
    scheme = models.OneToOneField(Scheme, on_delete=models.CASCADE, related_name="lending_crowdfunding")
    platform_fee_percent = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    loan_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    term_years = models.IntegerField(null=True, blank=True)
    fixed_interest_rate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)

    class Meta:
        db_table = "scheme_lending_crowdfunding"

class SchemeRoyaltyCrowdfunding(models.Model):
    scheme = models.OneToOneField(Scheme, on_delete=models.CASCADE, related_name="royalty_crowdfunding")
    platform_fee_percent = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    loan_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    term_years = models.IntegerField(null=True, blank=True)
    fixed_interest_rate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)

    class Meta:
        db_table = "scheme_royalty_crowdfunding"

class SchemeEPCFirstOut(models.Model):
    scheme = models.OneToOneField(Scheme, on_delete=models.CASCADE, related_name="epc_first_out")

    class Meta:
        db_table = "scheme_epc_first_out"

class SchemeEPCSharedSavings(models.Model):
    scheme = models.OneToOneField(Scheme, on_delete=models.CASCADE, related_name="epc_shared_savings")
    esco_fee_percent = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    term_years = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "scheme_epc_shared_savings"

class SchemeEPCGuaranteedSavings(models.Model):
    scheme = models.OneToOneField(Scheme, on_delete=models.CASCADE, related_name="epc_guaranteed_savings")
    guaranteed_savings_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    term_years = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "scheme_epc_guaranteed_savings"

class SchemeGreenBondLoan(models.Model):
    scheme = models.OneToOneField(Scheme, on_delete=models.CASCADE, related_name="green_bond_loan")
    loan_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    term_years = models.IntegerField(null=True, blank=True)
    fixed_interest_rate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    maintenance_cost = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "scheme_green_bond_loan"

class SchemeGreenBondBullet(models.Model):
    scheme = models.OneToOneField(Scheme, on_delete=models.CASCADE, related_name="green_bond_bullet")
    loan_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    term_years = models.IntegerField(null=True, blank=True)
    fixed_interest_rate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    maintenance_cost = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "scheme_green_bond_bullet"


class SchemeOnBill(models.Model):
    scheme = models.OneToOneField(Scheme, on_delete=models.CASCADE, related_name="on_bill")
    fixed_interest_rate = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    term_years = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "scheme_on_bill"

class SchemeOperationalLease(models.Model):
    scheme = models.OneToOneField(Scheme, on_delete=models.CASCADE, related_name="operational_lease")
    lease_payment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    term_years = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "scheme_operational_lease"

class Run(models.Model):
    class Status(models.TextChoices):
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.CharField(primary_key=True, max_length=32, default=generate_run_id, editable=False)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name="runs")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RUNNING)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "runs"
        indexes = [
            models.Index(fields=["experiment", "-started_at"]),
        ]

    def __str__(self):
        return f"{self.id} ({self.status})"


class SchemeResult(models.Model):
    id = models.CharField(primary_key=True, max_length=32, editable=False)
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name="results")
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="scheme_results")
    # TBD
    # npv = models.DecimalField(max_digits=15, decimal_places=2)
    # irr = models.DecimalField(max_digits=6, decimal_places=4)
    # payback_period_years = models.DecimalField(max_digits=6, decimal_places=2)
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "scheme_results"
        constraints = [
            models.UniqueConstraint(fields=["scheme", "building"], name="unique_result_per_scheme_building")
        ]
        indexes = [
            models.Index(fields=["scheme"]),
            models.Index(fields=["building"]),
        ]

