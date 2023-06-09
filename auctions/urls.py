from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("listing/<int:pk>/", views.listing, name="listing"),
    path("categories/", views.categories, name="categories"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("bid/", views.bid, name="bid"),
    path("watchlist_delete", views.watchlist_delete, name="watchlist_delete"),
    path("listing_delete", views.listing_delete, name="listing_delete"),
    path("create_listing/", views.create_listing, name="create_listing"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register")
]
