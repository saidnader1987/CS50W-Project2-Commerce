from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("category/<str:category>/", views.listings_of_category, name="listings_of_category"),
    path("seller/<str:seller>/", views.listings_of_seller, name="listings_of_seller"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listings/<int:listing_id>/", views.listings, name="listings"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("categories/", views.categories, name="categories"),
    path("create_listing/", views.create_listing, name="create_listing"),
    path("won_listings/", views.won_listings, name="won_listings"),
    path("closed_listings/", views.closed_listings, name="closed_listings")
]
