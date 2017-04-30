"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from datetime import timedelta
from app.forms import ApiForm
from app.models import QueryData, QueryText, JsonCache, UserData
from googleplaces import GooglePlaces, types, lang
from django.contrib.auth.decorators import login_required
import requests
import json
from django.utils.safestring import mark_safe

def refresh_cache(userid, token):
    r = requests.get('https://api.instagram.com/v1/users/' + userid + '/media/recent/?access_token='+token)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    
    cache = JsonCache.objects.filter(userid = userid)    
    if cache:
        cache.update(json = r.text, timestamp = now)

    else:
        cache = JsonCache(
            userid = userid,
            json = r.text,
            timestamp = now
        )
        cache.save()

    return r.text


@login_required
def home(request):
    """Renders the home page."""

    social = request.user.social_auth.get(provider='instagram')
    token = social.extra_data['access_token']

    user_data = UserData.objects.filter(userid = social.uid)

    if request.method == 'POST':   
        tag = request.POST['tag']
        dist = request.POST['dist']
        loc = request.POST['loc']
 
        if user_data:
            user_data.update(dist = dist, tag = tag, loc = loc)
        else:
            user_data = UserData(
                userid = social.uid,
                dist = dist,
                tag = tag,
                loc = loc
            )
            user_data.save()

    if not user_data:
        user_data = UserData(
            userid = social.uid,
            dist = '',
            tag = '',
            loc = ''
        )
        user_data.save()

    userids = []
    userids.append('5385953857') #jadedh
    userids.append('17025099') #alex_vahid
    userids.append('314279076') #shikhataori 
    userids.append('38461369') #k.annis 
    userids.append('29023929') #saribe0                       

    caches = JsonCache.objects.all()

    if not caches:
        for userid in userids:
            refresh_cache(userid, token)
        caches = JsonCache.objects.all()
                    
            
    return_pics = []
    for cache in caches:
        timestamp = datetime.strptime(cache.timestamp, "%Y-%m-%d %H:%M:%S.%f")
        elapsed = datetime.now() - timestamp
        if elapsed > timedelta(minutes=30):
            cache.json = refresh_cache(str(cache.userid), token)
                    
        jsonObj = json.loads(cache.json)
        if 'data' in jsonObj:
            for pic in jsonObj['data']:
                loc = pic['location']
                if loc and 'latitude' in loc:
                    return_pics.append({'lat' : float(loc['latitude']), 'long' : float(loc['longitude']), 'pic': pic['images']['standard_resolution']['url']})
    
    if request.method == 'POST':           
        return JsonResponse({'results': return_pics})            
                      
    #social = request.user.social_auth.get(provider='instagram')
    #token = social.extra_data['access_token']
    #r = requests.get('https://api.instagram.com/v1/tags/boston/media/recent?access_token='+token)
    #jsonObj = json.loads(r.text)
    #loc = jsonObj['data'][0]['location']
    
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
            'return_pics': mark_safe(json.dumps(return_pics))
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

