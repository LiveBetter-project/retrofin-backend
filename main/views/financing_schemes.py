from decimal import Decimal, InvalidOperation

from django.db.models import Min
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from main.models import (
    Experiment,
    Scheme,
    SchemeBankLoan,
    SchemeEPCFirstOut,
    SchemeEPCGuaranteedSavings,
    SchemeEPCSharedSavings,
    SchemeEquity,
    SchemeEquityCrowdfunding,
    SchemeGreenBondBullet,
    SchemeGreenBondLoan,
    SchemeLendingCrowdfunding,
    SchemeOnBill,
    SchemeOperationalLease,
    SchemeRoyaltyCrowdfunding,
)

# ---------------------------------------------------------------------------
# Static catalog: one entry per scheme_type
# ---------------------------------------------------------------------------

SCHEME_CATALOG = {
    "equity": {
        "key": "equity",
        "name": "Equity",
        "category": "equity",
        "fields": [],
    },
    "bank_loan": {
        "key": "bank_loan",
        "name": "Bank Loan",
        "category": "debt",
        "fields": [
            {"name": "loan_amount", "type": "number", "label": "Loan Amount (€)", "required": True, "minimum": 0},
            {"name": "term_years", "type": "integer", "label": "Term (Years)", "required": True, "minimum": 1},
        ],
    },
    "equity_crowdfunding": {
        "key": "equity_crowdfunding",
        "name": "Equity Crowdfunding",
        "category": "crowdfunding",
        "fields": [
            {"name": "platform_fee_percent", "type": "number", "label": "Platform Fee (0–1)", "required": True, "minimum": 0, "maximum": 1},
            {"name": "crowd_share_percent", "type": "number", "label": "Crowd Share (0–1)", "required": True, "minimum": 0, "maximum": 1},
        ],
    },
    "lending_crowdfunding": {
        "key": "lending_crowdfunding",
        "name": "Lending Crowdfunding",
        "category": "crowdfunding",
        "fields": [
            {"name": "platform_fee_percent", "type": "number", "label": "Platform Fee (0–1)", "required": True, "minimum": 0, "maximum": 1},
            {"name": "loan_amount", "type": "number", "label": "Loan Amount (€)", "required": True, "minimum": 0},
            {"name": "term_years", "type": "integer", "label": "Term (Years)", "required": True, "minimum": 1},
            {"name": "fixed_interest_rate", "type": "number", "label": "Fixed Interest Rate (0–1)", "required": True, "minimum": 0, "maximum": 1},
        ],
    },
    "royalty_crowdfunding": {
        "key": "royalty_crowdfunding",
        "name": "Royalty Crowdfunding",
        "category": "crowdfunding",
        "fields": [
            {"name": "platform_fee_percent", "type": "number", "label": "Platform Fee (0–1)", "required": True, "minimum": 0, "maximum": 1},
            {"name": "loan_amount", "type": "number", "label": "Loan Amount (€)", "required": True, "minimum": 0},
            {"name": "term_years", "type": "integer", "label": "Term (Years)", "required": True, "minimum": 1},
            {"name": "fixed_interest_rate", "type": "number", "label": "Fixed Interest Rate (0–1)", "required": True, "minimum": 0, "maximum": 1},
        ],
    },
    "epc_first_out": {
        "key": "epc_first_out",
        "name": "EPC First-Out",
        "category": "epc",
        "fields": [],
    },
    "epc_shared_savings": {
        "key": "epc_shared_savings",
        "name": "EPC Shared Savings",
        "category": "epc",
        "fields": [
            {"name": "esco_fee_percent", "type": "number", "label": "ESCO Fee (0–1)", "required": True, "minimum": 0, "maximum": 1},
            {"name": "term_years", "type": "integer", "label": "Term (Years)", "required": True, "minimum": 1},
        ],
    },
    "epc_guaranteed_savings": {
        "key": "epc_guaranteed_savings",
        "name": "EPC Guaranteed Savings",
        "category": "epc",
        "fields": [
            {"name": "guaranteed_savings_amount", "type": "number", "label": "Guaranteed Savings Amount (€)", "required": True, "minimum": 0},
            {"name": "term_years", "type": "integer", "label": "Term (Years)", "required": True, "minimum": 1},
        ],
    },
    "green_bond_loan": {
        "key": "green_bond_loan",
        "name": "Green Bond Loan",
        "category": "green_bond",
        "fields": [
            {"name": "loan_amount", "type": "number", "label": "Loan Amount (€)", "required": True, "minimum": 0},
            {"name": "term_years", "type": "integer", "label": "Term (Years)", "required": True, "minimum": 1},
            {"name": "fixed_interest_rate", "type": "number", "label": "Fixed Interest Rate (0–1)", "required": True, "minimum": 0, "maximum": 1},
            {"name": "maintenance_cost", "type": "number", "label": "Maintenance Cost (€/yr)", "required": True, "minimum": 0},
        ],
    },
    "green_bond_bullet": {
        "key": "green_bond_bullet",
        "name": "Green Bond Bullet",
        "category": "green_bond",
        "fields": [
            {"name": "loan_amount", "type": "number", "label": "Loan Amount (€)", "required": True, "minimum": 0},
            {"name": "term_years", "type": "integer", "label": "Term (Years)", "required": True, "minimum": 1},
            {"name": "fixed_interest_rate", "type": "number", "label": "Fixed Interest Rate (0–1)", "required": True, "minimum": 0, "maximum": 1},
            {"name": "maintenance_cost", "type": "number", "label": "Maintenance Cost (€/yr)", "required": True, "minimum": 0},
        ],
    },
    "on_bill": {
        "key": "on_bill",
        "name": "On-Bill Financing",
        "category": "utility",
        "fields": [
            {"name": "fixed_interest_rate", "type": "number", "label": "Fixed Interest Rate (0–1)", "required": True, "minimum": 0, "maximum": 1},
            {"name": "term_years", "type": "integer", "label": "Term (Years)", "required": True, "minimum": 1},
        ],
    },
    "operational_lease": {
        "key": "operational_lease",
        "name": "Operational Lease",
        "category": "lease",
        "fields": [
            {"name": "lease_payment", "type": "number", "label": "Lease Payment (€/yr)", "required": True, "minimum": 0},
            {"name": "term_years", "type": "integer", "label": "Term (Years)", "required": True, "minimum": 1},
        ],
    },
}

# Maps scheme_type → (Django model class, OneToOne related_name, list of field names)
SCHEME_TYPE_MODEL_MAP = {
    "equity":                {"model": SchemeEquity,              "related_name": "equity",               "fields": []},
    "bank_loan":             {"model": SchemeBankLoan,            "related_name": "bank_loan",            "fields": ["loan_amount", "term_years"]},
    "equity_crowdfunding":   {"model": SchemeEquityCrowdfunding,  "related_name": "equity_crowdfunding",  "fields": ["platform_fee_percent", "crowd_share_percent"]},
    "lending_crowdfunding":  {"model": SchemeLendingCrowdfunding, "related_name": "lending_crowdfunding", "fields": ["platform_fee_percent", "loan_amount", "term_years", "fixed_interest_rate"]},
    "royalty_crowdfunding":  {"model": SchemeRoyaltyCrowdfunding, "related_name": "royalty_crowdfunding", "fields": ["platform_fee_percent", "loan_amount", "term_years", "fixed_interest_rate"]},
    "epc_first_out":         {"model": SchemeEPCFirstOut,         "related_name": "epc_first_out",        "fields": []},
    "epc_shared_savings":    {"model": SchemeEPCSharedSavings,    "related_name": "epc_shared_savings",   "fields": ["esco_fee_percent", "term_years"]},
    "epc_guaranteed_savings":{"model": SchemeEPCGuaranteedSavings,"related_name": "epc_guaranteed_savings","fields": ["guaranteed_savings_amount", "term_years"]},
    "green_bond_loan":       {"model": SchemeGreenBondLoan,       "related_name": "green_bond_loan",      "fields": ["loan_amount", "term_years", "fixed_interest_rate", "maintenance_cost"]},
    "green_bond_bullet":     {"model": SchemeGreenBondBullet,     "related_name": "green_bond_bullet",    "fields": ["loan_amount", "term_years", "fixed_interest_rate", "maintenance_cost"]},
    "on_bill":               {"model": SchemeOnBill,              "related_name": "on_bill",              "fields": ["fixed_interest_rate", "term_years"]},
    "operational_lease":     {"model": SchemeOperationalLease,    "related_name": "operational_lease",    "fields": ["lease_payment", "term_years"]},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _serialize_scheme_instance(scheme):
    """Return the dict representation for a Scheme instance."""
    info = SCHEME_TYPE_MODEL_MAP.get(scheme.scheme_type, {})
    related_name = info.get("related_name")
    field_names = info.get("fields", [])

    params = {}
    if related_name and field_names:
        try:
            child = getattr(scheme, related_name)
            for f in field_names:
                val = getattr(child, f)
                # Convert Decimal to float for JSON serialisation
                if isinstance(val, Decimal):
                    val = float(val)
                params[f] = val
        except Exception:
            pass

    catalog_entry = SCHEME_CATALOG.get(scheme.scheme_type, {})
    return {
        "id": scheme.id,
        "scheme_key": scheme.scheme_type,
        "display_name": catalog_entry.get("name", scheme.scheme_type),
        "params": params,
        "created_at": scheme.created_at,
        "updated_at": scheme.updated_at,
    }


def _validate_params(scheme_type, params, check_required=True):
    """
    Validate params against the catalog field definitions.
    Returns a list of error dicts; empty list means valid.
    Pass check_required=False on initial creation to allow empty/draft params.
    """
    catalog = SCHEME_CATALOG.get(scheme_type)
    if catalog is None:
        return [{"path": "scheme_type", "message": f"Unknown scheme type: {scheme_type}"}]

    errors = []
    expected_fields = {f["name"]: f for f in catalog["fields"]}

    # Unknown fields
    for key in params:
        if key not in expected_fields:
            errors.append({"path": f"params.{key}", "message": "Unknown field."})

    # Required fields + range checks
    for fname, fdef in expected_fields.items():
        if check_required and fdef.get("required") and fname not in params:
            errors.append({"path": f"params.{fname}", "message": "This field is required."})
            continue
        if fname in params:
            val = params[fname]
            ftype = fdef.get("type")
            try:
                if ftype == "integer":
                    if not isinstance(val, int) or isinstance(val, bool):
                        raise ValueError
                    num = val
                else:
                    num = float(val)
            except (ValueError, TypeError):
                errors.append({"path": f"params.{fname}", "message": f"Must be a {ftype}."})
                continue
            if "minimum" in fdef and num < fdef["minimum"]:
                errors.append({"path": f"params.{fname}", "message": f"Must be ≥ {fdef['minimum']}."})
            if "maximum" in fdef and num > fdef["maximum"]:
                errors.append({"path": f"params.{fname}", "message": f"Must be ≤ {fdef['maximum']}."})

    return errors


def _create_child(scheme, scheme_type, params):
    """Create the type-specific child model for a new Scheme."""
    info = SCHEME_TYPE_MODEL_MAP[scheme_type]
    child_kwargs = {f: params[f] for f in info["fields"] if f in params}
    info["model"].objects.create(scheme=scheme, **child_kwargs)


def _update_child(scheme, scheme_type, params):
    """Update type-specific child model fields (partial)."""
    info = SCHEME_TYPE_MODEL_MAP[scheme_type]
    related_name = info["related_name"]
    try:
        child = getattr(scheme, related_name)
    except Exception:
        _create_child(scheme, scheme_type, params)
        return

    changed = []
    for f in info["fields"]:
        if f in params:
            setattr(child, f, params[f])
            changed.append(f)
    if changed:
        child.save(update_fields=changed)


# ---------------------------------------------------------------------------
# Catalog ViewSet  –  GET /api/financing-schemes/[{key}/]
# ---------------------------------------------------------------------------

class FinancingSchemeCatalogViewSet(viewsets.ViewSet):
    """
    Read-only catalog of available financing scheme types.
    No authentication required (public reference data).
    """

    def list(self, request):
        items = [
            {"key": v["key"], "name": v["name"], "category": v["category"]}
            for v in SCHEME_CATALOG.values()
        ]
        return Response({"items": items})

    def retrieve(self, request, pk=None):
        entry = SCHEME_CATALOG.get(pk)
        if entry is None:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": f"Scheme '{pk}' not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(entry)


# ---------------------------------------------------------------------------
# Experiment scheme instances  –  /api/experiments/{id}/financing-schemes/
# ---------------------------------------------------------------------------

class ExperimentSchemesViewSet(viewsets.ViewSet):
    """
    CRUD for financing scheme instances attached to an experiment.
    Supports: list, create, partial_update, destroy.
    """

    def _get_experiment(self, request, experiment_id):
        return get_object_or_404(Experiment, id=experiment_id, user=request.user)

    # GET /experiments/{experiment_id}/financing-schemes/
    def list(self, request, experiment_id=None):
        exp = self._get_experiment(request, experiment_id)
        schemes = exp.schemes.order_by("created_at")
        return Response({"items": [_serialize_scheme_instance(s) for s in schemes]})

    # POST /experiments/{experiment_id}/financing-schemes/
    def create(self, request, experiment_id=None):
        exp = self._get_experiment(request, experiment_id)

        scheme_type = request.data.get("scheme_type")
        params = request.data.get("params", {})

        if not scheme_type:
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "scheme_type is required.", "details": []}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if scheme_type not in SCHEME_CATALOG:
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": f"Unknown scheme_type '{scheme_type}'.", "details": []}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # On creation, required fields are not enforced so users can save drafts.
        errors = _validate_params(scheme_type, params, check_required=False)
        if errors:
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "Invalid params.", "details": errors}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        scheme = Scheme.objects.create(experiment=exp, scheme_type=scheme_type)
        _create_child(scheme, scheme_type, params)

        return Response(_serialize_scheme_instance(scheme), status=status.HTTP_201_CREATED)

    # PATCH /experiments/{experiment_id}/financing-schemes/{pk}/
    def partial_update(self, request, experiment_id=None, pk=None):
        exp = self._get_experiment(request, experiment_id)
        scheme = get_object_or_404(Scheme, id=pk, experiment=exp)

        params = request.data.get("params", {})
        errors = _validate_params(scheme.scheme_type, params)
        if errors:
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "Invalid params.", "details": errors}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Cross-entity validation: scheme term must not exceed the shortest building lifetime
        term_years = params.get("term_years")
        if term_years is not None:
            buildings = exp.buildings.all()
            if buildings.exists():
                min_lifetime = buildings.aggregate(min_lt=Min("eem_lifetime"))["min_lt"]
                if min_lifetime is not None and int(term_years) > int(min_lifetime):
                    return Response(
                        {
                            "error": {
                                "code": "VALIDATION_ERROR",
                                "message": (
                                    f"Scheme term ({term_years} yr) exceeds the shortest "
                                    f"building EEM lifetime ({min_lifetime} yr)."
                                ),
                                "details": [
                                    {
                                        "path": "params.term_years",
                                        "message": (
                                            f"Must be ≤ {min_lifetime} "
                                            f"(shortest building EEM lifetime)."
                                        ),
                                    }
                                ],
                            }
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        _update_child(scheme, scheme.scheme_type, params)
        # Touch Scheme so auto_now updated_at is refreshed
        scheme.save(update_fields=["updated_at"])
        scheme.refresh_from_db()
        return Response(_serialize_scheme_instance(scheme))

    # DELETE /experiments/{experiment_id}/financing-schemes/{pk}/
    def destroy(self, request, experiment_id=None, pk=None):
        exp = self._get_experiment(request, experiment_id)
        scheme = get_object_or_404(Scheme, id=pk, experiment=exp)
        scheme.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
