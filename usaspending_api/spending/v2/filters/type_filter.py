from datetime import datetime

from django.db.models import Sum

from usaspending_api.awards.models import FinancialAccountsByAwards
from usaspending_api.common.exceptions import InvalidParameterException
from usaspending_api.financial_activities.models import FinancialAccountsByProgramActivityObjectClass
from usaspending_api.spending.v2.filters.fy_filter import fy_filter
from usaspending_api.spending.v2.filters.spending_filter import spending_filter
from usaspending_api.spending.v2.views.explorer import Explorer


def type_filter(_type, filters):
    total = None
    fiscal_quarter = None
    fiscal_date = None

    _types = ['budget_function', 'budget_subfunction', 'federal_account', 'program_activity', 'object_class',
              'recipient', 'award', 'award_category', 'agency', 'agency_top', 'agency_sub']

    # Validate explorer _type
    if _type is None:
        raise InvalidParameterException('Missing Required Request Parameter, "type": "type"')

    elif _type not in _types:
        raise InvalidParameterException(
            'Type does not have a valid value. '
            'Valid Types: budget_function, budget_subfunction, federal_account, program_activity,'
            'object_class, recipient, award, award_category agency, agency_top, agency_sub')

    # Get fiscal_date and fiscal_quarter
    for key, value in filters.items():
        if key == 'fy':
            if value is not None:
                fiscal_date, fiscal_quarter = fy_filter(value, datetime.now().date())
            else:
                raise InvalidParameterException('Incorrect or Missing Fiscal Year Parameter, "fy": "YYYY"')

    # Recipient, Award Queryset
    alt_set = FinancialAccountsByAwards.objects.all().exclude(
            transaction_obligated_amount__isnull=True).filter(
            submission__reporting_fiscal_quarter=fiscal_quarter).annotate(
            amount=Sum('transaction_obligated_amount'))

    # Base Queryset
    queryset = FinancialAccountsByProgramActivityObjectClass.objects.all().exclude(
            obligations_incurred_by_program_object_class_cpe__isnull=True).filter(
            submission__reporting_fiscal_quarter=fiscal_quarter).annotate(
            amount=Sum('obligations_incurred_by_program_object_class_cpe'))

    # Annotate and get explorer _type results
    exp = Explorer(alt_set, queryset)

    if _type == 'recipient' or _type == 'award' or _type == 'award_category' or _type == 'agency_sub':
        if _type == 'recipient':
            queryset = exp.recipient()
        if _type == 'award':
            queryset = exp.award()
        if _type == 'award_category':
            queryset = exp.award_category()
        if _type == 'agency_sub':
            queryset = exp.awarding_sub_tier_agency()

        # Apply filters to queryset results
        queryset = spending_filter(alt_set, queryset, filters, _type)
        # Total value of filtered results
        total = queryset.aggregate(Sum('transaction_obligated_amount'))
        for key, value in total.items():
            total = value

    else:
        if _type == 'budget_function':
            queryset = exp.budget_function()
        if _type == 'budget_subfunction':
            queryset = exp.budget_subfunction()
        if _type == 'federal_account':
            queryset = exp.federal_account()
        if _type == 'program_activity':
            queryset = exp.program_activity()
        if _type == 'object_class':
            queryset = exp.object_class()
        if _type == 'agency':
            queryset = exp.agency()
        if _type == 'agency_top':
            queryset = exp.awarding_top_tier_agency()

        # Apply filters to queryset results
        queryset = spending_filter(alt_set, queryset, filters, _type)
        # Total value of filtered results
        total = queryset.aggregate(Sum('obligations_incurred_by_program_object_class_cpe'))
        for key, value in total.items():
            total = value

    results = {
        'total': total,
        'end_date': fiscal_date,
        'results': queryset
    }

    return results
