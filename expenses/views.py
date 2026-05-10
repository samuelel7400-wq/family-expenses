
from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense, Category
from django.db.models import Sum


def home(request):

    expenses = Expense.objects.all().order_by('-date')

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
        amount = request.POST['amount']
        note = request.POST['note']

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


