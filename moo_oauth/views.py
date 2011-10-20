from django.shortcuts import render_to_response
from django.template import RequestContext
from moo_api_examples import settings
from moo_api_examples.lib.moo import *


def render(template, variables_dict, request):   
    return render_to_response(template, variables_dict, context_instance=RequestContext(request))


def index(request):
    #if we're already authenticated we don't need to do anything
    if request.session.get('access_token'):
        render('index.html', locals(), request)

    #do the oauth dance. around around we go!
    client = MOOClient(settings.MOO_KEY, settings.MOO_SECRET)
    request_token = client.get_request_token(callback='http://localhost:8000/authorize')
    request.session['request_token'] = request_token
    url = client.get_authorization_url(request_token)
    return render('index.html', locals(), request)
    
    
def authorize(request):
    client = MOOClient(settings.MOO_KEY, settings.MOO_SECRET)
    oauth_verifier = request.GET.get('oauth_verifier', None)
    request_token = request.session.get('request_token')
    access_token = client.get_access_token(request_token, oauth_verifier)
    request.session['access_token'] = access_token
    return render('index.html', locals(), request)

            
def get_pack(request):
    client = MOOClient(settings.MOO_KEY, settings.MOO_SECRET)
    access_token = request.session.get('access_token')

    if not access_token:
        #if we don't have a token, we need to re-authenticate
        return render('no-pack.html', locals(), request)
        
    pack = client.create_empty_pack(request.session.get('access_token'), 'businesscard')
    return render('pack.html', locals(), request)
