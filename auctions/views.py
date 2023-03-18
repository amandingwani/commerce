from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from .models import *
from .forms import *

def index(request):
    category_id = request.GET.get('category', default = None)
    if category_id:
        listings = Listing.objects.filter(category=category_id)
        try:
            message = Category.objects.get(id=category_id)
        except ObjectDoesNotExist:
            message = "Invalid category"
    else:
        listings = Listing.objects.all()
        message = None

    return render(request, "auctions/index.html", context= {
        'message': message,
        'listings': listings
    })

def listing(request, pk):
    try:
        listing = Listing.objects.get(id=pk)
    except ObjectDoesNotExist:
        listing = None

    if listing:
        try:
            watchlist_obj = Watchlist.objects.get(user=request.user.id, listing=listing)
        except ObjectDoesNotExist:
            watchlist_obj = None
    else:
        watchlist_obj = None

    return render(request, "auctions/listing.html", context= {
        'listing': listing,
        "watchlist_obj": watchlist_obj
    })

def categories(request):
    try:
        categories = Category.objects.all()
    except ObjectDoesNotExist:
        categories = None
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

@login_required
def watchlist(request):
    if request.method == "POST":
        listing_id = request.POST.get('listing_id', default = None)
        if listing_id:
            try:
                listing_obj = Listing.objects.get(id=listing_id)
                user_obj = request.user
                try:
                    w = Watchlist.objects.get(user=user_obj, listing=listing_obj)
                    return HttpResponseRedirect(reverse('listing', args=[listing_id]))
                except ObjectDoesNotExist:
                    pass
                w = Watchlist(user=user_obj, listing=listing_obj)
                w.save()
                return HttpResponseRedirect(reverse('listing', args=[listing_id]))
            except ObjectDoesNotExist:
                pass

        return render(request, "auctions/index.html", context= {
        'message': "Adding to watchlist failed",
        })
    else:
        try:
            watchlists = Watchlist.objects.filter(user=request.user)
            listings = []
            for watchlist in watchlists:
                listings.append(watchlist.listing)
        except ObjectDoesNotExist:
            listings = None
        return render(request, "auctions/index.html", context= {
            'message': "Watchlist",
            'listings': listings
        })
    
@login_required
def watchlist_delete(request):
    if request.method == "POST":
        listing_id = request.POST.get('listing_id', default = None)
        if listing_id:
            try:
                listing_obj = Listing.objects.get(id=listing_id)
                user_obj = request.user
                try:
                    w = Watchlist.objects.get(user=user_obj, listing=listing_obj)
                    w.delete()
                except ObjectDoesNotExist:
                    pass
            except ObjectDoesNotExist:
                pass
            return HttpResponseRedirect(reverse('listing', args=[listing_id]))

        return render(request, "auctions/index.html", context= {
        'message': "Deleting from watchlist failed",
        })
    else:
        return HttpResponseRedirect(reverse('index'))

@login_required
def bid(request):
    if request.method == "POST":
        bid_value = request.POST.get('bid_value', default = None)
        try:
            bid_value = int(bid_value)
        except ValueError:
            return render(request, "auctions/index.html", context= {
            'message': "Error, bidding amount entered was invalid.",
            })

        listing_id = request.POST.get('listing_id', default = None)
        if listing_id:
            try:
                listing_obj = Listing.objects.get(id=listing_id)
                user_obj = request.user
            except ObjectDoesNotExist:
                return HttpResponseRedirect(reverse('listing', args=[listing_id]))
            
            # bid amount check
            if listing_obj.bids.first():
                max_bid = listing_obj.bids.first().bid_price
            else:
                max_bid = listing_obj.original_price
            
            if bid_value <= max_bid:
                return render(request, "auctions/index.html", context= {
                'message': "Error, bidding amount entered was less than or equal to the current bid.",
                })

            Bid(listing=listing_obj, user=user_obj, bid_price=bid_value).save()

            return HttpResponseRedirect(reverse('listing', args=[listing_id]))
            
        return render(request, "auctions/index.html", context= {
        'message': "Placing bid failed",
        })
    else:
        return HttpResponseRedirect(reverse('index'))

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
            return HttpResponseRedirect(reverse('listing', args=[listing.id]))
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

@login_required
def listing_delete(request):
    if request.method == "POST":
        listing_id = request.POST.get('listing_id', default = None)
        if listing_id:
            try:
                listing_obj = Listing.objects.get(id=listing_id)
                user_obj = request.user
                if (listing_obj.user.id == user_obj.id):
                    bid = listing_obj.bids.first()
                    # delete listing
                    listing_obj.delete()
                    if bid:
                        message = f"Successfully closed the listing with buyer {bid.user} and bid price {bid.bid_price}"
                    else:
                        message = "Successfully closed the listing."
                    return render(request, "auctions/index.html", context= {
                        'message': message
                        })
            except ObjectDoesNotExist:
                pass

        return render(request, "auctions/index.html", context= {
        'message': "Closing listing failed",
        })
    else:
        return HttpResponseRedirect(reverse('index'))

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
