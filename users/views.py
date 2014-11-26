import random
from slugify import slugify
from datetime import datetime

from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib import messages
from django.conf import settings

from django.contrib.auth import authenticate as django_authenticate, \
    login as django_auth_login
from django.contrib.auth.views import logout as django_logout

from users.models import User
from users.forms import UserForm, NewUserForm

RAND_NAMES = ['Tonja', 'Kaley', 'Bo', 'Tobias', 'Jacqui', 'Lorena', 'Isaac',
              'Adriene', 'Tuan', 'Shanon', 'Georgette', 'Chas', 'Yuonne',
              'Michelina', 'Juliana', 'Odell', 'Juliet', 'Carli', 'Asha',
              'Pearl', 'Kamala', 'Rubie', 'Elmer', 'Taren', 'Salley',
              'Raymonde', 'Shelba', 'Alison', 'Wilburn', 'Katy',
              'Denyse', 'Rosemary', 'Brooke', 'Carson', 'Tashina', 'Kristi',
              'Aline', 'Yevette', 'Eden', 'Christoper', 'Juana', 'Marcie',
              'Wendell', 'Vonda', 'Dania', 'Sheron', 'Meta', 'Frank', 'Thad',
              'Cherise']

get_rand_name = lambda: random.choice(RAND_NAMES)


def request_login(request):
    messages.add_message(request, messages.INFO,
                         "You must be logged in to do this")
    return HttpResponseRedirect(reverse('frontpage'))


def generate_new_user(request):
    username = get_rand_name()
    if User.objects.filter(username__exact=username).exists():
        user = User.objects.get(username=username)
    else:
        if User.objects.exclude(sid__exact="")\
                       .exclude(sid__exact="Deleted Content").count() == 0:
            # if there are no users with sids, give sid "s1"
            sid = "s1"
        else:
            previous_sid = User.objects.all()\
                                       .exclude(sid__exact="Deleted Content")\
                                       .last().sid
            previous_sid_num = previous_sid[1:]
            new_sid_num = int(previous_sid_num) + 1
            sid = "s" + str(new_sid_num)
        user = User.objects.create_user(username=username, password="",
                                        sid=sid)
        user.slug = slugify(user.username, max_length=100)
        user.save()
    user = django_authenticate(username=user.username, password="")
    if user is not None and settings.ENVIRONMENT == "dev":
        # django.contrib.auth.login only works in development environments. In
        # production, use django.contrib.auth.views.login.
        django_auth_login(request, user)
        return user
    else:
        raise Exception("User is None, or you tried to generate a new user "
                        "in a production environment!")


def profile(request, slug):
    try:
        user = User.objects.get(slug=slug)
    except:
        raise Http404
    if request.user == user:
        # own profile
        if request.method == "POST":
            # if the form as been submitted
            form = UserForm(request.POST,
                            instance=request.user)
            if form.is_valid():
                form.save()
                url = reverse("user",
                              kwargs={"slug": request.user.slug})
                return HttpResponseRedirect(url)
            else:
                return render(request,
                              "own_profile.html",
                              {"profile": user,
                               "form": form})
        form = UserForm(instance=request.user)
        return render(request,
                      "own_profile.html",
                      {'profile': user,
                       'form': form})
    elif user.hasProfile:
        # another's (public) profile
        return render(request,
                      "profile.html",
                      {'profile': user})
    else:
        return render(request,
                      "no_profile.html",
                      {"profile": user})


def logout(request):
    if settings.ENVIRONMENT == "dev":
        if request.user.is_authenticated():
            django_logout(request)
            messages.add_message(request,
                                 messages.SUCCESS,
                                 "You have been logged out.")
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 "You can't log out if you aren't logged "
                                 "in first!")
        return HttpResponseRedirect(reverse("frontpage"))

    elif settings.ENVIRONMENT == "production":
        post_logout_url = "https://www.ease.ed.ac.uk/logout.cgi"
        if request.user.is_authenticated():
            response = django_logout(request,
                                     next_page=post_logout_url)
            # Don't use delete_cookie() here, it doesn't work.
            response.set_cookie('cosign-eucsCosign-eusay.eusa.ed.ac.uk',
                                expires="Thu, 01 Jan 1970 00:00:00 GMT",
                                path="/")
            return response
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 "You can't log out if you aren't logged "
                                 "in first!")
            return HttpResponseRedirect(reverse("frontpage"))


def login(request):
    if settings.ENVIRONMENT == "dev" and request.user.is_authenticated():
        messages.add_message(request,
                     messages.ERROR,
                     "You are already logged in.")
    elif settings.ENVIRONMENT == "dev" and not request.user.is_authenticated():
        generate_new_user(request)
        messages.add_message(request,
                             messages.SUCCESS,
                             "You are now logged in.")
    # If settings.ENVIRONMENT is "production", /login/ will automatically
    # use EASE to login (as long as it's configured to be CosignProtected
    # in Apache).
    if request.user.username == request.user.sid:  # Default username is the sid
        return HttpResponseRedirect(reverse("prepare_new_user"))
    else:
        return HttpResponseRedirect(reverse("frontpage"))


def prepare_new_user(request):
    #if request.user.username != "":
     #   return HttpResponseRedirect(reverse("frontpage"))
    if not request.user.is_authenticated():
        messages.add_message(request,
                             messages.ERROR,
                             "You must be logged in to set a username.")
        return HttpResponseRedirect(reverse("frontpage"))
    form = NewUserForm(request.user)
    if request.method == "POST":
        form = NewUserForm(request.user, request.POST)
        if form.is_valid():
            user = request.user
            user.follows_tags.add(*form.cleaned_data['school_tags'])
            user.follows_tags.add(*form.cleaned_data['other_tags'])
            user.follows_tags.add(*form.cleaned_data['liberation_tags'])
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 "Welcome to eusay!")
            return HttpResponseRedirect(reverse("frontpage"))
    return render(request, "prepare_new_user.html", {"form": form})

def follow_tags_form(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse("frontpage"))
    form = User
