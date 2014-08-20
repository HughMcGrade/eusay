'''
Created on 18 Feb 2014

@author: Hugh
'''

from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseForbidden, HttpResponsePermanentRedirect, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth import authenticate as django_authenticate, \
    login as django_login, logout as django_logout
from django.core.urlresolvers import reverse
from django.contrib import messages

from eusay import forms
from .models import *
from .utils import better_slugify

import random
import datetime
from lxml.html.diff import htmldiff

def get_messages(request):
    return render(request, "get_messages.html")
