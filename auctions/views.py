from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.forms import ModelForm, Textarea
from PIL import Image
import requests

from .models import *

# Create listing form
class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        # Fields in form
        fields = ['item', 'description', 'starting_price','image_url', 'category']
        # Override field labels
        labels = {
                    "image_url": "Image url (optional)",
                    "category": "Category (optional)"
        }
    # Adding html classes to fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['starting_price'].widget.attrs.update({'class': 'form-control'})
        self.fields['image_url'].widget.attrs.update({'class': 'form-control'})
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
    # Validating input
    def clean_starting_price(self):
        if starting_price := self.cleaned_data["starting_price"]:
            # Starting price must be greater than 0
            if starting_price <= 0:
                raise forms.ValidationError("Starting price must be a positive number")
            return starting_price
    def clean_image_url(self):
        if image_url := self.cleaned_data["image_url"]:
            # Url must point to a valid image on the web
            try:
                with Image.open(requests.get(image_url, stream=True).raw) as img:
                    pass
            except:
                raise forms.ValidationError("Url doesn't point to a valid image on the web. You can also leave this field empty")
            else:
                return image_url

# Bid form
class PlaceBidForm(forms.ModelForm):
    # for handling more than one form in same route
    # place_bid = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    class Meta:
        model = Bid
        # Fields in the form
        fields = ['bid_price']

    # Adding html classes to fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bid_price'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Bid'})
        self.fields['bid_price'].label = ""
    # Validating input: Since we need info from Listing model to validate the bid price, we are just ensuring positive numbers here 
    def clean_bid_price(self):
        if bid_price := self.cleaned_data["bid_price"]:
            # Bid price must be greater than 0
            if bid_price <= 0:
                raise forms.ValidationError("Bid must be a positive number")
            return bid_price
        
# Add comment form
class AddCommentForm(forms.ModelForm):
    # for handling more than one form in same route
    # add_comment = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    class Meta:
        model = Comment
        # Fields in the form
        fields = ['comment']
    # Adding html classes to fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs.update({'class': 'form-control'})
        self.fields['comment'].label = ""


def index(request):
    # getting watchlist size if user is authenticated
    user = request.user
    if user.is_authenticated:
        watchlist_count = user.watchlist.count()
    else:
        watchlist_count = None
    # Getting list of listings
    won = []
    closed = []
    active = []
    # getting all listings
    listings = Listing.objects.all()
    # Iterating over all listings
    for listing in listings:
        # If there are bids for this listing
        if bids := listing.bids.all():
            # current price for listing is the max bid
            listing.current_price = bids.latest("id").bid_price
            # if the listing is sold and user is the max bid, then append listing to won list
            if listing.status == "SLD" and user == bids.latest("id").bidder:
                won.append(listing)
        # if there are no bids for this listing, current price is equal to starting price
        else:
            listing.current_price = listing.starting_price
        # If listing is closed or sold and the user is the listing seller, then append listing to closed list
        if listing.status in ["CLS", "SLD"] and listing.seller == user:
            closed.append(listing)
        elif listing.status == "ACT":
            active.append(listing)
    # Check len of won and closed lists
    won_count = len(won)
    closed_count = len(closed)

    # # Getting all active listings with active status
    # listings = Listing.objects.filter(status = "ACT")
    # # Since a listing object does not have its current price, we need to look up the current price inside the bid objects and fetch the latest if the listing has bids, or set the current_price to the starting_price otherwise
    # for listing in listings:
    #     if bids := listing.bids.all():
    #         listing.current_price = bids.latest("id").bid_price
    #     else:
    #         listing.current_price = listing.starting_price
    # # Getting list of won listings
    # won = []
    # # getting all sold listings
    # sold_listings = Listing.objects.filter(status="SLD")
    # # Iterating over all sold listings and checking if user is highest bidder. There has got to be a better way to do this with a complex Django model query, but I couldn't find it
    # for sold_listing in sold_listings:
    #     # bids for this listing
    #     bids = sold_listing.bids.all()
    #     if user == bids.latest("id").bidder:
    #         won.append(sold_listing)
    # won_count = len(won)

    return render(request, "auctions/index.html", {
        "listings":active,
        "watchlist_count": watchlist_count,
        "won_count": won_count,
        "closed_count": closed_count
    })


def listings_of_seller(request, seller):
    # getting watchlist size if user is authenticated
    user = request.user
    if user.is_authenticated:
        watchlist_count = user.watchlist.count()
    else:
        watchlist_count = None
    # Trying to get seller from database
    try:
        seller = User.objects.get(username = seller)
    except User.DoesNotExist:
        # If seller does not exist, redirect to index
        return HttpResponseRedirect(reverse("index"))
    else:
        # Getting list of listings
        won = []
        closed = []
        active = []
        # getting all listings
        listings = Listing.objects.all()
        # Iterating over all listings
        for listing in listings:
            # If there are bids for this listing
            if bids := listing.bids.all():
                # current price for listing is the max bid
                listing.current_price = bids.latest("id").bid_price
                # if the listing is sold and user is the max bid, then append listing to won list
                if listing.status == "SLD" and user == bids.latest("id").bidder:
                    won.append(listing)
            # if there are no bids for this listing, current price is equal to starting price
            else:
                listing.current_price = listing.starting_price
            # If listing is closed or sold and the user is the listing seller, then append listing to closed list
            if listing.status in ["CLS", "SLD"] and listing.seller == user:
                closed.append(listing)
            elif listing.status == "ACT" and listing.seller == seller:
                active.append(listing)
        # Check len of won and closed lists
        won_count = len(won)
        closed_count = len(closed)





        # # Getting all active listings with active status of seller
        # listings = Listing.objects.filter(status = "ACT", seller = seller)
        # # Since a listing object does not have its current price, we need to look up the current price inside the bid objects and fetch the latest if the listing has bids, or set the current_price to the starting_price otherwise
        # for listing in listings:
        #     if bids := listing.bids.all():
        #         listing.current_price = bids.latest("id").bid_price
        #     else:
        #         listing.current_price = listing.starting_price
        # # Getting list of won listings
        # won = []
        # # getting all sold listings
        # sold_listings = Listing.objects.filter(status="SLD")
        # # Iterating over all sold listings and checking if user is highest bidder. There has got to be a better way to do this with a complex Django model query, but I couldn't find it
        # for sold_listing in sold_listings:
        #     # bids for this listing
        #     bids = sold_listing.bids.all()
        #     if user == bids.latest("id").bidder:
        #         won.append(sold_listing)
        # won_count = len(won)





        return render(request, "auctions/index.html", {
            "listings":active,
            "watchlist_count": watchlist_count,
            "seller": seller.username,
            "won_count": won_count,
            "closed_count": closed_count

        })


def listings_of_category(request, category):
    # getting watchlist size if user is authenticated
    user = request.user
    if user.is_authenticated:
        watchlist_count = user.watchlist.count()
    else:
        watchlist_count = None
    # Trying to get category from database
    try:
        category = Category.objects.get(description = category)
    except Category.DoesNotExist:
        # If seller does not exist, redirect to index
        return HttpResponseRedirect(reverse("index"))
    else:
    # Getting list of listings
        won = []
        closed = []
        active = []
        # getting all listings
        listings = Listing.objects.all()
        # Iterating over all listings
        for listing in listings:
            # If there are bids for this listing
            if bids := listing.bids.all():
                # current price for listing is the max bid
                listing.current_price = bids.latest("id").bid_price
                # if the listing is sold and user is the max bid, then append listing to won list
                if listing.status == "SLD" and user == bids.latest("id").bidder:
                    won.append(listing)
            # if there are no bids for this listing, current price is equal to starting price
            else:
                listing.current_price = listing.starting_price
            # If listing is closed or sold and the user is the listing seller, then append listing to closed list
            if listing.status in ["CLS", "SLD"] and listing.seller == user:
                closed.append(listing)
            elif listing.status == "ACT" and listing.category == category:
                active.append(listing)
        # Check len of won and closed lists
        won_count = len(won)
        closed_count = len(closed)




        # # Getting all active listings with active status of seller
        # listings = Listing.objects.filter(status = "ACT", category = category)
        # # Since a listing object does not have its current price, we need to look up the current price inside the bid objects and fetch the latest if the listing has bids, or set the current_price to the starting_price otherwise
        # for listing in listings:
        #     if bids := listing.bids.all():
        #         listing.current_price = bids.latest("id").bid_price
        #     else:
        #         listing.current_price = listing.starting_price
        # # Getting list of won listings
        # won = []
        # # getting all sold listings
        # sold_listings = Listing.objects.filter(status="SLD")
        # # Iterating over all sold listings and checking if user is highest bidder. There has got to be a better way to do this with a complex Django model query, but I couldn't find it
        # for sold_listing in sold_listings:
        #     # bids for this listing
        #     bids = sold_listing.bids.all()
        #     if user == bids.latest("id").bidder:
        #         won.append(sold_listing)
        # won_count = len(won)




        return render(request, "auctions/index.html", {
            "listings":active,
            "watchlist_count": watchlist_count,
            "category": category.description,
            "won_count": won_count,
            "closed_count": closed_count
        })


def categories(request):
    # getting watchlist size if user is authenticated
    user = request.user
    if user.is_authenticated:
        watchlist_count = user.watchlist.count()
    else:
        watchlist_count = None
    categories = Category.objects.all().order_by('description').values()


    # Getting list of won listings and closed listings
    won = []
    closed = []
    # getting all listings
    listings = Listing.objects.all()
    # Iterating over all listings
    for listing in listings:
        # If there are bids for this listing
        if bids := listing.bids.all():
            # if the listing is sold and user is the max bid, then append listing to won list
            if listing.status == "SLD" and user == bids.latest("id").bidder:
                won.append(listing)
        else:
            listing.current_price = listing.starting_price
        # If listing is closed or sold and the user is the listing seller, then append listing to closed list
        if listing.status in ["CLS", "SLD"] and listing.seller == user:
            closed.append(listing)
    # Check len of won and closed lists
    won_count = len(won)
    closed_count = len(closed)



    # # Getting list of won listings
    # won = []
    # # getting all sold listings
    # sold_listings = Listing.objects.filter(status="SLD")
    # # Iterating over all sold listings and checking if user is highest bidder. There has got to be a better way to do this with a complex Django model query, but I couldn't find it
    # for sold_listing in sold_listings:
    #     # bids for this listing
    #     bids = sold_listing.bids.all()
    #     if user == bids.latest("id").bidder:
    #         won.append(sold_listing)
    # won_count = len(won)




    return render(request, "auctions/categories.html", {
        "categories":categories,
        "watchlist_count": watchlist_count,
        "won_count": won_count,
        "closed_count": closed_count
    })

@login_required(login_url='login')
def watchlist(request):
    # getting watchlist size if user is authenticated
    user = request.user
    watchlist = user.watchlist
    if user.is_authenticated:
        watchlist_count = watchlist.count()
    else:
        watchlist_count = None
    # user got here via get
    if request.method == "GET":

        # Getting list of listings
        won = []
        closed = []
        # getting all listings
        listings = Listing.objects.all()
        # Iterating over all listings
        for listing in listings:
            # If there are bids for this listing
            if bids := listing.bids.all():
                # current price for listing is the max bid
                listing.current_price = bids.latest("id").bid_price
                # if the listing is sold and user is the max bid, then append listing to won list
                if listing.status == "SLD" and user == bids.latest("id").bidder:
                    won.append(listing)
            # if there are no bids for this listing, current price is equal to starting price
            else:
                listing.current_price = listing.starting_price
            # If listing is closed or sold and the user is the listing seller, then append listing to closed list
            if listing.status in ["CLS", "SLD"] and listing.seller == user:
                closed.append(listing)
        # Check len of won and closed lists
        won_count = len(won)
        closed_count = len(closed)
        # Getting all active listings with active status
        listings = Listing.objects.filter(watched_by=user)
        # Since a listing object does not have its current price, we need to look up the current price inside the bid objects and fetch the latest if the listing has bids, or set the current_price to the starting_price otherwise
        for listing in listings:
            if bids := listing.bids.all():
                listing.current_price = bids.latest("id").bid_price
            else:
                listing.current_price = listing.starting_price




        # # Getting all active listings with active status
        # listings = Listing.objects.filter(watched_by=user)
        # # Since a listing object does not have its current price, we need to look up the current price inside the bid objects and fetch the latest if the listing has bids, or set the current_price to the starting_price otherwise
        # for listing in listings:
        #     if bids := listing.bids.all():
        #         listing.current_price = bids.latest("id").bid_price
        #     else:
        #         listing.current_price = listing.starting_price
        # # Getting list of won listings
        # won = []
        # # getting all sold listings
        # sold_listings = Listing.objects.filter(status="SLD")
        # # Iterating over all sold listings and checking if user is highest bidder. There has got to be a better way to do this with a complex Django model query, but I couldn't find it
        # for sold_listing in sold_listings:
        #     # bids for this listing
        #     bids = sold_listing.bids.all()
        #     if user == bids.latest("id").bidder:
        #         won.append(sold_listing)
        # won_count = len(won)




        return render(request, "auctions/index.html", {
            "listings":listings,
            "watchlist_count": watchlist_count,
            "watchlist":True,
            "won_count": won_count,
            "closed_count": closed_count
        })
    # user got here via post (Remove from watchlist)
    else:
        listing_id = request.POST["id"]
        try:
            listing = Listing.objects.get(pk=listing_id)
        except Listing.DoesNotExist:
            # If listing does not exist, redirect to index
            return HttpResponseRedirect(reverse("watchlist"))
        else:
            user.watchlist.remove(listing)
            return HttpResponseRedirect(reverse("watchlist"))


@login_required(login_url='login')
def won_listings(request):
    # getting user
    user = request.user
    # getting watchlist size if user is authenticated
    watchlist = user.watchlist
    if user.is_authenticated:
        watchlist_count = watchlist.count()
    else:
        watchlist_count = None
    # Getting list of won listings and closed listings
    won = []
    closed = []
    # getting all listings
    listings = Listing.objects.all()
    # Iterating over all listings
    for listing in listings:
        # If there are bids for this listing
        if bids := listing.bids.all():
            # current price for listing is the max bid
            listing.current_price = bids.latest("id").bid_price
            # if the listing is sold and user is the max bid, then append listing to won list
            if listing.status == "SLD" and user == bids.latest("id").bidder:
                won.append(listing)
        # if there are no bids for this listing, current price is equal to starting price
        else:
            listing.current_price = listing.starting_price
        # If listing is closed or sold and the user is the listing seller, then append listing to closed list
        if listing.status in ["CLS", "SLD"] and listing.seller == user:
            closed.append(listing)
    # Check len of won and closed lists
    won_count = len(won)
    closed_count = len(closed)
    
    return render(request, "auctions/index.html", {
        "listings":won,
        "won": True,
        "watchlist_count": watchlist_count,
        "won_count": won_count,
        "closed_count": closed_count
    })

    # # List of won listings
    # won = []
    # # getting all sold listings
    # sold_listings = Listing.objects.filter(status="SLD")
    # # Iterating over all sold listings and checking if user is highest bidder. There has got to be a better way to do this with a complex Django model query, but I couldn't find it
    # for sold_listing in sold_listings:
    #     # bids for this listing
    #     bids = sold_listing.bids.all()
    #     if user == bids.latest("id").bidder:
    #         sold_listing.current_price = bids.latest("id").bid_price
    #         won.append(sold_listing)
    # won_count = len(won)
    # return render(request, "auctions/index.html", {
    #     "listings":won,
    #     "won": True,
    #     "watchlist_count": watchlist_count,
    #     "won_count": won_count
    # })
    

@login_required(login_url='login')
def closed_listings(request):
    # getting user
    user = request.user
    # getting watchlist size if user is authenticated
    watchlist = user.watchlist
    if user.is_authenticated:
        watchlist_count = watchlist.count()
    else:
        watchlist_count = None
    # Getting list of won listings and closed listings
    won = []
    closed = []
    # getting all listings
    listings = Listing.objects.all()
    # Iterating over all listings
    for listing in listings:
        # If there are bids for this listing
        if bids := listing.bids.all():
            # current price for listing is the max bid
            listing.current_price = bids.latest("id").bid_price
            # if the listing is sold and user is the max bid, then append listing to won list
            if listing.status == "SLD" and user == bids.latest("id").bidder:
                won.append(listing)
        # if there are no bids for this listing, current price is equal to starting price
        else:
            listing.current_price = listing.starting_price
        # If listing is closed or sold and the user is the listing seller, then append listing to closed list
        if listing.status in ["CLS", "SLD"] and listing.seller == user:
            closed.append(listing)
    # Check len of won and closed lists
    won_count = len(won)
    closed_count = len(closed)
    
    return render(request, "auctions/index.html", {
        "listings":closed,
        "closed": True,
        "watchlist_count": watchlist_count,
        "won_count": won_count,
        "closed_count": closed_count
    })

    # # Getting list of won listings
    # won = []
    # # getting all sold listings
    # sold_listings = Listing.objects.filter(status="SLD")
    # # Iterating over all sold listings and checking if user is highest bidder. There has got to be a better way to do this with a complex Django model query, but I couldn't find it
    # for sold_listing in sold_listings:
    #     # bids for this listing
    #     bids = sold_listing.bids.all()
    #     if user == bids.latest("id").bidder:
    #         won.append(sold_listing)
    # won_count = len(won)

    # # Getting list of won listings
    # closed = []
    # # getting all sold listings
    # closed_listings = Listing.objects.exclude(status="ACT").filter(seller=user)
    # for closed_listing in closed_listings:
    #     if bids := closed_listing.bids.all():
    #         closed_listing.current_price = bids.latest("id").bid_price
    #     else:
    #         closed_listing.current_price = closed_listing.starting_price
    #     closed.append(closed_listing)
    # closed_count = len(closed)
    
    # return render(request, "auctions/index.html", {
    #     "listings":closed_listings,
    #     "closed": True,
    #     "watchlist_count": watchlist_count,
    #     "won_count": won_count,
    #     "closed_count": closed_count
    # })


@login_required(login_url='login')
def create_listing(request):
    # getting watchlist size if user is authenticated
    user = request.user
    if user.is_authenticated:
        watchlist_count = user.watchlist.count()
    else:
        watchlist_count = None

    # Getting list of won listings and closed listings
    won = []
    closed = []
    # getting all listings
    listings = Listing.objects.all()
    # Iterating over all listings
    for listing in listings:
        # If there are bids for this listing
        if bids := listing.bids.all():
            # if the listing is sold and user is the max bid, then append listing to won list
            if listing.status == "SLD" and user == bids.latest("id").bidder:
                won.append(listing)
        else:
            listing.current_price = listing.starting_price
        # If listing is closed or sold and the user is the listing seller, then append listing to closed list
        if listing.status in ["CLS", "SLD"] and listing.seller == user:
            closed.append(listing)
    # Check len of won and closed lists
    won_count = len(won)
    closed_count = len(closed)





    # # Getting list of won listings
    # won = []
    # # getting all sold listings
    # sold_listings = Listing.objects.filter(status="SLD")
    # # Iterating over all sold listings and checking if user is highest bidder. There has got to be a better way to do this with a complex Django model query, but I couldn't find it
    # for sold_listing in sold_listings:
    #     # bids for this listing
    #     bids = sold_listing.bids.all()
    #     if user == bids.latest("id").bidder:
    #         won.append(sold_listing)
    # won_count = len(won)


    # User got here via post request
    if request.method == "POST":
        # Getting form data
        form = NewListingForm(request.POST)
        # form validation
        if form.is_valid():
            # Get most of listing model data from form
            listing = form.save(commit=False)
            # Adding user to model data
            listing.seller = request.user
            # Saving to database
            listing.save()
            # Redirect to listings page
            return HttpResponseRedirect(reverse("index"))
        # Form not valid
        else:
            return render(request, "auctions/create_listing.html", {
                "form": form,
                "watchlist_count": watchlist_count,
                "won_count": won_count,
                "closed_count": closed_count
            })
    # User got here via get request
    return render(request, "auctions/create_listing.html", {
        "form": NewListingForm(),
        "watchlist_count": watchlist_count,
        "won_count": won_count,
        "closed_count": closed_count
    })


def listings(request, listing_id):
    # Checking user
    user = request.user
    # Attempt to retrieve listing from database
    try:
        listing = Listing.objects.get(pk=listing_id)
        print(listing)
    except Listing.DoesNotExist:
        # If listing does not exist, redirect to index
        return HttpResponseRedirect(reverse("index"))
    else:
        # Context data for both POST and GET routes

        # Getting list of won listings and closed listings
        won = []
        closed = []
        # getting all listings
        listings = Listing.objects.all()
        # Iterating over all listings
        for info_listing in listings:
            # If there are bids for this listing
            if bids := info_listing.bids.all():
                # if the listing is sold and user is the max bid, then append listing to won list
                if info_listing.status == "SLD" and user == bids.latest("id").bidder:
                    won.append(info_listing)
            else:
                info_listing.current_price = info_listing.starting_price
            # If listing is closed or sold and the user is the listing seller, then append listing to closed list
            if info_listing.status in ["CLS", "SLD"] and info_listing.seller == user:
                closed.append(info_listing)
        # Check len of won and closed lists
        won_count = len(won)
        closed_count = len(closed)



        # # Getting list of won listings
        # won = []
        # # getting all sold listings
        # sold_listings = Listing.objects.filter(status="SLD")
        # # Iterating over all sold listings and checking if user is highest bidder. There has got to be a better way to do this with a complex Django model query, but I couldn't find it
        # for sold_listing in sold_listings:
        #     # bids for this listing
        #     bids = sold_listing.bids.all()
        #     if user == bids.latest("id").bidder:
        #         won.append(sold_listing)
        # won_count = len(won)


        # Getting bid information for this listing
        bids = listing.bids.all()
        # Getting comment information for this listing
        comments = listing.comments.all()
        # if there are bids
        if bids:
            listing.current_price = bids.latest("id").bid_price
            bidden = True
            # Check to see if user is highest bidder
            if user == bids.latest("id").bidder:
                highest_bidder = True
            else:
                highest_bidder = False
            highest = bids.latest("id").bidder
            # Getting bid count
            bid_count = bids.count()
        else:
            listing.current_price = listing.starting_price
            bidden = False
            bid_count = 0
            highest_bidder = False
            highest = None
        # if user is authenticated check if he is seller or if he has this listing in his watchlist
        if user.is_authenticated:
            # getting watchlist size if user is authenticated
            watchlist_count = user.watchlist.count()
            # Check to see if user is the one who posted the listing
            if listing.seller == user:
                listing_seller = True
                watched = False
            # User is not the one who posted the listing
            else:
                listing_seller = False
                # Check to see if listing is in user watchlist
                if listing in user.watchlist.all():
                    watched = True
                else:
                    watched = False
        else:
            listing_seller = False
            watched = False
            watchlist_count = None
            won_count = None
            closed_count = None
        # User got here via POST. POST requests on this route are only allowed if listing status is active and user is logged in
        if request.method == "POST" and user.is_authenticated:
            print("hello")
            # Preventing a seller tinkering with the html adding own listing to or removing own listing from his watchlist, or placing bids on his own listings 
            # Actions allowed for non sellers
            if not listing_seller:
                # Place-bid form
                if 'bid_price'  in request.POST and listing.status == "ACT":
                    # Getting form data
                    form = PlaceBidForm(request.POST)
                    # form validation
                    if form.is_valid():
                        # Get most of bid model data from form
                        bid = form.save(commit=False)
                        # Adding rest of required data to model data
                        bid.bidder = request.user
                        bid.listing = listing
                        bid_price = form.cleaned_data["bid_price"]
                        if bidden == True and bid_price <= listing.current_price:
                            form.add_error('bid_price', 'Bid must be greater than current price')
                            return render(request, "auctions/listing.html", {
                                "listing": listing,
                                "watched": watched,
                                "bid_count": bid_count,
                                "highest_bidder": highest_bidder,
                                "listing_seller": listing_seller,
                                "bid_form": form,
                                "comments": comments,
                                "comment_form": AddCommentForm(),
                                "watchlist_count": watchlist_count,
                                "won_count": won_count,
                                "closed_count": closed_count,
                                "highest": highest
                            }) 
                        elif bidden == False and bid_price < listing.current_price:
                            form.add_error('bid_price', 'Bid must be equal or greater than starting price')
                            return render(request, "auctions/listing.html", {
                                "listing": listing,
                                "watched": watched,
                                "bid_count": bid_count,
                                "highest_bidder": highest_bidder,
                                "listing_seller": listing_seller,
                                "bid_form": form,
                                "comments": comments,
                                "comment_form": AddCommentForm(),
                                "watchlist_count": watchlist_count,
                                "won_count": won_count,
                                "closed_count": closed_count,
                                "highest": highest
                            }) 
                        else:
                            # Saving to database
                            bid.save()
                            # Redirect to listings page
                            return HttpResponseRedirect(reverse("listings", args=(listing_id,)))
                    # If the form is invalid, re-render the page with existing information.
                    else:
                        return render(request, "auctions/listing.html", {
                            "listing": listing,
                            "watched": watched,
                            "bid_count": bid_count,
                            "highest_bidder": highest_bidder,
                            "listing_seller": listing_seller,
                            "bid_form": form,
                            "comments": comments,
                            "comment_form": AddCommentForm(),
                            "watchlist_count": watchlist_count,
                            "won_count": won_count,
                            "closed_count": closed_count,
                            "highest": highest
                        }) 
                # Add-to-watchlist form
                elif 'watch' in request.POST and listing.status == "ACT" :
                    user.watchlist.add(listing)
                # Remove-from-watchlist form
                elif 'unwatch' in request.POST:
                    user.watchlist.remove(listing)
                # Add a comment
                elif 'comment' in request.POST and listing.status == "ACT" :
                    # Getting form data
                    form = AddCommentForm(request.POST)
                    # form validation
                    if form.is_valid():
                        # Get most of comment model data from form
                        comment = form.save(commit=False)
                        # Adding user to model data
                        comment.user = request.user
                        # Adding listing to model data
                        comment.listing = listing
                        # Saving to database
                        comment.save()
                        # Redirect to listings page
                        return HttpResponseRedirect(reverse("listings", args=(listing_id,)))
                    # If the form is invalid, re-render the page with existing information.
                    else:
                        return render(request, "auctions/listing.html", {
                            "listing": listing,
                            "watched": watched,
                            "bid_count": bid_count,
                            "highest_bidder": highest_bidder,
                            "listing_seller": listing_seller,
                            "bid_form": PlaceBidForm(),
                            "comments": comments,
                            "comment_form": form,
                            "watchlist_count": watchlist_count,
                            "won_count": won_count,
                            "closed_count": closed_count,
                            "highest": highest
                        }) 
                    
            # User is the seller of this listing   
            else:
                # Close listing
                if "close" in request.POST:
                    # No bids. Status -> CLS
                    if bid_count == 0:
                        listing.status = "CLS"
                        listing.save()
                    # At least one bid. Status -> SLD
                    else:
                        listing.status = "SLD"
                        listing.save()
            # Redirect to listings page
            return HttpResponseRedirect(reverse("listings", args=(listing_id,)))

        # User got here via Get
        else:
            print(listing)
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "watched": watched,
                "bid_count": bid_count,
                "highest_bidder": highest_bidder,
                "listing_seller": listing_seller,
                "bid_form": PlaceBidForm(),
                "comments": comments,
                "comment_form": AddCommentForm(),
                "watchlist_count": watchlist_count,
                "won_count": won_count,
                "closed_count": closed_count,
                "highest": highest
            }) 


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        print(request.body)
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
