from turtle import title
from unicodedata import category
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime, date
from django.utils import timezone


class User(AbstractUser):
    # references Listing with a string because it hasn't been assigned up to this point
    # A listing can only be watched once by a user. A user may have different listings in its watchlist. Model does not let you to insert the same listing twice
    watchlist = models.ManyToManyField("Listing", blank=True, related_name="watched_by") 


class Listing(models.Model):

    item = models.CharField(max_length=64)
    description = models.TextField(max_length=800)
    starting_price = models.FloatField()
    image_url = models.CharField(max_length = 800, blank = True, null = True)
    listing_date = models.DateTimeField(default=timezone.now)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")

    category = models.ForeignKey("Category", on_delete=models.CASCADE, blank = True, null = True, related_name="listings")
    ACTIVE = 'ACT'
    CLOSED = 'CLS'
    SOLD = 'SLD'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (CLOSED, 'Closed'),
        (SOLD, 'Sold'),
    ]
    status = models.CharField(
        max_length=3,
        choices=STATUS_CHOICES,
        default=ACTIVE,
    )
    # status = models.ForeignKey("Status", on_delete=models.CASCADE, related_name="Listings")
    def __str__(self):
        return f"{self.item}: {self.description}, listed by {self.seller} at a starting price of ${self.starting_price}"


class Category(models.Model):
    description = models.CharField(max_length=64)
    def __str__(self):
        return f"{self.description}"


class Bid(models.Model):
    # In contrast to watchlist, a user may bid for the same listing many times with this model
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bid_date = models.DateTimeField(default=timezone.now)
    bid_price = models.FloatField()
    def __str__(self):
        return f"{self.bidder} bade for listing: {self.listing}, a price of: ${self.bid_price} on {self.bid_date}"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField(max_length=800)
    comment_date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"{self.user} made a comment for listing: {self.listing}: '{self.comment}' on {self.comment_date}"
