from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.category

# model for the active listings
class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    original_price = models.FloatField()
    description = models.TextField(max_length=1000, blank=True)
    image = models.ImageField(upload_to='productImages/')
    created = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, related_name='products')

    def __str__(self) -> str:
        return self.name
    
class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(max_length=1000)

    def __str__(self) -> str:
        return self.comment[:25] + '...'
    
class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_price = models.FloatField()

    def __str__(self) -> str:
        return str(self.bid_price) + ' | ' + str(self.listing)
    
    class Meta:
        ordering = ['-bid_price']
    
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)