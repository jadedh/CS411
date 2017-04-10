"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from app.forms import ApiForm
from app.models import TestData

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )

import json
from django.http import JsonResponse
from django.core import serializers
def api(request):
    test = ''

    if request.method == 'POST':
        method = request.POST.get('method')
        if (method == 'check'):
            items = TestData.objects.filter(query = request.POST.get('query')).values()
            if (items.count() > 0):
                return JsonResponse({'results': list(items)})
            return JsonResponse({'results': None})
        else:
            query = request.POST['query']
            data = json.loads(request.POST['results'])
            for item in data:
                obj = TestData(
                    query=query,
                    lat=item['lat'],
                    long=item['long']
                )
                obj.save()
        
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/api.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
            'test':test,
        }
    )