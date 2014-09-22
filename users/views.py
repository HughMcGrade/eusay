import random
from slugify import slugify

from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.conf import settings

from django.contrib.auth import authenticate as django_authenticate, \
    login as django_auth_login
from django.contrib.auth.views import logout as django_logout

from users.models import User
from users.forms import UserForm, UsernameForm

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


def add_user(request):
    user = generate_new_user(request)
    return HttpResponse(user.username)


# TODO: remove this, since it's for debugging
def get_users(request):
    users = User.objects.all()
    s = "Current user is " + request.user.username + "<br />"
    for user in users:
        s = s + user.username + ", "
    return HttpResponse(s)


def profile(request, slug):
    user = User.objects.get(slug=slug)
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
                messages.add_message(request,
                                     messages.ERROR,
                                     "That username is unavailable or not "
                                     "allowed.")
                # error_msg = "That username is unavailable."
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


# Temporary for debugging
# TODO: remove this when users + mods are implemented
def make_mod(request):
    if not request.user.is_authenticated():
        return request_login(request)
    request.user.isModerator = True
    request.user.save()
    messages.add_message(request, messages.INFO, "You are now a moderator")
    return HttpResponseRedirect(reverse('frontpage'))


def make_staff(request):
    if not request.user.is_authenticated():
        return request_login(request)
    request.user.userStatus = "Staff"
    request.user.save()
    messages.add_message(request, messages.INFO, "You are now EUSA Staff")
    return HttpResponseRedirect(reverse('frontpage'))


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
            response.delete_cookie('cosign-eucsCosign-eusay.eusa.ed.ac.uk',
                                   domain="eusay.eusa.ed.ac.uk")
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
        return HttpResponseRedirect(reverse("setusername"))
    else:
        return HttpResponseRedirect(reverse("frontpage"))


def setusername(request):
    #if request.user.username != "":
     #   return HttpResponseRedirect(reverse("frontpage"))
    if request.method == "POST":
        form = UsernameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 "You've set your username. "
                                 "Welcome to eusay!")
            return HttpResponseRedirect(reverse("frontpage"))
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 "That username is unavailable or not "
                                 "allowed. Please try another one.")
            return HttpResponseRedirect(reverse("setusername"))
    form = UsernameForm(instance=request.user,
                        initial={"username": ""})
    return render(request, "setusername.html", {"form": form})
