from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import UserIncome, Source
from userpreferences.models import UserPreference
from django.contrib import messages

from django.core.paginator import Paginator

import json
from django.http import JsonResponse

def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)

@login_required(login_url='/authentication/login/')
def index(request):
    sources = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)

    # Pagination
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)

    currency = UserPreference.objects.get(user=request.user).currency

    context = {
        'sources': sources,
        'income': income,
        'page_obj' : page_obj,
        'currency': currency,
    }

    return render(request, 'income/index.html', context) 

def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':

        amount = request.POST['amount']
        if not amount:
            messages.error(request, f'Amount is required')
            return render(request, 'income/add_income.html', context)

        description = request.POST['description']
        if not description:
            messages.error(request, f'Description is required')
            return render(request, 'income/add_income.html', context)
        
        date = request.POST['income_date']
        source = request.POST['source']

        print(request.POST)

        if date:
            UserIncome.objects.create(owner=request.user, amount=amount, description=description, source=source, date=date)
        else:
            UserIncome.objects.create(owner=request.user, amount=amount, description=description, source=source)
        messages.success(request, f'Record saved successfully')

        return redirect('income')


def edit_income(request, id):
    sources = Source.objects.all()
    income = UserIncome.objects.get(pk=id)
    context = {
        'values' : income,
        'income' : income,
        'sources' : sources
    }

    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, f'Amount is required')
            return render(request, 'income/edit_income.html', context)

        description = request.POST['description']
        if not description:
            messages.error(request, f'Description is required')
            return render(request, 'income/edit_income.html', context)
        
        date = request.POST['income_date']
        source = request.POST['source']

        print(request.POST)

        if date:
            income.owner = request.user
            income.amount = amount
            income.description = description
            income.source = source
            income.date = date
        else:
            income.owner = request.user
            income.amount = amount
            income.description = description
            income.source = source
        income.save()
        messages.success(request, f'Record updated successfully')

        return redirect('income')
       

def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, f'Record removed')
    return redirect('income')