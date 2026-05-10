
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db import connection
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404

from .models import Expense, Category


AMOUNT_PLACES = Decimal('0.01')


def parse_amount(value, allow_zero=False):
    try:
        amount = Decimal(value).quantize(AMOUNT_PLACES)
    except (InvalidOperation, TypeError, ValueError):
        return None

    if not amount.is_finite():
        return None

    if amount < 0 or (amount == 0 and not allow_zero):
        return None

    if amount > Decimal('99999999.99'):
        return None

    return amount


def clean_invalid_expense_amounts():
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT id, amount FROM {Expense._meta.db_table}')
        rows = cursor.fetchall()

        for row_id, raw_amount in rows:
            amount = parse_amount(
                str(raw_amount).strip() if raw_amount is not None else '',
                allow_zero=True,
            )
            if amount is None:
                cursor.execute(
                    f'UPDATE {Expense._meta.db_table} SET amount = %s WHERE id = %s',
                    ['0.00', row_id],
                )


def home(request):

    clean_invalid_expense_amounts()

    expenses = Expense.objects.all().order_by('-id')[:10]

    total = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0

    dad_total = Expense.objects.filter(person='Dad').aggregate(total=Sum('amount'))['total'] or 0

    mom_total = Expense.objects.filter(person='Mom').aggregate(total=Sum('amount'))['total'] or 0

    categories = Category.objects.all()

    if request.method == 'POST':

        if 'new_category' in request.POST:

            new_category = request.POST['new_category']

            if new_category:
                Category.objects.create(name=new_category)

            return redirect('/')

        person = request.POST['person']
        category_id = request.POST['category']
        amount = parse_amount(request.POST.get('amount'))
        note = request.POST['note']

        if amount is None:
            messages.error(request, 'Enter a valid amount greater than 0.')
            return redirect('/')

        category = Category.objects.get(id=category_id)

        Expense.objects.create(
            person=person,
            category=category,
            amount=amount,
            note=note
        )

        return redirect('/')
    category_totals = Expense.objects.values(
        'category__name'
    ).annotate(
        total=Sum('amount')
    )
    context = {
        'expenses': expenses,
        'total': total,
        
        'dad_total': dad_total,
        'mom_total': mom_total,
        'category_totals': category_totals,
        'categories': categories
    }

    return render(request, 'home.html', context)


def delete_expense(request, id):

    expense = get_object_or_404(Expense, id=id)

    expense.delete()

    return redirect('/')


