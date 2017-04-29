"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from app.forms import ApiForm
from app.models import QueryData, QueryText
from googleplaces import GooglePlaces, types, lang
from django.contrib.auth.decorators import login_required
import requests
import json

@login_required
def home(request):
    """Renders the home page."""
    social = request.user.social_auth.get(provider='instagram')
    token = social.extra_data['access_token']
    r = requests.get('https://api.instagram.com/v1/tags/boston/media/recent?access_token='+token)
    jsonObj = json.loads(r.text)
    loc = jsonObj['data'][0]['location']
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
    if request.method == 'POST':   
        try:
            q = request.POST['query']
            query_text = QueryText.objects.get(query = q)
            return JsonResponse({'results': list(query_text.querydata_set.all().values())})
        except QueryText.DoesNotExist:
            google_places = GooglePlaces('AIzaSyCYwqirZB73zzrsHF3P7y0XZRX0df2c2TM')
            query_result = google_places.text_search(
                query=q,
                radius=500, 
                lat_lng={'lat': -33.8665433, 'lng': 151.1956316}
            )
            qt = QueryText(
                query = q
            )
            qt.save()
            qt_loaded = QueryText.objects.get(query = q)
            arr = []
            for item in query_result.places:
                lat=item.geo_location['lat']
                long=item.geo_location['lng']
                obj = QueryData(
                    query_id = qt_loaded.id,
                    lat = lat,
                    long = long
                )
                arr.append({'lat' : float(lat), 'long' : float(long)})
                obj.save()
                
            return JsonResponse({'results': arr})
            
        
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/api.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

