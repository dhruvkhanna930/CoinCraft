from django.shortcuts import render
import os
import json
from django.conf import settings
from .models import UserPreference
from django.contrib import messages

def index(request):
    currency_data = []
    file_path  = os.path.join(settings.BASE_DIR, 'currencies.json')

    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        for k,v in data.items():
            currency_data.append({'name': k, 'value': v})

    # import pdb   #debugger method
    # pdb.set_trace()
            
    context = {
        'currencies' : currency_data,
    }

    exists = UserPreference.objects.filter(user=request.user).exists()
    user_preferences = None
    if exists:
        user_preferences = UserPreference.objects.get(user=request.user)
        context['user_preferences'] = user_preferences
    if request.method == 'GET':
        return render(request, 'preferences/index.html', context)
    else:    #that is POST
        # if 'currency' in request.POST:
        #     currency = request.POST['currency']
        print(request.POST['currency'])
        curreny = request.POST["currency"]
        # import pdb   #debugger method
        # pdb.set_trace()

        if exists:
            user_preferences.currency = curreny
            user_preferences.save()
        else:
            UserPreference.objects.create(user=request.user, currency=curreny)
        context['user_preferences'] = user_preferences
        messages.success(request, f'Changes saved')
        return render(request, 'preferences/index.html', context)
    