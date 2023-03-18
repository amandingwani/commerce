from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Listing
from .forms import *

def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", context= {
        'listings': listings
    })

def listing(request, pk):
    try:
        listing = Listing.objects.get(id=pk)
    except ObjectDoesNotExist:
        listing = None
    return render(request, "auctions/listing.html", context= {
        'listing': listing
    })

def categories(request):
    return render(request, "auctions/index.html")

@login_required
def watchlist(request):
    return render(request, "auctions/index.html")

@login_required
def create_listing(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ListingForm(request.POST, request.FILES)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # Save the form data into the database
            listing = Listing(
                user = User.objects.get(pk=request.user.id),
                name = form.cleaned_data['name'],
                original_price = form.cleaned_data['original_price'],
                description = form.cleaned_data['description'],
                image = form.cleaned_data['image'],
                category = form.cleaned_data['category']
            )
            listing.save()

            # redirect to the new listing:
            return HttpResponse('TODO')
        else:
            return render(request, "auctions/create_listing.html", context= {
                "form": form,
                "errors": form.errors.as_json()
            })

    else:
        form = ListingForm()
        return render(request, "auctions/create_listing.html", context= {
            "form": form
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
