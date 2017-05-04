"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from datetime import timedelta
from app.forms import ApiForm
from app.models import JsonCache, UserData
from googleplaces import GooglePlaces, types, lang
from django.contrib.auth.decorators import login_required
import requests
import json
from django.utils.safestring import mark_safe
from math import sin, cos, sqrt, atan2, radians

def distance(lat1,lon1,lat2,lon2):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance

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
        lim = request.POST['lim']
 
        if user_data:
            user_data.update(dist = dist, tag = tag, loc = loc, lim = lim)
            user_data = user_data[0]
        else:
            user_data = UserData(
                userid = social.uid,
                dist = dist,
                tag = tag,
                loc = loc,
                lim = lim
            )
            user_data.save()

    if not user_data:
        user_data = UserData(
            userid = social.uid,
            dist = '',
            tag = '',
            loc = '',
            lim = ''
        )
        user_data.save()
    elif not request.method == 'POST':
        user_data = user_data[0]

    userids = []
    userids.append('5385953857') #jadedh
    userids.append('17025099') #alex_vahid
    userids.append('314279076') #shikhataori 
    userids.append('38461369') #k.annis 
    userids.append('29023929') #saribe0    
    userids.append('175984836') #emily_achter                 

    caches = JsonCache.objects.all()

    if not caches:
        for userid in userids:
            refresh_cache(userid, token)
        caches = JsonCache.objects.all()


    lat = "42.3601" #Boston
    long = "-71.057" 

    if user_data.loc:
        google_places = GooglePlaces('AIzaSyCYwqirZB73zzrsHF3P7y0XZRX0df2c2TM')
        places = google_places.text_search(
            query=user_data.loc,
        )
    
        if places:
            lat = places.places[0].geo_location['lat']
            long = places.places[0].geo_location['lng']
    elif request.method == 'POST':
        lat = request.POST['lat']
        long = request.POST['long']
                    
            
    return_pics = []
    for cache in caches:
        timestamp = datetime.strptime(cache.timestamp, "%Y-%m-%d %H:%M:%S.%f")
        elapsed = datetime.now() - timestamp
        if elapsed > timedelta(minutes=15):
            cache.json = refresh_cache(str(cache.userid), token)

                    
        jsonObj = json.loads(cache.json)
        if 'data' in jsonObj:
            for pic in jsonObj['data']:
                if user_data.lim and len(return_pics) >= int(user_data.lim):
                    break
                if user_data.tag:  
                    tag_exists = False
                    if pic['tags']:              
                        for tag in pic['tags']:
                            if user_data.tag in tag:
                                tag_exists = True
                    if not tag_exists:
                        continue
                    
                loc = pic['location']
                if loc and 'latitude' in loc:
                    if user_data.dist:           
                        if distance(float(loc['latitude']),float(loc['longitude']),float(lat),float(long)) > float(user_data.dist):
                            continue
                    if 'caption' in pic and pic['caption']:
                        caption = pic['caption']['text']
                    return_pics.append({'lat' : float(loc['latitude']), 'long' : float(loc['longitude']), 'pic': pic['images']['standard_resolution']['url'], 'caption': caption.replace("\'", "") })

    if request.method == 'POST':           
        return JsonResponse({'results': return_pics,'lat':float(lat),'long':float(long)})            
                      
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
            'return_pics': mark_safe(json.dumps({'results': return_pics,'lat':float(lat),'long':float(long)})),
            'tag':user_data.tag,
            'loc':user_data.loc,
            'dist':user_data.dist,
            'lim':user_data.lim
            
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
#    if request.method == 'POST':   
#        try:
#            q = request.POST['query']
#            query_text = QueryText.objects.get(query = q)
#            return JsonResponse({'results': list(query_text.querydata_set.all().values())})
#        except QueryText.DoesNotExist:
#            google_places = GooglePlaces('AIzaSyCYwqirZB73zzrsHF3P7y0XZRX0df2c2TM')
#            query_result = google_places.text_search(
#                query=q,
#                radius=500, 
#                lat_lng={'lat': -33.8665433, 'lng': 151.1956316}
#            )
#            qt = QueryText(
#                query = q
#            )
#            qt.save()
#            qt_loaded = QueryText.objects.get(query = q)
#            arr = []
#            for item in query_result.places:
#                lat=item.geo_location['lat']
#                long=item.geo_location['lng']
#                obj = QueryData(
#                    query_id = qt_loaded.id,
#                    lat = lat,
#                    long = long
#                )
#                arr.append({'lat' : float(lat), 'long' : float(long)})
#                obj.save()
                
#            return JsonResponse({'results': arr})
            
        
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/api.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

