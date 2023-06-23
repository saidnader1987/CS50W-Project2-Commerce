from django.contrib import admin
from .models import Listing, Category, Bid, Comment, User

class ListingAdmin(admin.ModelAdmin):
  list_display = ("id", "item", "description", "starting_price", "image_url", "listing_date", "seller", "category", "status")

class BidAdmin(admin.ModelAdmin):
  list_display = ("id", "bidder", "listing", "bid_date", "bid_price")

class CommentAdmin(admin.ModelAdmin):
  list_display = ("id", "listing", "user", "comment", "comment_date")

class CategoryAdmin(admin.ModelAdmin):
  list_display = ("id", "description")

# Register your models here.
admin.site.register(Listing, ListingAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(User)