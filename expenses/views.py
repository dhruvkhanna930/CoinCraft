from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Category, Expense
from userpreferences.models import UserPreference
from django.contrib import messages

from django.core.paginator import Paginator

import json
from django.http import JsonResponse

import datetime


def search_expense(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)
    

@login_required(login_url='/authentication/login/')
def index(request):
    catgories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)

    # Pagination
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)

    currency = UserPreference.objects.get(user=request.user).currency

    context = {
        'categories': catgories,
        'expenses': expenses,
        'page_obj' : page_obj,
        'currency': currency,
    }

    return render(request, 'expenses/index.html', context) 

def add_expense(request):
    catgories = Category.objects.all()
    context = {
        'categories': catgories,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':

        amount = request.POST['amount']
        if not amount:
            messages.error(request, f'Amount is required')
            return render(request, 'expenses/add_expense.html', context)

        description = request.POST['description']
        if not description:
            messages.error(request, f'Description is required')
            return render(request, 'expenses/add_expense.html', context)
        
        date = request.POST['expense_date']
        category = request.POST['category']

        print(request.POST)

        if date:
            Expense.objects.create(owner=request.user, amount=amount, description=description, category=category, date=date)
        else:
            Expense.objects.create(owner=request.user, amount=amount, description=description, category=category)
        messages.success(request, f'Expense saved successfully')

        return redirect('expenses')

def edit_expense(request, id):
    catgories = Category.objects.all()
    expense = Expense.objects.get(pk=id)
    context = {
        'values' : expense,
        'expense' : expense,
        'categories' : catgories
    }

    if request.method == 'GET':
        return render(request, 'expenses/edit_expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, f'Amount is required')
            return render(request, 'expenses/edit_expense.html', context)

        description = request.POST['description']
        if not description:
            messages.error(request, f'Description is required')
            return render(request, 'expenses/edit_expense.html', context)
        
        date = request.POST['expense_date']
        category = request.POST['category']

        print(request.POST)

        if date:
            expense.owner = request.user
            expense.amount = amount
            expense.description = description
            expense.category = category
            expense.date = date
        else:
            expense.owner = request.user
            expense.amount = amount
            expense.description = description
            expense.category = category
        expense.save()
        messages.success(request, f'Expense updated successfully')

        return redirect('expenses')
       

def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, f'Expense removed')
    return redirect('expenses')


def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=6*30)
    expenses = Expense.objects.filter(owner=request.user, date__gte = six_months_ago, date__lte = todays_date)

    finalrep = {}

    def get_category(expense):
        return expense.category
    
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount
    
    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data':finalrep}, safe=False)


def stats_view(request):
    return render(request, 'expenses/stats.html')